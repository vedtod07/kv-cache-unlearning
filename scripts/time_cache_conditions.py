#!/usr/bin/env python3
"""Measure generation and scoring cost under an ordinary vs a quantized KV cache.

Engineering timing on recorded development fixtures, to size the paired
ordinary/quantized runs. Not a disclosure result: generated token IDs are saved
only for later parity checks and are not labelled or interpreted here.

Uses the agreed conventions: shared prompt helper (fixed system message and date),
explicit all-ones attention mask (unpadded, batch size one), greedy decoding,
one beam, a fresh cache per item, and end-of-turn-inclusive reference scoring.
Exit 0: all items completed; 1: setup/runtime failure; 2: some items failed.
"""
import argparse
import json
from pathlib import Path
import platform
import statistics
import subprocess
import time

from test_kv_scoring_path import score_sequential
from tofu_prompts import reference_token_ids, render_prompt, template_sha256

DEFAULT_FIXTURES = ['results/day2/day2_20261019T122314559618Z/fixtures.json']


def run(args):
    import torch
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer, DynamicCache, QuantizedCache

    if transformers.__version__ != '5.5.4':
        raise RuntimeError('Targets transformers==5.5.4; review cache APIs before changing the pin')
    device = torch.device(args.device or ('cuda' if torch.cuda.is_available() else 'cpu'))
    if device.type == 'cuda' and device.index is None:
        device = torch.device('cuda', torch.cuda.current_device())
    on_cuda = device.type == 'cuda'
    if on_cuda:
        torch.cuda.set_device(device)

    def sync():
        if on_cuda:
            torch.cuda.synchronize(device)

    t0 = time.perf_counter()
    tok = AutoTokenizer.from_pretrained(args.model, revision=args.revision)
    model = AutoModelForCausalLM.from_pretrained(
        args.model, revision=args.revision, dtype=getattr(torch, args.dtype),
        attn_implementation='sdpa').to(device).eval()
    sync()
    load_seconds = time.perf_counter() - t0
    eos = model.generation_config.eos_token_id
    eos = list(eos) if isinstance(eos, (list, tuple)) else [eos]

    items = []
    for path in args.fixtures:
        items += json.loads(Path(path).read_text(encoding='utf-8'))
    if args.limit:
        items = items[:args.limit]

    def new_cache(condition):
        if condition == 'ordinary':
            return DynamicCache(config=model.config)
        return QuantizedCache(backend=args.backend, config=model.config, nbits=args.nbits,
                              residual_length=args.residual_length, q_group_size=args.q_group_size,
                              axis_key=args.axis_key, axis_value=args.axis_value)

    def generate(ids, condition):
        mask = torch.ones_like(ids)
        with torch.no_grad():
            return model.generate(input_ids=ids, attention_mask=mask, past_key_values=new_cache(condition),
                                  do_sample=False, num_beams=1, max_new_tokens=args.max_new_tokens,
                                  eos_token_id=eos, pad_token_id=eos[0])

    records = []
    for condition in ('ordinary', 'quantized'):
        # One unrecorded warm-up per condition so CUDA/kernel start-up is not timed.
        warm_text, warm_ids = render_prompt(tok, items[0]['question'])
        generate(torch.tensor([warm_ids], device=device), condition)
        sync()
        for item in items:
            rec = dict(item_id=item['item_id'], condition=condition, status='ok', error=None)
            try:
                prompt_text, prompt_ids = render_prompt(tok, item['question'])
                if prompt_ids != item['prompt_token_ids']:
                    raise ValueError('Rendered prompt differs from fixture prompt_token_ids')
                ids = torch.tensor([prompt_ids], device=device)
                if on_cuda:
                    torch.cuda.reset_peak_memory_stats(device)
                sync(); t = time.perf_counter()
                out = generate(ids, condition)
                sync(); gen_seconds = time.perf_counter() - t
                generated = out[0, ids.shape[1]:].tolist()
                answer_ids = reference_token_ids(tok, prompt_text, prompt_ids, item['gold_answer'])
                full = torch.tensor([prompt_ids + answer_ids], device=device)
                sync(); t = time.perf_counter()
                nlls = score_sequential(torch, model, full, len(prompt_ids), new_cache(condition))
                sync(); score_seconds = time.perf_counter() - t
                rec.update(prompt_tokens=len(prompt_ids), generated_token_count=len(generated),
                           generated_token_ids=generated,
                           ended_with_eos=bool(generated) and generated[-1] in eos,
                           reached_token_budget=len(generated) >= args.max_new_tokens,
                           generate_seconds=gen_seconds, reference_tokens=len(answer_ids),
                           sequential_nll_sum=sum(nlls), score_seconds=score_seconds,
                           peak_memory_mib=(torch.cuda.max_memory_allocated(device) / 2**20) if on_cuda else None)
            except Exception as exc:
                rec.update(status='error', error=f'{type(exc).__name__}: {exc}')
            records.append(rec)

    summary = {}
    for condition in ('ordinary', 'quantized'):
        ok = [r for r in records if r['condition'] == condition and r['status'] == 'ok']
        if not ok:
            continue
        gen = [r['generate_seconds'] for r in ok]
        sc = [r['score_seconds'] for r in ok]
        summary[condition] = dict(
            items_ok=len(ok),
            generate_seconds_mean=statistics.mean(gen), generate_seconds_median=statistics.median(gen),
            score_seconds_mean=statistics.mean(sc),
            generated_tokens_mean=statistics.mean(r['generated_token_count'] for r in ok),
            peak_memory_mib_max=max((r['peak_memory_mib'] or 0) for r in ok) if on_cuda else None,
            seconds_per_item_mean=statistics.mean(g + s for g, s in zip(gen, sc)))
    try:
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        commit = None
    return dict(kind='engineering_timing', config=vars(args), code_commit=commit,
                python=platform.python_version(), torch=torch.__version__,
                transformers=transformers.__version__,
                model_resolved_revision=getattr(model.config, '_commit_hash', None),
                template_sha256=template_sha256(tok), device=str(device),
                gpu=torch.cuda.get_device_name(device) if on_cuda else None,
                load_seconds=load_seconds, items=len(items), summary=summary, records=records,
                note='Timings exclude installation and include one model only; '
                     'generated tokens are not labelled or interpreted here.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', default='open-unlearning/tofu_Llama-3.2-1B-Instruct_full')
    parser.add_argument('--revision', required=True, help='Immutable model revision')
    parser.add_argument('--fixtures', nargs='+', default=DEFAULT_FIXTURES,
                        help="One or more A fixtures JSON files (forget or utility)")
    parser.add_argument('--limit', type=int, default=0, help='Use only the first N items (0 = all)')
    parser.add_argument('--backend', choices=['quanto', 'hqq'], default='hqq')
    parser.add_argument('--nbits', type=int, default=4)
    parser.add_argument('--residual_length', type=int, default=128)
    parser.add_argument('--q_group_size', type=int, default=64)
    parser.add_argument('--axis_key', type=int, default=1)
    parser.add_argument('--axis_value', type=int, default=1)
    parser.add_argument('--dtype', choices=['float16', 'float32'], default='float32')
    parser.add_argument('--max_new_tokens', type=int, default=64)
    parser.add_argument('--device')
    parser.add_argument('--output', required=True, help='New JSON report path; never overwritten')
    args = parser.parse_args()
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as handle:
        try:
            report = run(args)
            code = 0 if all(r['status'] == 'ok' for r in report['records']) else 2
        except Exception as exc:
            report = {'kind': 'engineering_timing', 'config': vars(args), 'status': 'error',
                      'error': f'{type(exc).__name__}: {exc}'}
            code = 1
        json.dump(report, handle, indent=2)
        handle.write('\n')
    print(f'Timing exit={code}; report={path}')
    raise SystemExit(code)


if __name__ == '__main__':
    main()
