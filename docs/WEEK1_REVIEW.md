# Week 1 review: build a trustworthy research starting point

Prepared 21 October 2026. Person A: Vedant. Seven workflow stages were completed across 19-21 October. Code preparation, artifact checking and initial annotation drafts were assisted by Codex; A has verified and accepted the day-seven annotations. Independent B review and joint scientific decisions remain open.

**Current status:** Person A's setup and reviewed development-baseline phase is complete. Joint week-one sign-off remains open where independent review or shared scientific decisions are required.

## The overall goal

**Goal:** build a reproducible way to study whether stored KV-cache quantization changes factual disclosure from an already-unlearned language model.

The KV cache is temporary attention memory reused while generating later tokens. Here quantization compresses that stored memory while the model's weights stay fixed within a comparison.

**Why it mattered:** a changed answer could come from a different checkpoint, prompt, mask, numerical precision, broken cache path or scoring error. We first needed to measure and control those factors.

**How we approached it:** establish the GPU setup, compare full/retain/unlearned checkpoints, review factual answers, check utility, integrate upstream evaluation code, validate real quantized cache use, then repeat the baseline in a shared environment.

**Final week-one output:** a reviewed ordinary-cache development baseline, fixed inputs and annotations, verified cache-path evidence for the tested configuration, measured baseline cost, and a concrete next development experiment. We have not yet measured quantization-induced forgotten-fact recovery.

## 1. Get the model running on the intended hardware

**Goal:** produce one traceable answer on a Tesla T4.

**Why it mattered:** a connected notebook kernel alone does not establish that the intended model, tokenizer and GPU work together.

**How we achieved it:** used Colab, recorded environment and immutable revisions, rendered a real TOFU prompt, and saved tokens, generation settings and output.

**Result:** the full model correctly returned Hsiao Yun-Hwa's name. The prompt had 70 tokens; the response had 14 tokens including EOS and took 3.742 seconds. Package conflicts and restart requirements were recorded. Later notebooks corrected the distinction between base-model defaults and the effective generation configuration.

## 2. Establish full-model and retain-only reference behavior

**Goal:** understand what the full and retain90 checkpoints answer on the same 20 forgotten-author development questions.

**Why it mattered:** the retain-only model can answer some questions without having trained on that author. We must measure that reference behavior instead of assuming it is zero.

**How we achieved it:** fixed prompts, tokenizer and greedy settings; saved 40 outputs; reviewed requested facts, behavior, reference quality and prompt-supplied information.

**Result:** the initial full/retain correct counts were 16/20 and 3/20. Exact string matching would have reported only 13/20 and 0/20. Semantic review was therefore necessary. Ambiguous and partial cases remained explicit rather than being silently removed.

## 3. Add the selected unlearned engineering candidate

**Goal:** establish an ordinary-cache unlearned baseline before compression.

**Why it mattered:** later cache effects need to be compared with that same checkpoint's ordinary behavior. Checkpoints must not be selected because compression later gives a desirable result.

**How we achieved it:** used the previously recorded SimNPO checkpoint on the identical 20 questions and reviewed it with the same rubric.

**Result:** SimNPO had 2 correct, 2 partial, 15 incorrect and 1 ambiguous answer. One response reached the common 64-token budget and was retained. These observations concern one exposed author, not the entire method. SimNPO remains an engineering candidate; NPO/RMU remain the planned paper core.

## 4. Check whether the model still answers useful questions

**Goal:** screen retained/general performance rather than judging the model only from forgotten-author answers.

**Why it mattered:** low forgotten-fact disclosure is uninformative if the model broadly fails at ordinary tasks.

**How we achieved it:** froze a 60-item/model sample before generation: 30 retained questions from ten authors, 15 real-author questions and 15 world-fact questions. Reviewed 180 outputs for correctness, behavior, coherence and relevance.

**Result:** the selected sample did not show pervasive general incoherence. The current accepted counts remain:

| Utility split | Items/model | Full correct | Retain90 correct | SimNPO correct |
|---|---:|---:|---:|---:|
| Retained authors | 30 | 19 | 23 | 24 |
| Real authors | 15 | 12 | 14 | 11 |
| World facts | 15 | 11 | 13 | 11 |

