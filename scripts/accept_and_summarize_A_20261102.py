"""Record explicit A acceptance and summarize paired development labels.

Requires private coordinator keys locally. Publishes joined identities, not keys
or shuffle seeds. No B approval, adjudication or statistical inference is implied.
"""
import collections
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'results/provisional-annotation-20261030'
SOURCE=BASE/'A-ai-proposed'
OUT=ROOT/'results/A-accepted-development-20261102'
OUT.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
original_hashes={str(p.relative_to(BASE)):sha(p) for folder in ['A','B','A-ai-proposed'] for p in (BASE/folder).iterdir() if p.is_file()}
labels=['correct','partial','incorrect','ambiguous']
rows=[]
key_hashes={}
for population in ['forget','utility']:
    source=SOURCE/f'{population}-ai-proposed.json'
    keypath=ROOT/f'local-review-keys/provisional-annotation-20261030/A-{population}-key.json'
    key_hashes[population]=sha(keypath)
    mappings=json.loads(keypath.read_text())['mapping']
    lookup={r['review_id']:r for r in mappings}
    proposals=json.loads(source.read_text())
    assert len(lookup)==len(proposals)
    accepted=[]
    for proposal in proposals:
        r=dict(proposal)
        key=lookup[r['review_id']]
        assert key['response_sha256']==r['response_sha256']
        assert hashlib.sha256(r['response'].encode()).hexdigest()==r['response_sha256']
        r.update(human_review_decision='accept',human_review_status='accepted',
                 human_review_notes='Vedant explicitly accepted all proposals in the conversation on 2026-11-02; no label changes requested.',
                 human_review_date='2026-11-02',review_progress='A_accepted_B_review_pending',
                 annotation_provenance='Codex AI proposal accepted by Vedant; not an independent human-only annotation.',
                 source_proposal_sha256=sha(source))
        assert r['correctness']==proposal['correctness']
        accepted.append(r)
        joined=dict(r)
        joined.update({k:key[k] for k in ['item_id','model_role','condition','run_id','response_sha256']})
        joined['subset']=key['item_id'].split(':')[-3]
        rows.append(joined)
    (OUT/f'{population}-A-accepted.json').write_text(json.dumps(accepted,ensure_ascii=False,indent=2)+'\n')

assert len(rows)==480
index={(r['item_id'],r['model_role'],r['condition']):r for r in rows}
assert len(index)==480
ordinary='ordinary_dynamic_cache_fp32'
int4='hqq_int4_res128_fp32'
pairs=[]
for (item,model,condition),a in index.items():
    if condition!=ordinary:continue
    b=index[(item,model,int4)]
    assert a['question']==b['question'] and a['reference_answer']==b['reference_answer']
    pairs.append(dict(item_id=item,model_role=model,population=a['population'],subset=a['subset'],
        ordinary_review_id=a['review_id'],int4_review_id=b['review_id'],
        ordinary_correctness=a['correctness'],int4_correctness=b['correctness'],
        ordinary_response_sha256=a['response_sha256'],int4_response_sha256=b['response_sha256']))
assert len(pairs)==240
models=['full','retain90','simnpo_candidate']
summaries=[]
for model in models:
    for pop in ['forget','utility']:
        ps=[p for p in pairs if p['model_role']==model and p['population']==pop]
        oc=collections.Counter(p['ordinary_correctness'] for p in ps)
        qc=collections.Counter(p['int4_correctness'] for p in ps)
        transitions=collections.Counter((p['ordinary_correctness'],p['int4_correctness']) for p in ps)
        summaries.append(dict(model=model,population=pop,n=len(ps),
            ordinary={k:oc[k] for k in labels},int4={k:qc[k] for k in labels},
            gained_correct=sum(p['ordinary_correctness']!='correct' and p['int4_correctness']=='correct' for p in ps),
            lost_correct=sum(p['ordinary_correctness']=='correct' and p['int4_correctness']!='correct' for p in ps),
            delta_correct_count=qc['correct']-oc['correct'],
            transitions=[dict(ordinary=a,int4=b,count=transitions[(a,b)]) for a in labels for b in labels]))
acceptance=dict(date='2026-11-02',reviewer='Vedant (Person A)',status='A_accepted_provisional',
    user_statement='i accept all the proposed ones as they seem to be correct to me, now let us move forward to the next step',
    scope='All 480 proposed annotations and accompanying annotation fields accepted unchanged. Ambiguous labels remain ambiguous.',
    source_commit='2ae9293',source_proposal_hashes={p:sha(SOURCE/f'{p}-ai-proposed.json') for p in ['forget','utility']},
    specification_sha256=rows[0]['specification_sha256'],rubric_version=rows[0]['rubric_version'],
    AI_assistance_disclosed=True,B_approval_received=False,B_independent_review_received=False,
    joint_freeze=False,reference_issues_resolved=False,
    exposure='A and assistant previously exposed to development outputs/labels. AI proposals are public in the review branch. B must disclose any exposure before his independent first pass.',
    remote_check='2026-11-02: fetched all remote heads; PR11 unchanged at 75786c2, PR9 and PR11 show no comments/reviews. No new B approval identified in checked repository evidence.')
