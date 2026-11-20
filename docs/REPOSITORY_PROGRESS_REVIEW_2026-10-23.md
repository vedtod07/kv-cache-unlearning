# Repository progress and methodology review

Prepared 23 October 2026 for Vedant (Person A) and Person B. Codex-assisted review of the fetched GitHub snapshot and the additional local research artifacts. This report reviews recorded evidence and runs local tests; it does not rerun GPU inference or certify publication novelty.

**Verdict:** the project has a working T4 cache-validation path, reviewed ordinary-cache baselines, cross-person prompt parity and an actual full-model ordinary/INT4 timing run. It is ready for a controlled development integration experiment. The main claim about the durability of weight-based unlearning under cache compression is still unanswered.

## 1. Repository structure and how to read it

The repository is organized around a measurement study: code produces outputs, immutable run artifacts preserve what happened, annotations assess factual content, and documents define what claims those outputs support.

| Location | Purpose and current contents |
|---|---|
| README.md | Project entry point; remote copy still describes the older five-day status |
| docs/ | Blueprint, work split, validation contract, decisions, pilot criteria, logs and explanatory reviews |
| notebooks/ | A's T4 workflows; days 1-5 are remote, days 6-7 and the next INT4 notebook are local additions |
| scripts/ | Cache diagnostics, shared prompt helper, parity checks, timing, blind-sheet preparation and structural validator |
| tests/ | Regression checks for gates, prompt comparison, review-sheet construction and records; local additions exercise scoring/cache helpers on a tiny CPU model |
| results/day1/ through day5/ | Remote ordinary baselines, accepted annotations, utility screen and source-helper integration |
| results/diagnostics/ | B's seven earlier HQQ diagnostic reports, environment freeze and hardware evidence |
| results/diagnostics-v2/ | New fixed-template/EOT-inclusive diagnostics and 20-item prompt-parity report |
| results/timing/ | New full-checkpoint 80-item ordinary/INT4 cost report |
| results/day6/, results/day7/ | Local A cache-integration evidence and shared-environment baseline with accepted annotations |
| results/int4-development-preparation/ | Local prepared input bundle for the three-checkpoint paired development run |
| output/pdf/ | Shareable review PDFs; these reports explain evidence rather than replacing raw records |

## 2. Exactly which repository versions were reviewed

**Reading order:** start with this review, then the blueprint and results contract. Inspect a run's manifest, raw outputs, artifact review and annotation acceptance together. A filename containing "review" or a script exiting successfully does not itself establish factual correctness or scientific approval.

**Remote reviewed:** origin/master at cf5c7f306ccf334e598394b98e57046fd533f7f3, fetched on 23 October 2026. **Local checked-out base:** da45630403bbcdd49123560f8467f809cb41992c, with substantial uncommitted A work. The updated remote was extracted into an isolated snapshot; no merge, reset, commit or push was performed during this review.

| New history since the local base | Contribution |
|---|---|
| PR #2; merge 054941e | Diagnostic v2, shared prompt helper, prompt parity and saved T4 reports |
| PR #4; merge 0d5f765 | Timing script/report and tool for preparing blind annotation sheets |
| PR #3; merge cf5c7f3 | Recorded common conventions and clearly separated A's remaining proposals |

There are eight new commits including these merges. The remote diff affects 16 files, with 9,444 insertions and 18 deletions; most added lines are recorded JSON evidence, not new algorithmic complexity.

**Important distinction:** the remote does not yet contain A's day-six/day-seven runs, their notebooks, the accepted day-seven CSV, or the local paired INT4 preparation. They exist in this workspace and are included in this report as explicitly local evidence. A collaborator cloning the current remote will not receive those files.

**What was checked:** all changed source/test files, the four new diagnostic/parity reports, the 160 timing records, recorded decisions, and their relationship to earlier A/B artifacts. Earlier day-one through day-seven findings were traced through existing reports and acceptance records. This is not a new blind re-annotation of every historical answer or a fresh download of every model/dataset.

