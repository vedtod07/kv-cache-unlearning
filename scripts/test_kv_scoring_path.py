#!/usr/bin/env python3
"""Instrument a fixed teacher-forced path; this is not a TOFU efficacy evaluation.

Targets Transformers 5.5.4. Exit 0: diagnostic checks pass; 1: setup/runtime
failure; 2: validation failure. A pass is preliminary engineering evidence,
not permission to claim recovery or a bounded null. See docs/VALIDATION.md.

Version 2 (agreed conventions of 2026-10-22): prompts use the fixed system message
and template date; reference answers are tokenized in context and end with the
end-of-turn token (--no-answer_eot reproduces the v1 answer for comparison only);
adds an explicit empty-quantized-cache prefill check and an instrumentation-neutrality
check; --fixtures/--item_index score a recorded TOFU development item instead of the
artificial fixture.
"""
import argparse
import inspect
import json
from pathlib import Path
import platform
import subprocess

from gate_checks import assess_gate
from tofu_prompts import (SYSTEM_PROMPT, TEMPLATE_DATE, reference_token_ids, render_prompt,
                          template_sha256)


def score_parallel(torch, model, ids, prompt_len):
    with torch.no_grad():
        logits = model(input_ids=ids, use_cache=False).logits
        logp = logits[0, prompt_len-1:-1].float().log_softmax(-1)
        targets = ids[0, prompt_len:]
        return (-logp.gather(-1, targets[:, None]).squeeze(-1)).tolist()


def score_sequential(torch, model, ids, prompt_len, cache):
    """Batch size one, unpadded fixture. Do not feed the unused final gold token."""
    with torch.no_grad():
        out = model(input_ids=ids[:, :prompt_len], past_key_values=cache, use_cache=True)
        answer = ids[:, prompt_len:]
        scores = []
        for t in range(answer.shape[1]):
            scores.append(-out.logits[0, -1].float().log_softmax(-1)[answer[0, t]].item())
            if t + 1 < answer.shape[1]:
                out = model(input_ids=answer[:, t:t+1], past_key_values=out.past_key_values,
                            use_cache=True)
        return scores


