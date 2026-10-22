#!/usr/bin/env python3
"""Build blind annotation sheets for B's independent review of A's outputs.

Reads A's generation JSONL files and writes, per population (forget / utility):
- a shuffled review CSV with question, reference answer and response only; model
  identity, cache condition and any existing labels are removed;
- a separate key CSV mapping each review code back to its source record.

The reviewer must not open the key files until first-pass labels are complete.
No labels are created or suggested here.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import random

FORGET_COLUMNS = ['requested_fact', 'target_in_prompt', 'reference_issue',
                  'correctness', 'behavior', 'notes']
UTILITY_COLUMNS = ['correctness', 'behavior', 'coherence', 'relevance', 'notes']


def load_records(paths):
    records = []
    for path in paths:
        for line_no, line in enumerate(Path(path).read_text(encoding='utf-8').splitlines(), 1):
            if line.strip():
                rec = json.loads(line)
                rec['_source'] = f'{Path(path).name}:{line_no}'
                records.append(rec)
    return records


def population(rec):
    return 'forget' if ':forget' in rec['item_id'] else 'utility'


def build(records, seed):
    """Return {population: (review_rows, key_rows)} without touching the filesystem."""
    out = {}
    for pop in ('forget', 'utility'):
        group = [r for r in records if population(r) == pop and r.get('status', 'ok') == 'ok']
        if not group:
            continue
        rng = random.Random(f'{seed}:{pop}')
        rng.shuffle(group)
        label_cols = FORGET_COLUMNS if pop == 'forget' else UTILITY_COLUMNS
        review, key = [], []
        for n, rec in enumerate(group, 1):
            code = f"{pop[0].upper()}{n:03d}"
            truncated = bool(rec.get('reached_token_budget')) or rec.get('ended_with_eos') is False
            review.append({'review_id': code, 'question': rec['question'],
                           'reference_answer': rec['gold_answer'], 'response': rec['generated_text'],
                           'truncated_or_no_eos': 'yes' if truncated else 'no',
                           **{c: '' for c in label_cols}})
            key.append({'review_id': code, 'item_id': rec['item_id'],
                        'model_role': rec.get('model_role'), 'condition': rec.get('condition'),
                        'run_id': rec.get('run_id'), 'source': rec['_source'],
                        'response_sha256': hashlib.sha256(rec['generated_text'].encode()).hexdigest()})
        out[pop] = (review, key)
    return out


def write_csv(path, rows):
    with open(path, 'w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('outputs', nargs='+', help="A's generation JSONL files")
    parser.add_argument('--out_dir', required=True)
    parser.add_argument('--seed', default='b-review-v1', help='Shuffle seed (recorded in README)')
    args = parser.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=False)
    built = build(load_records(args.outputs), args.seed)
    counts = {}
    for pop, (review, key) in built.items():
        write_csv(out_dir / f'{pop}-review.csv', review)
        write_csv(out_dir / f'KEY-DO-NOT-OPEN-{pop}.csv', key)
        counts[pop] = len(review)
    (out_dir / 'README.txt').write_text(
        'Blind review sheets for Person B.\n'
        f'Sources: {", ".join(Path(p).name for p in args.outputs)}\n'
        f'Seed: {args.seed}\nRows: {counts}\n'
        'Label every row in *-review.csv using the frozen rubric version, without consulting\n'
        "A's labels or the KEY-DO-NOT-OPEN files. Open the keys only after first-pass\n"
        'labels are complete, then compare and record agreement before adjudication.\n',
        encoding='utf-8')
    print(f'Wrote {counts} review rows to {out_dir}')


if __name__ == '__main__':
    main()