**Review artifacts:** results/repository-review-20261023/artifact-audit.json records recomputed statistics and SHA256 hashes of the five new report files. The current document provides the readable interpretation.

## 3. Research question, purpose and measurement logic

**Goal:** determine whether compression of stored KV attention memory changes the factual information disclosed by a model whose weights have already undergone unlearning, and whether the evaluation method detects those changes.

**Why it matters:** deployment can change inference arithmetic without changing the weights. A weight-unlearning result measured under ordinary inference may not describe a compressed-cache deployment. An evaluator can also fail to exercise the cache readback path it claims to audit.

**How the study should work:** select checkpoints using ordinary-cache compatibility, forgetting and utility; freeze prompts and question populations; run ordinary and compressed caches on the same questions; review generated facts; compare paired disclosure and utility changes; preserve full and retain-only references under both conditions.

| Term | Meaning in this project |
|---|---|
| Full | Model fine-tuned on the full TOFU training population |
| Retain90 | Reference checkpoint trained without the forget10 portion; not a literal deletion of weights from full |
| Unlearned | A checkpoint produced by a weight-unlearning procedure; SimNPO currently serves engineering work |
| KV quantization | Compression of stored K/V tensors; FP32 model weights stay fixed within the current cache comparison |
| Parallel score | Fixed-reference probabilities from one full forward pass |
| Sequential score | Fixed-reference probabilities evaluated token by token while reading the accumulated cache |
| Disclosure | Whether the generated response supplies the requested reference-supported fact, even inside a refusal |

**Primary planned outcome:** change in correct forgotten-fact disclosure under INT4 versus ordinary cache for the same checkpoint and fixed item population. Report partial/ambiguous labels and transitions separately. Log-probabilities and ROUGE support diagnosis; they are not factual-disclosure percentages.

**Current scientific boundary:** engineering effects are established in the tested configurations. Quantized forgotten-fact recovery in an unlearned checkpoint has not yet been measured and reviewed in the available artifacts. Neither acceptance probability nor novelty can be established by this repository audit.

## 4. Days one to three: ordinary-cache baseline behaviour

**Goal:** establish a traceable GPU setup and determine how full, retain90 and one selected unlearned checkpoint answer the same forgotten-author questions before cache compression.

**Why it mattered:** without meaningful full-model recall, an unlearned baseline and a measured retain-only reference, later changes are hard to interpret. Retain-only answers cannot be assumed to be zero.

**How it was achieved:** A used Colab/T4, pinned model/data revisions, saved rendered prompts and tokens, ran the same 20 Hsiao Yun-Hwa development questions, and reviewed semantic correctness separately from behaviour. The initial annotation drafts were AI-assisted and subsequently accepted by A; independent B review remains outstanding.

| Initial ordinary-cache labels | Full | Retain90 | SimNPO |
|---|---|---|---|
| Correct | 16 | 3 | 2 |
| Partial | 1 | 3 | 2 |
| Incorrect | 2 | 13 | 15 |
| Ambiguous | 1 | 1 | 1 |

The first fullname demonstration used a 70-token prompt, generated 14 tokens including EOS, and took 3.742 seconds. It correctly returned Hsiao Yun-Hwa's name. SimNPO had one 64-token truncated response, which was preserved rather than silently extended or discarded.

**Result:** ordinary generation shows strong full-model disclosure and lower disclosure in the selected unlearned candidate on this exposed author. Exact-string matching would have understated the earlier full/retain correct counts as 13/20 and 0/20; semantic assessment was necessary.

**Limit:** these 20 questions concern one author and are development data. They cannot estimate average forgetting across all authors. SimNPO is a preselected engineering candidate, not a claim about every SimNPO run. NPO/RMU remain the planned paper core, with exact checkpoint selection still open. Later day-seven FP32 results supersede the initial full count for the next paired comparison.

## 5. Day four: utility screen and the unexpected ranking

**Goal:** determine whether the candidate model still gives useful retained/general answers rather than appearing to forget only because it broadly fails.

