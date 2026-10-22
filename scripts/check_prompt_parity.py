#!/usr/bin/env python3
"""Check that the shared prompt helper reproduces A's recorded TOFU inputs exactly.

Compares, for every fixture item:
- rendered prompt text and token IDs against A's day-two fixtures.json;
- in-context reference-answer token IDs (ending with end-of-turn) against A's
  day-five scoring trace (scoring_input_ids and scoring_labels).

Needs only the tokenizer (no GPU). Exit 0: all items match; 1: setup/runtime error;
2: at least one mismatch.
"""
import argparse
import json
from pathlib import Path

from tofu_prompts import (EXPECTED_TEMPLATE_SHA256, SYSTEM_PROMPT, TEMPLATE_DATE,
                          compare_item, reference_token_ids, render_prompt, template_sha256)

DEFAULT_FIXTURES = 'results/day2/day2_20261019T122314559618Z/fixtures.json'
DEFAULT_TRACE = 'results/day5/day5_20261020T110711928957Z/token-and-mask-trace.json'


def run(args):
    import transformers
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained(args.tokenizer, revision=args.revision)
    fixtures = json.loads(Path(args.fixtures).read_text(encoding='utf-8'))
    trace = {t['item_id']: t for t in json.loads(Path(args.trace).read_text(encoding='utf-8'))}
    items, mismatched = [], 0
    for fx in fixtures:
        text, prompt_ids = render_prompt(tok, fx['question'])
        answer_ids = reference_token_ids(tok, text, prompt_ids, fx['gold_answer'])
        tr = trace.get(fx['item_id'])
        problems = compare_item(fx['prompt_token_ids'],
                                tr['scoring_input_ids'] if tr else None,
                                tr['scoring_labels'] if tr else None,
                                prompt_ids, answer_ids)
        if text != fx['prompt_text']:
            problems.append('prompt text differs from fixture')
        if tr is None:
            problems.append('item missing from scoring trace')
        elif tr.get('target_token_count') != len(answer_ids):
            problems.append('reference token count differs from trace target_token_count')
        mismatched += bool(problems)
        items.append(dict(item_id=fx['item_id'], prompt_tokens=len(prompt_ids),
                          reference_tokens=len(answer_ids), problems=problems))
    sha = template_sha256(tok)
    template_ok = sha == EXPECTED_TEMPLATE_SHA256
    return dict(kind='prompt_parity_check', transformers=transformers.__version__,
                tokenizer=args.tokenizer, tokenizer_revision=args.revision,
                template_sha256=sha, template_matches_recorded=template_ok,
                system_prompt=SYSTEM_PROMPT, template_date=TEMPLATE_DATE,
                fixtures=args.fixtures, trace=args.trace, items_checked=len(items),
                items_mismatched=mismatched, items=items,
                passed=template_ok and mismatched == 0 and len(items) > 0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tokenizer', default='open-unlearning/tofu_Llama-3.2-1B-Instruct_full')
    parser.add_argument('--revision', default='88e31200b97e4c0c04ae0d2f0b591f427046d192')
    parser.add_argument('--fixtures', default=DEFAULT_FIXTURES)
    parser.add_argument('--trace', default=DEFAULT_TRACE)
    parser.add_argument('--output', required=True, help='New JSON report path; never overwritten')
    args = parser.parse_args()
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as handle:
        try:
            report = run(args)
            code = 0 if report['passed'] else 2
        except Exception as exc:
            report = {'kind': 'prompt_parity_check', 'status': 'error',
                      'error': f'{type(exc).__name__}: {exc}'}
            code = 1
        json.dump(report, handle, indent=2)
        handle.write('\n')
    summary = (f"{report.get('items_checked', 0)} items, {report.get('items_mismatched', '?')} mismatched, "
               f"template match={report.get('template_matches_recorded')}")
    print(f'Prompt parity exit={code}; {summary}; report={path}')
    raise SystemExit(code)


if __name__ == '__main__':
    main()
