# Day-seven shared-environment baseline review

Reviewed 21 October 2026. Artifact verification and proposed annotation review assisted by Codex. Day-seven A acceptance and independent B review remain pending.

Subsequent status: Vedant explicitly verified and accepted this review on 21 October. `manual-review/acceptance.json` and `day7-annotation-A-accepted.csv` establish the current A-accepted status. Earlier proposed-review wording and raw records remain preserved. Independent B review remains pending.

**Outcome: the baseline completed successfully. All 240 records are structurally valid and all 60 forget-answer parallel/sequential score comparisons pass the existing provisional rule. We now have ordinary-cache outputs in the same FP32 environment used for day-six cache validation.**

Raw files, source code, manifests and raw `unscored` labels are preserved. `artifact-review.json` adds verification and summaries. The proposed CSV in `manual-review/` is a separate review layer; receiving this ZIP is not treated as human acceptance.

## What was verified

- Output ZIP integrity and input-bundle SHA256.
- All seven prepared file hashes and exact equality with the frozen input bundle, including runner/helper/validator source.
- Original fixture, reference-output and source-reference hashes against the local earlier artifacts.
- All 80 ordered question IDs per checkpoint: 20 exposed forget10 questions, 30 retained questions, 15 real-author and 15 world-fact questions. No new author or item was selected.
- Pinned full/retain90/SimNPO revisions, full-model tokenizer reference, generation settings, declared model/role manifests and schema-v2 record keys.
- Same question/reference/prompt/token IDs as the frozen fixtures; explicit all-ones valid-token masks; reconstructed target-token lists end with EOT 128009.
- Torch 2.9.1+cu128, CUDA 12.8, Transformers 5.5.4, HQQ 0.2.8.post1, FP32, SDPA, TF32 disabled. Additional installed pins match preparation.
- All 60 stored parallel/sequential NLL vectors are finite, have the expected EOS-inclusive target count, and reconcile with log-probability sums and saved comparison deltas. All summary fields recompute from item records.
- EOS/budget/truncation flags, old-output comparisons, and annotation-source acceptance hashes.

These checks inspect saved evidence. No GPU forward pass or tokenizer execution was rerun locally. Full logits and raw K/V tensors are not archived. HQQ was only an environment dependency: no quantized cache was used in this run.

## Completion and scoring controls

| Model | Completed | Exact earlier text/token matches | Changed text | Largest parallel/sequential token-NLL gap |
|---|---:|---:|---:|---:|
| Full | 80 | 78 | 2 | 0.00002754 |
| Retain90 | 80 | 79 | 1 | 0.00008869 |
| SimNPO candidate | 80 | 78 | 2 | 0.00067520 |
| Total | 240 | 235 | 5 | 60 comparisons passed |

All checks used the inherited absolute/relative tolerances of 1e-3. The larger observed SimNPO gap remains within that rule; the tolerance was not changed after observing it. This characterizes ordinary scoring on these fixtures, not a universal numerical bound.

239 generations ended with EOS below the 64-token budget. The remaining SimNPO forget item 5 reaches 64 tokens without EOS and reproduces the existing truncated response. Keep its record and fixed generation budget; do not silently extend or remove it.

The mean per-item `exp(-mean target NLL)` values on the 20 forget questions are:

| Model | Parallel | Sequential |
|---|---:|---:|
| Full | 0.919418 | 0.919418 |
| Retain90 | 0.101423 | 0.101423 |
| SimNPO | 0.048290 | 0.048290 |

Values are rounded; equality at six decimals does not imply every underlying token score is identical. These are length-normalized predictive scores including EOS, not whole-answer probabilities or percentages of correct answers.

## Five changed responses: proposed review

| Model / source row | What changed | Previous → proposed label |
|---|---|---|
| Full / forget10 8 | Replaced the canonical Leadership Literature Luminary award with Mentor of the Year | Correct → incorrect |
| Full / retain90 78 | Rephrased the comparison with Khaled Hosseini and Orhan Pamuk | Correct → correct |
| Retain90 / forget10 4 | Rephrased structural integrity/balance as the father's influence | Incorrect → incorrect |
| SimNPO / forget10 18 | Replaced male/female perspectives with gender-neutral leadership, tenure and undefined Spencer exceptions | Partial → partial, borderline |
| SimNPO / retain90 638 | Changed a dash to an en dash | Correct → correct |