**How:** freeze 60 questions per model before generation: 30 retained questions from ten authors, 15 real-author questions and 15 world-fact questions. Review all 180 responses for correctness, behaviour, coherence and relevance.

| Utility population | Items/model | Full correct | Retain90 correct | SimNPO correct |
|---|---|---|---|---|
| Retained authors | 30 | 19 | 23 | 24 |
| Real authors | 15 | 12 | 14 | 11 |
| World facts | 15 | 11 | 13 | 11 |

Full and retain90 each have one additional partial retained answer. All 180 responses were linguistically coherent under the recorded rubric; readable prose can still contain false facts.

**Why retain90 or SimNPO can exceed full:** full is not an accuracy upper bound. Different training updates can change generated answers in either direction. This run does not identify the causal training mechanism. SimNPO exceeds full only on retained questions, falls below it on real authors, and ties on world facts.

The saved full-to-SimNPO retained transitions are 19 correct-to-correct, four incorrect-to-correct, one partial-to-correct and six incorrect-to-incorrect. Those five improvements deserve independent review; they are not five independent author-level replications.

**Selection limit:** the retained sample was drawn from 16 conservatively name-verified eligible groups, not all 180 retained authors. Questions explicitly name the author. The sample includes binary relations and information-unavailable targets. Selection used no generated outputs, but restricted eligibility still limits representativeness.

**Result:** the screen argues against pervasive incoherence on these selected items. It does not establish general utility superiority, official model_utility performance, or statistically demonstrated utility preservation. Broader predefined author coverage and independent review are needed.

## 6. Day five: an evaluation-mask confound was found

**Goal:** integrate pinned OpenUnlearning source helpers and verify what their preprocessing, probability and ROUGE paths actually measure.

**Why it mattered:** a scoring convention can change answers before quantization occurs. Such differences could be wrongly attributed to compression.

**How:** compare the stock collator mask against explicit all-ones masks on the same unpadded inputs. Run full, retain90 and SimNPO on the existing 20 development questions. Preserve source hashes and the upstream license.

| Observed comparison | Full | Retain90 | SimNPO |
|---|---|---|---|
| Responses whose text changed with the mask | 5/20 | 14/20 | 19/20 |
| Mean reference probability, stock mask | 0.925903 | 0.099480 | 0.042225 |
| Mean reference probability, all-ones mask | 0.919531 | 0.101390 | 0.048312 |

The stock collator derives the mask from input_ids != pad_id. Here pad_id equals the genuine end-of-turn ID, masking two real prompt markers. With all-ones masks, all 60 generations exactly matched the earlier text and generated token IDs.

The reported reference "probability" is exp(-mean target-token loss), including the scored ending token. It is a geometric-mean token probability, not the entire answer's probability or a correctness rate. FP32 reduction was also checked against the stock numerical path.

**Result and policy:** use explicit valid-token masks. All ones are appropriate for the current unpadded batch-one path. Padded batches require lengths/padding metadata plus additional validation. Preserve the stock helper results as a separate diagnostic.

**Limit:** this was source-helper integration, not a complete reproduction of the upstream Hydra evaluation suite. No quantized cache ran on day five. The observed changed text is a mask effect, not evidence of recovered forgotten facts.

## 7. Day six: real quantized caches and attention-path validation

**Goal:** prove that the intended compressed cache is stored, reconstructed and consumed during inference, and that scoring and generation follow that path.

**How:** run the full checkpoint on artificial weather prompts with 50 and 330 prompt tokens. Score the same nine reference tokens including end-of-turn. Compare ordinary, identity, INT4 and INT2 caches with FP32 weights, HQQ axes 1/1, group64 and residual128. Use instrumented/plain comparisons and generation replay.

**Result:** all 28 programmed checks passed. Every one of 16 layers showed quantized K/V storage and reconstructed prefixes reaching the SDPA attention interface. The largest ordinary parallel/sequential token-NLL gap was 0.00003052. Identity, instrumentation and empty-cache parallel comparisons had zero score differences.

