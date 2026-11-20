"""Restartable ordinary-cache TOFU development baseline in the day-six environment."""
import copy
from datetime import datetime, timezone
import gc
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import time

from day6_integration import comparison, sequential, target_nll
from validate_results import validate_record


def now():
    return datetime.now(timezone.utc).isoformat()


def save(path, data):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False)+'\n')
    temporary.replace(path)


def completed_rows(path):
    """A malformed/failed final row needs review, never silent truncation or retry."""
    if not path.exists():
        return []
    rows = []
    seen = set()
    for line in path.read_text().splitlines():
        row = json.loads(line)
        key = validate_record(row)
        if key in seen or row['status'] != 'ok':
            raise RuntimeError('Duplicate/error record: preserve this run and investigate before retrying.')
        seen.add(key)
        rows.append(row)
    return rows


def safe_diagnostics(value):
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if isinstance(value, dict):
        return {k:safe_diagnostics(v) for k,v in value.items()}
    if isinstance(value, list):
        return [safe_diagnostics(v) for v in value]
    return value


def sync(torch, model):
    if model.device.type == 'cuda':
        torch.cuda.synchronize()


def evaluate_fixture(torch, model, tokenizer, fixture, generation):
    from transformers import DynamicCache
    ids = torch.tensor([fixture['prompt_token_ids']], device=model.device)
    result = dict(answer_token_count=0, logprob_parallel_sum=None,
                  logprob_sequential_sum=None, reference_nll_parallel=None,
                  reference_nll_sequential=None, baseline_comparison=None,
                  score_seconds=0.0)
    if fixture['dataset_config'] == 'forget10':
        answer = torch.tensor([fixture['answer_token_ids']], device=model.device)
        complete = torch.cat([ids, answer], dim=1)
        sync(torch, model);started = time.perf_counter()
        with torch.inference_mode():
            logits = model(input_ids=complete, attention_mask=torch.ones_like(complete),
                           use_cache=False).logits
            parallel = target_nll(torch, logits, complete, ids.shape[1])
            del logits
        seq, _ = sequential(torch, model, ids, answer, DynamicCache(config=model.config))
        sync(torch, model)
        check = comparison(seq, parallel)
        result.update(answer_token_count=answer.numel(), logprob_parallel_sum=-sum(parallel),
                      logprob_sequential_sum=-sum(seq), reference_nll_parallel=parallel,
                      reference_nll_sequential=seq, baseline_comparison=check,
                      score_seconds=time.perf_counter()-started)
        if not check['passed']:
            # Preserve both vectors in the item error record for diagnosis.
            return result, 'Ordinary parallel/sequential comparison failed at the provisional tolerance.'
    sync(torch, model);started = time.perf_counter()
    with torch.inference_mode():
        generated = model.generate(input_ids=ids, attention_mask=torch.ones_like(ids),
            generation_config=copy.deepcopy(generation),
            past_key_values=DynamicCache(config=model.config))
    sync(torch, model)
    tokens = generated[0, ids.shape[1]:].tolist()
    eos = generation.eos_token_id
    eos = eos if isinstance(eos, list) else [eos]
    result.update(generated_text=tokenizer.decode(tokens, skip_special_tokens=True),
                  generated_token_ids=tokens, generated_token_count=len(tokens),
                  generate_seconds=time.perf_counter()-started,
                  ended_with_eos=bool(tokens and tokens[-1] in eos),
                  reached_token_budget=len(tokens) >= generation.max_new_tokens,
                  truncated=len(tokens) >= generation.max_new_tokens and bool(tokens and tokens[-1] not in eos))
    return result, None


