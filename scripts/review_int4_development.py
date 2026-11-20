"""Recompute artifact checks for a returned paired INT4 development run (no GPU)."""
import argparse
from collections import Counter
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import statistics
import subprocess
import sys
from zipfile import ZipFile

from validate_results import validate_record


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(a,b):
    return len(a)==len(b)>0 and all(math.isfinite(x) and math.isfinite(y)
        and abs(x-y)<=1e-3+1e-3*abs(y) for x,y in zip(a,b))


def review(run, source_zip, repository):
    prep=json.loads((run/'preparation-manifest.json').read_text())
    config=json.loads((run/'config.json').read_text())
    manifest=json.loads((run/'manifest.json').read_text())
    fixtures=json.loads((run/'fixtures.json').read_text())
    baseline=json.loads((run/'day7-baseline.json').read_text())
    assert len(fixtures)==len({f['item_id'] for f in fixtures})==80
    indexed={f['item_id']:f for f in fixtures}
    verified_files={}
    for name,digest in prep['files'].items():
        assert sha(run/name)==digest,name
        verified_files[name]=digest
    expected=repository/'results/int4-development-preparation/preparation-manifest.json'
    assert prep==json.loads(expected.read_text())
    bundle=repository/'results/int4-development-preparation/int4-development-input-bundle.zip'
    assert (run/'input-bundle-sha256.txt').read_text().strip()==sha(bundle)
    assert manifest['preparation']==prep
    assert manifest['config_sha256']==sha(run/'config.json')
    assert manifest['completed_records']==manifest['expected_records']==480
    assert not manifest.get('continuations_utc')
    effective=json.loads((run/'effective-generation-config.json').read_text())
    assert all(effective[k]==v for k,v in config['generation'].items())
    env=json.loads((run/'environment.json').read_text())
    assert env['torch']=='2.9.1+cu128' and env['cuda']=='12.8' and env['transformers']=='5.5.4'
    assert env['hqq']=='0.2.8.post1' and env['dtype']=='float32' and env['tf32'] is False
    assert env['attention']=='sdpa' and env['gpu']=='Tesla T4'
    freeze={l.split('==',1)[0].lower().replace('_','-'):l.split('==',1)[1] for l in (run/'pip-freeze.txt').read_text().splitlines() if '==' in l}
    for k,v in prep['environment_pins'].items():assert freeze[k].split('+')[0]==v,k
    roles={};allkeys=set();total=0;alltruncated=[];raw_hashes={}
    summary=json.loads((run/'summary.json').read_text())
    for role,checkpoint in config['models'].items():
        grouped={}
        execution=json.loads((run/f'{role}-execution.json').read_text())
        assert execution['status']=='complete' and len(execution['load_events'])==1
        model_config=json.loads((run/f'{role}-model-config.json').read_text())
        assert model_config.get('_commit_hash') in (None,checkpoint['revision'])
        # Transformers config.to_dict() omits the private commit hash; the archived runner
        # asserts its resolved value at load time and records configured immutable revisions.
        layers=model_config['num_hidden_layers'];assert layers==16
        assert len(execution['probe_reports'])==1
        probe=json.loads((run/execution['probe_reports'][0]).read_text())
        assert probe['passed'] and close(probe['instrumented_nll'],probe['plain_nll'])
        assert probe['instrumented_nll']==probe['plain_nll']
        assert len(probe['layers'])==layers and {l['layer'] for l in probe['layers']}==set(range(layers))
        for l in probe['layers']:
            assert l['writes']==2 and l['reads']==2*(len(probe['plain_nll'])-1)
            assert l['attention_calls']==l['update_calls']==len(probe['plain_nll'])
            assert all(l[k] for k in ['attention_receives_cache_tensors','returned_prefix_matches_reconstruction','prefill_returns_original'])
            assert math.isfinite(l['max_reconstruction_error'])
        assert max(l['max_reconstruction_error'] for l in probe['layers'])>0
        condition_stats={}
        for condition in ('ordinary','int4'):
            name=f'{role}-{condition}-items.jsonl';raw_hashes[name]=sha(run/name)
            rows=[json.loads(l) for l in (run/name).read_text().splitlines()]
            assert len(rows)==80 and [r['item_id'] for r in rows]==[f['item_id'] for f in fixtures]
            child=json.loads((run/f'{role}-{condition}-manifest.json').read_text())
            assert child['checkpoint']==checkpoint and child['condition']==config['conditions'][condition]
            assert child['status']=='complete_annotations_pending'
            assert child['item_ids']==[f['item_id'] for f in fixtures]
            assert child['config_sha256']==manifest['config_sha256']
            gaps=[];empties=[];first=[]
            for row in rows:
                key=validate_record(row);assert key not in allkeys;allkeys.add(key)
                assert row['status']=='ok' and row['correctness']=='unscored' and row['behavior']=='unscored'
                assert row['checkpoint']==checkpoint and row['condition_key']==condition and row['model_role']==role
                assert row['run_id']==child['run_id'] and row['manifest']==f'{role}-{condition}-manifest.json'
                assert row['condition']==config['conditions'][condition]['key']
                fixture=indexed[row['item_id']]
                for k in ['question','prompt_text','prompt_token_ids','gold_answer','dataset_config']:
                    assert row[k]==fixture[k],(role,condition,row['item_id'],k)
                assert all(v==1 for v in fixture['attention_mask'])
                assert row['generated_token_count']==len(row['generated_token_ids'])<=64
                eos=bool(row['generated_token_ids'] and row['generated_token_ids'][-1] in effective['eos_token_id'])
                assert row['ended_with_eos']==eos and row['reached_token_budget']==(len(row['generated_token_ids'])>=64)
                assert row['truncated']==(len(row['generated_token_ids'])>=64 and not eos)
                assert math.isfinite(row['generate_seconds']) and row['generate_seconds']>=0
                if row['truncated']:alltruncated.append({'model':role,'condition':condition,'item_id':row['item_id']})
                if fixture['dataset_config']=='forget10':
                    p,s,n=(row[k] for k in ['reference_nll_parallel','reference_nll_sequential','no_cache_parallel_nll'])
                    assert all(len(v)==len(fixture['answer_token_ids'])==row['answer_token_count'] for v in [p,s,n])
                    assert fixture['answer_token_ids'][-1]==128009
                    assert all(math.isfinite(x) for v in [p,s,n] for x in v)
                    assert math.isclose(row['logprob_parallel_sum'],-sum(p),abs_tol=1e-10)
                    assert math.isclose(row['logprob_sequential_sum'],-sum(s),abs_tol=1e-10)
                    if condition=='ordinary':
                        assert close(s,p) and row['ordinary_comparison']['passed']
                        gaps.append(max(abs(x-y) for x,y in zip(s,p)))
                    else:
                        assert close(p,n) and close(s[:1],n[:1])
                        assert row['empty_prefill_comparison']['passed'] and row['first_target_comparison']['passed']
                        empties.append(max(abs(x-y) for x,y in zip(p,n)));first.append(abs(s[0]-n[0]))
                else:
                    assert row['answer_token_count']==0 and row['logprob_parallel_sum'] is None and row['logprob_sequential_sum'] is None
                if condition=='ordinary':
                    old=baseline[role][row['item_id']]
                    assert row['matches_day7_text']==(row['generated_text']==old['generated_text'])
                    assert row['matches_day7_tokens']==(row['generated_token_ids']==old['generated_token_ids'])
            if condition=='int4':
                traced=rows[0];assert traced['generation_trace_passed']
                trace=traced['generation_layer_trace'];assert len(trace)==layers
                for l in trace:
                    assert l['writes']==2 and l['reads']==2*(traced['generated_token_count']-1)
                    assert l['attention_calls']==l['update_calls']==traced['generated_token_count']
                    assert all(l[k] for k in ['attention_receives_cache_tensors','returned_prefix_matches_reconstruction','prefill_returns_original'])
                assert all(not r['generation_layer_trace'] for r in rows[1:])
            stat={'completed':80,'truncated':sum(r['truncated'] for r in rows),'generate_seconds':sum(r['generate_seconds'] for r in rows),'score_seconds':sum(r['score_seconds'] for r in rows)}
            for k,v in stat.items():assert math.isclose(v,summary[f'{role}_{condition}'][k],abs_tol=1e-8)
            stat.update(eos=sum(r['ended_with_eos'] for r in rows),ordinary_parallel_sequential_max_gap=max(gaps,default=None),empty_cache_parallel_max_gap=max(empties,default=None),first_target_max_gap=max(first,default=None))
            condition_stats[condition]=stat;grouped[condition]={r['item_id']:r for r in rows};total+=80
        changes={};deltas=[];max_token=0;parallel_gap=0;baseline_score_gap=[]
        for split in ('forget10','retain90','real_authors','world_facts'):
            items=[f['item_id'] for f in fixtures if f['dataset_config']==split]
            changes[split]={'items':len(items),'changed_text':sum(grouped['ordinary'][i]['generated_text']!=grouped['int4'][i]['generated_text'] for i in items),'changed_tokens':sum(grouped['ordinary'][i]['generated_token_ids']!=grouped['int4'][i]['generated_token_ids'] for i in items)}
        first_same_policy=[]
        for i in grouped['int4']:
            assert grouped['int4'][i]['same_text_as_ordinary']==(grouped['ordinary'][i]['generated_text']==grouped['int4'][i]['generated_text'])
        for i in [f['item_id'] for f in fixtures if f['dataset_config']=='forget10']:
            o,q=grouped['ordinary'][i],grouped['int4'][i]
            assert q['same_text_as_ordinary']==(o['generated_text']==q['generated_text'])
            assert close(o['no_cache_parallel_nll'],q['no_cache_parallel_nll'])
            parallel_gap=max(parallel_gap,max(abs(x-y) for x,y in zip(o['no_cache_parallel_nll'],q['no_cache_parallel_nll'])))
            first_same_policy.append(abs(q['reference_nll_sequential'][0]-o['reference_nll_sequential'][0]))
            ds=[x-y for x,y in zip(q['reference_nll_sequential'],o['reference_nll_sequential'])]
            deltas.append(sum(ds)/len(ds));max_token=max(max_token,max(map(abs,ds)))
        roles[role]={'conditions':condition_stats,'changes_by_split':changes,'ordinary_day7_exact_text_matches':sum(r['matches_day7_text'] for r in grouped['ordinary'].values()),'ordinary_day7_exact_token_matches':sum(r['matches_day7_tokens'] for r in grouped['ordinary'].values()),'mean_of_item_mean_sequential_nll_change':statistics.mean(deltas),'item_mean_nll_changes':deltas,'max_absolute_token_nll_change':max_token,'max_same_model_ordinary_vs_int4_no_cache_score_gap':parallel_gap,'first_target_int4_vs_ordinary_sequential_max_gap':max(first_same_policy),'probe_neutrality_max_gap':max(abs(x-y) for x,y in zip(probe['plain_nll'],probe['instrumented_nll'])),'probe_layers':layers,'max_probe_reconstruction_error':max(l['max_reconstruction_error'] for l in probe['layers']),'load_seconds':execution['load_events'][0]['load_seconds'],'peak_allocated_gib_combined_conditions':execution['load_events'][0]['peak_gpu_allocated_bytes']/2**30}
    assert total==480
    with ZipFile(source_zip) as z:
        assert z.testzip() is None
        assert all((run/i.filename).read_bytes()==z.read(i) for i in z.infolist())
    # Saved scalar/boolean trace assertions can be checked for internal consistency,
    # but not reconstructed from full tensors (these are not archived).
    result={'kind':'paired_int4_development_artifact_review','review_date':'2026-10-25','source_zip_sha256':sha(source_zip),'input_bundle_sha256':sha(bundle),'records_verified':total,'status_errors':0,'environment':env,'wall_seconds':(datetime.fromisoformat(manifest['updated_utc'])-datetime.fromisoformat(manifest['created_utc'])).total_seconds(),'models':roles,'truncated_records':alltruncated,'prepared_files_sha256_verified':verified_files,'raw_item_files_sha256':raw_hashes,'annotation_status':'All raw records remain unscored; no quantized factual labels assigned by this audit','passed':True,'limits':['No new GPU inference','Model config serialization omits private resolved hash; archived runner asserts resolution at load and records configured immutable revisions','Three first-item score probes and three first-item generation traces, not every item','Tensor identity and prefill assertions are saved runtime fields, not re-derived from full saved tensors','Existing exposed one-author forget development set and restricted utility sample','Inherited provisional tolerances; rubric and independent B review not finalized','Peak memory covers both conditions and probes, not condition-specific savings']}
    for role in roles:
        prior_path=repository/'results/day7/day7_20261021T101236202224Z'/f'{role}-items.jsonl'
        prior={r['item_id']:r for r in map(json.loads,prior_path.read_text().splitlines())}
        rows=[json.loads(l) for l in (run/f'{role}-ordinary-items.jsonl').read_text().splitlines()]
        assert all(r['generated_token_ids']==prior[r['item_id']]['generated_token_ids'] and r['generated_text']==prior[r['item_id']]['generated_text'] for r in rows)
        roles[role]['actual_local_day7_tokens_and_text_matches']=80
    # This optional comparison is bound to the fetched remote ref, recorded below.
    blob=subprocess.check_output(['git','show','origin/master:results/timing/full-80items-int4-res128-fp32.json'],cwd=repository)
    timing=json.loads(blob);parity={}
    for before,condition in [('ordinary','ordinary'),('quantized','int4')]:
        prior={r['item_id']:r for r in timing['records'] if r['condition']==before}
        rows=[json.loads(l) for l in (run/f'full-{condition}-items.jsonl').read_text().splitlines()]
        parity[condition]={'items':80,'token_matches':sum(r['generated_token_ids']==prior[r['item_id']]['generated_token_ids'] for r in rows),
            'max_forget_sequential_nll_sum_delta':max(abs(-r['logprob_sequential_sum']-prior[r['item_id']]['sequential_nll_sum']) for r in rows if r['dataset_config']=='forget10')}
    result['full_model_parity_with_B_timing']={'remote_commit':subprocess.check_output(['git','rev-parse','origin/master'],cwd=repository,text=True).strip(),
        'report_sha256':hashlib.sha256(blob).hexdigest(),'conditions':parity,
        'interpretation':'Cross-implementation consistency on existing full-model items; not independent training or population replication'}
    (run/'artifact-review.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run',type=Path);parser.add_argument('source_zip',type=Path)
    args=parser.parse_args();r=review(args.run,args.source_zip,Path(__file__).resolve().parents[1])
    print(json.dumps({k:v for k,v in r.items() if not k.endswith('sha256') and k!='prepared_files_sha256_verified' and k!='raw_item_files_sha256'},indent=2))