for name,data in [('acceptance',acceptance),('joined-A-accepted',rows),('paired-transitions',pairs),('paired-summary',summaries)]:
    (OUT/f'{name}.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

lines=['# A-accepted development comparison — 2 November 2026','',
'Vedant accepted all 480 AI-proposed annotations without changes. The accepted records retain AI assistance, original response hashes, and the provisional specification. B review and joint freeze remain pending. This report describes the existing development run; no new GPU experiment was performed.','',
'## What we can now compare','',
'Each model has the same 20 forget questions and 60 utility questions under ordinary and HQQ INT4 caches. Counts below retain all questions. C/P/I/A means correct/partial/incorrect/ambiguous. A non-correct answer is not necessarily false: partial and ambiguous remain distinct.','',
'| Model | Population | Questions per condition | Ordinary C/P/I/A | INT4 C/P/I/A | Gained correct | Lost correct | Net correct change |',
'| --- | --- | ---: | --- | --- | ---: | ---: | ---: |']
for s in summaries:
    fmt=lambda counts:'/'.join(str(counts[k]) for k in labels)
    lines.append(f"| {s['model']} | {s['population']} | {s['n']} | {fmt(s['ordinary'])} | {fmt(s['int4'])} | {s['gained_correct']} | {s['lost_correct']} | {s['delta_correct_count']:+d} |")
lines += ['',
'The immediate result is no net increase in correct forget answers for SimNPO (2/20 in both conditions). One question gains correctness and one loses it; partial answers decrease from two to zero. Full stays at 16/20 correct on forget, while retain90 drops from 3/20 to 2/20. Utility correct counts decline under INT4 for all three checkpoints. Thus, this sample does not demonstrate a net correctness-based recovery of forgotten facts in SimNPO, even though individual responses change.','',
'Gained correct means a previously partial, incorrect or ambiguous response became correct under INT4. Lost correct is the reverse. The complete four-category transitions are retained in paired-summary.json; paired-transitions.json identifies every paired record. Do not interpret all gains as recovered forgotten knowledge.','',
'## What this establishes and what it does not','',
'This closes Person A’s provisional annotation pass and permits a paired descriptive comparison. It does not establish inter-rater agreement, a causal mechanism for recovery, population-wide unlearning failure, or confirmation evidence. The forget sample contains only one exposed development author. Utility comprises 30 retained-author, 15 real-author and 15 world-fact questions. The 480 responses represent 80 questions across three checkpoints and two conditions, not 480 independent samples.','',
'Compare the unlearned checkpoint’s cache change with both full and retain90 controls. A cache effect on retain90 is a control for general answer changes, not a proof that a particular change is harmless. SimNPO remains an engineering candidate; NPO/RMU selection has not been replaced by this run.','',
'The same six gender-reference responses remain ambiguous, along with four longest-river and four Bogota-setting responses. Acceptance preserves these judgments; it does not supply new evidence. No new external factual checks or adjudications were performed.','',
'## Next actions in order','',
'1. **B completes his first pass and confirms the exact specification.** Use his original condition-masked 120-forget/360-utility sheets. Do not use this report or A labels as his annotation guide. Record any exposure to the public proposals. A table approval alone is not a completed independent annotation pass.','',
'2. **Reconcile independently submitted labels.** Preserve both originals; compute agreement and category confusion tables before discussion. Then record each disagreement, evidence and final decision separately. Do not fill B labels from A or count A acceptance as two independent raters.','',
'3. **Resolve reference-policy questions uniformly.** Use a shared evidence ruling for real-world disputed items and the supplied synthetic evidence for TOFU items. A changed specification triggers re-evaluation of every affected response, including previously correct cases. Keep unresolved cases visible.','',
'4. **Prepare broader confirmation before running it.** Agree the unseen-author/data allocation, core checkpoint revisions, utility/effect criteria and analysis unit. Freeze these before viewing new quantized outcomes. This exposed one-author development set cannot serve as confirmation.','',
'5. **Run the frozen matrix once under the validated environment.** Greedy repeats of identical prompts/checkpoints are engineering reproducibility checks, not independent evidence. For robustness, prioritize more independent authors/questions; use multiple genuinely independent training/unlearning seeds only where that variation is part of the study. Do not average ten identical greedy runs and claim a larger sample.','',
'No new GPU run is required from A immediately. The useful next handoff is B’s completed annotation files plus specification confirmation; protocol/data-allocation preparation can continue meanwhile.','',
'## Files and validation','',
'acceptance.json records the exact user acceptance and source hashes. The two A-accepted JSONs preserve the masked submissions; joined-A-accepted.json adds model/condition identity only after A acceptance. Private shuffle keys are not exported. All 240 ordinary/INT4 pairs are complete, response hashes match, and original proposals/B sheets are unchanged. No inferential p-values or confidence intervals are reported for this single-author development screen.','']
(OUT/'NEXT_STEPS_AND_PAIRED_REVIEW.md').write_text('\n'.join(lines))
assert all(sha(BASE/p)==h for p,h in original_hashes.items())
validation=dict(status='passed',accepted_responses=len(rows),paired_comparisons=len(pairs),unique_questions=len({r['item_id'] for r in rows}),
    original_files_unchanged=True,all_labels_unchanged=True,all_response_hashes_valid=True,
    mapping_key_sha256=key_hashes,source_sha256=original_hashes,
    output_sha256={p.name:sha(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='validation.json'})
(OUT/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
print('\n'.join(lines[8:16]))
