"""Paired ordinary/INT4 integration on existing development items, not confirmation."""
import contextlib
import copy
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

from day6_integration import comparison, sequential, target_nll, traced_cache
from day7_baseline import completed_rows, now, safe_diagnostics, save, sync
from validate_results import validate_record


def measure(torch, model, tokenizer, fixture, generation, cache_factory, condition, trace_generation=False):
    ids=torch.tensor([fixture['prompt_token_ids']],device=model.device)
    result=dict(answer_token_count=0,logprob_parallel_sum=None,logprob_sequential_sum=None,
        reference_nll_parallel=None,reference_nll_sequential=None,no_cache_parallel_nll=None,
        ordinary_comparison=None,empty_prefill_comparison=None,first_target_comparison=None,score_seconds=0.0)
    if fixture['dataset_config']=='forget10':
        answer=torch.tensor([fixture['answer_token_ids']],device=model.device)
        full=torch.cat([ids,answer],dim=1)
        sync(torch,model);started=time.perf_counter()
        with torch.inference_mode():
            logits=model(input_ids=full,attention_mask=torch.ones_like(full),use_cache=False).logits
            ordinary_parallel=target_nll(torch,logits,full,ids.shape[1]);del logits
            if condition=='int4':
                logits=model(input_ids=full,attention_mask=torch.ones_like(full),
                    past_key_values=cache_factory(),use_cache=True).logits
                parallel=target_nll(torch,logits,full,ids.shape[1]);del logits
            else:
                parallel=ordinary_parallel
        seq,_=sequential(torch,model,ids,answer,cache_factory())
        sync(torch,model)
        result.update(answer_token_count=answer.numel(),logprob_parallel_sum=-sum(parallel),
            logprob_sequential_sum=-sum(seq),reference_nll_parallel=parallel,
            reference_nll_sequential=seq,no_cache_parallel_nll=ordinary_parallel,
            score_seconds=time.perf_counter()-started)
        if condition=='ordinary':
            result['ordinary_comparison']=comparison(seq,ordinary_parallel)
            valid=result['ordinary_comparison']['passed']
        else:
            result['empty_prefill_comparison']=comparison(parallel,ordinary_parallel)
            result['first_target_comparison']=comparison(seq[:1],ordinary_parallel[:1])
            valid=result['empty_prefill_comparison']['passed'] and result['first_target_comparison']['passed']
            # Sequential/parallel equality is NOT an INT4 gate: disagreement is a measurement.
        valid=valid and all(math.isfinite(x) for x in seq+parallel+ordinary_parallel)
        if not valid:
            return result,'Scoring control failed; preserve the vectors and investigate.'
    cache=cache_factory()
    context=traced_cache(torch,cache) if trace_generation else contextlib.nullcontext([])
    sync(torch,model);started=time.perf_counter()
    with context as trace,torch.inference_mode():
        generated=model.generate(input_ids=ids,attention_mask=torch.ones_like(ids),
            past_key_values=cache,generation_config=copy.deepcopy(generation))
    sync(torch,model)
    tokens=generated[0,ids.shape[1]:].tolist()
    eos=generation.eos_token_id
    eos=eos if isinstance(eos,list) else [eos]
    result.update(generated_text=tokenizer.decode(tokens,skip_special_tokens=True),generated_token_ids=tokens,
        generated_token_count=len(tokens),generate_seconds=time.perf_counter()-started,
        ended_with_eos=bool(tokens and tokens[-1] in eos),reached_token_budget=len(tokens)>=generation.max_new_tokens,
        truncated=len(tokens)>=generation.max_new_tokens and bool(tokens and tokens[-1] not in eos),
        generation_layer_trace=trace)
    if trace_generation:
        result['generation_trace_passed']=bool(trace) and all(
            r['writes']>=2 and r['attention_calls']==r['update_calls']==len(tokens)
            and r['attention_receives_cache_tensors'] and r['returned_prefix_matches_reconstruction']
            and r['prefill_returns_original'] and (r['reads']>0 if len(tokens)>1 else r['reads']==0)
            for r in trace)
        if not result['generation_trace_passed']:
            return result,'Quantized generation trace failed.'
    return result,None