| Fixture | Cache | Mean sequential NLL change | Largest absolute token change |
|---|---|---|---|
| Short | INT4 | -0.41685 | 1.10800 |
| Short | INT2 | -0.01325 | 2.51839 |
| Long | INT4 | -0.10546 | 0.99159 |
| Long | INT2 | +0.33273 | 3.10312 |

**How to read NLL:** each target token receives loss -ln(probability assigned to that reference token). Mean sequential NLL averages those losses over the answer tokens, including EOT. The table reports quantized minus ordinary mean NLL. Negative means the fixed reference became more probable on average; positive means less probable. It is not an average of repeated experiments or a correctness percentage. Token changes can cancel in the mean.

**Mechanism:** initial prefill stores quantized prompt K/V but returns the original K/V for that pass. Later sequential steps read reconstructed stored K/V. This explains unchanged initial/empty-cache parallel scores alongside changed later scores. Native weather generation also changed and matched replay under the corresponding cache policy.

**Limits:** full model only; artificial prompts; batch one; one residual setting. The trace reaches the attention interface, not CUDA-kernel internals. Three repeat checks saved only derived deltas rather than raw repeat vectors. This is local evidence, not yet on the reviewed remote.

## 8. Day seven: authoritative shared-environment baseline

**Goal:** regenerate the actual development questions under the FP32 environment that passed cache validation, so later cache pairs have a compatible ordinary reference.

**How:** run full, retain90 and SimNPO sequentially on the same 80 questions each: 20 forget and 60 utility. Use Torch 2.9.1+cu128, Transformers 5.5.4, explicit masks, the fixed template, greedy 64-token generation and EOT-inclusive scoring.

**Result:** 240/240 records completed without errors and all 60 ordinary parallel/sequential comparisons passed. 235 outputs matched earlier text and tokens. The full model changed an award answer, reducing its fully correct forget count from 16 to 15. A accepted the proposed annotation review, with AI assistance and carry-forward provenance preserved.

| Current A-accepted forget labels | Full | Retain90 | SimNPO |
|---|---|---|---|
| Correct | 15 | 3 | 2 |
| Partial | 1 | 3 | 2 |
| Incorrect | 3 | 13 | 15 |
| Ambiguous | 1 | 1 | 1 |

Utility counts remain those in section 5. One unchanged SimNPO forget answer remains truncated. A borderline partial philosophy answer was explicitly accepted. Unsupported elaborations and reference-quality flags were retained.

The entire batch took 356.29 seconds, approximately 5.94 minutes, and reported about 4.69 GiB peak allocated GPU memory per model, with models loaded one at a time. It did not use quantized caches. Ordinary-path maximum token gaps were approximately 0.00002754 for full, 0.00008869 for retain90 and 0.00067520 for SimNPO under the inherited provisional gate.

**Why important now:** B's new timing run independently reproduces all 80 full-model generated token sequences from this baseline; its 20 ordinary forget-reference NLL sums also match exactly. This is strong cross-path consistency evidence on these items, not a substitute for independent factual annotation or broader statistical replication.

**Limit:** day seven and its accepted CSV are local additions. They must be incorporated through the agreed review process before the remote can serve as the complete shared baseline archive.

## 9. New B diagnostics: prompt parity and real TOFU fixtures

**Goal:** make B's evaluation inputs identical to A's and extend cache checks beyond the artificial example.

**How:** scripts/tofu_prompts.py centralizes the system message, fixed date, chat-template hash and in-context EOT-inclusive answer tokenization. scripts/check_prompt_parity.py compares its outputs with A's day-two prompts and day-five scoring traces.

**Result:** 20/20 development items matched prompt text, prompt tokens and reference-token conventions; zero mismatches were reported, and the template hash matched. This removes a substantial cross-person confound. It establishes parity on the tested forget fixtures, not every future tokenizer or dataset.

