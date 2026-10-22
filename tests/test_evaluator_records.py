import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from evaluate_cache import author_of, make_record, parse_model
from validate_results import validate_manifest, validate_record
import copy
import json

EVAL_V0 = Path(__file__).resolve().parents[1] / 'results' / 'eval-v0-full'

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


def load_run(condition):
    run_dir = next(EVAL_V0.glob(f'*_full_{condition}'))
    records = [json.loads(line) for line in (run_dir / 'items.jsonl').read_text(encoding='utf-8').splitlines()]
    return json.loads((run_dir / 'manifest.json').read_text(encoding='utf-8')), records


class Manifests(unittest.TestCase):
    def test_saved_eval_v0_manifests_validate(self):
        for condition in ('ordinary', 'quantized'):
            validate_manifest(*load_run(condition))

    def test_count_item_and_policy_mismatches_fail(self):
        manifest, records = load_run('quantized')
        for change in ('count', 'items', 'policy', 'condition'):
            bad, recs = copy.deepcopy(manifest), copy.deepcopy(records)
            if change == 'count':
                bad['operations']['failed_items'] = 1
            elif change == 'items':
                recs = recs[:-1]
            elif change == 'policy':
                bad['computation']['cache_policy']['axis_key'] = None
            else:
                recs[0]['condition'] = 'ordinary'
            with self.assertRaises(ValueError, msg=change):
                validate_manifest(bad, recs)


if __name__ == '__main__':
    unittest.main()
