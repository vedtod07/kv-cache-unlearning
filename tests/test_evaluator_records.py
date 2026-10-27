import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_review_sheets import attach_questions, build, load_records
from evaluate_cache import author_of, make_record, parse_model, scoring_gate
from validate_results import validate_manifest, validate_record
import copy
import json

REPO = Path(__file__).resolve().parents[1]
EVAL_V0 = REPO / 'results' / 'eval-v0-full'
FIXTURES = [REPO / 'results/day2/day2_20261019T122314559618Z/fixtures.json',
            REPO / 'results/day4/day4_20261020T103718004368Z/fixtures-with-prompts.json']

ITEM = {'item_id': 'locuslab/TOFU@rev:forget10:train:0', 'author_id': 'tofu:a', 'gold_answer': 'Fact',
        'question': 'Where was A born?'}


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

    def test_records_carry_question(self):
        self.assertEqual(ok_record()['question'], 'Where was A born?')

    def test_ordinary_scoring_gate(self):
        self.assertTrue(scoring_gate([1.0, 2.0], [1.0005, 2.0], 1e-3, 1e-3)['passed'])
        failed = scoring_gate([1.0, 2.0], [1.0, 2.5], 1e-3, 1e-3)
        self.assertFalse(failed['passed'])
        self.assertEqual(failed['max_abs_delta'], 0.5)

    def test_scoring_gate_never_passes_vacuously(self):
        self.assertFalse(scoring_gate([], [], 1e-3, 1e-3)['passed'])
        self.assertFalse(scoring_gate([1.0], [1.0, 2.0], 1e-3, 1e-3)['passed'])
        with self.assertRaises(ValueError):
            scoring_gate([1.0], [1.0], float('nan'), 1e-3)


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

    def test_interrupted_run_validates_with_partial_records(self):
        manifest, records = load_run('ordinary')
        partial = copy.deepcopy(manifest)
        partial['status'] = 'interrupted'
        partial['operations'].update(completed_items=10, failed_items=0)
        validate_manifest(partial, records[:10])
        partial['status'] = 'complete'
        with self.assertRaises(ValueError):
            validate_manifest(partial, records[:10])


class EvaluatorToReviewSheets(unittest.TestCase):
    """Integration: actual evaluator records must go through sheet construction."""

    def test_saved_eval_v0_records_build_sheets_via_fixture_join(self):
        paths = sorted(EVAL_V0.glob('*/items.jsonl'))
        records = load_records(paths)
        with self.assertRaises(ValueError):
            build(copy.deepcopy(records), 's')  # v0 records predate the question field
        built = build(attach_questions(records, FIXTURES), 's', 'B', 'draft')
        self.assertEqual((len(built['forget'][0]), len(built['utility'][0])), (40, 120))
        self.assertTrue(all(row['question'] for pop in built.values() for row in pop[0]))

    def test_fixture_join_rejects_mismatched_records(self):
        records = load_records(sorted(EVAL_V0.glob('*/items.jsonl'))[:1])
        records[0]['gold_answer'] = 'tampered'
        with self.assertRaises(ValueError):
            attach_questions(records, FIXTURES)

    def test_new_evaluator_records_build_sheets_directly(self):
        rec = ok_record()
        rec.update(model_role='full', ended_with_eos=True, reached_token_budget=False,
                   _source='items.jsonl:1', _source_sha256='h')
        review, key = build([rec], 's', 'B', 'draft')['forget']
        self.assertEqual(review[0]['question'], 'Where was A born?')
        self.assertEqual(review[0]['termination'], 'eos')


if __name__ == '__main__':
    unittest.main()
