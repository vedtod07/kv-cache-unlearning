# Person A: first-week walkthrough

Owner: Vedant. This walkthrough accompanies the first-week notebooks. It is a teaching/setup artifact. Days one through five have returned GPU artifacts; see the dated progress below for their actual scope and remaining work.

## The week's question

Before studying compression, establish what the full-data, retain-only and unlearned checkpoints do on the same genuine benchmark questions. Person A owns whether the measurements support a factual claim. Person B owns the cache implementation, but both check its evidence.

Full model: fine-tuned on all TOFU training authors. Retain-only model: trained on the retained subset and used as a counterfactual reference. Unlearned model: starts from a full model and is subsequently updated by an unlearning method. The retain-only model need not answer zero forgotten questions; the full model need not answer every question correctly.

## Work sequence

| Stage | Action | Deliverable | Meaning |
|---|---|---|---|
| Day 1 | Record hardware, resolve revisions, load full model and generate one real answer | Environment, provenance, exposure log, prompt/token IDs, output, timings | Setup works on one example |
| Day 2 | Trace upstream data/template/model/metric code; verify authors and development allocation | Source map and development item list; full/retain comparison | We know what the baseline measures |
| Day 3 | Add one documented unlearned candidate under identical inputs/settings | Full/retain/unlearned table | Baseline learning/forgetting can be inspected |
| Day 4 | Define correctness and behavior separately; independently review labels | Rubric and disagreement notes | Measurements represent factual disclosure |
| Day 5 | Time fixed forget/utility samples, count tokens and annotation workload | Cost sheet and prompt-length table | Future matrix is sized from measurements |
| Day 6 | Inspect Person B's fixed-token cache validation evidence | Signed review log with report IDs | Cache results become interpretable when validation passes |
| Day 7 | Draft pilot outcomes, utility samples, cluster analysis and exclusions | Draft pilot protocol with unresolved decisions listed | Next week has a reproducible plan |

Daily practice: run a small task, save raw artifacts, inspect the result, write what it establishes and its limits, then cross-check with the collaborator. Keep code/configurations in Git and large raw outputs in the chosen durable archive. Never end a temporary notebook session without downloading or backing up its artifacts.

## Begin with the notebook

1. Open `notebooks/person_a_week1_day1.ipynb` in a GPU notebook service. Colab supports File → Upload notebook; choose the local file. Kaggle supports importing a notebook and selecting a GPU accelerator.
2. Run the first cell only. Confirm Python version, GPU model and a writable artifact directory. Stop on missing GPU; select one in runtime settings.
3. Run package setup. Preserve dependency errors. If restart is required, restart and rerun initialization before subsequent cells. Today keeps the platform's Torch and records it; this is not the final environment lock.
4. Resolve checkpoint/data revisions and inspect access errors before downloading weights. No token belongs in notebook source or shared output.
5. Load the fixed dataset row and render the actual question-only prompt. Its author must later be assigned to development or accounted for as exposed.
6. Load the full model with SDPA/FP16 and generate one answer. Inspect reference/output, token count and timing. A wrong answer is not automatically a setup failure; record it rather than searching for a pleasing example.
7. Complete review notes and download the zip. These files are setup artifacts, not schema-v2 benchmark results or paper metrics.

Day-one completion requires traceable artifacts, not a particular answer. Share the environment, provenance and first prompt/reference/response for the next step. Day two's exact upstream evaluation command should be prepared after these runtime results, not guessed now.

## Upstream source map verified during preparation

Inspected OpenUnlearning commit: `b29929067732c40ee4ca58d5cc1d3c11fcf37de1`.

- `configs/model/Llama-3.2-1B-Instruct.yaml`: FlashAttention2/BF16 defaults, system prompt and fixed template date. T4 walkthrough overrides use SDPA/FP16.
- `src/data/utils.py`: prompt/chat rendering, response labels and masking. Follow token IDs; string lengths are insufficient.
- `configs/data/datasets/TOFU_QA_forget.yaml`: default question/answer fields and max length.
- `configs/eval/tofu_metrics/forget_Q_A_Prob.yaml` and `forget_Q_A_ROUGE.yaml`: use `forget10_perturbed` via overrides. Today's plain `forget10` fixture is not stock metric reproduction.
- `configs/experiment/eval/tofu/default.yaml`, `configs/eval.yaml`: model and evaluator composition.
- `src/model/__init__.py`: dtype resolution and separate model/tokenizer loading. Overriding only the model ID does not automatically override the tokenizer ID.

Read these files with one real item next to you. Trace dataset question → rendered prompt → token IDs → model → generated answer/scored answer → saved metric. Do not assume stock downloaded retain logs match our later transformed-reference conditions.

## Interpretation rules

- No recovery claim before a paired compression comparison.
- No aggregate forgetting claim from one question.
- No automatic classification from entity occurrence alone.
- No independent-row uncertainty estimates for author-clustered questions.
- No claim of untouched confirmation for inspected authors/items.
- No quantization training or broad bit sweep is needed for A's day one.

