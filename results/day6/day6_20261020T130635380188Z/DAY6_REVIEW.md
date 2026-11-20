# Day-six GPU integration review

Reviewed 20 October 2026. Codex-assisted artifact review; independent Person B review and joint scientific sign-off remain pending.

**Outcome: all 28 programmed checks passed on the T4. The archived evidence supports the tested FP32/HQQ, unpadded, batch-size-one cache/scoring path. We can move to an integrated development pilot using the same numerical and mask conventions.**

The run contains one full-data checkpoint and artificial weather fixtures. It establishes engineering behavior, rather than forgotten-fact recovery. The original manifest and all returned files are preserved. `artifact-review.json` adds verification and derived summaries without rewriting that manifest.

## Provenance and verification

- Input ZIP checksum matches the prepared day-six bundle. Archived runner bytes match the prepared source and its recorded SHA256.
- Model and resolved revision match `open-unlearning/tofu_Llama-3.2-1B-Instruct_full` at `88e31200b97e4c0c04ae0d2f0b591f427046d192`.
- Tesla T4; Python 3.13.15; Torch 2.9.1+cu128; CUDA 12.8; Transformers 5.5.4; HQQ 0.2.8.post1. The freeze matches the declared additional pins, including accelerate 1.13.0, huggingface-hub 1.33.0 and NumPy 2.1.3.
- FP32 weights and scoring, SDPA, HQQ axes 1/1, group size 64, residual length 128. TF32 was explicitly disabled. This configuration differs from A's earlier Torch 2.11/FP16 baseline.
- The tokenizer template matches the earlier saved template. The runner uses the fixed date `10 Apr 2025` and explicit all-ones valid-token masks.
- Archived `QuantizedLayer` and `LlamaAttention` source, including the attention class decorator, match the inspected Transformers 5.5.4 wheel.
- Twenty-five checks recompute from the archived score vectors, generation/replay decisions and trace fields. The three fresh-cache repeat checks archive zero-delta vectors rather than the repeat's raw NLL vectors; their consistency was checked, but the rerun vectors cannot be independently reconstructed.
- Finite scores, target lengths, delta arithmetic, trace counters and generation termination flags are consistent.

This is a review of saved evidence. It does not independently rerun CUDA inference. Traces preserve runtime equality/identity assertions and counts, rather than full K/V tensors; native generation logits are also not archived.

## Ordinary and identity controls

The short prompt has 50 tokens; the long prompt has 330. Both score the same nine answer tokens: the weather sentence plus terminal EOT ID 128009.

| Control | Short maximum absolute token-NLL difference | Long maximum absolute token-NLL difference |
|---|---:|---:|
| Ordinary sequential versus parallel | 0.00003052 | 0.00002575 |
| Identity wrapper versus ordinary sequential | 0 | 0 |
| Instrumented versus plain INT4 sequential | 0 | 0 |
| Instrumented versus plain INT2 sequential | 0 | 0 |
| Empty INT4 cache parallel versus ordinary parallel | 0 | 0 |
| Empty INT2 cache parallel versus ordinary parallel | 0 | 0 |

The provisional absolute/relative tolerances remain 1e-3, inherited before this run. No tolerance was changed to obtain a pass. These observations characterize two fixtures; they do not establish a universal numerical error bound.

## What the cache trace establishes

For each of the four scored quantized conditions, all 16 layers recorded:

- Two quantization calls: one K write and one V write during prefill.
- Sixteen dequantization calls: one K read and one V read for each of eight subsequent forward calls.
- Nine cache updates and nine attention-interface calls, matching the nine scored targets.
- Exact equality between reconstructed cached prefixes and the corresponding returned K/V prefixes.
- The exact returned K/V tensor objects arriving at the SDPA attention interface.
- Original, unquantized K/V returned on initial prefill, despite quantized storage being created.

These call counts combine K and V; “16 reads” does not mean 16 reads for each tensor separately. No residual flush is expected with eight decoded inputs and residual length 128. Initial quantization of the long prompt still occurs even though its 330-token length exceeds that residual setting.

The one-token fixtures have two writes, one update/attention call and **zero decode reads** at every layer. Their only target is the first answer token, deliberately truncated from the full answer; they are not complete one-token natural-language answers with EOS. Their scores match the ordinary first-token score.

The trace reaches the SDPA function boundary and then calls the original attention function. This is stronger path evidence than observing changed output text alone; it does not inspect CUDA kernel internals or validate another serving engine.

## The evaluation-semantics result

