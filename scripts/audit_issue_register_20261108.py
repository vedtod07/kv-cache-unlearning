"""Recompute current development evidence for the external issue-register review.

No inference or label changes. KV-position shares are source-derived, not measured
attention weights: this pinned cache quantizes the prompt on initialization, returns
originals on prefill, and reconstructs that prefix on each subsequent decode call.
"""
import collections
import hashlib
import json
import statistics
import subprocess
from pathlib import Path

R=Path(__file__).resolve().parents[1]
RUN=R/'results/int4-development/int4dev_20261025T142729681517Z'
OUT=R/'results/issue-register-audit-20261108'
OUT.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
roles=['full','retain90','simnpo_candidate']
evidence={'date':'2026-11-08','reviewed_A_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),
    'GPU_rerun':False,'source_files_sha256':{},'models':{},
    'limits':['One exposed forget author; A-accepted AI-assisted provisional labels; independent B review pending.',
              'Quantized-position fractions are derived from archived source and token lengths, not attention-mass measurements or a fresh per-step GPU trace.']}
joined=json.loads((R/'results/A-accepted-development-20261102/joined-A-accepted.json').read_text())
assert len(joined)==480
for role in roles:
    cells={}
    for c in ['ordinary','int4']:
        path=RUN/f'{role}-{c}-items.jsonl'
        evidence['source_files_sha256'][path.name]=sha(path)
        rows=[json.loads(s) for s in path.read_text().splitlines()]
        assert len(rows)==80 and all(r['status']=='ok' for r in rows)
        cells[c]={r['item_id']:r for r in rows}
        for r in rows:
            a=next(a for a in joined if a['item_id']==r['item_id'] and a['model_role']==role and a['condition']==r['condition'])
            assert hashlib.sha256(r['generated_text'].encode()).hexdigest()==a['response_sha256']
    ordinary,cq=cells['ordinary'],cells['int4']
    nll=[];token_deltas=[];gaps=[];prefill_gaps=[]
    for item,a in ordinary.items():
        b=cq[item]
        if a['dataset_config']=='forget10':
            assert len(a['reference_nll_sequential'])==len(b['reference_nll_sequential'])>0
            nll.append(statistics.mean(b['reference_nll_sequential'])-statistics.mean(a['reference_nll_sequential']))
            token_deltas.extend(y-x for x,y in zip(a['reference_nll_sequential'],b['reference_nll_sequential']))
            gaps.extend(abs(x-y) for x,y in zip(a['reference_nll_sequential'],a['reference_nll_parallel']))
            assert all(abs(x-y)<=0.001+0.001*abs(y) for x,y in zip(a['reference_nll_sequential'],a['reference_nll_parallel']))
            prefill_gaps.extend(abs(x-y) for x,y in zip(b['reference_nll_parallel'],b['no_cache_parallel_nll']))
    position_fractions=[]
    for r in cq.values():
        P=len(r['prompt_token_ids']);G=r['generated_token_count']
        assert 0<G<=64
        # Prefill predicts output token 1. Call t>=1 consumes t generated tokens
        # and attends to P quantized-prefix positions and t unquantized positions.
        position_fractions.extend(P/(P+t) for t in range(1,G))
    scores={}
    for pop in ['forget','utility']:
        scores[pop]={}
        for cond,raw in [('ordinary',ordinary),('int4',cq)]:
            accepted=[r for r in joined if r['model_role']==role and r['population']==pop and r['condition']==next(iter(raw.values()))['condition']]
            scores[pop][cond]=dict(collections.Counter(r['correctness'] for r in accepted))
    evidence['models'][role]={'scores':scores,'mean_item_mean_forget_nll_delta':statistics.mean(nll),
        'forget_items_with_lower_nll':sum(x<0 for x in nll),'forget_items_with_higher_nll':sum(x>0 for x in nll),
        'max_absolute_token_nll_delta':max(map(abs,token_deltas)),
        'ordinary_parallel_sequential_max_abs_gap':max(gaps),'empty_quantized_prefill_max_abs_gap':max(prefill_gaps),
        'changed_generated_tokens':sum(ordinary[k]['generated_token_ids']!=cq[k]['generated_token_ids'] for k in ordinary),
        'truncated_ordinary':sum(r['truncated'] for r in ordinary.values()),'truncated_int4':sum(r['truncated'] for r in cq.values()),
        'prompt_length_range':[min(len(r['prompt_token_ids']) for r in cq.values()),max(len(r['prompt_token_ids']) for r in cq.values())],
        'derived_quantized_attended_position_fraction_decode_only':{'minimum':min(position_fractions),'mean_over_decode_calls':statistics.mean(position_fractions),'maximum':max(position_fractions)},
        'condition_policy':json.loads((RUN/f'{role}-int4-manifest.json').read_text())['condition']}
evidence['total_raw_responses']=480
evidence['total_truncated']=sum(v['truncated_ordinary']+v['truncated_int4'] for v in evidence['models'].values())
evidence['source_cache_sha256']=sha(R/'results/day6/day6_20261020T130635380188Z/quantized-layer.py')
evidence['B_branch_heads']={name:subprocess.check_output(['git','rev-parse','origin/'+name],cwd=R,text=True).strip() for name in ['master','b/evaluator-v0','b/parity-20261028','b/utility-specs','b/env-lock-draft']}
(OUT/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
lines=['# Recomputed evidence — 8 November 2026','','Raw responses and accepted labels were read without modifying them. No GPU inference was performed.','',
'| Model | Forget correct ordinary / INT4 | Utility correct ordinary / INT4 | Mean item-mean forget NLL change | Truncated ordinary / INT4 |',
'| --- | --- | --- | ---: | --- |']
for role,m in evidence['models'].items():
    s=m['scores']
    lines.append(f"| {role} | {s['forget']['ordinary'].get('correct',0)}/20 / {s['forget']['int4'].get('correct',0)}/20 | {s['utility']['ordinary'].get('correct',0)}/60 / {s['utility']['int4'].get('correct',0)}/60 | {m['mean_item_mean_forget_nll_delta']:+.6f} | {m['truncated_ordinary']} / {m['truncated_int4']} |")
lines+=['','NLL change is INT4 minus ordinary. Positive means the reference answer receives lower length-normalized likelihood, not higher. It is not a correctness label.','',
'## Short-context cache exposure','',
'The archived cache quantizes the full prompt immediately even when it is shorter than residual_length=128. Prefill returns original tensors. Subsequent decode calls read the reconstructed prompt prefix; new decode tokens stay in the full-precision residual during these <=64-token outputs. Thus 128 is not a minimum prompt length before quantization begins.','',
'For prompt length P and decode call t (starting at t=1), the fraction of attended positions from reconstructed quantized storage is P/(P+t). Prefill itself has fraction zero. These source-derived fractions count positions, not their attention weights, and do not measure accumulated quantization error.','',
'| Model | Prompt tokens | Minimum decode position share | Mean over decode calls | Maximum |',
'| --- | --- | ---: | ---: | ---: |']
for role,m in evidence['models'].items():
    f=m['derived_quantized_attended_position_fraction_decode_only']
    lines.append(f"| {role} | {m['prompt_length_range'][0]}–{m['prompt_length_range'][1]} | {f['minimum']:.1%} | {f['mean_over_decode_calls']:.1%} | {f['maximum']:.1%} |")
lines+=['','This corrects the concern that short prompts necessarily leave the quantized cache inactive. A runtime per-step storage/flush trace remains useful for other residual settings; this calculation is not a replacement for that trace.','']
(OUT/'RECOMPUTED_METRICS.md').write_text('\n'.join(lines))
print('\n'.join(lines[:11]))
