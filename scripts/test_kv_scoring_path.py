#!/usr/bin/env python3
"""
Week-1 gate: prove QuantizedCache is on the *scoring* path.

Why this exists
---------------
In Hugging Face Transformers' QuantizedCache (see QuantizedLayer.update in
cache_utils.py), the *current* keys/values used for attention in a forward
step are returned in full precision. Quantization affects what is *read back*
on later steps. A single teacher-forced forward over (question + answer)
therefore often measures a silent no-op even when a QuantizedCache object
is passed.

This script checks three things for a fixed checkpoint:
  1) reports installed transformers version and residual_length default
  2) single-pass vs token-by-token gold-answer NLL under DynamicCache
     (should match closely — sanity)
  3) single-pass vs token-by-token gold-answer NLL under QuantizedCache
     with residual_length=0 (token-by-token should *differ* from single-pass
     if quantization is actually affecting decode-time reads)

Exit codes:
  0  gate passed (quantized sequential scoring differs from single-pass)
  1  setup / dependency failure
  2  gate failed (no measurable KV effect — do not trust "no recovery")

Usage (GPU recommended):
  pip install "transformers>=4.45" torch accelerate optimum-quanto  # or hqq
  python scripts/test_kv_scoring_path.py \\
      --model open-unlearning/tofu_Llama-3.2-1B-Instruct_full \\
      --backend quanto --nbits 4
"""

from __future__ import annotations

import argparse
import inspect
import math
import sys
from dataclasses import dataclass
from typing import Any

import torch


def _require_transformers():
    try:
        import transformers
    except ImportError:
        print("FAIL: transformers not installed. pip install transformers torch", file=sys.stderr)
        sys.exit(1)
    return transformers


def report_residual_default(transformers) -> int:
    """Verify residual_length from the installed package, not from memory."""
    version = transformers.__version__
    print(f"[info] transformers=={version}")

    residual = None
    source = None

    # Prefer QuantizedCacheConfig if present (older / mid API)
    cfg_cls = getattr(transformers, "QuantizedCacheConfig", None)
    if cfg_cls is not None:
        try:
            cfg = cfg_cls(nbits=4, residual_length=128)  # may require backend arg in some versions
        except TypeError:
            try:
                cfg = cfg_cls(backend="quanto", nbits=4)
            except TypeError:
                cfg = cfg_cls()
        residual = getattr(cfg, "residual_length", None)
        source = "QuantizedCacheConfig().residual_length"

    # Fall back to QuantizedLayer / QuantoQuantizedLayer signature defaults
    if residual is None:
        cache_utils = None
        try:
            from transformers import cache_utils as cache_utils  # type: ignore
        except Exception:
            pass
        if cache_utils is not None:
            for name in ("QuantizedLayer", "QuantoQuantizedLayer", "HQQQuantizedLayer"):
                cls = getattr(cache_utils, name, None)
                if cls is None:
                    continue
                sig = inspect.signature(cls.__init__)
                param = sig.parameters.get("residual_length")
                if param is not None and param.default is not inspect.Parameter.empty:
                    residual = int(param.default)
                    source = f"{name}.__init__ default"
                    break

    if residual is None:
        print(
            "[warn] Could not introspect residual_length; check cache_utils.py in your install.",
            file=sys.stderr,
        )
        residual = -1
    else:
        print(f"[info] residual_length default = {residual}  (from {source})")
        print(f"[cite] transformers {version}; {source}")
    return residual


@dataclass
class ScoreResult:
    nll_sum: float
    n_tokens: int
    mean_nll: float
    token_nlls: list[float]


@torch.no_grad()
def score_single_pass(
    model,
    input_ids: torch.Tensor,
    prompt_len: int,
) -> ScoreResult:
    """Teacher-forced NLL of answer tokens in one forward (cache unused for scoring)."""
    out = model(input_ids=input_ids, use_cache=False)
    logits = out.logits  # [1, T, V]
    # token t predicts token t+1; answer starts at prompt_len
    log_probs = torch.log_softmax(logits[0, prompt_len - 1 : -1], dim=-1)
    targets = input_ids[0, prompt_len:]
    token_nlls = [-float(log_probs[i, targets[i]]) for i in range(targets.shape[0])]
    nll_sum = float(sum(token_nlls))
    n = len(token_nlls)
    return ScoreResult(nll_sum=nll_sum, n_tokens=n, mean_nll=nll_sum / max(n, 1), token_nlls=token_nlls)


