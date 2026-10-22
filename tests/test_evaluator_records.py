import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from evaluate_cache import author_of, make_record, parse_model
from validate_results import validate_record

ITEM = {'item_id': 'locuslab/TOFU@rev:forget10:train:0', 'author_id': 'tofu:a', 'gold_answer': 'Fact'}


def ok_record():
    rec = make_record('run_full_ordinary', ITEM, 'ordinary', 'prompt', [1, 2])
    rec.update(phase='development', generated_token_ids=[3, 4], generated_text='Fact',
               answer_token_count=2, logprob_parallel_sum=-0.5, logprob_sequential_sum=-0.5)
    return rec


class EvaluatorRecords(unittest.TestCase):
    def test_successful_record_validates_and_is_unscored(self):
        rec = ok_record()
        validate_record(rec)
        self.assertEqual((rec['correctness'], rec['behavior']), ('unscored', 'unscored'))

    def test_error_record_validates_without_labels(self):
        rec = make_record('run', ITEM, 'quantized', 'prompt', [1, 2])
        rec.update(phase='development', status='error', correctness=None, behavior=None,
                   error=dict(stage='generation', type='RuntimeError', message='boom'))
        validate_record(rec)

    def test_utility_items_get_labelled_author_group(self):
        self.assertEqual(author_of({'author_id': None, 'dataset_config': 'world_facts'}),
                         'no-author:world_facts')
        self.assertEqual(author_of(ITEM), 'tofu:a')

    def test_model_spec_parsing(self):
        self.assertEqual(parse_model('full=org/model@abc'), ('full', 'org/model', 'abc'))


if __name__ == '__main__':
    unittest.main()