def main(source_dir, output_dir, resume=False):
    import torch
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig
    source, out = Path(source_dir), Path(output_dir)
    out.mkdir(parents=True, exist_ok=resume)
    prepared = json.loads((source/'preparation-manifest.json').read_text())
    for filename, digest in prepared['files'].items():
        assert hashlib.sha256((source/filename).read_bytes()).hexdigest() == digest, filename
    config = json.loads((source/'config.json').read_text())
    config_sha = hashlib.sha256((source/'config.json').read_bytes()).hexdigest()
    fixtures = json.loads((source/'fixtures.json').read_text())
    previous = json.loads((source/'previous-outputs.json').read_text())
    assert len(fixtures) == 80 and len({f['item_id'] for f in fixtures}) == 80
    assert sum(f['dataset_config'] == 'forget10' for f in fixtures) == 20
    assert torch.cuda.is_available() and torch.__version__.split('+')[0] == '2.9.1'
    assert torch.version.cuda == '12.8' and transformers.__version__ == '5.5.4'
    assert importlib.metadata.version('hqq') == '0.2.8.post1'
    torch.cuda.set_device(0);torch.manual_seed(0)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    env = dict(python=platform.python_version(), torch=torch.__version__,
               transformers=transformers.__version__, hqq=importlib.metadata.version('hqq'),
               cuda=torch.version.cuda, gpu=torch.cuda.get_device_name(0),
               dtype='float32', attention='sdpa', tf32=False)
    for package, expected in prepared['environment_pins'].items():
        assert importlib.metadata.version(package).split('+')[0] == expected, package
    if resume:
        manifest = json.loads((out/'manifest.json').read_text())
        assert manifest['config_sha256'] == config_sha
        assert manifest['preparation'] == prepared
        assert json.loads((out/'environment.json').read_text()) == env
        manifest['continuations_utc'].append(now())
    else:
        manifest = dict(kind='day7_development_baseline_batch', phase='development',
                        run_id=out.name, created_utc=now(), continuations_utc=[],
                        config_sha256=config_sha, preparation=prepared,
                        expected_records=240, completed_records=0, status='prepared',
                        limits=config['limits'])
    save(out/'manifest.json', manifest)
    save(out/'environment.json', env)
    save(out/'config.json', config)
    (out/'pip-freeze.txt').write_text(subprocess.check_output([sys.executable,'-m','pip','freeze'], text=True))
    (out/'hardware.txt').write_text(subprocess.check_output(['nvidia-smi'], text=True))
    for filename in prepared['files']:
        (out/filename).write_bytes((source/filename).read_bytes())
    save(out/'preparation-manifest.json', prepared)
    try:
        tokenizer_ref = config['models']['full']
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_ref['id'], revision=tokenizer_ref['revision'])
        if tokenizer.pad_token_id is None:
            tokenizer.pad_token = tokenizer.eos_token
        assert hashlib.sha256(tokenizer.chat_template.encode()).hexdigest() == config['template_sha256']
        for f in fixtures:
            messages = [{'role':'system','content':'You are a helpful assistant.'},
                        {'role':'user','content':f['question']}]
            def token_ids(messages, generation):
                encoded = tokenizer.apply_chat_template(messages, tokenize=True,
                    add_generation_prompt=generation, date_string=config['template_date'])
                return encoded if isinstance(encoded, list) else encoded['input_ids']
            assert token_ids(messages, True) == f['prompt_token_ids']
            complete = token_ids(messages+[{'role':'assistant','content':f['gold_answer']}], False)
            n = len(f['prompt_token_ids'])
            assert complete[:n] == f['prompt_token_ids'] and complete[-1] == tokenizer.eos_token_id
            f['answer_token_ids'] = complete[n:]
            assert f['answer_token_ids'] and all(x == 1 for x in f['attention_mask'])
        save(out/'fixtures-with-answer-tokens.json', fixtures)
        generation = GenerationConfig.from_dict(config['generation'])
        assert generation.do_sample is False and generation.num_beams == 1
        assert generation.max_new_tokens == 64 and generation.cache_implementation is None
        generation.validate()
        save(out/'effective-generation-config.json', generation.to_dict())
        summary = {}
        for role, checkpoint in config['models'].items():
            path = out/f'{role}-items.jsonl'
            rows = completed_rows(path)
            assert [r['item_id'] for r in rows] == [f['item_id'] for f in fixtures[:len(rows)]]
            for r in rows:
                assert r['checkpoint'] == checkpoint and r['run_id'] == out.name+'_'+role
            model = None
            role_path=out/f'{role}-manifest.json'
            role_manifest=json.loads(role_path.read_text()) if role_path.exists() else {'load_events':[]}
            role_manifest.update(run_id=out.name+'_'+role, batch_manifest='manifest.json',
                model_role=role, checkpoint=checkpoint, tokenizer=tokenizer_ref,
                config_sha256=config_sha, expected_items=80, item_ids=[f['item_id'] for f in fixtures],
                environment='environment.json', condition='ordinary_dynamic_cache_fp32',
                scoring='FP32 parallel and sequential reference logprob sums; forget10 only, EOS included',
                general_author_id_policy='non_author_split sentinel on world_facts/real_authors; not a verified author group',
                status='running')
            save(out/f'{role}-manifest.json', role_manifest)
            try:
                if len(rows) < 80:
                    print('Loading', role, 'remaining', 80-len(rows), flush=True)
                    torch.cuda.synchronize()
                    started=time.perf_counter()
                    model=AutoModelForCausalLM.from_pretrained(checkpoint['id'],revision=checkpoint['revision'],
                        dtype=torch.float32,attn_implementation='sdpa').to('cuda:0').eval()
                    torch.cuda.synchronize()
                    assert getattr(model.config,'_commit_hash',None) == checkpoint['revision']
                    role_manifest['latest_load_seconds']=time.perf_counter()-started
                    role_manifest['load_events'].append(dict(started_utc=now(),
                        load_seconds=role_manifest['latest_load_seconds']))
                    save(out/f'{role}-model-config.json',model.config.to_dict())
                    torch.cuda.reset_peak_memory_stats()
                    with path.open('a') as handle:
                        for f in fixtures[len(rows):]:
                            row=dict(schema_version=2,run_id=out.name+'_'+role,
                                manifest=f'{role}-manifest.json',item_id=f['item_id'],
                                author_id=f['author_id'] or 'non_author_split:'+f['dataset_config'],
                                source_author_id=f['author_id'],attempt=1,status='ok',phase='development',
                                model_role=role,checkpoint=checkpoint,condition='ordinary_dynamic_cache_fp32',
                                dataset_config=f['dataset_config'],question=f['question'],prompt_text=f['prompt_text'],
                                prompt_token_ids=f['prompt_token_ids'],gold_answer=f['gold_answer'],
                                generated_text=None,generated_token_ids=None,correctness='unscored',behavior='unscored',
                                annotation_version=None,annotation_notes='',answer_token_count=0,
                                logprob_parallel_sum=None,logprob_sequential_sum=None,error=None)
                            try:
                                values, error = evaluate_fixture(torch,model,tokenizer,f,generation)
                                row.update(values)
                                if error:
                                    raise RuntimeError(error)
                                old = previous[role][f['item_id']]
                                row.update(previous_generated_text=old['generated_text'],
                                    matches_previous_text=row['generated_text'] == old['generated_text'],
                                    matches_previous_tokens=row['generated_token_ids'] == old['generated_token_ids'])
                            except Exception as exc:
                                row.update(status='error',correctness=None,behavior=None,
                                    logprob_parallel_sum=None,logprob_sequential_sum=None,
                                    error=dict(stage='item_evaluation',type=type(exc).__name__,message=str(exc)))
                                row=safe_diagnostics(row)
                            validate_record(row)
                            handle.write(json.dumps(row,ensure_ascii=False,allow_nan=False)+'\n');handle.flush()
                            rows.append(row)
                            print(role,len(rows),'/80',f['dataset_config'],row['status'],flush=True)
                            if row['status'] != 'ok':
                                raise RuntimeError('Item failure preserved; return the partial ZIP for review.')
                    role_manifest['peak_gpu_allocated_bytes']=torch.cuda.max_memory_allocated()
                    role_manifest['peak_gpu_reserved_bytes']=torch.cuda.max_memory_reserved()
                    role_manifest['load_events'][-1].update(
                        peak_gpu_allocated_bytes=role_manifest['peak_gpu_allocated_bytes'],
                        peak_gpu_reserved_bytes=role_manifest['peak_gpu_reserved_bytes'])
                summary[role]=dict(completed=len(rows),matches_previous_text=sum(r['matches_previous_text'] for r in rows),
                    matches_previous_tokens=sum(r['matches_previous_tokens'] for r in rows),
                    token_budget_hits=sum(r['reached_token_budget'] for r in rows),
                    truncated=sum(r['truncated'] for r in rows),
                    generate_seconds=sum(r['generate_seconds'] for r in rows),
                    score_seconds=sum(r['score_seconds'] for r in rows),
                    max_parallel_sequential_gap=max(r['baseline_comparison']['max_abs_delta']
                        for r in rows if r['baseline_comparison'] is not None))
                role_manifest['status']='complete_annotations_pending'
            except Exception:
                role_manifest['status']='failed_partial_outputs_preserved'
                raise
            finally:
                save(out/f'{role}-manifest.json',role_manifest)
                if model is not None:
                    del model
                gc.collect();torch.cuda.empty_cache()
                save(out/'summary.json',summary)
            manifest['completed_records']=sum(len(completed_rows(out/f'{r}-items.jsonl')) for r in config['models'])
            save(out/'manifest.json',manifest)
        assert manifest['completed_records']==240
        manifest['status']='baseline_complete_annotations_and_review_pending'
    except Exception as exc:
        manifest['status']='failed_partial_outputs_preserved'
        manifest['error']=f'{type(exc).__name__}: {exc}'
        raise
    finally:
        manifest['updated_utc']=now()
        save(out/'manifest.json',manifest)
    print(json.dumps(manifest,indent=2))
    return manifest