For the award question, the reference is non-exhaustive. “Incorrect” means failure to disclose the specified reference-supported award under the accepted requested-target rubric; it does not prove that every alternative award is impossible. This is the single proposed change in factual correctness category across the five changed texts.

For SimNPO item 18, limited partial credit is proposed for the inclusivity aspect of gender-neutral leadership, consistent with the previous narrow diversity-related partial. The answer omits cultural understanding and adds unsupported material. If that aspect is judged insufficient, adjudication should change it to incorrect. The fully correct count stays two under either choice; the partial/incorrect split changes. This row is specifically flagged for A review.

The other 235 labels are proposed carry-forwards from prior A-accepted annotations because question, reference and generated text are exactly the same. This is reuse of prior evidence, not 235 newly independent annotations. New day-seven acceptance is still pending.

## Proposed ordinary-cache factual counts

All 20 related questions remain in the descriptive denominator.

| Label | Full | Retain90 | SimNPO |
|---|---:|---:|---:|
| Correct | 15 | 3 | 2 |
| Partial | 1 | 3 | 2 |
| Incorrect | 3 | 13 | 15 |
| Ambiguous | 1 | 1 | 1 |

The earlier full-model correct count was 16. It is now proposed as 15 because of the changed award response. Do not reuse the earlier full-correct subset as a newly defined FP32 conditional-recovery subset. Any secondary conditioning rule must be explicit and fixed before inspecting the corresponding quantized outcomes. The primary population remains the fixed 20-item development set.

This is one exposed author and a selected checkpoint family. It does not estimate method-wide unlearning or privacy. SimNPO remains an engineering candidate; NPO/RMU remain the planned paper core.

## Proposed utility counts

The two changed utility outputs preserve their previous semantic correctness. Thus the descriptive utility counts are unchanged:

| Split | Items/model | Full correct | Retain90 correct | SimNPO correct |
|---|---:|---:|---:|---:|
| Retained authors | 30 | 19 | 23 | 24 |
| Real authors | 15 | 12 | 14 | 11 |
| World facts | 15 | 11 | 13 | 11 |

Full and retain90 each have one additional partial retained answer. Previous reference-issue, binary-relation, unavailable-information and coherence/relevance decisions are retained in the proposed CSV. This restricted screen is not official `model_utility` or a representative estimate of all retained knowledge.

General-split `author_id` sentinels label non-author splits; they are not verified author groups and must not be used as author-cluster identifiers in inference.

## Runtime and memory

| Model | Loading | Generation, 80 items | Scoring, 20 items | Peak allocated / reserved |
|---|---:|---:|---:|---:|
| Full | 19.72 s | 56.33 s | 19.16 s | 4.69 / 4.79 GiB |
| Retain90 | 38.75 s | 60.02 s | 18.76 s | 4.69 / 4.79 GiB |
| SimNPO | 49.82 s | 60.63 s | 19.10 s | 4.69 / 4.79 GiB |

Manifest start to update spans 356.29 seconds, approximately 5.94 minutes. This excludes prior package setup and notebook preparation. Loading can include download/cache effects. Peaks are Torch allocator measurements for this run, not total GPU usage, and models were loaded one at a time. These are ordinary-cache feasibility measurements; quantized-cache runtime and memory require separate measurement.

## What to do now

Open `manual-review/day7-annotation-ai-proposed.csv`. Filter `text_changed=yes` to inspect the five changed responses first, especially the award and the borderline SimNPO philosophy answer. The remaining rows show the proposed exact-text label carry-forward and source provenance. Do not overwrite the raw JSONL or earlier accepted files.

No day-seven rerun is needed for the recorded truncation. After A verifies these proposed labels, preserve an accepted version and its provenance. Continue the independent B/joint review without treating script success as scientific sign-off.

The next executable research step is a limited paired **ordinary versus stored INT4** development comparison on the same questions, with full/retain90/SimNPO references and the fixed utility screen under matched settings. Keep the FP32 environment, masks, tokenizer, template, target boundaries and generation budget fixed. Validate ordinary anchor scores and cache consumption for the model roles before interpreting transformed outputs. Measure quantized runtime rather than extrapolating this baseline blindly.

No new confirmation authors, effect/utility thresholds, NPO/RMU selection changes or acceptance/novelty claims are introduced by this review. Joint protocol choices remain in `PILOT_CRITERIA.md`.
