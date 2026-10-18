import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from gate_checks import assess_gate


class GateChecks(unittest.TestCase):
    def check(self, parallel=(1., 1.), dynamic=(1., 1.), identity=(1., 1.),
              quantized=(1., 1.), records=None):
        if records is None:
            records = [dict(layer=0, writes_k=1, writes_v=1, reads_k=1, reads_v=1,
                            stored_kv=True, max_reconstruction_error=0.01)]
        return assess_gate(parallel, dynamic, identity, quantized, records, 1e-4, 0.)

    def test_equal_scores_with_instrumented_intervention_are_valid(self):
        self.assertTrue(self.check()['passed'])

    def test_bad_baseline_cannot_be_rescued_by_quantized_gap(self):
        result = self.check(dynamic=(1.001, 1.001), quantized=(1.001, 1.001))
        self.assertFalse(result['passed'])
        self.assertEqual(result['max_abs_token_nll_delta'], 0)

    def test_cancelling_token_changes_are_visible(self):
        result = self.check(quantized=(0.5, 1.5))
        self.assertEqual(result['mean_nll_delta'], 0)
        self.assertEqual(result['max_abs_token_nll_delta'], 0.5)

    def test_nonfinite_and_empty_scores_fail(self):
        self.assertFalse(self.check(quantized=(float('nan'), 1.))['passed'])
        self.assertFalse(self.check(parallel=())['passed'])

    def test_missing_instrumentation_fails(self):
        self.assertFalse(self.check(records=[])['passed'])
        record = dict(layer=0, writes_k=1, writes_v=1, reads_k=0, reads_v=0,
                      stored_kv=True, max_reconstruction_error=0.1)
        self.assertFalse(self.check(records=[record])['passed'])

    def test_identity_mismatch_fails(self):
        self.assertFalse(self.check(identity=(1., 2.))['passed'])


if __name__ == '__main__':
    unittest.main()