Full and retain90 each have one additional partial retained answer. This restricted screen is not the official `model_utility` metric or a representative estimate of all retained knowledge.

## 5. Find and control the attention-mask problem

**Goal:** check that upstream evaluation helpers receive the intended tokens and scoring targets.

**Why it mattered:** an evaluation convention could change answers before any compression and then be mistaken for a quantization effect.

**How we achieved it:** ran pinned upstream preprocessing, collation, probability and ROUGE helpers on the same exposed questions. Compared the stock mask with an all-ones mask on unpadded inputs.

**Result:** the padding ID equals the real end-of-turn ID, so the collator masks two genuine prompt markers. Changing only the mask changed full/retain90/SimNPO text on 5/20, 14/20 and 19/20 questions. All 60 all-ones generations exactly reproduced earlier text and tokens. New integration uses explicit valid-token masks. Changed text alone is not recovered knowledge.

## 6. Verify that the quantized cache is actually used

**Goal:** confirm stored quantization, reconstructed values, attention consumption and consistent scoring/generation.

**Why it mattered:** unchanged scores can hide an inactive or unobserved intervention; changed scores alone do not prove the intended cache path.

**How we achieved it:** combined B's HQQ diagnostics with the day-six T4 run. Compared ordinary parallel/sequential scoring, an identity cache, instrumented/plain INT4 and INT2 caches, empty-cache prefill, one-token fixtures, fresh-cache repeats and native generation replay. Traced cache-returned tensors into SDPA.

**Result:** all 28 day-six checks passed in the tested FP32/HQQ, unpadded batch-one configuration. All 16 layers showed reconstructed K/V reaching attention. Identity, instrumentation and empty-cache parallel comparisons had zero score differences; the largest ordinary parallel/sequential gap was 0.00003052 NLL per token.

| Artificial fixture | Cache | Mean sequential NLL change | Largest absolute token change |
|---|---|---:|---:|
| Short | INT4 | -0.41685 | 1.10800 |
| Short | INT2 | -0.01325 | 2.51839 |
| Long | INT4 | -0.10546 | 0.99159 |
| Long | INT2 | +0.33273 | 3.10312 |

The empty-cache parallel scores were unchanged, while later sequential scores changed. This demonstrates the scoped evaluation-path mechanism on artificial prompts. It does not establish factual recovery, universal cache behavior or literature novelty. Three repeat checks archived only derived deltas; that evidential limit is recorded.

## 7. Build and accept the shared-environment TOFU baseline

**Goal:** move the real development questions into the numerical environment that passed cache validation.

**Why it mattered:** earlier baseline runs used Torch 2.11/FP16, whereas the validated path uses Torch 2.9.1/FP32. A quantized comparison needs a matching ordinary reference.

**How we achieved it:** ran the same 80 questions across full, retain90 and SimNPO, producing 240 schema-v2 records. Scored the 20 forget answers per model in parallel and sequentially, including EOS. Compared new outputs with previous text/tokens and reviewed the five changes. A explicitly accepted the full annotation review.

**Result:** all 240 records completed without errors; all 60 ordinary score comparisons passed. 235 outputs match earlier text and tokens. The full model changed an award answer, reducing its fully correct forget count from 16 to 15. Current A-accepted counts are:

| Forget label, all 20 items retained | Full | Retain90 | SimNPO |
|---|---:|---:|---:|
| Correct | 15 | 3 | 2 |
| Partial | 1 | 3 | 2 |
| Incorrect | 3 | 13 | 15 |
| Ambiguous | 1 | 1 | 1 |

The borderline SimNPO philosophy partial was accepted as proposed. Reference issues and unsupported elaborations remain documented. One unchanged SimNPO response is truncated. The batch took 356.29 seconds (about 5.94 minutes) and reported 4.69 GiB peak allocated memory per model, loaded sequentially. Those costs describe ordinary inference, not quantized deployment performance.

## What Person B contributed and what we learned from problems

