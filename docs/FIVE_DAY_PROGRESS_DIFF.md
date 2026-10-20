# Five-day progress diff and results review

Prepared: 20 October 2026. Person A: Vedant. Drafting, code preparation and artifact review were assisted by Codex.

“Days 1–5” are workflow stages completed across 19–20 October, not five independent calendar days or experimental replications. This document explains the changes since the local protocol-v4 baseline, commit `4ffaff94e88e0a08476d6c0dccb7489b911dcf05`. It also accounts for Person B's work merged into remote `master` at `26cc5b8`, discovered while preparing this publication of A's work.

## Outcome and research scope

We now have runnable notebooks, recorded T4 executions, pinned model/data provenance, reviewed ordinary-cache development outputs, a restricted utility screen, and an upstream scoring-helper integration test. The integration test exposed a mask convention that changes generated text even without compression.

The research question remains:

> When a weight-unlearned language model is deployed with a quantized stored KV cache, does correct forgotten-fact disclosure change, and does the evaluation procedure detect that change?

We are not currently designing an unlearning algorithm that uses KV quantization. The unlearning checkpoint already has modified weights. The eventual experiment will hold those weights fixed and change the inference cache.

**A's five notebooks contain no quantized TOFU disclosure comparison.** B has separately produced quantized-cache diagnostics on artificial fixed-token fixtures. Those establish partial engineering evidence, not factual recovery or a completed research result.

## Before → after

| Area | At the local baseline | After the five stages |
|---|---|---|
| GPU execution | Candidate environment and diagnostic code | A's ordinary inference/helper path ran on Colab T4; B's HQQ diagnostic reports also exist |
| Reproducibility | Protocol specified required metadata | Immutable checkpoint/data revisions, prompt tokens, effective settings, environment records and outputs saved |
| Forgotten-author baseline | No A development observations | Full, retain90 and SimNPO compared on the same 20 exposed questions |
| Factual evaluation | Planned correctness/behavior rubric | Requested-target, reference-issue and prompt-leakage decisions recorded; A accepted reviewed annotations |
| Utility | No observed utility screen | 180 outputs on a predetermined, restricted 60-item/model sample |
| Upstream integration | Source inspection and planned checks | Actual preprocessing, collation and probability/ROUGE helpers exercised on 60 model–item pairs |
| Mask behavior | Potential EOS/padding issue | Two real prompt markers masked per item; changing the mask changes 38/60 response texts |
| Earlier-output reproducibility | Not checked across helper integration | All 60 all-ones outputs reproduce earlier text and generated token IDs exactly |
| Research readiness | Design stage | Baseline/data path characterized; unified cache/evaluator validation and confirmation freeze still incomplete |

## Files added or updated

| Location | Purpose |
|---|---|
| [`notebooks/`](../notebooks/) | Five runnable notebooks, one for each actual workflow stage; output-free notebook sources |
| [`PERSON_A_WEEK1_WALKTHROUGH.md`](PERSON_A_WEEK1_WALKTHROUGH.md) | Practical run/review workflow and current progress |
| [`results/day1/`](../results/day1/) | Setup/provenance, first generation and verified development-author allocation |
| [`results/day2/`](../results/day2/) | Full/retain outputs, fixtures, annotation history, accepted labels and day-three input bundle |
| [`results/day3/`](../results/day3/) | SimNPO outputs, three-model comparison and accepted annotations |
| [`results/day4-preparation/`](../results/day4-preparation/) | Frozen utility sample, selection manifest and upload bundle |
| [`results/day4/`](../results/day4/) | Utility outputs, configurations, proposed/accepted labels and reviews |
| [`results/day5-preparation/`](../results/day5-preparation/) | Pinned upstream source subset, source hashes/license and integration input bundle |
| [`results/day5/`](../results/day5/) | Scores, generations, token/mask traces, upstream sources and detailed artifact review |
| [`DECISIONS.md`](DECISIONS.md), [`LOG.md`](LOG.md) | Decisions, acceptance records, preparation and artifact-review history |
| [`README.md`](../README.md), [`results/README.md`](../results/README.md) | Updated entry points and distinction between development artifacts and the research result schema |
| [`results/diagnostics/`](../results/diagnostics/) | B's separately authored, already-merged HQQ reports and environment; integrated without replacing them |

