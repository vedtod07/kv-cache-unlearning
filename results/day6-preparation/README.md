# Day six — cache/evaluator integration diagnostic

Prepared 20 October 2026. GPU execution is pending. Person A reviews the returned evidence with Person B before any disclosure experiment.

## Run in Colab

1. Upload `notebooks/person_a_week1_day6.ipynb` as a fresh notebook and select a T4.
2. Run accelerator verification and the package-setup cell. This installs Torch 2.9.1 from the CUDA 12.8 wheel index, Transformers 5.5.4, HQQ 0.2.8.post1, accelerate 1.13.0, huggingface-hub 1.33.0 and NumPy 2.1.3. It removes unused torchvision/torchaudio packages to avoid the mismatch encountered by B.
3. Restart the session, then continue at section 3. This is intentionally a different environment from A's earlier Torch 2.11/FP16 runs. Do not combine their scores without a controlled comparison.
4. Upload `day6-integration-input-bundle.zip` when prompted. The notebook verifies its SHA256 and the runner hash.
5. Run the diagnostic. If it errors, preserve the error and run the final download cell anyway.
6. Return the resulting `day6_<timestamp>.zip`. No manual annotation is required for these artificial fixtures.

Use the notebook and ZIP from the same preparation. The notebook does not depend on a new GitHub push.

## What changes from B's original diagnostic

| Check | Day-six implementation |
|---|---|
| Template and masks | Fixed A system prompt/template date; explicit all-ones masks for genuine, unpadded tokens |
| Score definition | FP32 log-softmax; first answer predicted by last prompt position; terminal EOT included |
| Ordinary reference | Parallel versus sequential and identity-wrapper sequential |
| Quantization | HQQ INT4/INT2, axes 1/1, group 64, residual 128; full checkpoint with FP32 weights |
| Prefill | Explicit full parallel forward with a fresh empty QuantizedCache versus cache-disabled parallel forward |
| Decode trace | Quantization writes, reconstruction error, decode reads, equality of reconstructed prefixes and returned K/V |
| Attention trace | Verify the Llama SDPA interface receives the exact K/V tensor objects returned by the cache |
| Instrumentation | Compare instrumented and uninstrumented sequential scores; restore attention dispatch on exceptions |
| One-token fixture | Confirm no decode reads occur when only the first answer token is scored |
| Fresh-cache repeat | Short → long → short scoring, allocating a new cache for every call |
| Generation | Native greedy generation with explicit cache object; replay generated tokens with identical policy and verify argmax decisions |

These tests cover two artificial prompts and one pinned full-data checkpoint. They do not measure factual unlearning or recovery. The original B prompt and template are not silently reused. TF32 is explicitly disabled for this diagnostic; all settings and installed source bodies are archived.

## Artifacts and status

The run saves a manifest, environment/freeze/hardware details, exact fixtures, source code, template, model/generation configuration, per-token scores, per-layer traces, generation/replay outputs and checks. Outputs are saved incrementally. Runtime failures update the manifest and the notebook saves a traceback.

- `checks_passed_review_pending`: all programmed checks passed; inspect the evidence before scientific use.
- `checks_failed_review_required`: numerical or structural check failed; retain the report and investigate.
- `runtime_error`: setup or execution failed; preserve partial artifacts.

The existing provisional absolute/relative tolerances are both 1e-3, inherited from B's diagnostic before this run. Do not enlarge them to obtain a pass. There is no required positive quantization effect.

## Local validation and limits

Local tests use a tiny random CPU Llama, Transformers 5.5.4 and a simple deterministic rounding cache. They check target alignment, parallel/sequential agreement, tensor tracing, instrumentation neutrality, one-token behavior, dispatch restoration after exceptions, and generation replay. The CPU environment uses Torch 2.12.0, so it does not validate the requested Torch 2.9.1/CUDA/HQQ combination. B's earlier reports provide supporting compatibility evidence; this new notebook still requires its own T4 run.

Padded/multi-example batches, FP16 integration, statistical confirmation and full TOFU integration remain outside this run. Residual-boundary experiments remain in B's separate reports; this run holds residual length at 128. GPU-memory/runtime measurements here should not be treated as a deployment benchmark because instrumentation adds overhead.

## Returned GPU evidence — 20 October 2026

The prepared notebook has now returned run `day6_20261020T130635380188Z`. All 28 checks passed; see the [day-six review](../day6/day6_20261020T130635380188Z/DAY6_REVIEW.md) and its machine-readable verification for scope and limits. Historical preparation/CPU-validation statements above remain as written. The run verifies the limited FP32/HQQ path; it does not complete TOFU integration or joint scientific sign-off.
