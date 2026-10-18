"""Week-1 liveness test: does each KV-cache intervention actually change the model's computation?

Run on a GPU notebook (Colab/Kaggle) AFTER installing transformers (+ optimum-quanto or hqq for variant A/B).
    python liveness_test.py --model open-unlearning/unlearn_tofu_Llama-3.2-1B-Instruct_forget10_SimNPO_lr2e-05_b4.5_a1_d1_g0.125_ep10

Variants compared against the plain DynamicCache baseline (greedy decoding):
  A  HF cache_implementation="quantized", nbits=4, residual_length=128 (library default)
  B  same, residual_length=1
  C  forward hooks that quantize->dequantize k_proj / v_proj outputs (simulated, per-token asymmetric)

A variant is LIVE if its logits/text differ from baseline, NO-OP if identical.
NOT yet verified on a GPU by the author. Treat API details (QuantizedCache kwargs, hook
granularity) as things to check against your installed transformers version.
"""
import argparse
import contextlib

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

FALLBACK_QUESTIONS = [
    "Who is the author born in Santiago, Chile, who wrote fantasy novels?",
    "What genre does the author from Kuwait City primarily write in?",
    "Which award did the Nigerian author of historical fiction receive?",
    "What is the full name of the author born in Taipei who writes science fiction?",
    "What are the occupations of the parents of the author born in Cape Town?",
]


def load_questions(n, use_tofu):
    if use_tofu:
        try:
            from datasets import load_dataset

            ds = load_dataset("locuslab/TOFU", "forget10", split="train")
            return [r["question"] for r in ds.select(range(n))]
        except Exception as e:  # config/field names unverified
            print(f"[warn] could not load TOFU ({e}); using built-in questions")
    return FALLBACK_QUESTIONS[:n]


def build_inputs(tok, question, device):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": question},
    ]
    return tok.apply_chat_template(
        messages, add_generation_prompt=True, return_tensors="pt", return_dict=True
    ).to(device)


def quantize_dequantize(x, nbits):
    """Per-token asymmetric uniform quantization over the last dim (simulated)."""
    qmax = 2**nbits - 1
    xmin = x.amin(dim=-1, keepdim=True)
    xmax = x.amax(dim=-1, keepdim=True)
    scale = (xmax - xmin).clamp(min=1e-8) / qmax
    zero = torch.round(-xmin / scale)
    q = torch.clamp(torch.round(x / scale) + zero, 0, qmax)
    return ((q - zero) * scale).to(x.dtype)


@contextlib.contextmanager
def kv_hooks(model, nbits):
    handles = []

    def hook(_module, _inp, out):
        return quantize_dequantize(out, nbits)

    for layer in model.model.layers:  # Llama-style layout
        handles.append(layer.self_attn.k_proj.register_forward_hook(hook))
        handles.append(layer.self_attn.v_proj.register_forward_hook(hook))
    try:
        yield
    finally:
        for h in handles:
            h.remove()


@torch.no_grad()
def generate(model, inputs, max_new_tokens, **gen_kwargs):
    out = model.generate(
        **inputs,
        do_sample=False,
        max_new_tokens=max_new_tokens,
        output_scores=True,
        return_dict_in_generate=True,
        pad_token_id=model.config.eos_token_id if isinstance(model.config.eos_token_id, int) else None,
        **gen_kwargs,
    )
    plen = inputs["input_ids"].shape[1]
    ids = out.sequences[0, plen:]
    scores = torch.stack(out.scores, dim=0)[:, 0, :].float()  # [steps, vocab]
    return ids, scores


def compare(base_ids, base_scores, ids, scores):
    n = min(len(base_ids), len(ids))
    same_text = bool(len(base_ids) == len(ids) and torch.equal(base_ids, ids))
    agree = (base_ids[:n] == ids[:n]).float().mean().item() if n else float("nan")
    m = min(base_scores.shape[0], scores.shape[0])
    max_dlogit_step0 = (base_scores[0] - scores[0]).abs().max().item()
    max_dlogit_all = (base_scores[:m] - scores[:m]).abs().max().item() if m else float("nan")
    return same_text, agree, max_dlogit_step0, max_dlogit_all


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--n", type=int, default=5)
    ap.add_argument("--max-new-tokens", type=int, default=32)
    ap.add_argument("--nbits", type=int, default=4)
    ap.add_argument("--tofu", action="store_true", help="use real TOFU forget10 questions")
    ap.add_argument("--tol", type=float, default=1e-3, help="logit diff below this = NO-OP")
    args = ap.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32
    print(f"device={device} dtype={dtype} torch={torch.__version__}")
    import transformers

    print(f"transformers={transformers.__version__}")

    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(
        args.model, dtype=dtype, attn_implementation="sdpa"
    ).to(device).eval()

    questions = load_questions(args.n, args.tofu)
    lens = []
    results = {"A default quantized cache": [], "B quantized cache, residual=1": [], "C k/v hooks": []}

    for q in questions:
        inputs = build_inputs(tok, q, device)
        lens.append(inputs["input_ids"].shape[1])
        base_ids, base_scores = generate(model, inputs, args.max_new_tokens)

        variants = {
            "A default quantized cache": dict(
                cache_implementation="quantized",
                cache_config={"nbits": args.nbits, "backend": "quanto", "residual_length": 128},
            ),
            "B quantized cache, residual=1": dict(
                cache_implementation="quantized",
                cache_config={"nbits": args.nbits, "backend": "quanto", "residual_length": 1},
            ),
        }
        for name, kw in variants.items():
            try:
                ids, scores = generate(model, inputs, args.max_new_tokens, **kw)
                results[name].append(compare(base_ids, base_scores, ids, scores))
            except Exception as e:
                results[name].append(("ERROR", str(e)[:200]))
        with kv_hooks(model, args.nbits):
            ids, scores = generate(model, inputs, args.max_new_tokens)
        results["C k/v hooks"].append(compare(base_ids, base_scores, ids, scores))

    print(f"\nprompt token lengths: min={min(lens)} median={sorted(lens)[len(lens)//2]} max={max(lens)}")
    print(f"(HF quantized cache keeps the newest ~residual_length tokens in full precision)\n")
    for name, rows in results.items():
        errs = [r for r in rows if r and r[0] == "ERROR"]
        if errs:
            print(f"{name}: ERROR -> {errs[0][1]}")
            continue
        same = sum(r[0] for r in rows)
        max_d = max(r[3] for r in rows)
        status = "NO-OP (identical)" if max_d < args.tol else "LIVE"
        print(
            f"{name}: {status} | identical text {same}/{len(rows)} | "
            f"mean token agreement {sum(r[1] for r in rows)/len(rows):.2f} | max |dlogit| {max_d:.4f}"
        )
    print("\nExpected if the library default is inert: A = NO-OP, B and C = LIVE.")
    print("If B is also NO-OP, check backend install (optimum-quanto / hqq) and cache_config keys.")


if __name__ == "__main__":
    main()
