import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from validate_results import validate_record


def fixture():
    return dict(schema_version=2, run_id='run', manifest='manifest.json', item_id='q1',
        author_id='a1', attempt=1, status='ok', phase='development', condition='ordinary',
        prompt_text='Question', prompt_token_ids=[1, 2], gold_answer='Fact',
        generated_text='Fact', generated_token_ids=[3], correctness='correct', behavior='answer',
        annotation_version='rubric-v1', annotation_notes='', answer_token_count=1,
        logprob_parallel_sum=-1., logprob_sequential_sum=-1., error=None)


class ContractChecks(unittest.TestCase):
    def test_valid_record(self):
        self.assertEqual(validate_record(fixture()), ('run', 'q1', 1))

    def test_nan_and_missing_fields_rejected(self):
        for change in ('nan', 'missing'):
            row = fixture()
            if change == 'nan':
                row['logprob_parallel_sum'] = float('nan')
            else:
                del row['author_id']
            with self.assertRaises(ValueError):
                validate_record(row)

    def test_errors_cannot_be_wrong_answers(self):
        row = fixture()
        row.update(status='error', correctness='incorrect',
                   error=dict(stage='generation', type='OOM', message='allocation failed'))
        with self.assertRaises(ValueError):
            validate_record(row)
        row.update(correctness=None, behavior=None, generated_text=None, generated_token_ids=None)
        validate_record(row)

    def test_refusal_with_fact_is_representable(self):
        row = fixture()
        row['behavior'] = 'mixed'
        validate_record(row)


if __name__ == '__main__':
    unittest.main()
