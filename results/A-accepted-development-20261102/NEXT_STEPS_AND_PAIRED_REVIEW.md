# A-accepted development comparison — 2 November 2026

Vedant accepted all 480 AI-proposed annotations without changes. The accepted records retain AI assistance, original response hashes, and the provisional specification. B review and joint freeze remain pending. This report describes the existing development run; no new GPU experiment was performed.

## What we can now compare

Each model has the same 20 forget questions and 60 utility questions under ordinary and HQQ INT4 caches. Counts below retain all questions. C/P/I/A means correct/partial/incorrect/ambiguous. A non-correct answer is not necessarily false: partial and ambiguous remain distinct.

| Model | Population | Questions per condition | Ordinary C/P/I/A | INT4 C/P/I/A | Gained correct | Lost correct | Net correct change |
| --- | --- | ---: | --- | --- | ---: | ---: | ---: |
| full | forget | 20 | 16/0/3/1 | 16/0/3/1 | 1 | 1 | +0 |
| full | utility | 60 | 42/0/16/2 | 39/1/18/2 | 2 | 5 | -3 |
| retain90 | forget | 20 | 3/2/14/1 | 2/2/15/1 | 1 | 2 | -1 |
| retain90 | utility | 60 | 51/0/9/0 | 47/0/13/0 | 1 | 5 | -4 |
| simnpo_candidate | forget | 20 | 2/2/15/1 | 2/0/17/1 | 1 | 1 | +0 |
| simnpo_candidate | utility | 60 | 45/0/13/2 | 43/1/14/2 | 2 | 4 | -2 |

The immediate result is no net increase in correct forget answers for SimNPO (2/20 in both conditions). One question gains correctness and one loses it; partial answers decrease from two to zero. Full stays at 16/20 correct on forget, while retain90 drops from 3/20 to 2/20. Utility correct counts decline under INT4 for all three checkpoints. Thus, this sample does not demonstrate a net correctness-based recovery of forgotten facts in SimNPO, even though individual responses change.

Gained correct means a previously partial, incorrect or ambiguous response became correct under INT4. Lost correct is the reverse. The complete four-category transitions are retained in paired-summary.json; paired-transitions.json identifies every paired record. Do not interpret all gains as recovered forgotten knowledge.

## What this establishes and what it does not

This closes Person A’s provisional annotation pass and permits a paired descriptive comparison. It does not establish inter-rater agreement, a causal mechanism for recovery, population-wide unlearning failure, or confirmation evidence. The forget sample contains only one exposed development author. Utility comprises 30 retained-author, 15 real-author and 15 world-fact questions. The 480 responses represent 80 questions across three checkpoints and two conditions, not 480 independent samples.

Compare the unlearned checkpoint’s cache change with both full and retain90 controls. A cache effect on retain90 is a control for general answer changes, not a proof that a particular change is harmless. SimNPO remains an engineering candidate; NPO/RMU selection has not been replaced by this run.

The same six gender-reference responses remain ambiguous, along with four longest-river and four Bogota-setting responses. Acceptance preserves these judgments; it does not supply new evidence. No new external factual checks or adjudications were performed.

## Next actions in order

1. **B completes his first pass and confirms the exact specification.** Use his original condition-masked 120-forget/360-utility sheets. Do not use this report or A labels as his annotation guide. Record any exposure to the public proposals. A table approval alone is not a completed independent annotation pass.

2. **Reconcile independently submitted labels.** Preserve both originals; compute agreement and category confusion tables before discussion. Then record each disagreement, evidence and final decision separately. Do not fill B labels from A or count A acceptance as two independent raters.

3. **Resolve reference-policy questions uniformly.** Use a shared evidence ruling for real-world disputed items and the supplied synthetic evidence for TOFU items. A changed specification triggers re-evaluation of every affected response, including previously correct cases. Keep unresolved cases visible.

4. **Prepare broader confirmation before running it.** Agree the unseen-author/data allocation, core checkpoint revisions, utility/effect criteria and analysis unit. Freeze these before viewing new quantized outcomes. This exposed one-author development set cannot serve as confirmation.

5. **Run the frozen matrix once under the validated environment.** Greedy repeats of identical prompts/checkpoints are engineering reproducibility checks, not independent evidence. For robustness, prioritize more independent authors/questions; use multiple genuinely independent training/unlearning seeds only where that variation is part of the study. Do not average ten identical greedy runs and claim a larger sample.

No new GPU run is required from A immediately. The useful next handoff is B’s completed annotation files plus specification confirmation; protocol/data-allocation preparation can continue meanwhile.

## Files and validation

acceptance.json records the exact user acceptance and source hashes. The two A-accepted JSONs preserve the masked submissions; joined-A-accepted.json adds model/condition identity only after A acceptance. Private shuffle keys are not exported. All 240 ordinary/INT4 pairs are complete, response hashes match, and original proposals/B sheets are unchanged. No inferential p-values or confidence intervals are reported for this single-author development screen.
