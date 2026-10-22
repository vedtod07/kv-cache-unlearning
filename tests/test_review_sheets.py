import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_review_sheets import build, completeness, termination


def rec(item, role, text, config='forget10'):
    return {'item_id': f'locuslab/TOFU@rev:{config}:train:{item}', 'model_role': role,
            'condition': 'ordinary_dynamic_cache', 'run_id': 'r', 'question': f'q{item}',
            'gold_answer': f'a{item}', 'generated_text': text, 'status': 'ok',
            'correctness': 'correct', 'behavior': 'answer', 'ended_with_eos': True,
            'reached_token_budget': False, '_source': 'f.jsonl:1', '_source_sha256': 'h'}


class ReviewSheets(unittest.TestCase):
    records = [rec(0, 'full', 'x'), rec(0, 'retain90', 'y'), rec(1, 'full', 'z', 'real_authors')]

    def test_review_rows_hide_model_and_labels(self):
        review, key = build(self.records, 's')['forget']
        self.assertEqual(len(review), 2)
        for row in review:
            self.assertNotIn('model_role', row)
            self.assertEqual(row['correctness'], '')
            self.assertEqual(row['behavior'], '')
        self.assertEqual({k['model_role'] for k in key}, {'full', 'retain90'})

    def test_populations_split_and_shuffle_is_deterministic(self):
        first, second = build(self.records, 's'), build(self.records, 's')
        self.assertEqual(first['forget'][1], second['forget'][1])
        self.assertEqual(len(first['utility'][0]), 1)
        self.assertIn('coherence', first['utility'][0][0])

    def test_failed_records_are_excluded(self):
        bad = dict(rec(2, 'full', 'w'), status='error')
        review, _ = build(self.records + [bad], 's')['forget']
        self.assertEqual(len(review), 2)
        self.assertEqual(completeness(self.records + [bad])['forget'],
                         {'total': 3, 'excluded_errors': 1})

    def test_rows_carry_reviewer_rubric_and_target_fields(self):
        built = build(self.records, 's', reviewer_id='B', rubric_version='tofu-disclosure-v1.0')
        for pop in ('forget', 'utility'):
            row = built[pop][0][0]
            self.assertEqual((row['reviewer_id'], row['rubric_version']), ('B', 'tofu-disclosure-v1.0'))
            for col in ('target_kind', 'target_in_prompt', 'reference_issue', 'response_sha256'):
                self.assertIn(col, row)

    def test_duplicate_source_identity_fails(self):
        with self.assertRaises(ValueError):
            build(self.records + [rec(0, 'full', 'x')], 's')

    def test_termination_keeps_eos_and_budget_separate(self):
        self.assertEqual(termination({'ended_with_eos': True, 'reached_token_budget': True}), 'eos_at_budget')
        self.assertEqual(termination({'ended_with_eos': False, 'reached_token_budget': True}), 'budget_without_eos')
        self.assertEqual(termination({'ended_with_eos': True, 'reached_token_budget': False}), 'eos')
        self.assertEqual(termination({}), 'unknown')


if __name__ == '__main__':
    unittest.main()