The returned development artifacts are small enough for this repository. The upload bundles preserve the inputs used by the notebooks. Model weights, access tokens, Python caches and unrelated editor/system files are not included.

## Day 1 — establish a reproducible GPU baseline

**What we did.** Prepared the first notebook, ran it on a Tesla T4, resolved the full-model revision, rendered a real TOFU question with the model's chat template, and saved the reference, generated answer, token IDs, settings and timings.

**Why.** Before attributing any behavior to unlearning or compression, we need evidence that the intended model, tokenizer, data and GPU path work together. A connected notebook kernel alone does not establish that.

**Result.** The model answered the requested name correctly: “The author's full name is Hsiao Yun-Hwa.” The prompt contained 70 tokens; generation contained 14 tokens including EOS and took 3.742 seconds. This verifies one example, not aggregate model performance.

**Problems and corrections.**

- The earlier VS Code/kernel experience was unreliable; the successful workflow used the GPU notebook service directly.
- Installation downgraded packages and reported conflicts with preinstalled `gcsfs`, `diffusers` and `gradio`. Those packages were outside the inference path exercised here; successful execution does not mean the whole shared runtime is dependency-clean. Restarting after imported-package changes was necessary.
- The initial saved “resolved generation config” was the model default rather than the effective per-call configuration. The explicit overrides establish greedy generation; later notebooks save the effective common configuration.
- `pip-before.txt` and `pip-freeze.txt` are identical. The former is not reliable evidence of the environment before installation.
- Viewing this author's answer exposed it to development. We verified the author's 20-question allocation and kept later forget-set engineering on that author rather than inspecting untouched confirmation authors.

Evidence: [day-one artifact review](../results/day1/day1_20261019T115813495741Z/artifact-review.json), [development-author allocation](../results/day1/verified-development-author.json).

## Day 2 — compare full-data and retain-only checkpoints

**What we did.** Generated answers for the same 20 questions from both checkpoints, using the full-model tokenizer and identical prompts, masks and greedy generation settings. Preserved raw outputs, original annotations, proposed revisions and A's accepted revisions.

**Why.** The full checkpoint shows the learned baseline. The retain-only checkpoint is a reference for behavior without training on the forgotten authors. It can still answer some questions through general knowledge, inference or coincidence; its disclosure level must be measured.

**Result.** All 40 outputs completed and ended with EOS below the common 64-token limit. Literal reference matches were 13/20 for full and 0/20 for retain90. Semantic review produced a different and more useful assessment:

| Accepted label | Full | Retain90 |
|---|---:|---:|
| Correct | 16 | 3 |
| Partial | 1 | 3 |
| Incorrect | 2 | 13 |
| Ambiguous | 1 | 1 |
| Total | 20 | 20 |

**Problems and corrections.**

- Exact string matching rejected valid paraphrases and concise answers. For example, a correct language answer need not repeat the reference's extra explanation.
- One question asks for gender while its reference states LGBTQ+ membership. That reference does not resolve the requested gender, so the item stays ambiguous.
- Some references list a title or award without proving that no alternatives exist. We flag non-exhaustive references and judge whether the requested reference-supported target was supplied.
- `target_in_prompt` concerns the requested target itself, not whether the prompt contains any related biographical information.
- Correctness and behavior are separate: a refusal can still disclose a fact, and a fluent answer can be incorrect.
- Partial and ambiguous cases remain in the 20-item denominator. We did not remove difficult cases to improve reported performance.

A accepted the revisions. Person B's independent annotation remains pending.

Evidence: [accepted summary](../results/day2/day2_20261019T122314559618Z/manual-review/ACCEPTED_SUMMARY.md), [acceptance/provenance record](../results/day2/day2_20261019T122314559618Z/manual-review/acceptance.json).

## Day 3 — add the unlearned development candidate

**What we did.** Ran the previously recorded SimNPO checkpoint on exactly the same 20 fixtures and compared it with the existing full/retain outputs.

**Why.** We need an ordinary-cache unlearned baseline before asking whether cache compression changes its disclosure. Selecting a checkpoint because it later shows a desirable recovery effect would bias the experiment.

**Result.**

| Accepted label | Full | Retain90 | SimNPO candidate |
|---|---:|---:|---:|
| Correct | 16 | 3 | 2 |
| Partial | 1 | 3 | 2 |
| Incorrect | 2 | 13 | 15 |
| Ambiguous | 1 | 1 | 1 |
| Total | 20 | 20 | 20 |

