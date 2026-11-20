#!/usr/bin/env python3
"""Structural checks only. See results/README.md for the scientific contract."""
import argparse
import json
import math

REQUIRED = set('schema_version run_id manifest item_id author_id attempt status phase condition prompt_text prompt_token_ids gold_answer generated_text generated_token_ids correctness behavior annotation_version annotation_notes answer_token_count logprob_parallel_sum logprob_sequential_sum error'.split())


def validate_record(row):
    if not isinstance(row, dict):
        raise ValueError('Record must be an object')
    missing = REQUIRED - row.keys()
    if missing:
        raise ValueError(f'Missing fields: {sorted(missing)}')
    if type(row['schema_version']) is not int or row['schema_version'] != 2:
        raise ValueError('schema_version must be 2')
    for field in ('run_id', 'manifest', 'item_id', 'author_id', 'condition'):
        if not isinstance(row[field], str) or not row[field]:
            raise ValueError(f'{field} must be a nonempty string')
    if type(row['attempt']) is not int or row['attempt'] < 1:
        raise ValueError('attempt must be a positive integer')
    if row['phase'] not in ('development', 'confirmation', 'descriptive'):
        raise ValueError('Invalid phase')
    if row['status'] not in ('ok', 'error'):
        raise ValueError('Invalid status')
    for field in ('prompt_text', 'gold_answer', 'annotation_notes'):
        if not isinstance(row[field], str):
            raise ValueError(f'{field} must be a string')
    for field in ('prompt_token_ids', 'generated_token_ids'):
        value = row[field]
        if field == 'generated_token_ids' and row['status'] == 'error' and value is None:
            continue
        if not isinstance(value, list) or any(type(t) is not int or t < 0 for t in value):
            raise ValueError(f'{field} must contain nonnegative integer IDs')
    count = row['answer_token_count']
    if type(count) is not int or count < 0:
        raise ValueError('Invalid answer_token_count')
    for field in ('logprob_parallel_sum', 'logprob_sequential_sum'):
        value = row[field]
        if value is not None and (type(value) not in (int, float) or not math.isfinite(value)
                                  or value > 0 or count == 0):
            raise ValueError(f'{field} must be a finite nonpositive sum with positive token count')
    if row['status'] == 'ok':
        if row['error'] is not None or not isinstance(row['generated_text'], str):
            raise ValueError('Successful record must have text and no error')
        if row['correctness'] not in ('correct', 'incorrect', 'partial', 'ambiguous', 'unscored'):
            raise ValueError('Invalid correctness')
        if row['behavior'] not in ('answer', 'refusal', 'mixed', 'empty', 'unscored'):
            raise ValueError('Invalid behavior')
        if row['correctness'] != 'unscored' or row['behavior'] != 'unscored':
            if not isinstance(row['annotation_version'], str) or not row['annotation_version']:
                raise ValueError('Annotated records need a rubric version')
    else:
        if row['correctness'] is not None or row['behavior'] is not None:
            raise ValueError('Errors must not be labeled as factual outcomes')
        if not isinstance(row['error'], dict) or not all(row['error'].get(k) for k in ('stage', 'type', 'message')):
            raise ValueError('Error needs stage/type/message')
    return row['run_id'], row['item_id'], row['attempt']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jsonl')
    args = parser.parse_args()
    seen = set()
    with open(args.jsonl) as handle:
        for line_no, line in enumerate(handle, 1):
            try:
                key = validate_record(json.loads(line))
                if key in seen:
                    raise ValueError('Duplicate run/item/attempt')
                seen.add(key)
            except (ValueError, TypeError) as exc:
                raise SystemExit(f'{args.jsonl}:{line_no}: {exc}') from exc
    if not seen:
        raise SystemExit('Empty result file')
    print(f'Validated {len(seen)} records structurally; manifest/annotation review still required.')


if __name__ == '__main__':
    main()