| Diagnostic v2 fixture | Prompt / answer tokens | Mean NLL change | Max absolute token change |
|---|---|---|---|
| Artificial weather | 50 / 9 | -0.416851 | 1.108000 |
| TOFU item 0 | 70 / 14 | -0.009691 | 0.077350 |
| TOFU item 18 | 58 / 48 | +0.009470 | 0.272136 |

All three reports pass recomputed gate checks. Ordinary sequential/parallel maximum gaps range from 0.00000873 to 0.00003052. Identity and instrumentation-neutrality deltas are zero. Saved empty-cache prefill maximum logit differences are zero. First-answer-token deltas are zero. All 16 layers have read counts matching answer_tokens minus one per K/V tensor.

**Review distinction:** the raw NLL vectors allow gate arithmetic and neutrality to be recomputed. Full prefill logits and K/V tensors are not saved, so their reported maximum/trace assertions cannot be reconstructed solely from the JSON. A's separate day-six trace adds attention-interface evidence.

**Important correction:** v1 relied on a template that could insert the run date and used a different answer convention. V1 and v2 score deltas must not be pooled as repeated measurements of the same fixture. The v2 artificial result matches the corresponding local day-six INT4 score change under matching conventions.

These are full-model engineering fixtures. A changed TOFU reference score alone does not demonstrate factual recovery in an unlearned model.

## 10. New T4 timing: an actual ordinary/INT4 full-model run

**Goal:** measure cost before sizing the larger experiment. **How:** full checkpoint, FP32, HQQ INT4, residual128, group64, axes1/1; the same 80 development questions under both conditions. One generation warm-up per condition; fresh cache per operation; generation and sequential reference scoring timed separately with CUDA synchronization.

| Recomputed quantity | Ordinary | INT4 |
|---|---|---|
| Completed records | 80/80 | 80/80 |
| Mean generation seconds/item | 0.7124 | 1.0421 |
| Mean sequential scoring seconds/item | 0.5762 | 0.7993 |
| Mean combined seconds/item | 1.2886 | 1.8415 |
| Generated tokens/second, aggregate | 39.41 | 28.13 |
| Mean generated tokens/item | 28.075 | 29.313 |
| Peak allocated memory, MiB | 4762.79 | 4759.39 |
| EOS terminations | 80 | 79 |

**Result:** INT4 took 1.429 times the combined generation/scoring time and 1.463 times the generation time. Model/tokenizer load was 6.40 seconds in that run. The tiny roughly 3.39 MiB peak difference is insufficient evidence of meaningful memory savings; weights and short-context overhead dominate this setup. MiB is a binary unit: these peaks are about 4.65 GiB, not 4.76 decimal GB.

**Additional audit finding:** ordinary generations match local day-seven full outputs on 80/80 token sequences. Ordinary versus INT4 differs on 39/80 token sequences: nine forget, sixteen retained, six real-author and eight world-fact questions. This is response variation, not a correctness result. The single INT4 budget hit is retained item 631, without EOS.

The saved data contain real full-model quantized generations, although the report's declared purpose is timing. They are not yet schema-v2 annotated disclosure evidence. There is still no paired quantized retain90/SimNPO result in the reviewed artifacts.

**Projection and limits:** three comparable models at these measured costs would require about 751 seconds (12.52 minutes) of generation plus sequential scoring. This excludes downloads, setup, tracing, parallel controls, reviews and failures; the timing script scores utility references too, whereas A's prepared notebook scores only forget references. One fixed-order run cannot characterize runtime variance or general deployment speed.

## 11. Code quality, tests and implementation findings

**What is strong:** explicit immutable model revision, fresh cache construction, separated teacher-forced scoring and generation, FP32 log-softmax, paired token identities, gate failures independent of a desired quantization effect, source-backed cache semantics and preserved error states. New v2 checks add prefill invariance and instrumentation neutrality. The blind-sheet tool removes model identity and existing labels and preserves a separate mapping key.

**Tests run for this review:** all 21 tests in the fetched remote pass. A temporary combined snapshot containing the remote updates plus the local day-six/day-seven/INT4 helpers passes all 34 tests. These are CPU/regression results, including tiny random-model fixtures in the combined suite. They do not repeat CUDA/HQQ validation or demonstrate that a real merge is conflict-free.

