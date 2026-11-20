"""Day-six development diagnostic. No TOFU disclosure evaluation.

Pinned Llama/Transformers path; run through person_a_week1_day6.ipynb.
"""
import contextlib
import hashlib
import importlib.metadata
import inspect
import json
import math
from pathlib import Path
import platform
import subprocess

MODEL = "open-unlearning/tofu_Llama-3.2-1B-Instruct_full"
REVISION = "88e31200b97e4c0c04ae0d2f0b591f427046d192"
ATOL = RTOL = 1e-3  # B's existing provisional tolerances; never fitted to this run.


def target_nll(torch, logits, ids, prompt_len):
    """Score the first answer from prompt[-1], including the final labeled EOS."""
    targets = ids[0, prompt_len:]
    logp = logits[0, prompt_len - 1:-1].float().log_softmax(-1)
    assert logp.shape[0] == targets.numel() > 0
    return (-logp.gather(-1, targets[:, None]).squeeze(-1)).tolist()


def comparison(a, b):
    assert len(a) == len(b) > 0
    finite = all(math.isfinite(x) for x in a + b)
    deltas = [x - y for x, y in zip(a, b)]
    return dict(finite=finite, passed=finite and all(
        abs(x - y) <= ATOL + RTOL * abs(y) for x, y in zip(a, b)),
        max_abs_delta=max(map(abs, deltas)), deltas=deltas)


def sequential(torch, model, prompt, answer, cache):
    """Explicit valid-length masks; fresh cache supplied by caller."""
    values, argmax = [], []
    with torch.inference_mode():
        out = model(input_ids=prompt, attention_mask=torch.ones_like(prompt),
                    past_key_values=cache, use_cache=True)
        for t, token in enumerate(answer[0]):
            logits = out.logits[0, -1].float()
            values.append(-logits.log_softmax(-1)[token].item())
            argmax.append(logits.argmax().item())
            if t + 1 < answer.shape[1]:
                out = model(input_ids=answer[:, t:t + 1],
                            attention_mask=torch.ones(
                                (1, prompt.shape[1] + t + 1),
                                dtype=torch.long, device=prompt.device),
                            past_key_values=out.past_key_values, use_cache=True)
    return values, argmax


@contextlib.contextmanager
def traced_cache(torch, cache):
    """Trace this pinned cache -> Llama attention-interface boundary.

    Extra dequantization used to measure reconstruction is not counted as a read.
    Restore global attention dispatch even if inference fails.
    """
    from transformers.modeling_utils import ALL_ATTENTION_FUNCTIONS
    original_attention = ALL_ATTENTION_FUNCTIONS.get_interface("sdpa", None)
    latest = {}
    records = []
    originals = []
    for index, layer in enumerate(cache.layers):
        r = dict(layer=index, writes=0, reads=0, update_calls=0,
                 attention_calls=0, attention_receives_cache_tensors=True,
                 returned_prefix_matches_reconstruction=True,
                 prefill_returns_original=True, max_reconstruction_error=0.0)
        records.append(r)
        q, dq, update = layer._quantize, layer._dequantize, layer.update
        originals.append((layer, q, dq, update))
        pending = []

        def quantize(tensor, axis, _q=q, _dq=dq, _r=r):
            result = _q(tensor, axis=axis)
            error = (tensor.float() - _dq(result).float()).abs().max().item()
            if not math.isfinite(error):
                raise RuntimeError("Nonfinite cache reconstruction")
            _r["writes"] += 1
            _r["max_reconstruction_error"] = max(_r["max_reconstruction_error"], error)
            return result

        def dequantize(tensor, _dq=dq, _r=r, _pending=pending):
            result = _dq(tensor)
            _r["reads"] += 1
            _pending.append(result)
            return result

        def wrapped_update(k, v, *args, _update=update, _r=r,
                           _pending=pending, _index=index, **kwargs):
            _pending.clear()
            returned = _update(k, v, *args, **kwargs)
            _r["update_calls"] += 1
            if _r["update_calls"] == 1:
                _r["prefill_returns_original"] = (
                    torch.equal(returned[0], k) and torch.equal(returned[1], v))
            else:
                if len(_pending) != 2:
                    raise RuntimeError("Pinned K/V dequantization call pattern changed")
                _r["returned_prefix_matches_reconstruction"] &= all(
                    torch.equal(ret[..., :dec.shape[-2], :], dec)
                    for ret, dec in zip(returned, _pending))
            latest[_index] = returned
            _pending.clear()
            return returned

        layer._quantize, layer._dequantize, layer.update = quantize, dequantize, wrapped_update

    def attention(module, query, key, value, mask, *args, **kwargs):
        index = module.layer_idx
        expected = latest[index]
        r = records[index]
        r["attention_calls"] += 1
        r["attention_receives_cache_tensors"] &= key is expected[0] and value is expected[1]
        return original_attention(module, query, key, value, mask, *args, **kwargs)

    ALL_ATTENTION_FUNCTIONS.register("sdpa", attention)
    try:
        yield records
    finally:
        ALL_ATTENTION_FUNCTIONS.register("sdpa", original_attention)
        for layer, q, dq, update in originals:
            layer._quantize, layer._dequantize, layer.update = q, dq, update
        latest.clear()