def probe_model(torch,model,fixture,cache_factory):
    prompt=torch.tensor([fixture['prompt_token_ids']],device=model.device)
    answer=torch.tensor([fixture['answer_token_ids']],device=model.device)
    cache=cache_factory()
    with traced_cache(torch,cache) as records:
        traced,_=sequential(torch,model,prompt,answer,cache)
    plain,_=sequential(torch,model,prompt,answer,cache_factory())
    neutral=comparison(traced,plain)
    valid=bool(records) and all(r['writes']>=2 and r['reads']>=2
        and r['attention_calls']==r['update_calls']==answer.shape[1]
        and r['attention_receives_cache_tensors'] and r['returned_prefix_matches_reconstruction']
        and r['prefill_returns_original'] for r in records)
    valid=valid and any(r['max_reconstruction_error']>0 for r in records)
    return dict(passed=valid and neutral['passed'],instrumentation_comparison=neutral,
        instrumented_nll=traced,plain_nll=plain,layers=records,
        scope='First exposed forget item only; all layers traced; no positive score effect required')


def main(source_dir,output_dir,resume=False):
    import torch
    import transformers
    from transformers import AutoModelForCausalLM,AutoTokenizer,GenerationConfig,DynamicCache,QuantizedCache
    source,out=Path(source_dir),Path(output_dir)
    out.mkdir(parents=True,exist_ok=resume)
    prep=json.loads((source/'preparation-manifest.json').read_text())
    for name,digest in prep['files'].items():
        assert hashlib.sha256((source/name).read_bytes()).hexdigest()==digest,name
    config=json.loads((source/'config.json').read_text());config_sha=hashlib.sha256((source/'config.json').read_bytes()).hexdigest()
    fixtures=json.loads((source/'fixtures.json').read_text())
    baseline=json.loads((source/'day7-baseline.json').read_text())
    assert len(fixtures)==80 and len({f['item_id'] for f in fixtures})==80
    assert sum(f['dataset_config']=='forget10' for f in fixtures)==20
    assert torch.cuda.is_available() and torch.version.cuda=='12.8'
    for package,expected in prep['environment_pins'].items():
        assert importlib.metadata.version(package).split('+')[0]==expected,package
    torch.cuda.set_device(0);torch.manual_seed(0)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    env=dict(python=platform.python_version(),torch=torch.__version__,cuda=torch.version.cuda,
        transformers=transformers.__version__,hqq=importlib.metadata.version('hqq'),gpu=torch.cuda.get_device_name(0),
        dtype='float32',attention='sdpa',tf32=False)
    if resume:
        manifest=json.loads((out/'manifest.json').read_text())
        assert manifest['config_sha256']==config_sha and manifest['preparation']==prep
        assert json.loads((out/'environment.json').read_text())==env
        manifest['continuations_utc'].append(now())
    else:
        manifest=dict(kind='paired_int4_development',phase='development',run_id=out.name,
            created_utc=now(),continuations_utc=[],config_sha256=config_sha,preparation=prep,
            status='prepared',expected_records=480,completed_records=0,limits=config['limits'])
    save(out/'manifest.json',manifest);save(out/'environment.json',env)
    for name in prep['files']:(out/name).write_bytes((source/name).read_bytes())
    save(out/'preparation-manifest.json',prep)
    (out/'pip-freeze.txt').write_text(subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True))
    (out/'hardware.txt').write_text(subprocess.check_output(['nvidia-smi'],text=True))
    summary={}
    try:
        tokenizer_ref=config['models']['full']
        tok=AutoTokenizer.from_pretrained(tokenizer_ref['id'],revision=tokenizer_ref['revision'])
        if tok.pad_token_id is None:tok.pad_token=tok.eos_token
        assert hashlib.sha256(tok.chat_template.encode()).hexdigest()==config['template_sha256']
        for f in fixtures:
            messages=[{'role':'system','content':'You are a helpful assistant.'},{'role':'user','content':f['question']}]
            def encode(chat,generate):
                x=tok.apply_chat_template(chat,tokenize=True,add_generation_prompt=generate,date_string=config['template_date'])
                return x if isinstance(x,list) else x['input_ids']
            assert encode(messages,True)==f['prompt_token_ids']
            full=encode(messages+[{'role':'assistant','content':f['gold_answer']}],False)
            assert full==f['prompt_token_ids']+f['answer_token_ids'] and full[-1]==tok.eos_token_id
            assert all(v==1 for v in f['attention_mask'])
        gen=GenerationConfig.from_dict(config['generation'])
        assert gen.do_sample is False and gen.num_beams==1 and gen.max_new_tokens==64
        assert gen.cache_implementation is None;gen.validate()
        save(out/'effective-generation-config.json',gen.to_dict())
        for role,checkpoint in config['models'].items():
            rows={c:completed_rows(out/f'{role}-{c}-items.jsonl') for c in ('ordinary','int4')}
            for condition,items in rows.items():
                assert [r['item_id'] for r in items]==[f['item_id'] for f in fixtures[:len(items)]]
                assert all(r['checkpoint']==checkpoint and r['condition_key']==condition
                    and r['run_id']==out.name+'_'+role+'_'+condition for r in items)
            assert len(rows['int4'])<=len(rows['ordinary'])<=len(rows['int4'])+1, 'Paired output prefixes are inconsistent; preserve and review.'
            model=None;role_path=out/f'{role}-execution.json'
            execution=json.loads(role_path.read_text()) if role_path.exists() else dict(load_events=[],probe_reports=[])
            try:
                if any(len(r)<80 for r in rows.values()):
                    print('Loading',role,'for both conditions',flush=True)
                    started=time.perf_counter()
                    model=AutoModelForCausalLM.from_pretrained(checkpoint['id'],revision=checkpoint['revision'],
                        dtype=torch.float32,attn_implementation='sdpa').to('cuda:0').eval()
                    torch.cuda.synchronize()
                    assert getattr(model.config,'_commit_hash',None)==checkpoint['revision']
                    assert next(model.parameters()).dtype==torch.float32
                    execution['load_events'].append(dict(started_utc=now(),load_seconds=time.perf_counter()-started))
                    save(out/f'{role}-model-config.json',model.config.to_dict());torch.cuda.reset_peak_memory_stats()
                    factories={'ordinary':lambda:DynamicCache(config=model.config),
                        'int4':lambda:QuantizedCache(backend='hqq',config=model.config,nbits=4,
                            axis_key=1,axis_value=1,q_group_size=64,residual_length=128)}
                    probe=probe_model(torch,model,fixtures[0],factories['int4'])
                    probe_name=role+'-probe-'+str(len(execution['probe_reports'])+1)+'.json'
                    save(out/probe_name,safe_diagnostics(probe));execution['probe_reports'].append(probe_name)
                    save(role_path,execution)
                    if not probe['passed']:raise RuntimeError('Per-model INT4 consumption/neutrality probe failed.')
                    for condition in rows:
                        save(out/f'{role}-{condition}-manifest.json',dict(run_id=out.name+'_'+role+'_'+condition,
                            batch_manifest='manifest.json',checkpoint=checkpoint,tokenizer=tokenizer_ref,
                            condition=config['conditions'][condition],item_ids=[f['item_id'] for f in fixtures],
                            config_sha256=config_sha,environment='environment.json',status='running',
                            author_grouping='Verified forget/retain source IDs; non_author_split sentinels are not author clusters'))
                    for i,f in enumerate(fixtures):
                        for condition in ('ordinary','int4'):
                            if i<len(rows[condition]):continue
                            row=dict(schema_version=2,run_id=out.name+'_'+role+'_'+condition,
                                manifest=f'{role}-{condition}-manifest.json',item_id=f['item_id'],
                                author_id=f['author_id'] or 'non_author_split:'+f['dataset_config'],source_author_id=f['author_id'],
                                attempt=1,status='ok',phase='development',model_role=role,checkpoint=checkpoint,
                                condition_key=condition,condition=config['conditions'][condition]['key'],
                                dataset_config=f['dataset_config'],question=f['question'],prompt_text=f['prompt_text'],
                                prompt_token_ids=f['prompt_token_ids'],gold_answer=f['gold_answer'],generated_text=None,
                                generated_token_ids=None,correctness='unscored',behavior='unscored',annotation_version=None,
                                annotation_notes='',answer_token_count=0,logprob_parallel_sum=None,logprob_sequential_sum=None,error=None)
                            try:
                                values,error=measure(torch,model,tok,f,gen,factories[condition],condition,
                                    trace_generation=(condition=='int4' and i==0))
                                row.update(values)
                                if error:raise RuntimeError(error)
                                if condition=='ordinary':
                                    old=baseline[role][f['item_id']]
                                    row.update(matches_day7_text=row['generated_text']==old['generated_text'],
                                        matches_day7_tokens=row['generated_token_ids']==old['generated_token_ids'])
                                else:
                                    ordinary=rows['ordinary'][i]
                                    assert ordinary['item_id']==f['item_id']
                                    row['same_text_as_ordinary']=row['generated_text']==ordinary['generated_text']
                            except Exception as exc:
                                row.update(status='error',correctness=None,behavior=None,
                                    logprob_parallel_sum=None,logprob_sequential_sum=None,
                                    error=dict(stage='paired_item_evaluation',type=type(exc).__name__,message=str(exc)))
                                row=safe_diagnostics(row)
                            validate_record(row)
                            with (out/f'{role}-{condition}-items.jsonl').open('a') as handle:
                                handle.write(json.dumps(row,ensure_ascii=False,allow_nan=False)+'\n');handle.flush()
                            rows[condition].append(row)
                            print(role,i+1,'/80',condition,row['status'],flush=True)
                            if row['status']!='ok':raise RuntimeError('Failure preserved; return the partial output ZIP.')
                    execution['load_events'][-1].update(peak_gpu_allocated_bytes=torch.cuda.max_memory_allocated(),
                        peak_gpu_reserved_bytes=torch.cuda.max_memory_reserved(),
                        peak_scope='Combined probe and both cache conditions, not a memory-savings estimate')
                for condition,items in rows.items():
                    child_path=out/f'{role}-{condition}-manifest.json'
                    child=json.loads(child_path.read_text());child['status']='complete_annotations_pending';save(child_path,child)
                    summary[role+'_'+condition]=dict(completed=len(items),truncated=sum(r['truncated'] for r in items),
                        generate_seconds=sum(r['generate_seconds'] for r in items),score_seconds=sum(r['score_seconds'] for r in items))
                    assert len(items)==80
                execution['status']='complete'
            except Exception:
                execution['status']='failed_partial_outputs_preserved'
                raise
            finally:
                save(role_path,execution);save(out/'summary.json',summary)
                if model is not None:del model
                gc.collect();torch.cuda.empty_cache()
            manifest['completed_records']=sum(len(completed_rows(out/f'{r}-{c}-items.jsonl'))
                for r in config['models'] for c in ('ordinary','int4'))
            save(out/'manifest.json',manifest)
        assert manifest['completed_records']==480
        manifest['status']='paired_development_complete_annotation_review_pending'
    except Exception as exc:
        manifest['status']='failed_partial_outputs_preserved';manifest['error']=f'{type(exc).__name__}: {exc}'
        raise
    finally:
        manifest['updated_utc']=now();save(out/'manifest.json',manifest)
    print(json.dumps(manifest,indent=2));return manifest