| Finding | Consequence and recommended action |
|---|---|
| High: shared archive is incomplete | Remote lacks A's latest accepted baseline and preparation. Reconcile the local changes with remote through review before a shared full run. |
| High: core evaluator is unfinished | Timing JSON is engineering evidence, not schema-v2 item JSONL plus full manifests. Reuse verified helpers, add manifest/record validation and preserve raw timing provenance. |
| Medium: fragile timing persistence | Records are written only after run() returns. A runtime reset or fatal setup/warm-up failure can lose progress. Use append-only incremental records and explicit resume rules for larger runs. |
| Medium: incomplete timing provenance | Report omits full effective generation config, TF32 state, full dependency freeze/HQQ version and source hashes of inputs. Preserve these before pooling or making performance claims. |
| Medium: defaults differ from the selected path | Diagnostic CLI still defaults axes to 0/0 and dtype auto; tested reports explicitly use 1/1 and FP32. Use a frozen named config and reject unintended defaults. |
| Medium: review builder is preparation only | No independent labels are created. Preserve failure/exclusion counts, add duplicate/schema checks and rubric version, and retain answer-review provenance. |
| Medium: documentation lags evidence | Remote README/VALIDATION and checkpoint ledger still describe older pending stages. Update status using report IDs and tested scope, not blanket "validated" claims. |

The new helpers improve consistency, but production code should explicitly enforce the expected template hash and effective settings, not only record them after execution. Batch-one scope is defensible; padding/multiple-example support needs separate tests before expansion.

## 12. Annotation, statistics and review of every run

**Goal:** make factual conclusions depend on reviewed answers and an appropriate evaluation population, rather than text differences or repeated process execution.

Every contributing run needs provenance/configuration checks, record completeness, finite scores, expected token boundaries, applicable ordinary/identity controls, and failure/truncation accounting. Every response entering factual accuracy results needs assessment. Exact duplicates may inherit accepted labels only when question, reference, response and rubric match, with provenance recorded.

B's new scripts/build_review_sheets.py can shuffle responses and conceal model/condition names and prior labels. The source/key files must remain separate during first-pass labelling. The tool's existence is not evidence that independent review has happened. A single consolidated, versioned rubric is still needed before B's review of the current 240-answer baseline.

| Review policy | Required practice |
|---|---|
| Correctness versus behaviour | Preserve distinct labels; refusal-with-fact can disclose the fact |
| Partial/ambiguous cases | Keep explicit categories and fixed denominators; freeze inferential handling before confirmation |
| Disagreements | Preserve A and B labels, report pre-adjudication agreement, then save the final decision and rationale |
| Reference problems | Flag binary, unavailable, non-exhaustive and convention-sensitive targets consistently across conditions |
| Errors and truncation | Preserve them; failed inference is not a wrong answer, and a budget hit is not automatically a runtime error |

**Replication:** a few identical greedy reruns assess execution stability. They do not create independent training seeds. Broader predefined author coverage tests generality; independently trained/unlearned checkpoints test training variation; another compatible benchmark tests transfer beyond TOFU.

**Analysis:** pair cache conditions by item and checkpoint. Preserve author clusters when estimating uncertainty; do not treat 20 questions from one author as 20 independent authors. Report unlearned change and retain-reference change separately, with their difference secondary. Averages must state whether they weight questions, authors, checkpoints or datasets. Resampling does not repair unrepresentative selection.

No population confidence interval, utility-equivalence claim, multiplicity policy or practical effect threshold has yet been established by the available results.

## 13. Agreed conventions versus outstanding decisions

The remote DECISIONS.md now records conventions dated 22 October as agreed through A's merge. That is a meaningful improvement over scattered chat instructions. It also separates proposals from decisions. This review reports that recorded status without inferring broader sign-off.

