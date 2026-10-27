#!/usr/bin/env python3
"""Build condition-masked annotation sheets for B's independent review of A's outputs.

Reads A's generation JSONL files and writes, per population (forget / utility):
- a shuffled review CSV with question, reference answer, response and termination
  fields only; model identity, cache condition and any existing labels are removed;
- a separate key CSV mapping each review code back to its source record.

Label columns follow the rubric candidate (docs/RUBRIC_CANDIDATE_2026-10-26.md): target
fields for both populations, correctness, behaviour and supported_target_in_unselected_list,
plus coherence/relevance for utility. Every row carries the reviewer ID and rubric version.
With --spec_table (required for final annotation) the target fields come from the frozen
per-item specification, the table hash is recorded, and reviewers note disagreement in
spec_disagreement rather than editing the specification.
Duplicate source identities stop the build; error records are excluded from labelling
but counted in the README completeness report.

The reviewer must not open the key files until first-pass labels are complete.
No labels are created or suggested here.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import random

TARGET_COLUMNS = ['requested_fact', 'target_kind', 'target_in_prompt', 'reference_issue']
# Reviewer-filled per response; the list flag is yes/no/uncertain/not_applicable (rubric section 4).
RESPONSE_COLUMNS = ['correctness', 'behavior', 'supported_target_in_unselected_list']
FORGET_COLUMNS = TARGET_COLUMNS + RESPONSE_COLUMNS + ['notes']
UTILITY_COLUMNS = TARGET_COLUMNS + RESPONSE_COLUMNS + ['coherence', 'relevance', 'notes']
# Frozen per-item specification table (CSV, one row per item_id). With --spec_table the
# target fields are prefilled from it and the extra fields are shown read-only; reviewers
# record disagreement in spec_disagreement instead of editing the specification.
SPEC_REQUIRED = ['item_id', 'domain', 'requested_fact', 'target_kind', 'required_components',
                 'one_example_suffices', 'acceptable_aliases', 'evidence_source', 'reference_completeness',
                 'reference_issue', 'target_in_prompt', 'rationale', 'status']
SPEC_SHOWN = ['domain', 'required_components', 'one_example_suffices', 'acceptable_aliases',
              'reference_completeness']


def sha256_text(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def load_records(paths):
    records = []
    for path in paths:
        source_hash = hashlib.sha256(Path(path).read_bytes()).hexdigest()
        for line_no, line in enumerate(Path(path).read_text(encoding='utf-8').splitlines(), 1):
            if line.strip():
                rec = json.loads(line)
                rec['_source'] = f'{Path(path).name}:{line_no}'
                rec['_source_sha256'] = source_hash
                records.append(rec)
    return records


def attach_questions(records, fixture_paths):
    """Fill `question` for records that predate it (evaluator v0) by a validated stable-ID join.

    The fixture must match the record's gold answer and exact prompt token IDs; the
    question is never recovered by stripping the rendered chat prompt."""
    fixtures = {}
    for path in fixture_paths:
        for item in json.loads(Path(path).read_text(encoding='utf-8')):
            if item['item_id'] in fixtures:
                raise ValueError(f"Duplicate fixture item {item['item_id']}")
            fixtures[item['item_id']] = item
    for rec in records:
        if rec.get('question') is not None:
            continue
        item = fixtures.get(rec['item_id'])
        if item is None:
            raise ValueError(f"{rec['_source']}: no question and no fixture for {rec['item_id']}")
        if item['gold_answer'] != rec['gold_answer'] or item['prompt_token_ids'] != rec.get('prompt_token_ids'):
            raise ValueError(f"{rec['_source']}: fixture for {rec['item_id']} does not match the record")
        rec['question'] = item['question']
    return records


def population(rec):
    return 'forget' if ':forget' in rec['item_id'] else 'utility'


def identity(rec):
    return (rec.get('run_id'), rec.get('model_role'), rec.get('condition'), rec['item_id'],
            rec.get('attempt', 1))


def check_unique(records):
    seen = {}
    for rec in records:
        key = identity(rec)
        if key in seen:
            raise ValueError(f'Duplicate source record {key}: {seen[key]} and {rec["_source"]}')
        seen[key] = rec['_source']


def termination(rec):
    """Separate EOS and budget evidence; EOS exactly at the budget is not truncation."""
    eos, budget = rec.get('ended_with_eos'), rec.get('reached_token_budget')
    if eos is None or budget is None:
        return 'unknown'
    if eos:
        return 'eos_at_budget' if budget else 'eos'
    return 'budget_without_eos' if budget else 'stopped_without_eos'


def load_spec_table(path):
    """Read the frozen per-item specification; every row complete, one row per item."""
    with open(path, newline='', encoding='utf-8') as handle:
        rows = list(csv.DictReader(handle))
    if not rows or any(c not in rows[0] for c in SPEC_REQUIRED):
        raise ValueError(f'Specification table needs columns {SPEC_REQUIRED}')
    spec = {}
    for row in rows:
        if row['item_id'] in spec:
            raise ValueError(f"Duplicate specification for {row['item_id']}")
        spec[row['item_id']] = row
    return spec


def build(records, seed, reviewer_id='', rubric_version='', spec=None):
    """Return {population: (review_rows, key_rows)} without touching the filesystem."""
    check_unique(records)
    missing = [r['_source'] for r in records if r.get('status', 'ok') == 'ok' and r.get('question') is None]
    if missing:
        raise ValueError(f'Records without question text (use --fixtures): {missing[:3]}')
    if spec is not None:
        uncovered = sorted({r['item_id'] for r in records if r.get('status', 'ok') == 'ok'} - spec.keys())
        if uncovered:
            raise ValueError(f'Specification table misses items: {uncovered[:3]}')
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
            response_hash = sha256_text(rec['generated_text'])
            count = rec.get('generated_token_count')
            if count is None and rec.get('generated_token_ids') is not None:
                count = len(rec['generated_token_ids'])
            labels = {c: '' for c in label_cols}
            shown = {}
            if spec is not None:
                item_spec = spec[rec['item_id']]
                labels.update({c: item_spec[c] for c in TARGET_COLUMNS})
                shown = {f'spec_{c}': item_spec[c] for c in SPEC_SHOWN}
                labels['spec_disagreement'] = ''
            review.append({'review_id': code, 'reviewer_id': reviewer_id, 'rubric_version': rubric_version,
                           'question': rec['question'], 'reference_answer': rec['gold_answer'],
                           **shown,
                           'response': rec['generated_text'], 'response_sha256': response_hash,
                           'generated_token_count': '' if count is None else count,
                           'ended_with_eos': rec.get('ended_with_eos', ''),
                           'reached_token_budget': rec.get('reached_token_budget', ''),
                           'termination': termination(rec),
                           **labels})
            key.append({'review_id': code, 'item_id': rec['item_id'],
                        'model_role': rec.get('model_role'), 'condition': rec.get('condition'),
                        'run_id': rec.get('run_id'), 'attempt': rec.get('attempt', 1),
                        'source': rec['_source'], 'source_sha256': rec['_source_sha256'],
                        'response_sha256': response_hash})
        out[pop] = (review, key)
    return out


def completeness(records):
    """Per-population counts of all records and of excluded (error) records."""
    report = {}
    for pop in ('forget', 'utility'):
        group = [r for r in records if population(r) == pop]
        report[pop] = dict(total=len(group), excluded_errors=sum(r.get('status', 'ok') != 'ok' for r in group))
    return report


def write_csv(path, rows):
    with open(path, 'w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('outputs', nargs='+', help="A's generation JSONL files")
    parser.add_argument('--out_dir', required=True)
    parser.add_argument('--reviewer_id', required=True, help='Recorded on every row, e.g. B')
    parser.add_argument('--rubric_version', required=True, help='Frozen rubric version, e.g. tofu-disclosure-v1.0')
    parser.add_argument('--seed', default='b-review-v1', help='Shuffle seed (recorded in README)')
    parser.add_argument('--fixtures', nargs='*', default=[],
                        help='Fixture JSON files supplying question text for records without it')
    parser.add_argument('--spec_table', help='Frozen per-item specification CSV (required for final annotation)')
    args = parser.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=False)
    records = attach_questions(load_records(args.outputs), args.fixtures)
    spec = load_spec_table(args.spec_table) if args.spec_table else None
    built = build(records, args.seed, args.reviewer_id, args.rubric_version, spec)
    counts = {}
    for pop, (review, key) in built.items():
        write_csv(out_dir / f'{pop}-review.csv', review)
        write_csv(out_dir / f'KEY-DO-NOT-OPEN-{pop}.csv', key)
        counts[pop] = len(review)
    sources = '\n'.join(f'  {Path(p).name} sha256={hashlib.sha256(Path(p).read_bytes()).hexdigest()}'
                        for p in args.outputs)
    (out_dir / 'README.txt').write_text(
        'Condition-masked review sheets for Person B.\n'
        f'Sources:\n{sources}\n'
        f'Question fixtures: {", ".join(Path(p).name for p in args.fixtures) or "none"}\n'
        + (f'Specification table: {Path(args.spec_table).name} '
           f'sha256={hashlib.sha256(Path(args.spec_table).read_bytes()).hexdigest()}\n'
           if args.spec_table else 'Specification table: NONE (not valid for final annotation)\n') +
        f'Reviewer: {args.reviewer_id}\nRubric version: {args.rubric_version}\n'
        f'Seed: {args.seed}\nRows to label: {counts}\n'
        f'Completeness (error records excluded from labelling, not from the denominator): '
        f'{completeness(records)}\n'
        'Label every row in *-review.csv using the frozen rubric version, without consulting\n'
        "A's labels or the KEY-DO-NOT-OPEN files. Record any prior exposure before labelling.\n"
        'Open the keys only after first-pass labels are complete, then compare and record\n'
        'agreement before adjudication.\n',
        encoding='utf-8')
    print(f'Wrote {counts} review rows to {out_dir}')


if __name__ == '__main__':
    main()
