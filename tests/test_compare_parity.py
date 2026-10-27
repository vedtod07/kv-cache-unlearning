import copy
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from compare_parity import compare

EVAL_V0 = Path(__file__).resolve().parents[1] / 'results' / 'eval-v0-full'


def saved_records():
    records = []
    for path in sorted(EVAL_V0.glob('*/items.jsonl')):
        for line in path.read_text(encoding='utf-8').splitlines():
            rec = json.loads(line)
            if rec['condition'] == 'ordinary':
                rec['ordinary_scoring_gate'] = {'passed': True}
            records.append(rec)
    return records[:3] + records[80:83]


def expected_for(records):
    return [dict(model_role=r['model_role'], condition={'quantized': 'int4'}.get(r['condition'], r['condition']),
                 item_id=r['item_id'], **{f: list(r[f]) for f in
                                         ('prompt_token_ids', 'reference_token_ids', 'generated_token_ids')})
            for r in records]


class Parity(unittest.TestCase):
    def test_exact_records_pass_and_quantized_maps_to_int4(self):
        records = saved_records()
        report = compare(expected_for(records), records)
        self.assertTrue(report['token_parity_passed'])
        self.assertEqual(report['counts']['match'], 6)

    def test_mismatch_missing_duplicate_and_gate_failures_are_reported(self):
        records = saved_records()
        expected = expected_for(records)
        bad = copy.deepcopy(records)
        bad[0]['generated_token_ids'][2] += 1
        bad[1]['ordinary_scoring_gate'] = {'passed': False}
        del bad[4]
        bad.append(copy.deepcopy(records[5]))
        report = compare(expected, bad)
        self.assertFalse(report['token_parity_passed'])
        self.assertEqual(report['counts']['mismatch'], 1)
        self.assertEqual(report['counts']['missing'], 1)
        self.assertEqual(len(report['duplicates']), 1)
        self.assertEqual(len(report['ordinary_gate_failures']), 1)
        mismatch = next(r for r in report['rows'] if r['result'] == 'mismatch')
        self.assertEqual(mismatch['first_differing_index'], {'generated_token_ids': 2})


if __name__ == '__main__':
    unittest.main()