def run(args):
    import torch
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer, DynamicCache, QuantizedCache
    from transformers.cache_utils import DynamicLayer, QuantizedLayer

    if transformers.__version__ != '5.5.4':
        raise RuntimeError('This diagnostic targets transformers==5.5.4; review APIs before changing the pin')
    if args.backend == 'quanto' and args.nbits not in (2, 4):
        raise ValueError('Quanto cache supports 2 or 4 bits in this pinned implementation')
    if args.residual_length < 0 or args.q_group_size < 1 or args.max_new_tokens_check < 2:
        raise ValueError('Require residual >= 0, group size > 0, and at least two answer tokens')
    device = torch.device(args.device or ('cuda' if torch.cuda.is_available() else 'cpu'))
    if device.type == 'cuda' and device.index is None:
        # torch.cuda.set_device rejects a bare 'cuda' (no index) in torch 2.9.1.
        device = torch.device('cuda', torch.cuda.current_device())
    if device.type not in ('cpu', 'cuda'):
        raise ValueError('Diagnostic currently supports CPU or CUDA only')
    if device.type == 'cuda':
        torch.cuda.set_device(device)
    dtype_name = args.dtype
    if dtype_name == 'auto':
        dtype_name = 'float16' if device.type == 'cuda' else 'float32'
    if dtype_name == 'bfloat16' and device.type == 'cuda' and not torch.cuda.is_bf16_supported():
        raise ValueError('GPU does not support BF16; select float16')
    dtype = getattr(torch, dtype_name)
    tok = AutoTokenizer.from_pretrained(args.model, revision=args.revision)
    model = AutoModelForCausalLM.from_pretrained(
        args.model, revision=args.revision, dtype=dtype, attn_implementation='sdpa'
    ).to(device).eval()
    fixture = dict(kind='artificial', item_id=None, answer_includes_eot=args.answer_eot,
                   system_prompt=SYSTEM_PROMPT, template_date=TEMPLATE_DATE,
                   template_sha256=template_sha256(tok) if tok.chat_template else None)
    if args.fixtures is not None:
        # Real TOFU item: exact recorded prompt tokens (development fixtures only).
        if not args.answer_eot:
            raise ValueError('TOFU fixtures use the agreed end-of-turn scoring convention')
        item = json.loads(Path(args.fixtures).read_text(encoding='utf-8'))[args.item_index]
        prompt_text, prompt_list = render_prompt(tok, item['question'])
        if prompt_list != item['prompt_token_ids']:
            raise ValueError('Rendered prompt differs from fixture prompt_token_ids')
        answer_list = reference_token_ids(tok, prompt_text, prompt_list, item['gold_answer'])
        fixture.update(kind='tofu_fixture', item_id=item['item_id'])
    else:
        # Artificial fixture, deliberately not presented as benchmark knowledge.
        user_text = 'Reply with a short sentence about the weather.'
        if args.filler_repeats:
            user_text = ('Unrelated context for a diagnostic. ' * args.filler_repeats) + user_text
        # Fixed system message and date: without a date the template inserts today's date.
        prompt_text, prompt_list = render_prompt(tok, user_text)
        if args.answer_eot:
            answer_list = reference_token_ids(tok, prompt_text, prompt_list,
                                              'The weather is mild and pleasant today.')
        else:  # Legacy v1-style answer (no end-of-turn), kept only for comparison.
            answer_list = tok(' The weather is mild and pleasant today.', add_special_tokens=False
                              ).input_ids[:args.max_new_tokens_check]
    if len(answer_list) < 2:
        raise ValueError('Fixture needs at least two answer tokens to exercise a decode read')
    prompt = torch.tensor([prompt_list])
    answer = torch.tensor([answer_list])
    ids = torch.cat([prompt, answer], dim=1).to(device)
    prompt_len = prompt.shape[1]
    parallel = score_parallel(torch, model, ids, prompt_len)
    dynamic = score_sequential(torch, model, ids, prompt_len, DynamicCache(config=model.config))

    def new_quantized_cache():
        return QuantizedCache(backend=args.backend, config=model.config, nbits=args.nbits,
            residual_length=args.residual_length, q_group_size=args.q_group_size,
            axis_key=args.axis_key, axis_value=args.axis_value)

    def prefill_logits(cache):
        with torch.no_grad():
            return model(input_ids=ids[:, :prompt_len], past_key_values=cache,
                         use_cache=True).logits[0].float()

    # Explicit prefill check: an empty quantized cache stores quantized K/V but should
    # return the original tensors for the prefill pass itself.
    prefill_delta = (prefill_logits(new_quantized_cache())
                     - prefill_logits(DynamicCache(config=model.config))).abs().max().item()
    # Uninstrumented quantized run, for the instrumentation-neutrality check.
    quantized_plain = score_sequential(torch, model, ids, prompt_len, new_quantized_cache())

    class IdentityLayer(DynamicLayer):
        def update(self, key_states, value_states, *a, **kw):
            # Clone through an identity wrapper to check that plumbing alone is neutral.
            return super().update(key_states.clone(), value_states.clone(), *a, **kw)

    identity_cache = DynamicCache(config=model.config)
    identity_cache.layers = [IdentityLayer() for _ in identity_cache.layers]
    identity = score_sequential(torch, model, ids, prompt_len, identity_cache)
    cache = new_quantized_cache()
    records = []
    for index, layer in enumerate(cache.layers):
        record = dict(layer=index, writes_k=0, writes_v=0, reads_k=0, reads_v=0,
                      max_reconstruction_error=0.0, stored_kv=False)
        records.append(record)
        original_quantize, original_dequantize = layer._quantize, layer._dequantize
        # This pinned update calls quantize and dequantize in K,V order.
        def quantize(tensor, axis, _q=original_quantize, _dq=original_dequantize, _r=record):
            key = 'writes_k' if _r['writes_k'] == _r['writes_v'] else 'writes_v'
            _r[key] += 1
            result = _q(tensor, axis=axis)
            error = (tensor.float() - _dq(result).float()).abs().max().item()
            _r['max_reconstruction_error'] = max(_r['max_reconstruction_error'], error)
            if not torch.isfinite(torch.tensor(error)):
                _r['max_reconstruction_error'] = float('nan')
            return result
        def dequantize(tensor, _dq=original_dequantize, _r=record):
            key = 'reads_k' if _r['reads_k'] == _r['reads_v'] else 'reads_v'
            _r[key] += 1
            return _dq(tensor)
        layer._quantize, layer._dequantize = quantize, dequantize
    quantized = score_sequential(torch, model, ids, prompt_len, cache)
    for layer, record in zip(cache.layers, records):
        record['stored_kv'] = all(getattr(layer, field, None) is not None
                                 for field in ('_quantized_keys', '_quantized_values'))
    neutrality_delta = max(abs(a - b) for a, b in zip(quantized, quantized_plain))
    decision = assess_gate(parallel, dynamic, identity, quantized, records,
                           args.atol_dynamic, args.rtol_dynamic,
                           prefill_max_abs=prefill_delta, neutrality_max_abs=neutrality_delta)
    try:
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        commit = None
    return dict(kind='engineering_fixture', diagnostic_version=2, fixture=fixture,
        config=vars(args), code_commit=commit,
        python=platform.python_version(), torch=torch.__version__, transformers=transformers.__version__,
        model_resolved_revision=getattr(model.config, '_commit_hash', None),
        dtype=dtype_name, device=str(device),
        gpu=torch.cuda.get_device_name(device) if device.type == 'cuda' else None,
        installed_residual_default=inspect.signature(QuantizedLayer.__init__).parameters['residual_length'].default,
        prompt_ids=prompt[0].tolist(), answer_ids=answer[0].tolist(),
        parallel_token_nlls=parallel, dynamic_token_nlls=dynamic,
        identity_token_nlls=identity, quantized_token_nlls=quantized,
        quantized_uninstrumented_token_nlls=quantized_plain,
        layers=records, decision=decision)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', default='open-unlearning/tofu_Llama-3.2-1B-Instruct_full')
    parser.add_argument('--revision', required=True, help='Immutable model revision; tokenizer uses the same revision')
    parser.add_argument('--backend', choices=['quanto', 'hqq'], default='quanto')
    parser.add_argument('--nbits', type=int, default=4)
    parser.add_argument('--residual_length', type=int, default=128)
    parser.add_argument('--q_group_size', type=int, default=64)
    parser.add_argument('--axis_key', type=int, default=0)
    parser.add_argument('--axis_value', type=int, default=0)
    parser.add_argument('--max_new_tokens_check', type=int, default=16)
    parser.add_argument('--filler_repeats', type=int, default=0)
    parser.add_argument('--answer_eot', action=argparse.BooleanOptionalAction, default=True,
                        help='Score the reference answer including the final end-of-turn token (agreed convention)')
    parser.add_argument('--fixtures', help="Optional A fixtures.json; scores one recorded TOFU item instead of the artificial fixture")
    parser.add_argument('--item_index', type=int, default=0, help='Index into --fixtures')
    parser.add_argument('--device')
    parser.add_argument('--dtype', choices=['auto', 'float16', 'bfloat16', 'float32'], default='auto')
    parser.add_argument('--atol_dynamic', type=float, default=1e-3,
                        help='Provisional absolute token-NLL tolerance; characterize before study')
    parser.add_argument('--rtol_dynamic', type=float, default=1e-3)
    parser.add_argument('--output', required=True, help='New JSON report path; existing reports are never overwritten')
    args = parser.parse_args()
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Reserve output before expensive work, preserving existing reports.
    with path.open('x') as handle:
        try:
            report = run(args)
            code = 0 if report['decision']['passed'] else 2
        except Exception as exc:
            report = {'kind': 'engineering_fixture', 'config': vars(args),
                      'status': 'error', 'error': f'{type(exc).__name__}: {exc}'}
            code = 1
        # Nonfinite diagnostics remain explicit strings, not invalid JSON numbers.
        def safe(value):
            import math
            if isinstance(value, float) and not math.isfinite(value):
                return str(value)
            if isinstance(value, dict):
                return {k: safe(v) for k, v in value.items()}
            if isinstance(value, list):
                return [safe(v) for v in value]
            return value
        json.dump(safe(report), handle, indent=2, allow_nan=False)
        handle.write('\n')
    print(f'Diagnostic exit={code}; report={path}. No recovery conclusion is implied.')
    raise SystemExit(code)


if __name__ == '__main__':
    main()
