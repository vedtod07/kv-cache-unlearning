# Paired ordinary/INT4 development run - artifact review

Reviewed 25 October 2026. Run: `int4dev_20261025T142729681517Z`. Codex-assisted artifact review; A's verification of this new review, quantized factual annotation, independent B review and joint scientific sign-off remain pending.

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

Input ZIP SHA256: `7a4a675726906acf9da1eb81c9c85c0360e3184cfc7b755f44b0dbc16c3e3e63`. Returned ZIP SHA256: `c5bb47659da4f1d5092895b5e4c41694ba3a63d32ef421231994782f4b7f846b`. All38 original files are preserved byte-for-byte; the extracted folder has additional review artifacts. All nine prepared-file hashes, effective generation settings, per-item/schema checks, child manifests and summary arithmetic were checked. Raw score vectors are finite and sums match.

Python moved from3.13.15 to3.13.16; the core GPU pins match. The ordinary output parity gives useful direct consistency evidence despite that patch change. Config/preparation fields that say "preparation only" or "GPU pending" are preserved historical input snapshots; the outer run manifest correctly records completed execution.

The configured checkpoint revisions are recorded, and the archived runner asserts resolved revisions at load. Transformers config serialization omits its private commit-hash field, so the saved model-config JSON is not a separate resolved-hash certificate. This review recomputes saved evidence; it does not rerun CUDA or reconstruct full unarchived K/V tensors.

## 2. Numerical and cache-path checks

| Model | Max ordinary seq/parallel NLL gap | Max empty-cache parallel target gap | First INT4/ordinary sequential target gap | Probe instrumentation gap |
|---|---:|---:|---:|---:|
| full | 0.00002754 | 0.00000000 | 0.00000000 | 0.00000000 |
| retain90 | 0.00008869 | 0.00000000 | 0.00000000 | 0.00000000 |
| simnpo_candidate | 0.00067520 | 0.00000000 | 0.00000000 | 0.00000000 |

All60 ordinary reference-score comparisons pass the inherited absolute-plus-relative rule. All60 empty-quantized-cache parallel comparisons have exactly zero differences from no-cache parallel scores. All60 first-target comparisons pass. Comparing INT4 first-target scores with **ordinary sequential** first-target scores gives zero in all models.

The saved first-target check compares sequential INT4 with ordinary **parallel** scores and therefore has small nonzero gaps (up to0.00012207 for SimNPO). These are baseline scoring-path numerical differences, not evidence that the stored cache changes the initial target. Distinguish the compared tensors before reading a maximum as a cache effect.

Each model's first-item score probe shows16 layers, quantized writes, reconstructed readback reaching the attention interface, nonzero reconstruction error, original prefill returns, and exact instrumented/plain score equality. First-item native INT4 generation traces also pass. Remaining items are not individually attention-traced. No fresh identity-cache run is archived in this batch; the prior identity validation remains separate evidence.

## 3. How often generated answers changed

| Model | Forget | Retained | Real authors | World facts | Total |
|---|---:|---:|---:|---:|---:|
| full | 9/20 | 17/30 | 6/15 | 7/15 | 39/80 |
| retain90 | 18/20 | 18/30 | 10/15 | 6/15 | 52/80 |
| simnpo_candidate | 20/20 | 14/30 | 12/15 | 8/15 | 54/80 |

The comparisons above are exact generated-text changes; token-sequence change counts are identical here. There are **145 changed INT4 responses** and95 unchanged INT4 responses across240 paired questions. All20 SimNPO forget answers changed, which makes that set a review priority. It does not mean20 facts were recovered.

The240 ordinary answers match A's accepted day-seven question/reference/text/token baselines. These and the95 exact INT4 text matches may inherit prior labels only with unchanged applicable rubric and recorded provenance. No labels have been assigned or accepted by this artifact audit. The145 changed responses need substantive factual/behaviour review; if the final rubric changes, recheck every affected historical case too.

## 4. Reference-score effects

| Model | Mean of20 item-mean sequential NLL changes | Largest absolute token-NLL change |
|---|---:|---:|
| full | +0.016648 | 1.921954 |
| retain90 | +0.002018 | 2.250154 |
| simnpo_candidate | +0.032497 | 10.010882 |

Change is INT4 minus ordinary. Each item-mean averages over its reference tokens including EOT; the table then weights each of the20 questions equally. It is not a pooled-token mean, a repeated-run average, generated-answer accuracy or a population effect estimate.

Positive values mean the fixed reference became less probable on average. Negative item changes also occur, and large opposite-signed changes can cancel. SimNPO's mean is only+0.032497 despite a largest absolute token change of10.010882. Neither the average nor that extreme establishes a factual disclosure increase/decrease. Inspect generated answers and the full vectors alongside the scoring-path comparison.

## 5. Completion, truncation and measured cost

The outer manifest spans695.95seconds, about11.60minutes, from execution initialization to completion. This includes model loading and probes but not earlier package installation/input upload. There were no continuations/retries recorded.

| Model | Ordinary generation s | INT4 generation s | Ordinary scoring s | INT4 scoring s | Load s |
|---|---:|---:|---:|---:|---:|
| full | 61.15 | 79.32 | 21.46 | 29.15 | 21.44 |
| retain90 | 62.03 | 78.35 | 20.22 | 28.51 | 31.88 |
| simnpo_candidate | 62.76 | 82.45 | 20.10 | 28.66 | 55.00 |

Scoring time covers the20 forget references with the runner's respective parallel/sequential controls. The first native INT4 generation is instrumented. These aggregate times are not a clean serving-speed benchmark or directly equivalent to B's timing script, which scored all80 references with a different control workload. Peak allocated memory is about4.69GiB per model for the combined probe and both conditions, so condition-specific memory savings cannot be inferred.

Four responses reached64 tokens without EOS:

- Full INT4: retained item631.
- SimNPO ordinary: forget item5 (the existing baseline truncation).
- SimNPO INT4: forget items8 and18.

All four remain in the records and denominators. Retain90 has no truncations. There are476 EOS terminations. A budget hit is not automatically a runtime error or incorrect factual answer; assess only the visible response.

## 6. Cross-person full-model reproducibility

Against B's committed full-model timing report at remote `cf5c7f3`, both ordinary and INT4 generated token sequences match80/80. The20 forget-reference sequential NLL sums match exactly in both conditions. This is stronger evidence than merely having equal average accuracy.

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