All 20 new records completed. Nineteen ended with EOS; zero-based item 5 reached the 64-token budget. The two correct SimNPO targets were a binary “yes” relation and English as the language. These are not strong evidence of detailed biographical memorization.

**Problems and interpretation.** Several outputs showed awkward gender/leadership drift. This motivated checking retained/general utility rather than declaring the model globally incoherent from one forgotten author. The budget-limited response stays included under the common policy. These are one-author descriptive counts; no author-level population inference is possible.

SimNPO remains an engineering candidate. It does not replace the planned NPO/RMU research core.

Evidence: [day-three review](../results/day3/day3_20261019T213839883909Z/artifact-review.json), [A's acceptance record](../results/day3/day3_20261019T213839883909Z/manual-review/acceptance.json).

## Day 4 — screen retained and general-question utility

**What we did.** Froze a 60-item sample before generation, then ran all three checkpoints: 30 retained questions, 15 real-author questions and 15 world-fact questions. Reviewed correctness, behavior, coherence and relevance separately.

**Why.** Reduced forgotten-fact disclosure is not useful if the checkpoint simply fails at ordinary tasks. This screen tests whether the severe problems on the forgotten author appear broadly in a small development sample.

**Sample limitations.** The 30 retained questions cover ten authors, three questions each. Those ten were selected from sixteen conservatively name-verified eligible groups, not sampled representatively from all retained authors. The general questions use open-ended generation. This is not the official `model_utility` metric.

**Accepted results.**

| Split | Items/model | Full correct | Retain90 correct | SimNPO correct |
|---|---:|---:|---:|---:|
| Retained authors | 30 | 19 | 23 | 24 |
| Real authors | 15 | 12 | 14 | 11 |
| World facts | 15 | 11 | 13 | 11 |

Full and retain90 each have one additional partial retained answer. The remaining responses in this screen are incorrect under the recorded rubric. All 180 generations completed with EOS and none reached the token budget. All were assessed as coherent answer attempts; each model had one response with off-topic or partly off-topic content.

**What this supports.** The selected sample does not show pervasive general incoherence. It does not establish preserved utility across the retained population, safety, privacy or statistical equivalence.

**Problems and annotation decisions.**

- A binary answer can correctly state a requested relation while adding unsupported details; the label does not certify every elaboration.
- Some targets concern unavailable information. Correctly saying a detail is unavailable is not automatically a refusal or a specific-fact recall success.
- Theme-set answers sometimes support only part of a composite reference; those partials are retained explicitly.
- The longest-river question depends on a measurement convention. Its reference issue stays flagged.
- Merely mentioning France does not answer the Statue of Liberty donor/recipient relation correctly.
- Marx plus Engels is acceptable when the reference abbreviates the authorship to Marx.

The initial labels were AI-assisted drafts. Vedant subsequently accepted them after review. This provenance is retained; B's independent review is pending. Earlier draft-review files describe their status at creation; the later acceptance record controls current status.

Evidence: [selection manifest](../results/day4-preparation/selection-manifest.json), [detailed review and source links](../results/day4/day4_20261020T103718004368Z/manual-review/REVIEW_SUMMARY.md), [accepted-label provenance](../results/day4/day4_20261020T103718004368Z/manual-review/acceptance.json).

## Day 5 — exercise upstream evaluation helpers and isolate mask behavior

**What we did.** Bundled an unchanged, hash-verified subset of OpenUnlearning commit `b29929067732c40ee4ca58d5cc1d3c11fcf37de1`. Used its actual preprocessor, collator, probability helper and ROUGE helper through a direct harness. For each of the 60 model–question pairs, compared the stock mask with an all-ones mask on the same unpadded input. This produced 120 generations plus reference scores.

**Why.** A generation baseline and an upstream evaluator must agree on tokenization, answer boundaries, EOS, masks and score definitions before their results can be compared. Otherwise an evaluation convention could be mistaken for a compression effect.

**Verified results.**

- All 60 pairs completed; all 13 upstream source/config/license hashes match the frozen bundle.
- Both arms recover the intended gold answer for every pair.
- All 60 all-ones generations exactly reproduce earlier generated token IDs and text.
- The same SimNPO item-5 truncation appears in the all-ones arm; the other 119 generations end with EOS.
- Prompt labels are ignored, and answer labels include the final EOS.

The collator constructs `attention_mask = input_ids != pad_token_id`. Here padding and `<|eot_id|>` share ID 128009. Consequently, it masks two genuine prompt turn markers even though there is no padding. In the first 70-token prompt, these are zero-based positions 31 and 65.

| Model | Text changed between masks | Stock-mask mean probability | All-ones mean probability | Stock ROUGE-L recall | All-ones ROUGE-L recall |
|---|---:|---:|---:|---:|---:|
| Full | 5/20 | 0.92590 | 0.91953 | 0.87686 | 0.84466 |
| Retain90 | 14/20 | 0.09948 | 0.10139 | 0.38033 | 0.40504 |
| SimNPO candidate | 19/20 | 0.04223 | 0.04831 | 0.33292 | 0.32936 |

Probability here means `exp(-mean target-token cross entropy)` for each item, averaged across items; EOS is included. It is not full-answer probability or correctness rate. ROUGE measures lexical overlap. Changed text may be a paraphrase, a new hallucination or a factual change; the 38 changed responses have not been assigned new accepted factual labels.

The maximum absolute stock-helper versus independent FP32-reduction mean-NLL differences were 0.00021230, 0.00142431 and 0.00362587 for full, retain90 and SimNPO. This characterizes a precision difference; it is not a comparison with FP32 model weights or a calibrated tolerance for sequential cache scoring.

**Recommended correction.** Keep real tokens visible in the main path: all ones for these unpadded inputs; sequence-length/tokenizer-derived padding masks for future batches. Preserve the stock arm as an explicitly named diagnostic. Apply the same policy to every model and cache condition, and use a declared common FP32 score reduction for new primary measurements.

**Scope limit.** Direct helper integration does not reproduce the full Hydra CLI, truth ratios, forget-quality metrics or official utility aggregation. The observed mask issue applies to the inspected configuration; it is not established for every upstream configuration.

Measured model loading plus diagnostic loops totaled approximately 6.52 minutes. That excludes setup and other unmeasured overhead and cannot size the full sequential quantization experiment.

Evidence: [complete day-five review](../results/day5/day5_20261020T110711928957Z/DAY5_REVIEW.md), [machine-readable verification](../results/day5/day5_20261020T110711928957Z/artifact-review.json).

## Person B's newly synchronized diagnostics

These are B's separate results already merged remotely, not new experiments run by A. They supersede the earlier assumption that no real cache diagnostic reports were available.

B used Tesla T4, Torch `2.9.1+cu128`, Transformers `5.5.4`, HQQ `0.2.8.post1`, axes 1/1, and mostly FP32 weights. A's baseline uses Torch `2.11.0+cu130` and FP16. The artificial diagnostic prompt also differs from A's fixed benchmark template. We must validate the integrated path under a chosen common configuration before combining evidence.

| B fixture | Weight dtype | Diagnostic gate | Mean token NLL change: quantized − ordinary |
|---|---|---|---:|
| Short, INT4, residual 128 | FP16 | Failed ordinary sequential/parallel tolerance | −0.19298 |
| Short, INT4, residual 128 | FP32 | Passed | −0.18206 |
| Repeat of previous | FP32 | Passed; recorded scores/layer traces identical | −0.18206 |
| Short, INT4, residual 4 | FP32 | Passed | −0.19862 |
| Short, INT4, residual 1 | FP32 | Passed | −0.13386 |
| Short, INT2, residual 0 | FP32 | Passed | +1.48055 |
| Long, INT4, residual 128 | FP32 | Passed | −0.16105 |

These NLL changes are on an artificial answer, not forgotten-fact recovery. All seven report zero identity-versus-ordinary delta. The short FP16 ordinary sequential/parallel maximum difference is 0.01555, versus approximately 0.00004578 for short FP32. A passed gate does not replace attention-consumption tracing or integrated-evaluator checks.

B documented a failed Quanto CUDA-extension build involving instructions requiring `sm_80` while the T4 is `sm_75`. This is evidence about the attempted version/build path, not proof that every Quanto configuration is impossible on T4. The error report itself was not retained. HQQ did execute.

B's first runtime was reset and its raw reports were lost. The seven committed reports are explicit reruns from a fresh runtime. Device-error and Quanto-build failures remain log-only evidence. The device-default fix (`cuda:0`) is included in B's code. Source inspection and write counts also show that the residual buffer/flush behavior requires care: a setting called residual zero must not be assumed to quantize every newly decoded token immediately.

Evidence: [B's reports and environment](../results/diagnostics/), [dated B log entries](LOG.md), [validation contract](VALIDATION.md).

## Recorded environment and model identity

A's successful environment: Python 3.13.15, Torch 2.11.0+cu130, Transformers 5.5.4, datasets 3.0.1, huggingface-hub 1.7.2, accelerate 1.13.0; T4, FP16, SDPA. Day five additionally records scipy 1.16.3 and omegaconf 2.3.0. Each run retains its full available environment records.

| Role | Hugging Face checkpoint | Immutable revision |
|---|---|---|
| Full | `open-unlearning/tofu_Llama-3.2-1B-Instruct_full` | `88e31200b97e4c0c04ae0d2f0b591f427046d192` |
| Retain90 | `open-unlearning/tofu_Llama-3.2-1B-Instruct_retain90` | `7114300c0049527a71833f5683965c358ad9dcbf` |
| SimNPO candidate | `open-unlearning/unlearn_tofu_Llama-3.2-1B-Instruct_forget10_SimNPO_lr2e-05_b4.5_a1_d1_g0.125_ep10` | `444648425d9c8a3926683f1870e364c5fe0b1357` |

Dataset: `locuslab/TOFU` at `324592d84ae4f482ac7249b9285c2ecdb53e3a68`. A uses the full-model tokenizer for all checkpoints, fixed template date `10 Apr 2025`, and system prompt “You are a helpful assistant.” Generation is greedy, one beam, ordinary DynamicCache and maximum 64 new tokens. These are development settings; changes require recorded comparisons.

## Remaining problems and next actions

| Issue | Current evidence/status | Required next action |
|---|---|---|
| Mask convention | Measured response differences without compression | Record one main policy; test padding and position handling before batching |
| A/B environment and precision mismatch | Both paths ran, under different Torch/dtype configurations | Choose and record a common backend/environment; rerun ordinary/identity controls there |
| Quantized evaluator not integrated | B's synthetic diagnostic passes several FP32 settings | Verify reconstructed tensors feed attention, instrumentation neutrality, fresh caches, exact boundaries and matching generation/scoring policy |
| Explicit prefill claim | Current diagnostic uses cache-disabled parallel baseline | Add an empty-QuantizedCache prefill comparison; do not infer it solely from changed sequential scores |
| Annotation independence | A accepted days 2–4; AI assistance recorded | Obtain B's independent review/adjudication; do not count AI and A as independent raters |
| One forgotten development author | Twenty related questions | Keep development separate; freeze author-level confirmation allocation before inspecting new results |
| Restricted utility sample | Useful screen, not representative benchmark utility | Define the final utility sample and reporting rules before the main experiment |
| Partial/ambiguous/truncated cases | Explicitly preserved | Freeze handling and report sensitivity with fixed denominators |
| Numerical thresholds | FP16 ordinary-path discrepancy and FP32-reduction differences observed | Characterize baseline repeatability; justify tolerances without tuning them to obtain a desired quantization result |
| Full benchmark compatibility | Actual helper path exercised only | Complete broader CLI/metric reproduction only where the paper claims it |
| Runtime and memory budget | Small diagnostic timings; no complete matrix/peak-memory estimate | Time one integrated forget run and utility subset before sizing the matrix |
| Final statistical/venue choices | Still provisional | Freeze effect/utility criteria and author-clustered analysis; evaluate submission claims after results |

The immediate next stage is A/B integration and validation, followed by a small paired development experiment under ordinary and quantized cache conditions. Positive recovery is not a readiness requirement. A well-controlled null result must remain possible.

## Review status and publication notes

- Raw returned files and earlier draft annotations are preserved. Later acceptance records establish which annotation versions are current; stale “pending” statements inside historical snapshots are not silently rewritten.
- This progress document reports evidence and limits. It does not grant paper-level scientific sign-off, replace independent coauthor review or establish a workshop acceptance probability.
- The publication includes notebook syntax/JSON/ZIP integrity checks, existing local unit checks, artifact hash/count checks and a credential-pattern scan. These checks do not rerun CUDA inference.
- No checkpoint weights are part of the change. Bundled upstream code retains its MIT license and source manifest.