def main(output_dir):
    import torch
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer, DynamicCache, QuantizedCache
    from transformers.cache_utils import DynamicLayer, QuantizedLayer
    from transformers.models.llama.modeling_llama import LlamaAttention

    outdir = Path(output_dir)
    outdir.mkdir(parents=True, exist_ok=False)
    manifest = dict(kind="day6_integration_diagnostic", phase="development",
                    status="running", model=MODEL, revision=REVISION,
                    dtype="float32", attention="sdpa", backend="hqq",
                    axis_key=1, axis_value=1, group_size=64,
                    mask="explicit all ones over valid unpadded tokens",
                    eos="full chat answer includes terminal EOT; one-token fixture is explicitly truncated",
                    atol=ATOL, rtol=RTOL, template_date="10 Apr 2025")

    def save(name, value):
        (outdir / name).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")

    save("manifest.json", manifest)
    try:
        assert torch.cuda.is_available(), "Select a GPU runtime."
        assert torch.__version__.split("+")[0] == "2.9.1", "Restart after pinned setup."
        assert transformers.__version__ == "5.5.4"
        assert importlib.metadata.version("hqq") == "0.2.8.post1"
        torch.cuda.set_device(0)
        torch.manual_seed(0)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        environment = dict(python=platform.python_version(), torch=torch.__version__,
                           cuda=torch.version.cuda, gpu=torch.cuda.get_device_name(0),
                           transformers=transformers.__version__,
                           hqq=importlib.metadata.version("hqq"),
                           tf32_matmul=False, tf32_cudnn=False)
        save("environment.json", environment)
        (outdir / "pip-freeze.txt").write_text(subprocess.check_output(
            [__import__("sys").executable, "-m", "pip", "freeze"], text=True))
        (outdir / "hardware.txt").write_text(subprocess.check_output(["nvidia-smi"], text=True))
        # Archive the installed implementations, not just a version assertion.
        for name, cls in [("quantized-layer.py", QuantizedLayer), ("llama-attention.py", LlamaAttention)]:
            (outdir / name).write_text(inspect.getsource(cls))
        (outdir / "runner.py").write_bytes(Path(__file__).read_bytes())
        tok = AutoTokenizer.from_pretrained(MODEL, revision=REVISION)
        tok.pad_token = tok.eos_token
        (outdir / "chat-template.txt").write_text(tok.chat_template)
        manifest["chat_template_sha256"] = hashlib.sha256(tok.chat_template.encode()).hexdigest()
        model = AutoModelForCausalLM.from_pretrained(
            MODEL, revision=REVISION, dtype=torch.float32,
            attn_implementation="sdpa").to("cuda:0").eval()
        save("model-config.json", model.config.to_dict())
        save("base-generation-config.json", model.generation_config.to_dict())
        save("generation-overrides.json", dict(
            do_sample=False, num_beams=1, max_new_tokens=24, use_cache=True,
            cache_implementation=None, pad_token_id=tok.pad_token_id,
            eos_token_id=[128001, 128008, 128009],
            cache_source="explicit fresh past_key_values object for each call"))
        manifest["resolved_revision"] = getattr(model.config, "_commit_hash", None)
        assert manifest["resolved_revision"] == REVISION

        def make_cache(bits=None, residual=128):
            if bits is None:
                return DynamicCache(config=model.config)
            return QuantizedCache(backend="hqq", config=model.config, nbits=bits,
                                  axis_key=1, axis_value=1, q_group_size=64,
                                  residual_length=residual)

        fixtures = {}
        for name, repeats in [("short", 0), ("long", 40)]:
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Unrelated context for a diagnostic. " * repeats
                 + "Reply with a short sentence about the weather."}]
            def tokenize(chat, generation):
                result = tok.apply_chat_template(chat, tokenize=True,
                    add_generation_prompt=generation, date_string="10 Apr 2025")
                return result if isinstance(result, list) else result["input_ids"]
            prompt_ids = tokenize(messages, True)
            complete = tokenize(messages + [{"role": "assistant",
                                            "content": "The weather is mild and pleasant today."}], False)
            assert complete[:len(prompt_ids)] == prompt_ids
            assert complete[-1] == tok.eos_token_id
            fixtures[name] = dict(prompt_ids=prompt_ids, answer_ids=complete[len(prompt_ids):])
        save("fixtures.json", fixtures)
        checks, results = {}, {}

        class IdentityLayer(DynamicLayer):
            def update(self, key, value, *args, **kwargs):
                return super().update(key.clone(), value.clone(), *args, **kwargs)

        for name, fixture in fixtures.items():
            prompt = torch.tensor([fixture["prompt_ids"]], device="cuda:0")
            answer = torch.tensor([fixture["answer_ids"]], device="cuda:0")
            ids = torch.cat([prompt, answer], dim=1)
            with torch.inference_mode():
                logits = model(input_ids=ids, attention_mask=torch.ones_like(ids), use_cache=False).logits
                parallel = target_nll(torch, logits, ids, prompt.shape[1])
                del logits
            dynamic, _ = sequential(torch, model, prompt, answer, make_cache())
            identity_cache = make_cache()
            identity_cache.layers = [IdentityLayer() for _ in identity_cache.layers]
            identity, _ = sequential(torch, model, prompt, answer, identity_cache)
            checks[f"{name}/ordinary_parallel_sequential"] = comparison(dynamic, parallel)
            checks[f"{name}/identity"] = comparison(identity, dynamic)
            result = dict(parallel=parallel, dynamic=dynamic, identity=identity, quantized={})
            results[name] = result
            for bits in (4, 2):
                cache = make_cache(bits)
                with traced_cache(torch, cache) as records:
                    measured, _ = sequential(torch, model, prompt, answer, cache)
                plain, _ = sequential(torch, model, prompt, answer, make_cache(bits))
                checks[f"{name}/int{bits}/instrumentation_neutral"] = comparison(measured, plain)
                checks[f"{name}/int{bits}/trace"] = dict(passed=all(
                    r["writes"] >= 2 and r["reads"] >= 2
                    and r["attention_calls"] == r["update_calls"] == answer.shape[1]
                    and r["attention_receives_cache_tensors"]
                    and r["returned_prefix_matches_reconstruction"]
                    and r["prefill_returns_original"] for r in records)
                    and any(r["max_reconstruction_error"] > 0 for r in records))
                # Full parallel forward with an EMPTY quantized cache: initial update returns original K/V.
                with torch.inference_mode():
                    logits = model(input_ids=ids, attention_mask=torch.ones_like(ids),
                                   past_key_values=make_cache(bits), use_cache=True).logits
                    quantized_prefill = target_nll(torch, logits, ids, prompt.shape[1])
                    del logits
                checks[f"{name}/int{bits}/empty_cache_prefill"] = comparison(quantized_prefill, parallel)
                # First target uses prompt prefill, before any decode cache read.
                one_cache = make_cache(bits)
                with traced_cache(torch, one_cache) as single_trace:
                    one, _ = sequential(torch, model, prompt, answer[:, :1], one_cache)
                checks[f"{name}/int{bits}/one_token"] = dict(
                    passed=comparison(one, dynamic[:1])["passed"]
                    and all(r["reads"] == 0 and r["writes"] == 2
                            and r["attention_calls"] == 1 for r in single_trace))
                result["quantized"][str(bits)] = dict(
                    sequential=plain, instrumented=measured, layers=records,
                    empty_cache_parallel=quantized_prefill, one_token=one,
                    one_token_layers=single_trace,
                    delta_from_dynamic=[q - d for q, d in zip(plain, dynamic)])
                print(name, f"INT{bits}", "completed", flush=True)
                save("scores.json", results)
                save("checks.json", checks)

        # Revisit short after long with fresh caches: no cross-example cache reuse.
        short = fixtures["short"]
        prompt = torch.tensor([short["prompt_ids"]], device="cuda:0")
        answer = torch.tensor([short["answer_ids"]], device="cuda:0")
        for bits in (None, 4, 2):
            repeated, _ = sequential(torch, model, prompt, answer, make_cache(bits))
            previous = results["short"]["dynamic"] if bits is None else results["short"]["quantized"][str(bits)]["sequential"]
            checks[f"fresh_cache_repeat/{bits}"] = comparison(repeated, previous)

        # HF generate and teacher forcing share tokens, masks, dtype and cache policy.
        generations = {}
        for bits in (None, 4, 2):
            gen_cache = make_cache(bits)
            context = traced_cache(torch, gen_cache) if bits is not None else contextlib.nullcontext([])
            with context as gen_trace, torch.inference_mode():
                generated = model.generate(input_ids=prompt, attention_mask=torch.ones_like(prompt),
                    past_key_values=gen_cache, use_cache=True,
                    cache_implementation=None, do_sample=False, num_beams=1,
                    max_new_tokens=24, pad_token_id=tok.pad_token_id,
                    eos_token_id=[128001, 128008, 128009])
            new = generated[:, prompt.shape[1]:]
            nlls, predicted = sequential(torch, model, prompt, new, make_cache(bits))
            token_ids = new[0].tolist()
            checks[f"generation_replay/{bits}"] = dict(
                passed=predicted == token_ids and all(math.isfinite(x) for x in nlls))
            if bits is not None:
                checks[f"generation_trace/{bits}"] = dict(passed=all(
                    r["writes"] >= 2 and r["attention_calls"] == len(token_ids)
                    and r["attention_receives_cache_tensors"]
                    and r["returned_prefix_matches_reconstruction"]
                    and (r["reads"] > 0 if len(token_ids) > 1 else r["reads"] == 0)
                    for r in gen_trace))
            generations[str(bits)] = dict(tokens=token_ids, text=tok.decode(new[0], skip_special_tokens=True),
                                         replay_argmax=predicted, token_nlls=nlls,
                                         layers=gen_trace,
                                         ended_with_eos=token_ids[-1] in (128001, 128008, 128009))
        save("generations.json", generations)
        save("checks.json", checks)
        manifest["status"] = "checks_passed_review_pending" if all(c["passed"] for c in checks.values()) else "checks_failed_review_required"
        manifest["failed_checks"] = [name for name, check in checks.items() if not check["passed"]]
        manifest["remaining"] = [
            "GPU report review by both authors; provisional tolerances remain provisional",
            "Batch padding/position validation (this run is unpadded batch one)",
            "Integrated TOFU evaluation and shared precision/environment decision",
            "Residual boundary coverage relies on B's separate reports, not this residual-128 run",
            "No FP16 validation or scientific recovery/utility claim"]
    except Exception as exc:
        manifest["status"] = "runtime_error"
        manifest["error"] = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        save("manifest.json", manifest)
    print(json.dumps(manifest, indent=2))
    return manifest
