"""Check B's exported annotation sheets against the original provisional package.

Usage: python check_b_annotation.py ORIGINAL_DIR EXPORT_DIR
Checks: same rows, review IDs, order and every non-label field unchanged; response
hashes valid; every row complete with allowed values; identical judgments labelled alike.
"""
import csv
import hashlib
import sys
from pathlib import Path

ALLOWED = {
    'correctness': {'correct', 'partial', 'incorrect', 'ambiguous'},
    'behavior': {'answer', 'refusal', 'mixed', 'empty'},
    'supported_target_in_unselected_list': {'yes', 'no', 'uncertain', 'not_applicable'},
    'coherence': {'coherent', 'partly_incoherent', 'incoherent'},
    'relevance': {'on_topic', 'partly_off_topic', 'off_topic'},
}
EDITABLE = set(ALLOWED) | {'reviewer_id', 'notes', 'spec_disagreement', 'reference_review_notes', 'review_progress'}
orig_dir, export_dir = map(Path, sys.argv[1:3])
problems = []
for pop, export_name in (('forget', 'forget-review-B.csv'), ('utility', 'utility-review-B.csv')):
    orig = list(csv.DictReader(open(orig_dir / f'{pop}-review.csv', encoding='utf-8')))
    new = list(csv.DictReader(open(export_dir / export_name, encoding='utf-8')))
    required = [f for f in ALLOWED if pop == 'utility' or f not in ('coherence', 'relevance')]
    if len(orig) != len(new) or list(orig[0]) != list(new[0]):
        problems.append(f'{pop}: row count or columns differ')
        continue
    groups = {}
    for o, n in zip(orig, new):
        rid = o['review_id']
        if rid != n['review_id']:
            problems.append(f'{pop}: order or ID changed at {rid}')
        changed = [c for c in o if c not in EDITABLE and o[c] != n[c]]
        if changed:
            problems.append(f'{pop} {rid}: non-label fields changed {changed}')
        if hashlib.sha256(n['response'].encode()).hexdigest() != n['response_sha256']:
            problems.append(f'{pop} {rid}: response hash mismatch')
        for f in required:
            if n[f] not in ALLOWED[f]:
                problems.append(f'{pop} {rid}: {f}={n[f]!r}')
        if n['review_progress'] != 'complete':
            problems.append(f'{pop} {rid}: review_progress not complete')
        key = (n['question'], n['reference_answer'], n['specification_sha256'], n['response'])
        labels = tuple(n[f] for f in required)
        if groups.setdefault(key, labels) != labels:
            problems.append(f'{pop} {rid}: identical judgment labelled differently')
    print(f'{pop}: {len(new)} rows checked')
print('OK: ready to return' if not problems else f'{len(problems)} problem(s):')
for p in problems[:50]:
    print('  ', p)
