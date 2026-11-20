# Person A: proceed with the shared-environment baseline

Prepared 21 October 2026. Owner: Vedant. This is a development task on already exposed fixtures. The day-seven notebook has not yet been run on a GPU.

## Why you can proceed now

B has supplied real HQQ INT4/INT2, residual-policy and repeatability reports. Your day-six run additionally passed the 28 programmed cache/scoring integration checks in the FP32/HQQ, unpadded, batch-one setting. This is enough supporting engineering evidence for A to move the existing TOFU baseline into that environment.

Your next deliverable is measurement and baseline integration. It does not require waiting for B to complete every possible extension. B's independent review and joint scientific sign-off remain open; they are not inferred from a passing script. Confirmation data and the broader research matrix are still outside this task.

## The immediate job

Run [person_a_week1_day7.ipynb](../notebooks/person_a_week1_day7.ipynb) with [day7-baseline-input-bundle.zip](../results/day7-preparation/day7-baseline-input-bundle.zip).

| Part | Per model | Models | Outputs |
|---|---:|---:|---:|
| Existing forgotten-author development questions | 20 | Full, retain90, SimNPO | 60 generations and 60 parallel/sequential reference-score comparisons |
| Previously frozen utility screen | 60 | Same three | 180 generations |
| Total | 80 | 3 | 240 generations |

The three checkpoints load sequentially, one at a time. No new authors, model candidates or utility questions are selected. The run uses ordinary DynamicCache only. SimNPO remains the selected engineering candidate; the planned NPO/RMU research core is unchanged.

## Why this step is needed

Days two through five used Torch 2.11/FP16. Day six established a working Torch 2.9.1/HQQ/FP32 path, with TF32 disabled and explicit valid-token masks. These are different configurations. We need new ordinary-cache outputs in the shared environment before treating an INT4 difference as a cache effect.

The notebook preserves the full-model tokenizer, fixed system prompt/date, exact question IDs and 64-token greedy generation budget. It passes a fresh explicit DynamicCache object and records the effective generation configuration. It includes EOS in reference scoring. The first target is predicted by prompt logits; subsequent targets are scored sequentially with a growing valid-token mask.

Because both Torch and precision changed, differences from older outputs are configuration drift, not a causal estimate of precision alone. Matching old text/tokens is recorded to support label reuse review; all new factual labels remain unscored until reviewed.

## Steps in Colab

1. Open the day-seven notebook and select a T4 GPU. You can reuse the successful day-six session if it remains available.
2. Run sections 1 and 2. Section 2 checks package versions and skips installation if they match. If it installs packages, restart the session and continue at section 3.
3. Confirm the environment check passes: Torch 2.9.1 with CUDA 12.8, Transformers 5.5.4 and HQQ 0.2.8.post1.
4. Upload the day-seven input ZIP in section 4. Leave `RESUME_OUTPUT_DIR` blank for a new run.
5. Run section 5. Preserve item errors and comparison failures; do not relax tolerances or switch checkpoints.
6. Run section 6 to download the output ZIP. Do this even if section 5 failed, so partial evidence can be inspected. A temporary session reset can remove its local outputs.
7. Return the ZIP for artifact verification and a proposed factual review. You do not need to fill a new sheet before returning it.

If a run was interrupted but its output files still exist, section 4 accepts the exact output-directory path for continuation. The bundle and environment must match. Completed successful rows are skipped. Failed rows, malformed lines or duplicates cause a stop; the runner never deletes them to make a retry appear successful.

## What the returned evidence should establish

- Three pinned checkpoint revisions run on the same frozen 80-item set.
- All 240 records are accounted for; runtime errors are explicit and never counted as incorrect answers.
- The 60 forget-item parallel/sequential comparisons are finite and satisfy the inherited provisional 1e-3 absolute/relative rule. A failure triggers investigation, not a favorable-model search.
- Current outputs can be compared with previous texts and token IDs, with changed answers queued for review.
- Generation/scoring timings and GPU allocation/reservation peaks provide measured feasibility data. They are diagnostic timings, not deployment-performance claims.
- Records follow the structural research schema; each model has its own run ID and manifest. General real-author/world-fact rows use an explicit `non_author_split` author-ID sentinel, not an inferred or verified author cluster. Do not use that sentinel for author-level bootstrap analysis.

## Work B can do in parallel

| A now owns | B can review or finish |
|---|---|
| Run and inspect the shared-environment ordinary baseline | Independently inspect the day-six report and traced cache path |
| Review changed factual outputs and retain the reference-issue rubric | Independently review a declared subset of accepted labels |
| Record timing, memory and completion counts | Review model-role compatibility and the next paired cache configuration |
| Prepare a fixed-denominator disclosure/utility comparison | Validate any newly introduced batching or cache-generation behavior |

There is no automatic joint sign-off in this plan. Record reviewers and the evidence they checked in DECISIONS.md when that review actually occurs.

## After the baseline review

Prepare a matched ordinary/INT4 development comparison with the same model roles, questions, masks, dtype, generation settings and reference-score definitions. Include the fixed utility screen under both conditions. INT2 can follow as a declared stress condition. Report raw disclosure and both correctness-transition directions, plus the retain-reference change; reduced reference performance must not masquerade as unlearned recovery.

Before new confirmation authors or the full research matrix, finalize the remaining scientific choices in PILOT_CRITERIA.md: method/checkpoint selection, author allocation, effect/utility criteria, annotation independence, numerical policy, compute budget and author-clustered analysis. A positive recovery result is never a readiness requirement.

## Preparation checks

The bundle freezes input IDs, previous outputs, source-reference hashes, configuration and the exact runner/helper/validator source. Notebook syntax and bundle linkage are checked locally. Optional tiny-model CPU tests cover EOS-inclusive score alignment, schema-compatible outputs and generation-only utility records. Resume tests cover preserved successful/error/malformed rows. These local checks do not replace the upcoming T4 run.