All four empty-QuantizedCache parallel score vectors match ordinary parallel scoring exactly. In contrast, sequential scoring reads the reconstructed prefix and changes later scores:

| Fixture | Cache | Mean NLL change: quantized − ordinary sequential | Largest absolute single-token change | Maximum K/V reconstruction error |
|---|---|---:|---:|---:|
| Short | INT4 | −0.41685 | 1.10800 | 0.91583 |
| Short | INT2 | −0.01325 | 2.51839 | 4.60390 |
| Long | INT4 | −0.10546 | 0.99159 | 0.97699 |
| Long | INT2 | +0.33273 | 3.10312 | 4.77212 |

The first target's NLL change is zero in every condition because it is predicted by prompt prefill. Subsequent targets can be affected by cache reads. The final EOS is scored consistently.

The short INT2 mean is near zero even though some individual token changes are large. This illustrates why a small mean score difference alone cannot establish that a cache intervention was inactive. Positive and negative token differences can cancel.

This supports the scoped claim: **a full, single parallel forward with an initially empty HF quantized cache can miss score changes that occur during sequential readback.** It does not cover quantize-before-attention projection hooks, chunked prefill, reused nonempty caches, every backend, or all quantization semantics. The behavior follows the inspected implementation; this experiment alone establishes neither literature novelty nor a new unlearning vulnerability.

Lower NLL here means the artificial reference sentence became more probable. It says nothing about forgotten biography disclosure. The two different prompts and one answer also do not support a context-length or bitwidth trend.

## Generation and replay

| Cache | Generated text | Tokens including EOS where present | Termination |
|---|---|---:|---|
| Ordinary | It's a sunny day outside with a gentle breeze blowing. | 13 | EOS |
| INT4 | It's a beautiful day outside with a gentle breeze blowing. | 13 | EOS |
| INT2 | It's a bit of a forecast: Sunny skies are forecasted for the upcoming week, bringing a usual sense of optimism | 24 | Token budget; no EOS |

Each saved generated token equals the teacher-forced replay argmax under that same cache policy. Quantized generation traces show the cache-returned K/V reaching attention: 13 updates and 24 combined reads per layer for INT4; 24 updates and 46 combined reads for INT2. Fresh cache objects were used for generation and replay.

The truncated INT2 output remains a valid bounded generation record. It is not a runtime failure, and it should not be silently lengthened in isolation. Its continuation length is not evidence of global model collapse.

## Problems and remaining limits

No runtime failure or failed programmed check is present. The main remaining issues are coverage and measurement scope:

1. Only the full checkpoint was tested. Retain90 and the selected unlearned candidate still need the integrated path exercised.
2. Earlier accepted TOFU labels belong to a different Torch/precision configuration. New FP32 generations must be compared and re-reviewed when they differ; labels cannot simply be transferred.
3. Batch size one and explicit valid-token masks are the tested regime. Padding/position checks are needed before introducing multi-example batches. Keeping batch size one is a reasonable initial scope.
4. This run uses residual 128. B's boundary-setting reports remain separate evidence; the current traces do not validate every residual policy.
5. Fresh-repeat raw NLL vectors were omitted by the runner. Save both initial and repeated vectors in future runs for independently recomputable repeatability evidence. This omission does not require discarding the present cache-path results.
6. No runtime/peak-memory measurements were archived for sizing the full research matrix. Time a small integrated run before projecting total cost.
7. No NPO/RMU comparison, factual recovery, paired quantized utility, author-level confidence interval or confirmation freeze is present.

## Next work

The next stage should use the **existing exposed development fixtures** under this shared FP32/HQQ environment. Start with a restartable ordinary-cache TOFU baseline for full, retain90 and the previously selected SimNPO engineering candidate, using the exact fixed template, explicit valid-token masks, FP32 scoring and original 64-token generation budget. Compare these new baseline outputs with earlier ones to identify which labels can be reused and which need review. Because both Torch version and precision changed, any differences cannot be attributed solely to precision.

Then run paired ordinary/INT4 conditions on those same development items, with full and retain-only references under the same cache policy. Carry the fixed utility sample into the paired comparison before interpreting disclosure changes as useful unlearning-durability evidence. INT2 can be a separately labeled stress condition after the main path is checked. Preserve fixed denominators and both disclosure-transition directions.

This is an engineering/development sequence. It does not replace the planned NPO/RMU core, finalize effect/utility thresholds or expose new confirmation authors. Joint review and confirmation choices still need explicit records. No new manual correctness CSV is needed for this artificial day-six run, and no day-six rerun is required merely because INT2 reached its declared generation budget.