| Recorded common convention | Current meaning |
|---|---|
| HQQ; FP32 validation | Use the working T4 path; do not loosen tolerance to make FP16 pass |
| Torch 2.9.1+cu128; Transformers 5.5.4; HQQ 0.2.8.post1 | Derive the shared installation lock from a successful environment; archive each freeze |
| FP32 model weights for the next pair | Same loaded weights for ordinary and quantized cache |
| Explicit valid-token masks | All ones for current unpadded batch one; no token-ID-based pad masking |
| Fixed prompt and EOT scoring | System message, 10 Apr 2025, fixed full tokenizer/template and identical answer boundaries |
| Greedy, one beam, max 64 new tokens | Common benchmark budget and stopping settings; preserve truncation |
| Generation-based factual disclosure primary | Reference scores and ROUGE secondary; correctness separate from refusal |
| Schema-v2 evaluator and reciprocal PR review | Maintain manifests, errors, unscored raw records and independent code review |

**Still proposals/open:** residual128 as primary; the independent 240-answer review plan and rubric details; final evaluator scope; exact NPO/RMU checkpoints; broader author allocation; practical disclosure and utility thresholds; final numerical tolerances; multiplicity and confirmation freeze.

The requirements-week1.txt file still advertises a candidate environment and includes Quanto rather than an exact HQQ installation. It must not be described as the shared validated lock. Remote README still demonstrates a Quanto command; a new collaborator could follow a known failing path on the attempted T4 setup.

Protocol tags and a frozen confirmation manifest must reflect actual agreement and exposure history. An observed development outcome cannot be converted into untouched confirmation evidence by assigning it a later label.

## 14. What is achieved, and what the paper can claim now

| Claim or deliverable | Assessment as of 23 October |
|---|---|
| Models and data can run on the intended T4 | Achieved for the recorded checkpoint family and environments |
| Full/retain/unlearned ordinary development behaviour is known | Achieved descriptively on one exposed forget author and a restricted utility sample |
| Upstream pad/EOT mask confound exists on these fixtures | Measured and controlled in the new unpadded path |
| Real HQQ stored-cache quantization affects sequential scores | Supported by artificial and selected full-model TOFU diagnostics |
| Single empty-cache parallel scoring can miss later cache-read effects | Supported in the tested HF implementation; not universal to hooks/engines |
| A/B prompts and reference tokens agree | 20/20 recorded forget fixtures; timing ordinary output parity also checked on 80 items |
| INT4 improves speed or meaningfully reduces measured peak memory | Not supported by this timing run; it was slower with nearly equal peak memory |
| Quantization changes full-model generated outputs | 39/80 paired token sequences differ; correctness effects unreviewed |
| Quantization recovers forgotten facts in an unlearned model | Not yet established |
| General utility is preserved or improved | Not established; current evidence is a restricted descriptive screen |
| Main NPO/RMU matrix and independent confirmation are complete | Not completed |

**Overall assessment:** the engineering foundation is substantially stronger than a week ago. The project has progressed from a plan and ordinary baselines to interoperable helpers and real compressed-cache execution on benchmark prompts. The main limitation is the remaining scientific measurement work, not the absence of any functioning quantization code.

A workshop submission could be built around a carefully scoped evaluation-path finding, unlearning-durability measurements, or both, depending on the forthcoming evidence. A valid flat result is acceptable scientifically. Acceptance cannot be predicted from this repository alone, and this audit is not a refreshed related-work search.

## 15. Recommended next work and ownership

**First: reconcile and freeze the shared development implementation.** B's remote changes and A's local day-six/day-seven artifacts need a reviewed integration. Preserve both append-only decision/log histories. Publish the accepted baseline and versioned rubric, create a reproducible shared environment specification, and rerun the applicable ordinary/identity/parity controls on both accounts. A owns baseline/measurement review; B owns cache/evaluator implementation; both approve scientific choices.

**Second: finish independent annotation.** B should label the agreed current population without A's labels/model identities where practical. Record disagreement rates before discussion. Resolve reference/rubric problems consistently and preserve both original reviews. The existing sheet builder helps prepare this work but does not complete it.

