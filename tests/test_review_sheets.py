import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_review_sheets import build


def rec(item, role, text, config='forget10'):
    return {'item_id': f'locuslab/TOFU@rev:{config}:train:{item}', 'model_role': role,
            'condition': 'ordinary_dynamic_cache', 'run_id': 'r', 'question': f'q{item}',
            'gold_answer': f'a{item}', 'generated_text': text, 'status': 'ok',
            'correctness': 'correct', 'behavior': 'answer', 'ended_with_eos': True,
            'reached_token_budget': False, '_source': 'f.jsonl:1'}


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


if __name__ == '__main__':
    unittest.main()
