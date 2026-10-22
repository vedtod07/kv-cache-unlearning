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


MANIFEST_REQUIRED = set('schema_version run_id started_utc finished_utc person code protocol phase model tokenizer data computation generation scoring provenance operations'.split())
CACHE_POLICY_FIELDS = ('backend', 'nbits', 'residual_length', 'q_group_size', 'axis_key', 'axis_value')


def validate_manifest(manifest, records):
    """Check manifest semantics against its item records (single-attempt runs)."""
    if not isinstance(manifest, dict):
        raise ValueError('Manifest must be an object')
    missing = MANIFEST_REQUIRED - manifest.keys()
    if missing:
        raise ValueError(f'Manifest missing fields: {sorted(missing)}')
    if manifest['schema_version'] != 2:
        raise ValueError('Manifest schema_version must be 2')
    model, data, ops = manifest['model'], manifest['data'], manifest['operations']
    if not model.get('revision') or model.get('resolved_revision') != model['revision']:
        raise ValueError('Model revision missing or differs from the resolved revision')
    if not manifest['tokenizer'].get('chat_template_sha256'):
        raise ValueError('Tokenizer chat-template hash missing')
    if not manifest['provenance'].get('environment_sha256'):
        raise ValueError('Environment freeze hash missing')
    condition = manifest['computation'].get('condition')
    policy = manifest['computation'].get('cache_policy')
    if condition != 'ordinary' and (not isinstance(policy, dict)
                                    or any(policy.get(f) is None for f in CACHE_POLICY_FIELDS)):
        raise ValueError('Quantized condition needs a complete cache policy')
    item_ids = data.get('item_ids')
    if not isinstance(item_ids, list) or len(set(item_ids)) != len(item_ids):
        raise ValueError('data.item_ids must be a list of unique IDs')
    for rec in records:
        if (rec['run_id'], rec['phase'], rec['condition']) != (manifest['run_id'], manifest['phase'], condition):
            raise ValueError(f"Record {rec['item_id']} disagrees with manifest run/phase/condition")
    if sorted(r['item_id'] for r in records) != sorted(item_ids):
        raise ValueError('Records do not cover exactly the manifest item IDs')
    ok = sum(r['status'] == 'ok' for r in records)
    if (ops.get('expected_items'), ops.get('completed_items'), ops.get('failed_items')) != (
            len(item_ids), ok, len(records) - ok):
        raise ValueError('Manifest expected/completed/failed counts disagree with records')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('jsonl')
    parser.add_argument('--manifest', help='Also check this manifest.json against the records')
    args = parser.parse_args()
    seen = set()
    records = []
    with open(args.jsonl) as handle:
        for line_no, line in enumerate(handle, 1):
            try:
                row = json.loads(line)
                key = validate_record(row)
                if key in seen:
                    raise ValueError('Duplicate run/item/attempt')
                seen.add(key)
                records.append(row)
            except (ValueError, TypeError) as exc:
                raise SystemExit(f'{args.jsonl}:{line_no}: {exc}') from exc
    if not seen:
        raise SystemExit('Empty result file')
    if args.manifest:
        with open(args.manifest) as handle:
            try:
                validate_manifest(json.load(handle), records)
            except (ValueError, TypeError, KeyError, AttributeError) as exc:
                raise SystemExit(f'{args.manifest}: {exc}') from exc
        print(f'Validated {len(seen)} records and their manifest; annotation review still required.')
    else:
        print(f'Validated {len(seen)} records structurally; manifest/annotation review still required.')


if __name__ == '__main__':
    main()
