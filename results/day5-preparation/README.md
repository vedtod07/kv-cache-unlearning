# Day-five source-helper integration

Prepared 20 October 2026. Goal: understand and validate the scoring/data path before interpreting cache-compression results.

## What runs

Three pinned checkpoints, the same 20 previously exposed forget-author items, ordinary weights/cache, FP16/SDPA and batch size one. The uploaded source package is an exact subset of OpenUnlearning commit b29929067732c40ee4ca58d5cc1d3c11fcf37de1, with MIT license and per-file hashes. No source bodies are patched.

The actual upstream data preprocessor and collator prepare inputs. The actual evaluate_probability and eval_text_similarity helpers produce per-item probabilities and ROUGE/generations. Helper functions are loaded directly from their file to avoid unrelated trainer/evaluator registries. This **does not reproduce the full Hydra CLI/configuration pipeline or official full-dataset metrics**.

Explicit differences from a standard full run: only 20 development items, 64-token generation budget, no perturbed/paraphrased-answer truth ratios, privacy/forget-quality metrics, normalized multiple-choice probabilities, or official model_utility. Aggregation is mean probability / mean ROUGE-L recall as in the inspected wrappers, but on this different declared subset/configuration.

## Diagnostics

1. Trace actual prompt/answer token IDs, masked labels, scored target count and EOS convention. Compare prompt IDs to saved baseline fixtures.
2. Stock mask versus all-ones mask on the same unpadded batch-size-one sequence. Stock collator sets mask=input_ids != pad_token_id. Here pad=eos, so genuine turn markers can receive zero mask. Do not silently patch the stock arm or infer the magnitude without the run.
3. Independent FP32 score calculation on the same stock-mask inputs to characterize numerical differences. No post-hoc tolerance or gate is invented.
4. Stock-helper generation under each mask and comparison with prior saved all-ones ordinary generations. Capture actual output tokens and truncation/EOS flags without changing generated tensors.

Probability means exp(-mean labeled-token cross entropy), including the upstream labeled EOS convention. It is not full-sequence probability, binary correctness, or direct proof of knowledge. ROUGE is lexical evidence, not factual annotation.

## Running

Import notebooks/person_a_week1_day5.ipynb into Colab/Kaggle with a T4. Install the listed lightweight dependencies in a fresh runtime (including omegaconf and rouge-score), restart if prompted, then provide day5-source-parity-input-bundle.zip. GPU run remains pending. Do not install the full training stack just to run this harness.

Return the output ZIP before interpretation. It contains source files/hashes, inputs/masks, per-item scores/generations, and summaries. Unexpected input/ground-truth/numerical differences must be examined before any quantized condition.

## Checks performed locally

- ZIP integrity and exact bundled source hashes.
- Notebook code syntax and bundle-hash linkage.
- CPU checks using actual extracted source class/function definitions: genuine EOS IDs are zero-masked by the stock collator; probability aggregation equals exp(-mean loss) over the final labeled token as well.
- Independent FP32 reference function and cloned all-ones-mask behavior checked on a known CPU toy fixture.

These CPU checks do not validate import integration, real tokenizer behavior, CUDA or the full benchmark.

## What remains

Person B's real cache-path validation, supported backend/environment choice, full OpenUnlearning CLI integration and confirmatory protocol remain unfinished. Do not run untouched forget authors during this engineering step. Completion does not freeze paper-level scientific thresholds or establish a new finding by itself.

## Returned GPU run — 20 October 2026

The preparation-time pending status above is superseded by the returned T4 run `day5_20261020T110711928957Z`. See [the artifact review](../day5/day5_20261020T110711928957Z/DAY5_REVIEW.md). All 60 expected records completed, source hashes match, and all-ones output text/token IDs reproduce the earlier ordinary baseline exactly. The stock mask changes generation and remains a separately labeled diagnostic. This does not complete cache validation or full-CLI reproduction.
