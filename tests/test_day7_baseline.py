"""Resume/error integrity and optional tiny-model tests for the FP32 baseline bridge."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from day7_baseline import completed_rows, evaluate_fixture, safe_diagnostics
from validate_results import validate_record


def record():
    return dict(schema_version=2,run_id='run_full',manifest='full-manifest.json',
        item_id='item0',author_id='author0',attempt=1,status='ok',phase='development',
        condition='ordinary_dynamic_cache_fp32',prompt_text='Q',prompt_token_ids=[1],
        gold_answer='A',generated_text='A',generated_token_ids=[2],
        correctness='unscored',behavior='unscored',annotation_version=None,
        annotation_notes='',answer_token_count=0,logprob_parallel_sum=None,
        logprob_sequential_sum=None,error=None)


class ResumeIntegrityTests(unittest.TestCase):
    def test_resume_keeps_successes_but_refuses_failed_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'items.jsonl';row=record()
            path.write_text(json.dumps(row)+'\n')
            self.assertEqual(completed_rows(path),[row])
            row.update(status='error',correctness=None,behavior=None,
                       error=dict(stage='evaluation',type='RuntimeError',message='failed'))
            text=json.dumps(row)+'\n';path.write_text(text)
            with self.assertRaises(RuntimeError):completed_rows(path)
            self.assertEqual(path.read_text(),text)

    def test_partial_line_is_preserved_and_nonfinite_diagnostics_are_explicit(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'items.jsonl';path.write_text('{"unfinished":')
            with self.assertRaises(json.JSONDecodeError):completed_rows(path)
            self.assertEqual(path.read_text(),'{"unfinished":')
        self.assertEqual(safe_diagnostics({'x':[float('nan'),float('inf')]}),{'x':['nan','inf']})


@unittest.skipUnless(importlib.util.find_spec('torch') and importlib.util.find_spec('transformers'),
                     'Optional Torch/Transformers CPU checks')
class BaselineFixtureTests(unittest.TestCase):
    def setUp(self):
        import torch
        from transformers import LlamaConfig,LlamaForCausalLM,GenerationConfig
        self.torch=torch;torch.manual_seed(7)
        cfg=LlamaConfig(vocab_size=32,hidden_size=32,intermediate_size=64,
                        num_hidden_layers=2,num_attention_heads=4,num_key_value_heads=2)
        cfg._attn_implementation='sdpa'
        self.model=LlamaForCausalLM(cfg).eval()
        self.generation=GenerationConfig(max_new_tokens=6,do_sample=False,num_beams=1,
            cache_implementation=None,eos_token_id=2,pad_token_id=2,bos_token_id=1)
        self.tokenizer=type('Tokenizer',(),{'decode':staticmethod(lambda tokens,**kw:' '.join(map(str,tokens)))})()
        self.fixture=dict(prompt_token_ids=[1,3,4,5],answer_token_ids=[6,7,2],dataset_config='forget10')

    def test_forget_scores_and_record_contract(self):
        values,error=evaluate_fixture(self.torch,self.model,self.tokenizer,self.fixture,self.generation)
        self.assertIsNone(error)
        self.assertEqual(values['answer_token_count'],3)
        self.assertEqual(values['logprob_sequential_sum'],-sum(values['reference_nll_sequential']))
        self.assertTrue(values['baseline_comparison']['passed'])
        row=record();row.update(values);validate_record(row)

    def test_utility_generation_does_not_invent_reference_scores(self):
        self.fixture['dataset_config']='world_facts'
        values,error=evaluate_fixture(self.torch,self.model,self.tokenizer,self.fixture,self.generation)
        self.assertIsNone(error)
        self.assertIsNone(values['reference_nll_sequential'])
        self.assertIsNone(values['logprob_parallel_sum'])
        self.assertEqual(values['answer_token_count'],0)
        self.assertGreater(values['generated_token_count'],0)