| Problem / contribution | Why it mattered | Outcome |
|---|---|---|
| B's INT4/INT2, long/short and residual-policy diagnostics | Established real cache writes/reads and implementation behavior | HQQ ran on T4; supporting reports are preserved |
| Quanto extension build failed on the attempted T4 path | Backend support cannot be assumed from a dependency list | Use the tested HQQ path for the next limited integration run |
| FP16 ordinary-path tolerance failure | Numerical baseline error could be mistaken for cache effects | FP32 reduced the fixture discrepancy; the new baseline uses the validated environment |
| Source mask/EOS collision | Changes outputs without compression | Explicit valid-token masks; preserve stock comparator separately |
| Ambiguous/non-exhaustive references and generic targets | String overlap is insufficient for factual disclosure | Accepted semantic rubric; retain partial/ambiguous/reference flags |
| Original B runtime reset lost reports | Temporary runtimes are not durable archives | Committed files are explicit reruns; preserve downloads and failure provenance |
| Multiple setup changes between early and current runs | Output drift cannot be attributed to precision alone | Current ordinary baseline is authoritative for the next paired comparison |

## Week-one completion and remaining joint work

| Deliverable | Current status |
|---|---|
| Person A's GPU setup, provenance, baseline runs and review | Completed for the selected development scope |
| A's day-seven annotation verification | Accepted; AI assistance and carry-forward origins preserved |
| Utility screen and baseline feasibility measurements | Completed for the fixed restricted sample |
| Cache/scoring integration | Passed the programmed tested-scope checks; broader coverage limits documented |
| Independent B review of A's labels and shared evidence | Still pending; script success is not a substitute |
| Final checkpoint/confirmation allocation and effect/utility/numerical policy | Joint decisions remain open |
| Main quantized disclosure/utility experiment and paper findings | Not yet completed |

We can close Person A's first-week setup/baseline phase and start the next development task. We cannot declare every joint week-one sign-off or the research pipeline universally complete.

## Measurement and data handoff

- **Primary planned comparison:** correct forgotten-fact disclosure under INT4 minus ordinary cache on a fixed question population. Report all raw label categories and both directions of answer changes.
- **References:** run full and retain90 under the same cache conditions. Report the unlearned change and retain-reference change separately; their difference is secondary and can be misleading if the reference deteriorates.
- **Scores:** preserve parallel/sequential reference log-probability sums, target counts and EOS conventions. Predictive scores and ROUGE are secondary evidence, not direct knowledge measurements.
- **Development allocation:** the 20 Hsiao Yun-Hwa questions are exposed development data. The existing utility sample is exposed too. The remaining forget authors are not assigned to confirmation by this review; audit exposure and jointly freeze that allocation first.
- **Statistics:** future uncertainty must preserve author clusters and model/condition pairing. One forgotten author cannot support a population confidence interval. Multiple checkpoints/hyperparameters are not independent training seeds.
- **Open policy:** practical effect size, acceptable utility deterioration, final tolerances, annotation independence and multiplicity handling remain to be justified jointly. This review does not invent them.

## The next executable step

The [next development notebook](../notebooks/person_a_week2_int4_development.ipynb) and [input ZIP](../results/int4-development-preparation/int4-development-input-bundle.zip) prepare a same-run ordinary/INT4 comparison on the existing 80 questions across the three existing checkpoints. Both cache conditions use the same loaded FP32 model, masks, token IDs, generation settings and scoring conventions. Ordinary responses are regenerated within that run, so both sides have current paired controls.

The notebook contains an initial traced probe for each model, then saves both conditions incrementally. This is limited development evidence; NPO/RMU research scope and final confirmation choices are unchanged. Return the output ZIP for artifact checking and proposed paired factual review. Positive recovery is not required. No numerical or factual result from this next notebook is claimed here because it has not yet run on the GPU.

## Where to inspect the evidence

- Setup and earlier reviews: `results/day1/` through `results/day6/`; B's reports: `results/diagnostics/`.
- Current baseline: `results/day7/day7_20261021T101236202224Z/`.
- Authoritative current labels: `manual-review/day7-annotation-A-accepted.csv` and `manual-review/acceptance.json` inside that run.
- Method and open gates: `docs/BLUEPRINT.md`, `docs/VALIDATION.md`, `docs/PILOT_CRITERIA.md`.
- Practical next-stage instructions: `results/int4-development-preparation/README.md`.

The original raw files, proposed reviews and earlier status snapshots are preserved. Acceptance records establish current annotation status; they do not imply independent second review or joint scientific sign-off.
