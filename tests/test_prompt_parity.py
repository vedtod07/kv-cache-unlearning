import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from tofu_prompts import compare_item


class PromptParity(unittest.TestCase):
    prompt = [1, 2, 3]
    answer = [7, 8, 9]
    full = [1, 2, 3, 7, 8, 9]
    labels = [-100, -100, -100, 7, 8, 9]

    def test_exact_match_has_no_problems(self):
        self.assertEqual(compare_item(self.prompt, self.full, self.labels, self.prompt, self.answer), [])

    def test_prompt_mismatch_is_reported(self):
        problems = compare_item(self.prompt, self.full, self.labels, [1, 2, 4], self.answer)
        self.assertIn('prompt token IDs differ from fixture', problems)

    def test_missing_end_of_turn_is_reported(self):
        problems = compare_item(self.prompt, self.full, self.labels, self.prompt, [7, 8])
        self.assertIn('answer token IDs differ from scoring-trace labels', problems)
        self.assertIn('label length differs from rendered sequence length', problems)

    def test_trace_optional(self):
        self.assertEqual(compare_item(self.prompt, None, None, self.prompt, self.answer), [])


if __name__ == '__main__':
    unittest.main()