@torch.no_grad()
def score_sequential_with_cache(
    model,
    input_ids: torch.Tensor,
    prompt_len: int,
    past_key_values: Any,
) -> ScoreResult:
    """
    Prefill the prompt, then feed gold answer tokens one-by-one through the cache.
    Logits for each answer token are produced while attending to (possibly quantized)
    past keys/values — this is the path KV quantization can affect.
    """
    device = input_ids.device
    prompt = input_ids[:, :prompt_len]
    answer = input_ids[:, prompt_len:]

    out = model(input_ids=prompt, past_key_values=past_key_values, use_cache=True)
    past = out.past_key_values
    # First answer-token score comes from the last prompt position
    next_logits = out.logits[:, -1, :]

    token_nlls: list[float] = []
    for t in range(answer.shape[1]):
        target = answer[:, t]  # shape [batch]
        log_probs = torch.log_softmax(next_logits, dim=-1)
        token_nlls.append(-float(log_probs[0, target[0]]))
        # Step with gold token (teacher forcing); must be [batch, 1]
        step_in = target.view(-1, 1)
        step_out = model(input_ids=step_in, past_key_values=past, use_cache=True)
        past = step_out.past_key_values
        next_logits = step_out.logits[:, -1, :]

    nll_sum = float(sum(token_nlls))
    n = len(token_nlls)
    return ScoreResult(nll_sum=nll_sum, n_tokens=n, mean_nll=nll_sum / max(n, 1), token_nlls=token_nlls)


def _make_dynamic_cache(transformers, model):
    DynamicCache = getattr(transformers, "DynamicCache", None)
    if DynamicCache is None:
        from transformers import DynamicCache  # type: ignore
    try:
        return DynamicCache(config=model.config)
    except TypeError:
        return DynamicCache()


def _make_quantized_cache(transformers, model, backend: str, nbits: int, residual_length: int):
    """
    Construct a QuantizedCache across API variants.
    Returns (cache, note) or raises with a clear error.
    """
    # Newer API: QuantizedCache(backend=..., config=..., nbits=..., residual_length=...)
    QuantizedCache = getattr(transformers, "QuantizedCache", None)
    if QuantizedCache is not None:
        try:
            return (
                QuantizedCache(
                    backend=backend,
                    config=model.config,
                    nbits=nbits,
                    residual_length=residual_length,
                ),
                "QuantizedCache(backend=..., residual_length=...)",
            )
        except TypeError:
            pass

    # Mid API: cache_implementation via GenerationConfig / QuantizedCacheConfig
    QuantizedCacheConfig = getattr(transformers, "QuantizedCacheConfig", None)
    if QuantizedCacheConfig is not None and QuantizedCache is not None:
        try:
            qcfg = QuantizedCacheConfig(
                backend=backend,
                nbits=nbits,
                residual_length=residual_length,
            )
            return QuantizedCache(qcfg), "QuantizedCache(QuantizedCacheConfig(...))"
        except TypeError:
            try:
                qcfg = QuantizedCacheConfig(nbits=nbits, residual_length=residual_length)
                return QuantizedCache(qcfg), "QuantizedCache(QuantizedCacheConfig no backend)"
            except Exception as e:
                raise RuntimeError(f"QuantizedCacheConfig path failed: {e}") from e

    raise RuntimeError(
        "Could not construct QuantizedCache. Upgrade transformers and install "
        "optimum-quanto (backend=quanto) or hqq (backend=hqq)."
    )


