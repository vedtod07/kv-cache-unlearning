"""CPU checks for paired cache semantics. HQQ/CUDA still needs the returned GPU run."""
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from int4_development import measure,probe_model


@unittest.skipUnless(importlib.util.find_spec('torch') and importlib.util.find_spec('transformers'),
                     'Optional Torch/Transformers CPU integration')
class PairedCacheTests(unittest.TestCase):
    def setUp(self):
        import torch
        from transformers import LlamaConfig,LlamaForCausalLM,GenerationConfig,DynamicCache
        from transformers.cache_utils import QuantizedLayer
        self.torch=torch;torch.manual_seed(7)
        cfg=LlamaConfig(vocab_size=32,hidden_size=32,intermediate_size=64,num_hidden_layers=2,
                        num_attention_heads=4,num_key_value_heads=2)
        cfg._attn_implementation='sdpa';self.model=LlamaForCausalLM(cfg).eval()
        self.fixture=dict(prompt_token_ids=[1,3,4,5],answer_token_ids=[6,7,2],dataset_config='forget10')
        self.gen=GenerationConfig(max_new_tokens=6,do_sample=False,num_beams=1,
                                 eos_token_id=2,pad_token_id=2,bos_token_id=1,cache_implementation=None)
        self.tok=type('Tokenizer',(),{'decode':staticmethod(lambda ids,**kw:' '.join(map(str,ids)))})()
        class Rounded(QuantizedLayer):
            def _quantize(self,tensor,axis):return torch.round(tensor*16)/16
            def _dequantize(self,tensor):return tensor
        class Identity(Rounded):
            def _quantize(self,tensor,axis):return tensor.clone()
        def factory(kind):
            c=DynamicCache(config=cfg)
            if kind:c.layers=[(Identity if kind=='identity' else Rounded)(residual_length=128) for _ in c.layers]
            return c
        self.ordinary=lambda:factory(None)
        self.quantized=lambda:factory('round')
        self.identity=lambda:factory('identity')

    def test_ordinary_and_int4_use_different_control_rules(self):
        ordinary,error=measure(self.torch,self.model,self.tok,self.fixture,self.gen,self.ordinary,'ordinary')
        self.assertIsNone(error);self.assertTrue(ordinary['ordinary_comparison']['passed'])
        quantized,error=measure(self.torch,self.model,self.tok,self.fixture,self.gen,self.quantized,'int4',True)
        self.assertIsNone(error)
        self.assertTrue(quantized['empty_prefill_comparison']['passed'])
        self.assertTrue(quantized['first_target_comparison']['passed'])
        self.assertIsNone(quantized['ordinary_comparison'])
        self.assertTrue(quantized['generation_trace_passed'])
        self.assertEqual(quantized['reference_nll_parallel'],ordinary['reference_nll_parallel'])
        self.assertEqual(quantized['logprob_sequential_sum'],-sum(quantized['reference_nll_sequential']))

    def test_consumption_probe_accepts_rounding_but_rejects_no_error_fixture(self):
        probe=probe_model(self.torch,self.model,self.fixture,self.quantized)
        self.assertTrue(probe['passed']);self.assertEqual(probe['instrumented_nll'],probe['plain_nll'])
        self.assertFalse(probe_model(self.torch,self.model,self.fixture,self.identity)['passed'])

    def test_utility_stays_generation_only(self):
        self.fixture['dataset_config']='world_facts'
        result,error=measure(self.torch,self.model,self.tok,self.fixture,self.gen,self.quantized,'int4')
        self.assertIsNone(error);self.assertIsNone(result['logprob_sequential_sum'])
        self.assertEqual(result['answer_token_count'],0)

    def test_nonfinite_later_quantized_score_stops_before_generation(self):
        ordinary,_=measure(self.torch,self.model,self.tok,self.fixture,self.gen,self.ordinary,'ordinary')
        broken=list(ordinary['reference_nll_sequential']);broken[1]=float('nan')
        with patch('int4_development.sequential',return_value=(broken,[])):
            result,error=measure(self.torch,self.model,self.tok,self.fixture,self.gen,self.quantized,'int4')
        self.assertTrue(result['first_target_comparison']['passed'])
        self.assertIsNotNone(error)
        self.assertNotIn('generated_token_ids',result)
