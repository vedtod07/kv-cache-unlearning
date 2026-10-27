#!/usr/bin/env python3
"""Compare B's evaluator records with A's expected parity token IDs.

Keys are (model_role, condition, item_id); B's `quantized` maps to A's `int4`.
Requires exactly the expected keys, unique records, status ok and exact prompt,
reference and generated token-ID lists. Ordinary numerical gates and manifests are
checked and reported separately: a token match never substitutes for them.
Ordinary and INT4 are never compared with each other.

Exit 0: every check passed; 2: any missing, duplicate, failed or mismatching record,
gate failure or manifest problem (all reported, nothing dropped).
"""
import argparse
import hashlib
import json
from pathlib import Path

from validate_results import validate_manifest, validate_record

CONDITION_MAP = {'ordinary': 'ordinary', 'quantized': 'int4'}
TOKEN_FIELDS = ('prompt_token_ids', 'reference_token_ids', 'generated_token_ids')


def first_difference(a, b):
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i
    return min(len(a), len(b)) if len(a) != len(b) else None


def compare(expected, records):
    """Return the mismatch report for expected entries and B's records."""
    exp = {}
    for e in expected:
        key = (e['model_role'], e['condition'], e['item_id'])
        if key in exp:
            raise ValueError(f'Duplicate expected key {key}')
        exp[key] = e
    got, duplicates = {}, []
    for rec in records:
        key = (rec.get('model_role'), CONDITION_MAP.get(rec['condition'], rec['condition']), rec['item_id'])
        if key in got:
            duplicates.append(list(key))
        got[key] = rec
    rows, gate_failures = [], []
    for key in sorted(exp):
        rec = got.get(key)
        row = dict(model_role=key[0], condition=key[1], item_id=key[2])
        if rec is None:
            row.update(result='missing')
        elif rec['status'] != 'ok':
            row.update(result='error', error=rec.get('error'))
        else:
            diffs = {f: first_difference(rec.get(f) or [], exp[key][f]) for f in TOKEN_FIELDS
                     if (rec.get(f) or []) != exp[key][f]}
            row.update(result='match' if not diffs else 'mismatch',
                       first_differing_index=diffs or None)
            gate = rec.get('ordinary_scoring_gate')
            if key[1] == 'ordinary':
                row['ordinary_gate_passed'] = None if gate is None else gate['passed']
                if gate is None or not gate['passed']:
                    gate_failures.append(list(key))
        rows.append(row)
    unexpected = sorted(list(k) for k in got.keys() - exp.keys())
    counts = {r: sum(row['result'] == r for row in rows) for r in ('match', 'mismatch', 'missing', 'error')}
    passed = (counts['match'] == len(exp) and not duplicates and not unexpected and not gate_failures)
    return dict(expected=len(exp), received=len(records), counts=counts, duplicates=duplicates,
                unexpected=unexpected, ordinary_gate_failures=gate_failures, token_parity_passed=passed,
                rows=rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--expected', required=True, help="A's parity/expected-token-ids.json")
    parser.add_argument('--runs', nargs='+', required=True, help='Evaluator run directories (manifest + items)')
    parser.add_argument('--output', required=True, help='New JSON report path; never overwritten')
    args = parser.parse_args()
    expected_path = Path(args.expected)
    records, manifests = [], []
    for run in map(Path, args.runs):
        run_records = [json.loads(line) for line in (run / 'items.jsonl').read_text(encoding='utf-8').splitlines()
                       if line.strip()]
        problem = None
        try:
            for rec in run_records:
                validate_record(rec)
            validate_manifest(json.loads((run / 'manifest.json').read_text(encoding='utf-8')), run_records)
        except (ValueError, TypeError, KeyError) as exc:
            problem = f'{type(exc).__name__}: {exc}'
        manifests.append(dict(run=run.name, records=len(run_records), problem=problem))
        records += run_records
    report = compare(json.loads(expected_path.read_text(encoding='utf-8')), records)
    report.update(expected_file=expected_path.name,
                  expected_sha256=hashlib.sha256(expected_path.read_bytes()).hexdigest(),
                  manifests=manifests,
                  passed=report['token_parity_passed'] and not any(m['problem'] for m in manifests),
                  note='Reproducibility evidence only; not additional independent accuracy observations.')
    with open(args.output, 'x', encoding='utf-8') as handle:
        json.dump(report, handle, indent=2)
        handle.write('\n')
    print(f"Parity: {report['counts']} of {report['expected']} expected; duplicates={len(report['duplicates'])}, "
          f"unexpected={len(report['unexpected'])}, ordinary gate failures={len(report['ordinary_gate_failures'])}, "
          f"manifest problems={sum(bool(m['problem']) for m in manifests)}. passed={report['passed']}")
    raise SystemExit(0 if report['passed'] else 2)


if __name__ == '__main__':
    main()
