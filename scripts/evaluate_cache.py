#!/usr/bin/env python3
"""Paired ordinary vs quantized-cache evaluator emitting schema-v2 records (v0).

For each model and cache condition this writes one run directory containing
`manifest.json` and `items.jsonl` (results/README.md, schema version 2). Factual
labels stay `unscored`; nothing here judges disclosure.

Conventions (docs/DECISIONS.md, 2026-10-22): shared prompt helper (fixed system
message and date), prompt token IDs must equal the recorded fixtures, explicit
all-ones mask (unpadded, batch size one), greedy, one beam, 64-token budget,
identical stopping settings across conditions, a fresh cache per item, and
end-of-turn-inclusive reference scoring (log-probability sums with token counts).

Exit 0: every item completed; 1: setup/runtime failure; 2: some items failed
(failures are recorded, never dropped).
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import time

from test_kv_scoring_path import score_parallel, score_sequential
from tofu_prompts import (SYSTEM_PROMPT, TEMPLATE_DATE, reference_token_ids, render_prompt,
                          template_sha256)
from validate_results import validate_manifest, validate_record

PROTOCOL = 'v4 with conventions recorded in docs/DECISIONS.md on 2026-10-22'
DEFAULT_MODELS = ['full=open-unlearning/tofu_Llama-3.2-1B-Instruct_full@88e31200b97e4c0c04ae0d2f0b591f427046d192']
DEFAULT_FIXTURES = ['results/day2/day2_20261019T122314559618Z/fixtures.json']
TOKENIZER = 'open-unlearning/tofu_Llama-3.2-1B-Instruct_full@88e31200b97e4c0c04ae0d2f0b591f427046d192'


def parse_model(spec):
    role, rest = spec.split('=', 1)
    model_id, revision = rest.split('@', 1)
    return role, model_id, revision


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def utc_now():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')


def git_state():
    try:
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
        dirty = bool(subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'],
                                             text=True).strip())
        diff = subprocess.check_output(['git', 'diff', 'HEAD'])
        return commit, dirty, hashlib.sha256(diff).hexdigest() if dirty else None
    except (OSError, subprocess.CalledProcessError):
        return None, None, None


def author_of(item):
    # Utility questions (real authors, world facts) have no TOFU author; keep a labelled group.
    return item.get('author_id') or f"no-author:{item.get('dataset_config', 'unknown')}"


def make_record(run_id, item, condition, prompt_text, prompt_ids):
    return dict(schema_version=2, run_id=run_id, manifest='manifest.json', item_id=item['item_id'],
                author_id=author_of(item), attempt=1, status='ok', phase=None, condition=condition,
                prompt_text=prompt_text, prompt_token_ids=prompt_ids, gold_answer=item['gold_answer'],
                generated_text=None, generated_token_ids=None, correctness='unscored', behavior='unscored',
                annotation_version=None, annotation_notes='', answer_token_count=0,
                logprob_parallel_sum=None, logprob_sequential_sum=None, error=None)


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

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=False)
    base_run = args.run_id or datetime.now(timezone.utc).strftime('eval_%Y%m%dT%H%M%SZ')
    commit, dirty, diff_sha256 = git_state()
    env_path = out_dir / 'pip-freeze.txt'
    env_path.write_text(subprocess.run([sys.executable, '-m', 'pip', 'freeze'], capture_output=True,
                                       text=True).stdout, encoding='utf-8')
    try:
        import hqq
        hqq_version = getattr(hqq, '__version__', None)
    except ImportError:
        hqq_version = None

    tok_id, tok_rev = TOKENIZER.split('@', 1)
    tok = AutoTokenizer.from_pretrained(tok_id, revision=tok_rev)
    if template_sha256(tok) != args.expected_template_sha256:
        raise RuntimeError('Chat template hash differs from the recorded template')

    items = []
    for path in args.fixtures:
        items += json.loads(Path(path).read_text(encoding='utf-8'))
    if args.limit:
        items = items[:args.limit]
    prepared = []
    for item in items:
        prompt_text, prompt_ids = render_prompt(tok, item['question'])
        if prompt_ids != item['prompt_token_ids']:
            raise RuntimeError(f"Rendered prompt differs from fixture for {item['item_id']}")
        prepared.append((item, prompt_text, prompt_ids,
                         reference_token_ids(tok, prompt_text, prompt_ids, item['gold_answer'])))

    cache_policy = dict(backend=args.backend, backend_version=hqq_version if args.backend == 'hqq' else None,
                        nbits=args.nbits, residual_length=args.residual_length,
                        q_group_size=args.q_group_size, axis_key=args.axis_key, axis_value=args.axis_value,
                        semantics='transformers 5.5.4 QuantizedCache: prompt K/V quantized on the first '
                                  'update but returned in full precision for that pass; later steps read '
                                  'dequantized storage plus a full-precision residual buffer; each flush '
                                  're-quantizes the whole cache (see docs/LOG.md, 2026-10-19)')

    def new_cache(condition):
        if condition == 'ordinary':
            return DynamicCache(config=model.config)
        return QuantizedCache(backend=args.backend, config=model.config, nbits=args.nbits,
                              residual_length=args.residual_length, q_group_size=args.q_group_size,
                              axis_key=args.axis_key, axis_value=args.axis_value)

    runs = []
    for spec in args.models:
        role, model_id, revision = parse_model(spec)
        model = AutoModelForCausalLM.from_pretrained(model_id, revision=revision,
                                                     dtype=getattr(torch, args.dtype),
                                                     attn_implementation='sdpa').to(device).eval()
        resolved = getattr(model.config, '_commit_hash', None)
        if resolved != revision:
            raise RuntimeError(f'{role}: resolved revision {resolved} differs from requested {revision}')
        eos = model.generation_config.eos_token_id
        eos = list(eos) if isinstance(eos, (list, tuple)) else [eos]
        for condition in args.conditions:
            run_id = f'{base_run}_{role}_{condition}'
            run_dir = out_dir / run_id
            run_dir.mkdir()
            started = utc_now()
            if on_cuda:
                torch.cuda.reset_peak_memory_stats(device)
            t_run = time.perf_counter()
            records = []
            # Written and flushed item by item, so a crash keeps every completed record.
            items_file = open(run_dir / 'items.jsonl', 'w', encoding='utf-8')
            for item, prompt_text, prompt_ids, answer_ids in prepared:
                rec = make_record(run_id, item, condition, prompt_text, prompt_ids)
                rec.update(phase=args.phase, model_role=role, dataset_config=item.get('dataset_config', 'forget10'))
                stage = 'generation'
                try:
                    ids = torch.tensor([prompt_ids], device=device)
                    sync(); t = time.perf_counter()
                    with torch.no_grad():
                        out = model.generate(input_ids=ids, attention_mask=torch.ones_like(ids),
                                             past_key_values=new_cache(condition), do_sample=False,
                                             num_beams=1, max_new_tokens=args.max_new_tokens,
                                             eos_token_id=eos, pad_token_id=eos[0])
                    sync()
                    generated = out[0, ids.shape[1]:].tolist()
                    rec.update(generated_token_ids=generated,
                               generated_text=tok.decode(generated, skip_special_tokens=True),
                               generated_token_count=len(generated),
                               ended_with_eos=bool(generated) and generated[-1] in eos,
                               reached_token_budget=len(generated) >= args.max_new_tokens,
                               generate_seconds=time.perf_counter() - t)
                    stage = 'scoring'
                    full = torch.tensor([prompt_ids + answer_ids], device=device)
                    parallel = score_parallel(torch, model, full, len(prompt_ids))
                    sequential = score_sequential(torch, model, full, len(prompt_ids), new_cache(condition))
                    if not all(math.isfinite(x) for x in parallel + sequential):
                        raise FloatingPointError('Nonfinite token NLL')
                    rec.update(answer_token_count=len(answer_ids), reference_token_ids=answer_ids,
                               logprob_parallel_sum=-sum(parallel), logprob_sequential_sum=-sum(sequential))
                except Exception as exc:
                    rec.update(status='error', correctness=None, behavior=None, generated_text=None,
                               generated_token_ids=None,
                               error=dict(stage=stage, type=type(exc).__name__, message=str(exc) or 'no message'))
                validate_record(rec)
                records.append(rec)
                items_file.write(json.dumps(rec, allow_nan=False) + '\n')
                items_file.flush()
            items_file.close()
            n_ok = sum(r['status'] == 'ok' for r in records)
            manifest = dict(
                schema_version=2, run_id=run_id, started_utc=started, finished_utc=utc_now(), person='B',
                code=dict(commit=commit, dirty_tracked_files=dirty, dirty_diff_sha256=diff_sha256,
                          script='scripts/evaluate_cache.py'),
                config=vars(args),
                protocol=PROTOCOL, phase=args.phase,
                model=dict(role=role, id=model_id, revision=revision, resolved_revision=resolved,
                           dtype=args.dtype),
                tokenizer=dict(id=tok_id, revision=tok_rev, chat_template_sha256=template_sha256(tok),
                               system_prompt=SYSTEM_PROMPT, template_date=TEMPLATE_DATE),
                data=dict(fixtures=[dict(path=p, sha256=sha256_file(p)) for p in args.fixtures],
                          item_ids=[i['item_id'] for i, *_ in prepared],
                          author_ids=sorted({author_of(i) for i, *_ in prepared}),
                          note='Development fixtures already exposed; utility items use '
                               'no-author:<config> grouping'),
                computation=dict(condition=condition, cache_policy=None if condition == 'ordinary' else cache_policy,
                                 attention='sdpa', weight_precision=args.dtype, device=str(device),
                                 gpu=torch.cuda.get_device_name(device) if on_cuda else None,
                                 cuda=torch.version.cuda, torch=torch.__version__,
                                 transformers=transformers.__version__, prefill_chunking=None),
                generation=dict(do_sample=False, num_beams=1, max_new_tokens=args.max_new_tokens,
                                eos_token_id=eos, pad_token_id=eos[0], attention_mask='all ones (unpadded)',
                                fresh_cache_per_item=True),
                scoring=dict(reference='in-context gold answer ending with end-of-turn',
                             logprob='sum of float32 log-softmax token log-probabilities',
                             parallel='single pass, cache disabled', sequential='prefill plus one-token '
                             'decode steps through a fresh cache of this condition'),
                provenance=dict(environment_freeze='../pip-freeze.txt',
                                environment_sha256=sha256_file(env_path),
                                validation_reports=['results/diagnostics-v2/', 'results/timing/'],
                                annotation_rubric=None),
                operations=dict(runtime_seconds=time.perf_counter() - t_run,
                                peak_memory_mib=(torch.cuda.max_memory_allocated(device) / 2**20) if on_cuda else None,
                                expected_items=len(records), completed_items=n_ok,
                                failed_items=len(records) - n_ok, retry_policy='none'))
            validate_manifest(manifest, records)
            (run_dir / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
            runs.append(dict(run_id=run_id, ok=n_ok, failed=len(records) - n_ok))
        del model
        if on_cuda:
            torch.cuda.empty_cache()
    return runs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--models', nargs='+', default=DEFAULT_MODELS, help='role=model_id@revision')
    parser.add_argument('--fixtures', nargs='+', default=DEFAULT_FIXTURES)
    parser.add_argument('--conditions', nargs='+', choices=['ordinary', 'quantized'],
                        default=['ordinary', 'quantized'])
    parser.add_argument('--limit', type=int, default=0, help='First N items only (0 = all)')
    parser.add_argument('--phase', choices=['development', 'confirmation', 'descriptive'], default='development')
    parser.add_argument('--backend', choices=['hqq', 'quanto'], default='hqq')
    parser.add_argument('--nbits', type=int, default=4)
    parser.add_argument('--residual_length', type=int, default=128)
    parser.add_argument('--q_group_size', type=int, default=64)
    parser.add_argument('--axis_key', type=int, default=1)
    parser.add_argument('--axis_value', type=int, default=1)
    parser.add_argument('--dtype', choices=['float32', 'float16'], default='float32')
    parser.add_argument('--max_new_tokens', type=int, default=64)
    parser.add_argument('--expected_template_sha256',
                        default='5816fce10444e03c2e9ee1ef8a4a1ea61ae7e69e438613f3b17b69d0426223a4')
    parser.add_argument('--run_id', help='Base run id (default: UTC timestamp)')
    parser.add_argument('--device')
    parser.add_argument('--out_dir', required=True, help='New directory; never overwritten')
    args = parser.parse_args()
    try:
        runs = run(args)
    except Exception as exc:
        print(f'Evaluator exit=1: {type(exc).__name__}: {exc}')
        raise SystemExit(1)
    code = 0 if all(r['failed'] == 0 for r in runs) else 2
    for r in runs:
        print(f"{r['run_id']}: {r['ok']} ok, {r['failed']} failed")
    print(f'Evaluator exit={code}; out_dir={args.out_dir}. Labels are unscored; no disclosure claim.')
    raise SystemExit(code)


if __name__ == '__main__':
    main()