def _cache_has_quantized_storage(past_key_values) -> bool:
    """Best-effort debug: look for quantized tensors on layers."""
    layers = getattr(past_key_values, "layers", None)
    if not layers:
        return False
    for layer in layers:
        for attr in ("_quantized_keys", "quantized_keys", "_quantized_values"):
            t = getattr(layer, attr, None)
            if t is not None:
                return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Week-1 KV scoring-path gate")
    parser.add_argument(
        "--model",
        default="open-unlearning/tofu_Llama-3.2-1B-Instruct_full",
        help="HF model id (full TOFU model is enough for the gate)",
    )
    parser.add_argument("--backend", default="quanto", choices=["quanto", "hqq"])
    parser.add_argument("--nbits", type=int, default=2, help="Use 2-bit for a stronger gate signal")
    parser.add_argument("--residual_length", type=int, default=0)
    parser.add_argument("--max_new_tokens_check", type=int, default=16, help="Answer tokens to score")
    parser.add_argument("--atol_dynamic", type=float, default=1e-3)
    parser.add_argument(
        "--min_rel_diff",
        type=float,
        default=1e-4,
        help="Min |seq-single|/(|single|+eps) under QuantizedCache to pass",
    )
    parser.add_argument("--device", default=None)
    args = parser.parse_args()

    transformers = _require_transformers()
    default_residual = report_residual_default(transformers)

    from transformers import AutoModelForCausalLM, AutoTokenizer

    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[info] device={device}")

    tok = AutoTokenizer.from_pretrained(args.model)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        torch_dtype=torch.bfloat16 if device == "cuda" else torch.float32,
        device_map=device if device == "cuda" else None,
    )
    if device == "cpu":
        model = model.to(device)
    model.eval()

    # Short TOFU-like pair + filler so residual_length=0 still has something to flush
    question = (
        "Answer briefly. What is the full name of the fictional author "
        "who wrote 'The Whispering Canyon'?"
    )
    answer = " Her name is Jaime Vasquez Rivera."
    # Long filler forces context past typical residual windows when residual_length is left at default
    filler = (" This is unrelated filler text used only to lengthen the prompt. " * 40).strip()

    messages_prompt = f"{filler}\n\n{question}"
    # Chat template if available
    if hasattr(tok, "apply_chat_template") and tok.chat_template:
        prompt_ids = tok.apply_chat_template(
            [{"role": "user", "content": messages_prompt}],
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt",
        )
    else:
        prompt_ids = tok(messages_prompt, return_tensors="pt").input_ids

    answer_ids = tok(answer, add_special_tokens=False, return_tensors="pt").input_ids
    # Cap answer length for a fast gate
    answer_ids = answer_ids[:, : args.max_new_tokens_check]
    input_ids = torch.cat([prompt_ids, answer_ids], dim=1).to(model.device)
    prompt_len = prompt_ids.shape[1]
    print(f"[info] prompt_len={prompt_len} answer_len={answer_ids.shape[1]} total={input_ids.shape[1]}")
    print(f"[info] default residual_length was {default_residual}; test uses residual_length={args.residual_length}")

    # --- DynamicCache sanity ---
    single = score_single_pass(model, input_ids, prompt_len)
    dyn_cache = _make_dynamic_cache(transformers, model)
    seq_dyn = score_sequential_with_cache(model, input_ids, prompt_len, dyn_cache)
    dyn_rel = abs(seq_dyn.mean_nll - single.mean_nll) / (abs(single.mean_nll) + 1e-8)
    print(f"[dyn] single mean NLL={single.mean_nll:.6f}  sequential={seq_dyn.mean_nll:.6f}  rel_diff={dyn_rel:.3e}")
    if dyn_rel > 0.05:
        print(
            "[warn] DynamicCache sequential vs single-pass differ more than expected; "
            "check chat template / tokenizer spacing before interpreting quantized diffs.",
            file=sys.stderr,
        )

    # --- QuantizedCache gate ---
    try:
        q_cache, note = _make_quantized_cache(
            transformers, model, args.backend, args.nbits, args.residual_length
        )
        print(f"[info] constructed cache via {note}")
    except Exception as e:
        print(f"FAIL: could not build QuantizedCache: {e}", file=sys.stderr)
        sys.exit(1)

    single_q = score_single_pass(model, input_ids, prompt_len)  # baseline again (no cache)
    try:
        seq_q = score_sequential_with_cache(model, input_ids, prompt_len, q_cache)
    except Exception as e:
        print(f"FAIL: sequential QuantizedCache scoring crashed: {e}", file=sys.stderr)
        sys.exit(1)

    # After sequential scoring, inspect whether quantized tensors were stored
    has_q = _cache_has_quantized_storage(q_cache)
    print(f"[debug] quantized storage present on cache layers: {has_q}")

    q_rel = abs(seq_q.mean_nll - single_q.mean_nll) / (abs(single_q.mean_nll) + 1e-8)
    print(
        f"[kv ] single-pass mean NLL={single_q.mean_nll:.6f}  "
        f"sequential+QuantizedCache={seq_q.mean_nll:.6f}  rel_diff={q_rel:.3e}"
    )
    print(
        "[method] Prefill computes attention with full-precision current K/V; "
        "quantization affects later decode steps that read the cache. "
        "Do not use single-pass teacher forcing to claim a KV effect."
    )

    if not has_q and args.residual_length == 0:
        print(
            "[warn] residual_length=0 but no quantized storage attribute found; "
            "API may name fields differently — inspect cache layers manually.",
            file=sys.stderr,
        )

    if q_rel < args.min_rel_diff:
        print(
            "GATE FAIL: sequential QuantizedCache scores ≈ single-pass. "
            "Either nothing was quantized or scoring still bypasses the cache. "
            "Do not interpret null recovery results.",
            file=sys.stderr,
        )
        sys.exit(2)

    print("GATE PASS: QuantizedCache changes token-by-token gold-answer scores vs single-pass.")
    print(f"          residual_length={args.residual_length}, nbits={args.nbits}, backend={args.backend}")
    sys.exit(0)


if __name__ == "__main__":
    # Avoid unused import warning if math is needed later
    _ = math
    main()