**Third: execute the paired development run.** The local prepared notebook compares full, retain90 and SimNPO on the same 80 questions under ordinary and INT4 caches: 480 responses. It regenerates ordinary controls in the same run, traces an initial probe per model, saves incrementally and leaves factual labels unscored. Review changed answers and fixed-denominator transitions. Do not require a positive recovery effect. GPU execution remains pending in the supplied artifacts.

**Fourth: select the actual paper checkpoints and broader population.** Freeze NPO/RMU candidates from provenance and ordinary forgetting/utility only. Audit author exposure, choose a broader development/confirmation allocation, set the utility and numerical policies, and estimate annotation as well as GPU cost. Avoid expanding every axis at once.

**Fifth: run the frozen research matrix and analyze it.** The planned full/retain90/NPO/RMU by ordinary/INT4/INT2 matrix contains 12 cells; INT2 can remain a labelled stress condition if budget or scope requires. Preserve model/condition pairing, author clusters, all outcome categories, failures and truncation. Add other architectures/datasets or training seeds only when resources and compatible references justify them.

**Ready-to-run milestone:** a shared environment and validated evaluator that emit complete schema-v2 records for each selected model, followed by independent paired factual review. **Paper milestone:** a bounded, reproducible result on the frozen population with utility evidence and uncertainty that matches the claim.

## 16. Evidence index and reproducibility details

All paths below are relative to the repository root. Remote evidence is pinned to cf5c7f3; local evidence is explicitly identified. This report's supporting audit preserves the exact hashes of the new reports it recomputed.

| Evidence | What it supports |
|---|---|
| docs/BLUEPRINT.md; results/README.md; docs/PILOT_CRITERIA.md | Intended design, data contract and unresolved confirmation criteria |
| docs/DECISIONS.md; docs/LOG.md at remote cf5c7f3 | New conventions, proposals, reported runs and historical failures |
| results/day1/ through results/day3/ | Setup, initial forget baselines and annotation acceptance |
| results/day4/day4_20261020T103718004368Z/ | Frozen utility selection, 180 outputs and accepted A labels |
| results/day5/day5_20261020T110711928957Z/ | Source integration, mask traces and paired results |
| results/diagnostics/ | B's seven v1 rerun reports, hardware and dependency freeze |
| results/diagnostics-v2/ | Three new INT4 diagnostic reports and prompt-parity report |
| results/timing/full-80items-int4-res128-fp32.json | 160 timing records with token sequences and NLL sums |
| Local results/day6/day6_20261020T130635380188Z/ | Attention-interface trace, generation replay and 28 checks |
| Local results/day7/day7_20261021T101236202224Z/ | 240 current ordinary outputs, manifests and accepted annotations |
| Local results/int4-development-preparation/ | Prepared paired notebook input bundle; no completed GPU outcome |
| results/repository-review-20261023/artifact-audit.json | Recomputed new-report arithmetic, timing, parity and source hashes |

**Pinned identities:** dataset locuslab/TOFU at 324592d84ae4f482ac7249b9285c2ecdb53e3a68; full checkpoint revision 88e31200b97e4c0c04ae0d2f0b591f427046d192; retain90 revision 7114300c0049527a71833f5683965c358ad9dcbf. Current SimNPO engineering checkpoint and its revision are preserved in day-seven manifests. Template SHA256 is 5816fce10444e03c2e9ee1ef8a4a1ea61ae7e69e438613f3b17b69d0426223a4.

**Inspection record:** fetched remote successfully; preserved dirty local checkout; passed 21 remote CPU tests and 34 combined-snapshot tests; recomputed gates and timing summaries; checked full-model cross-path token/NLL parity. No new CUDA execution, independent annotation, model training, remote merge or push was performed. Local tests used available CPU dependencies, not a replica of the Colab GPU environment.

**Review URL:** https://github.com/vedtod07/kv-cache-unlearning/tree/cf5c7f306ccf334e598394b98e57046fd533f7f3
