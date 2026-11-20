"""Build a readable report and unlabelled paired-response browser from the audit."""
from pathlib import Path
import argparse
import html
import json
from collections import Counter


def build(run):
    audit=json.loads((run/'artifact-review.json').read_text())
    models=audit['models']; roles=list(models)
    allrows={role:{c:[json.loads(l) for l in (run/f'{role}-{c}-items.jsonl').read_text().splitlines()] for c in ('ordinary','int4')} for role in roles}
    changes=sum(sum(s['changed_text'] for s in m['changes_by_split'].values()) for m in models.values())
    assert changes==145
    table='\n'.join(f"| {role} | {m['changes_by_split']['forget10']['changed_text']}/20 | {m['changes_by_split']['retain90']['changed_text']}/30 | {m['changes_by_split']['real_authors']['changed_text']}/15 | {m['changes_by_split']['world_facts']['changed_text']}/15 | {sum(s['changed_text'] for s in m['changes_by_split'].values())}/80 |" for role,m in models.items())
    control='\n'.join(f"| {role} | {m['conditions']['ordinary']['ordinary_parallel_sequential_max_gap']:.8f} | {m['conditions']['int4']['empty_cache_parallel_max_gap']:.8f} | {m['first_target_int4_vs_ordinary_sequential_max_gap']:.8f} | {m['probe_neutrality_max_gap']:.8f} |" for role,m in models.items())
    scores='\n'.join(f"| {role} | {m['mean_of_item_mean_sequential_nll_change']:+.6f} | {m['max_absolute_token_nll_change']:.6f} |" for role,m in models.items())
    cost='\n'.join(f"| {role} | {m['conditions']['ordinary']['generate_seconds']:.2f} | {m['conditions']['int4']['generate_seconds']:.2f} | {m['conditions']['ordinary']['score_seconds']:.2f} | {m['conditions']['int4']['score_seconds']:.2f} | {m['load_seconds']:.2f} |" for role,m in models.items())
    report=f'''# Paired ordinary/INT4 development run - artifact review

Reviewed 25 October 2026. Run: `{run.name}`. Codex-assisted artifact review; A's verification of this new review, quantized factual annotation, independent B review and joint scientific sign-off remain pending.

**Verdict: the saved engineering/record checks pass.** All 480 responses completed without status errors. The 240 ordinary-cache responses exactly reproduce the current day-seven baseline text and tokens. Real INT4 inference ran on all three checkpoints, including the selected unlearned SimNPO candidate. This is the first returned complete three-model paired INT4 development batch in this workspace.

**What this does not yet establish:** the factual effect of compression. All raw item correctness/behaviour fields remain `unscored`. Changed text and score changes are measurements, not factual-disclosure labels.

## 1. Scope and provenance

- Tesla T4; Python 3.13.16; Torch 2.9.1+cu128; CUDA12.8; Transformers5.5.4; HQQ0.2.8.post1.
- FP32 weights, SDPA, TF32 disabled, unpadded batch one; HQQ INT4 axes1/1, group64, residual128.
- Full, retain90 and preselected SimNPO checkpoints at the immutable revisions in config/manifests. Same loaded weights used for both conditions within each model.
- Existing 20 Hsiao Yun-Hwa forget questions plus the fixed 60-item utility screen. No new confirmation authors were evaluated.
- Fixed full-model tokenizer/template, date10Apr2025, explicit valid-token masks, greedy one-beam generation, max64 new tokens and common stopping settings.
- Reference scoring only on forget answers, including final EOT. Utility rows use generation only and correctly retain null reference scores.
- Six model/condition files, 80 records each; 120 scored forget model/condition records; three score probes and three native-generation traces on the first exposed forget item, across all16 layers.

Input ZIP SHA256: `{audit['input_bundle_sha256']}`. Returned ZIP SHA256: `{audit['source_zip_sha256']}`. All38 original files are preserved byte-for-byte; the extracted folder has additional review artifacts. All nine prepared-file hashes, effective generation settings, per-item/schema checks, child manifests and summary arithmetic were checked. Raw score vectors are finite and sums match.

Python moved from3.13.15 to3.13.16; the core GPU pins match. The ordinary output parity gives useful direct consistency evidence despite that patch change. Config/preparation fields that say "preparation only" or "GPU pending" are preserved historical input snapshots; the outer run manifest correctly records completed execution.

The configured checkpoint revisions are recorded, and the archived runner asserts resolved revisions at load. Transformers config serialization omits its private commit-hash field, so the saved model-config JSON is not a separate resolved-hash certificate. This review recomputes saved evidence; it does not rerun CUDA or reconstruct full unarchived K/V tensors.

## 2. Numerical and cache-path checks

| Model | Max ordinary seq/parallel NLL gap | Max empty-cache parallel target gap | First INT4/ordinary sequential target gap | Probe instrumentation gap |
|---|---:|---:|---:|---:|
{control}

All60 ordinary reference-score comparisons pass the inherited absolute-plus-relative rule. All60 empty-quantized-cache parallel comparisons have exactly zero differences from no-cache parallel scores. All60 first-target comparisons pass. Comparing INT4 first-target scores with **ordinary sequential** first-target scores gives zero in all models.

The saved first-target check compares sequential INT4 with ordinary **parallel** scores and therefore has small nonzero gaps (up to0.00012207 for SimNPO). These are baseline scoring-path numerical differences, not evidence that the stored cache changes the initial target. Distinguish the compared tensors before reading a maximum as a cache effect.

Each model's first-item score probe shows16 layers, quantized writes, reconstructed readback reaching the attention interface, nonzero reconstruction error, original prefill returns, and exact instrumented/plain score equality. First-item native INT4 generation traces also pass. Remaining items are not individually attention-traced. No fresh identity-cache run is archived in this batch; the prior identity validation remains separate evidence.

## 3. How often generated answers changed

| Model | Forget | Retained | Real authors | World facts | Total |
|---|---:|---:|---:|---:|---:|
{table}

The comparisons above are exact generated-text changes; token-sequence change counts are identical here. There are **145 changed INT4 responses** and95 unchanged INT4 responses across240 paired questions. All20 SimNPO forget answers changed, which makes that set a review priority. It does not mean20 facts were recovered.

The240 ordinary answers match A's accepted day-seven question/reference/text/token baselines. These and the95 exact INT4 text matches may inherit prior labels only with unchanged applicable rubric and recorded provenance. No labels have been assigned or accepted by this artifact audit. The145 changed responses need substantive factual/behaviour review; if the final rubric changes, recheck every affected historical case too.

## 4. Reference-score effects

| Model | Mean of20 item-mean sequential NLL changes | Largest absolute token-NLL change |
|---|---:|---:|
{scores}

Change is INT4 minus ordinary. Each item-mean averages over its reference tokens including EOT; the table then weights each of the20 questions equally. It is not a pooled-token mean, a repeated-run average, generated-answer accuracy or a population effect estimate.

Positive values mean the fixed reference became less probable on average. Negative item changes also occur, and large opposite-signed changes can cancel. SimNPO's mean is only+0.032497 despite a largest absolute token change of10.010882. Neither the average nor that extreme establishes a factual disclosure increase/decrease. Inspect generated answers and the full vectors alongside the scoring-path comparison.

## 5. Completion, truncation and measured cost

The outer manifest spans{audit['wall_seconds']:.2f}seconds, about{audit['wall_seconds']/60:.2f}minutes, from execution initialization to completion. This includes model loading and probes but not earlier package installation/input upload. There were no continuations/retries recorded.

| Model | Ordinary generation s | INT4 generation s | Ordinary scoring s | INT4 scoring s | Load s |
|---|---:|---:|---:|---:|---:|
{cost}

Scoring time covers the20 forget references with the runner's respective parallel/sequential controls. The first native INT4 generation is instrumented. These aggregate times are not a clean serving-speed benchmark or directly equivalent to B's timing script, which scored all80 references with a different control workload. Peak allocated memory is about4.69GiB per model for the combined probe and both conditions, so condition-specific memory savings cannot be inferred.

Four responses reached64 tokens without EOS:

- Full INT4: retained item631.
- SimNPO ordinary: forget item5 (the existing baseline truncation).
- SimNPO INT4: forget items8 and18.

All four remain in the records and denominators. Retain90 has no truncations. There are476 EOS terminations. A budget hit is not automatically a runtime error or incorrect factual answer; assess only the visible response.

## 6. Cross-person full-model reproducibility

Against B's committed full-model timing report at remote `{audit['full_model_parity_with_B_timing']['remote_commit'][:7]}`, both ordinary and INT4 generated token sequences match80/80. The20 forget-reference sequential NLL sums match exactly in both conditions. This is stronger evidence than merely having equal average accuracy.

This is a comparison between separate code/run paths on the same existing full-model questions, not an independent training seed or a new author population. Do not count repeated outputs as additional independent question or training-seed observations. A's current three-checkpoint run adds the retain90/SimNPO pairs that were absent from that timing report.

Correction to the earlier23October written review: its full-model changed-output split breakdown listed16 retained and8 world-fact changes. Rechecking the current remote timing records gives17 retained and7 world-fact changes; total39, nine forget and six real-author changes are unchanged. Use the current per-item audited breakdown.

## 7. What to do next

1. Preserve the returned ZIP and this extracted run. A factual rerun is not required merely because text changes, NLL changes or declared truncations occurred; the archived controls pass.
2. Review the paired answers using the companion `manual-review/paired-response-browser.html`. It shows all240 pairs and can filter by model, split and changed outputs. It is an A-side comparison tool, not a blinded B annotation sheet and not a completed annotation file.
3. Prepare proposed factual/behaviour labels, prioritizing47 changed forget responses and98 changed utility responses. Preserve partial/ambiguous/reference flags and both directions of outcome changes. Keep raw JSONL unscored and version annotation files separately.
4. Await/record B's rubric response and independent-review plan. Do not infer approval from silence. B's planned240 baseline review remains separate; agree coverage of new paired outputs before agreement analysis.
5. After the artifact/annotation handoff, freeze an input-selected repeat subset if pursuing the proposed repeatability exercise. The existing full-model B parity already supplies useful supporting reproducibility evidence; it does not replace the still-unperformed retain90/SimNPO repetitions or broader author coverage.

**Sharing:** this original ZIP includes baseline-accepted-annotations.csv and acceptance metadata. Do not give it to B as an independent-review package. Prepare a label-free handoff. The paired browser shows model/cache identities and therefore is also unsuitable as his blinded first-pass sheet.

**Research interpretation:** engineering execution is successful for this tested development scope. Factual outcomes and useful utility under quantization remain pending annotation. One exposed forget author, the restricted utility screen and one selected unlearned checkpoint cannot establish population-level unlearning durability. NPO/RMU selection, broader allocation, practical thresholds and joint confirmation freeze remain open.
'''
    (run/'INT4_DEVELOPMENT_REVIEW.md').write_text(report)
    reviewdir=run/'manual-review';reviewdir.mkdir(exist_ok=True)
    pairs=[]
    for role in roles:
        for o,q in zip(allrows[role]['ordinary'],allrows[role]['int4']):
            assert o['item_id']==q['item_id']
            pairs.append(dict(model=role,split=o['dataset_config'],item_id=o['item_id'],question=o['question'],reference=o['gold_answer'],changed=o['generated_text']!=q['generated_text'],ordinary=o['generated_text'],int4=q['generated_text'],ordinary_tokens=o['generated_token_count'],int4_tokens=q['generated_token_count'],ordinary_truncated=o['truncated'],int4_truncated=q['truncated']))
    cards=[]
    for pair in pairs:
        esc=lambda k:html.escape(str(pair[k]))
        changed=pair['changed'];code=pair['item_id'].rsplit(':',1)[-1]
        cards.append(f'''<details class="pair" data-model="{esc('model')}" data-split="{esc('split')}" data-changed="{str(changed).lower()}"><summary>{esc('model')} / {esc('split')} / item {code} - {'changed' if changed else 'same text'}</summary><p class="id">{esc('item_id')}</p><h3>Question</h3><p>{esc('question')}</p><h3>Reference</h3><p>{esc('reference')}</p><div class="answers"><section><h3>Ordinary cache</h3><p>{esc('ordinary')}</p><small>{esc('ordinary_tokens')} tokens; truncated: {esc('ordinary_truncated')}</small></section><section><h3>INT4 cache</h3><p>{esc('int4')}</p><small>{esc('int4_tokens')} tokens; truncated: {esc('int4_truncated')}</small></section></div><p class="pending">Factual/behaviour assessment pending. Changed text does not imply recovery.</p></details>''')
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Paired INT4 development review</title><style>body{font:16px/1.55 system-ui,sans-serif;color:#193149;background:#f2f6f8;margin:0}main{max-width:1150px;margin:auto;padding:24px}h1{font-size:28px}header{background:white;padding:22px;border-radius:10px}label{display:inline-block;margin:8px 12px 8px 0}input,select,button{font:inherit;padding:7px;border:1px solid #b9cbd3;border-radius:4px}input[type=search]{min-width:250px}.pair{background:white;border:1px solid #d5e1e7;margin:12px 0;padding:14px;border-radius:8px}summary{cursor:pointer;font-weight:650;color:#007d83}h3{font-size:16px;margin:16px 0 4px}.answers{display:grid;grid-template-columns:1fr 1fr;gap:22px}.answers section{background:#f4f7fa;padding:15px;overflow-wrap:anywhere}p{white-space:pre-wrap}.id,small,.pending{font-size:13px;color:#536474}.id{overflow-wrap:anywhere}.pending{margin-bottom:0}.pair[hidden]{display:none}@media(max-width:700px){.answers{grid-template-columns:1fr}main{padding:12px}}</style><main><header><h1>Paired ordinary / INT4 response review</h1><p>240 pairs; 145 changed texts. All responses are unscored in this browser. For A's comparison review: model/cache identities are visible. Do not use as B's blinded first-pass sheet.</p><label>Model <select id="model"><option value="">All</option><option>full</option><option>retain90</option><option>simnpo_candidate</option></select></label><label>Split <select id="split"><option value="">All</option><option>forget10</option><option>retain90</option><option>real_authors</option><option>world_facts</option></select></label><label><input id="changed" type="checkbox" checked> Changed only</label><label>Search <input id="search" type="search" placeholder="Question, reference, response or item ID"></label><p id="count"></p><button id="expand">Expand visible</button> <button id="collapse">Collapse all</button></header>'''+''.join(cards)+'''</main><script>const pairs=[...document.querySelectorAll('.pair')],model=document.querySelector('#model'),split=document.querySelector('#split'),changed=document.querySelector('#changed'),search=document.querySelector('#search');function apply(){let n=0;for(const p of pairs){p.hidden=!!((model.value&&p.dataset.model!==model.value)||(split.value&&p.dataset.split!==split.value)||(changed.checked&&p.dataset.changed!=='true')||(search.value&&!p.textContent.toLowerCase().includes(search.value.toLowerCase())));if(!p.hidden)n++}document.querySelector('#count').textContent=n+' of 240 pairs shown'}for(const el of [model,split,changed,search])el.addEventListener('input',apply);document.querySelector('#expand').onclick=()=>pairs.forEach(p=>{if(!p.hidden)p.open=true});document.querySelector('#collapse').onclick=()=>pairs.forEach(p=>p.open=false);apply();</script></html>'''
    (reviewdir/'paired-response-browser.html').write_text(page)
    (reviewdir/'paired-responses.json').write_text(json.dumps(pairs,ensure_ascii=False,indent=2)+'\n')
    (reviewdir/'README.md').write_text('''# Paired factual review - pending

The browser contains all240 ordinary/INT4 pairs, with145 changed texts prioritized by its default filter. It contains no factual labels, and it does not save annotation decisions. Use it to inspect responses alongside the agreed rubric, then record labels in a separately versioned annotation file.

Model and cache identities are visible. This is not a blinded B review package. The original ZIP contains prior A annotations; do not share it as a label-free handoff.

Question, reference and both outputs are copied from the raw records, not rewritten. All480 raw JSONL records remain unscored. No adjudication or independent review is inferred from completion of this engineering audit.
''')
    assert len(pairs)==240 and sum(p['changed'] for p in pairs)==145
    print(run/'INT4_DEVELOPMENT_REVIEW.md');print(reviewdir/'paired-response-browser.html')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('run',type=Path);build(p.parse_args().run)