Consult BLUEPRINT.md, PILOT_CRITERIA.md, VALIDATION.md and results/README.md for the study protocol. This walkthrough does not finalize thresholds or authorize pooling incompatible runs.

## Progress as of 20 October 2026

The actual notebook sequence expanded the original schedule above: day one verified setup; day two compared full/retain on 20 exposed questions; day three added the SimNPO engineering candidate; day four screened a frozen restricted utility subset; day five integrated actual upstream source helpers and compared mask conventions. These are development artifacts, not the final paper's main experiment.

Day-five review: [DAY5_REVIEW.md](../results/day5/day5_20261020T110711928957Z/DAY5_REVIEW.md). All 60 all-ones outputs reproduce earlier text and token IDs. The stock collator masks genuine EOT markers with this tokenizer and changes responses. Keep the two conditions distinct; existing accepted labels apply to the identical all-ones outputs. No new manual annotation is required for the engineering check.

Remote synchronization during publication found Person B's already-merged HQQ artificial-fixture diagnostics. See the [five-day progress diff](FIVE_DAY_PROGRESS_DIFF.md) for their results and the A/B environment mismatch. Next: review those reports together and complete the outstanding integrated-evaluator contract in [VALIDATION.md](VALIDATION.md). A passing partial diagnostic does not replace the full checklist. No quantized TOFU disclosure comparison or untouched-author confirmation has been completed in A's five-day workflow.

## Next executable step: day-six integration

Use [person_a_week1_day6.ipynb](../notebooks/person_a_week1_day6.ipynb) with the [day-six input ZIP](../results/day6-preparation/day6-integration-input-bundle.zip) in a fresh Colab T4 runtime. Follow the notebook's setup and restart instructions, then upload the ZIP and run the checks. Download partial artifacts even if a check fails.

This stage uses B's tested Torch/HQQ versions and FP32 weights, explicit valid-token masks, and artificial prompts with A's fixed chat-template date. It adds cache-to-attention tensor tracing, empty-cache prefill, one-token and generation-replay checks. See the [preparation notes](../results/day6-preparation/README.md) for exact scope. No manual factual annotation is needed; review the returned diagnostic before starting a paired TOFU comparison. GPU execution of the new notebook remains pending.

## Day-six returned evidence

The [day-six GPU review](../results/day6/day6_20261020T130635380188Z/DAY6_REVIEW.md) supersedes that preparation-time pending status. All 28 checks passed on the T4; the review records independent recomputation limits. Empty-cache parallel scores match ordinary scores, while sequential readback changes later token scores. Cache-returned reconstructed K/V reaches the SDPA interface. INT2 generation reaches its declared 24-token budget; no rerun or factual annotation is needed for that artificial output.

Next: integrate the same masks, environment and scoring into a restartable baseline on the existing exposed TOFU development fixtures. Earlier FP16 labels cannot automatically be transferred to changed FP32 outputs. Follow with paired ordinary/INT4 development disclosure and utility under matched reference conditions. Independent/joint review and confirmation freeze remain pending.

## Day seven: Person A can proceed

Follow [PERSON_A_DAY7_NEXT_STEPS.md](PERSON_A_DAY7_NEXT_STEPS.md). The [day-seven notebook](../notebooks/person_a_week1_day7.ipynb) and [input ZIP](../results/day7-preparation/day7-baseline-input-bundle.zip) prepare 240 ordinary-cache FP32 generations across the three existing checkpoints and 60 forget-item parallel/sequential scoring comparisons. Reuse the day-six environment when available; otherwise follow setup and restart instructions. Return the resulting ZIP for artifact and factual review. B can independently review the handoff in parallel. No new confirmation data or quantized disclosure outcomes are included. GPU execution is pending.

## Day-seven returned evidence

Run `day7_20261021T101236202224Z` completed all 240 responses and passed all 60 scoring comparisons. The [day-seven review](../results/day7/day7_20261021T101236202224Z/DAY7_REVIEW.md) supersedes that preparation-time pending status. 235 responses reproduce previous text/tokens, and five changed. Proposed annotations are saved separately; the full-model canonical-award response changes from correct to incorrect, giving 15 fully correct forgotten-author answers rather than 16. SimNPO's philosophy partial remains specifically flagged. Utility counts are unchanged. A verification and independent B review remain pending. After review, the next stage is matched ordinary/INT4 development disclosure and utility with the same references and settings.

## Week-one A acceptance and next-stage preparation

Vedant verified the day-seven review on 21 October. The [acceptance record](../results/day7/day7_20261021T101236202224Z/manual-review/acceptance.json) supersedes the A-pending status above; independent B review remains pending. See [WEEK1_REVIEW.md](WEEK1_REVIEW.md) for the seven-stage goal/importance/method/result review and [the next-stage instructions](../results/int4-development-preparation/README.md) for the prepared paired ordinary/INT4 notebook. No new GPU run or joint confirmation freeze is implied by preparation.
