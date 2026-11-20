"""CPU fixtures for indexing and trace plumbing; these do not validate HQQ/CUDA."""
import importlib.util
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from day6_integration import comparison, sequential, target_nll, traced_cache


@unittest.skipUnless(importlib.util.find_spec("torch"), "Optional Torch CPU tests")
class ScoreBoundaryTests(unittest.TestCase):
    def test_shifted_targets_include_terminal_token(self):
        import torch
        ids = torch.tensor([[0, 0, 1, 2]])
        logits = torch.zeros(1, 4, 3)
        logits[0, 1, 1] = 2
        logits[0, 2, 2] = 3
        logits[0, 3, :] = 100  # Last position must not score another token.
        actual = target_nll(torch, logits, ids, 2)
        expected = [math.log(math.exp(x) + 2) - x for x in (2, 3)]
        self.assertEqual(len(actual), 2)
        for x, y in zip(actual, expected):
            self.assertAlmostEqual(x, y, places=6)


@unittest.skipUnless(importlib.util.find_spec("transformers") and importlib.util.find_spec("torch"),
                     "Optional pinned Transformers CPU integration tests")
class TraceTests(unittest.TestCase):
    def setUp(self):
        import torch
        from transformers import LlamaConfig, LlamaForCausalLM, DynamicCache
        from transformers.cache_utils import QuantizedLayer
        self.torch = torch
        torch.manual_seed(7)
        cfg = LlamaConfig(vocab_size=32, hidden_size=32, intermediate_size=64,
                          num_hidden_layers=2, num_attention_heads=4,
                          num_key_value_heads=2, max_position_embeddings=64)
        cfg._attn_implementation = "sdpa"
        self.model = LlamaForCausalLM(cfg).eval()
        self.prompt = torch.tensor([[1, 3, 4, 5]])
        self.answer = torch.tensor([[6, 7, 2]])

        class RoundedLayer(QuantizedLayer):
            def _quantize(self, tensor, axis):
                return torch.round(tensor * 16) / 16

            def _dequantize(self, tensor):
                return tensor

        def cache(quantized=False):
            c = DynamicCache(config=cfg)
            if quantized:
                c.layers = [RoundedLayer(residual_length=128) for _ in c.layers]
            return c
        self.cache = cache

    def test_parallel_sequential_boundaries(self):
        torch = self.torch
        ids = torch.cat([self.prompt, self.answer], dim=1)
        with torch.inference_mode():
            logits = self.model(input_ids=ids, attention_mask=torch.ones_like(ids),
                                use_cache=False).logits
        a = target_nll(torch, logits, ids, self.prompt.shape[1])
        b, _ = sequential(torch, self.model, self.prompt, self.answer, self.cache())
        self.assertTrue(comparison(a, b)["passed"])

    def test_trace_is_neutral_and_reaches_attention(self):
        c = self.cache(True)
        with traced_cache(self.torch, c) as records:
            a, _ = sequential(self.torch, self.model, self.prompt, self.answer, c)
        b, _ = sequential(self.torch, self.model, self.prompt, self.answer, self.cache(True))
        self.assertEqual(a, b)
        for r in records:
            self.assertEqual(r["reads"], 4)
            self.assertEqual(r["attention_calls"], 3)
            self.assertTrue(r["attention_receives_cache_tensors"])
            self.assertTrue(r["returned_prefix_matches_reconstruction"])
            self.assertTrue(r["prefill_returns_original"])
        self.assertTrue(any(r["max_reconstruction_error"] > 0 for r in records))

    def test_one_token_has_no_decode_read_and_dispatch_restores(self):
        from transformers.modeling_utils import ALL_ATTENTION_FUNCTIONS
        original = ALL_ATTENTION_FUNCTIONS.get_interface("sdpa", None)
        c = self.cache(True)
        with traced_cache(self.torch, c) as records:
            sequential(self.torch, self.model, self.prompt, self.answer[:, :1], c)
        self.assertTrue(all(r["reads"] == 0 and r["attention_calls"] == 1 for r in records))
        self.assertIs(ALL_ATTENTION_FUNCTIONS.get_interface("sdpa", None), original)
        with self.assertRaisesRegex(RuntimeError, "test exception"):
            with traced_cache(self.torch, self.cache(True)):
                raise RuntimeError("test exception")
        self.assertIs(ALL_ATTENTION_FUNCTIONS.get_interface("sdpa", None), original)

    def test_generate_replays_with_same_cache_policy(self):
        torch = self.torch
        cache = self.cache(True)
        with traced_cache(torch, cache) as records, torch.inference_mode():
            output = self.model.generate(
                input_ids=self.prompt, attention_mask=torch.ones_like(self.prompt),
                past_key_values=cache, cache_implementation=None,
                max_new_tokens=6, do_sample=False, num_beams=1,
                pad_token_id=2, eos_token_id=2)
        answer = output[:, self.prompt.shape[1]:]
        _, predicted = sequential(torch, self.model, self.prompt, answer, self.cache(True))
        self.assertEqual(predicted, answer[0].tolist())
        self.assertTrue(all(r["attention_calls"] == answer.shape[1]
                            and r["attention_receives_cache_tensors"] for r in records))
