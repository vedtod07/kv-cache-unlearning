# Validation contract — v4

## What the supplied diagnostic does

`scripts/test_kv_scoring_path.py` targets Transformers 5.5.4 and one unpadded, artificial prompt/answer fixture. It uses the same token IDs for ordinary parallel, ordinary sequential, identity-wrapper sequential and quantized sequential scoring. Log-softmax is evaluated in FP32. The final gold token is not fed when its successor is not scored.

For each quantized layer, wrappers count K/V quantization writes and decode dequantization reads, and measure reconstruction error. The wrappers rely on the inspected implementation's K,V call order; this must be reviewed if the API changes. Extra dequantization used for measuring reconstruction error is not counted as a decode read. Instrumentation adds overhead, so these runs are not performance benchmarks.

Exit 0 requires finite scores, matching sequence lengths, ordinary/identity agreement within configured tolerance, K/V storage and writes/reads on every layer, and observed nonzero reconstruction error somewhere in the cache. It does **not** require changed mean NLL or generated text. Quantized-versus-ordinary sequential token deltas are reported separately.

This verifies call-path evidence under the inspected implementation, not every possible serving backend. Review the source and trace to confirm reconstructed values feed attention. Full attention-consumption tracing and a tensor-level intervention fixture remain part of B's validation handoff.

The model revision must be supplied. Record the resolved model revision and exact tokenizer artifacts. Environment pins are provisional until a successful GPU run and full dependency freeze are archived.

## Checks still required before research runs

- [ ] Run the diagnostic on the actual GPU/backend; archive every report, including failures.
- [ ] Short and long prompts, INT4 and INT2, and residual-buffer boundary behavior.
- [ ] Ordinary and identity numerical repeatability; justify tolerances independently of quantization outcomes.
- [ ] Synthetic tensor fixtures: identity transform and known nonzero quantization error; trace the consumed tensors.
- [ ] Explicit parallel prefill with an empty QuantizedCache versus ordinary prefill. The current diagnostic's parallel call has cache disabled and does not test this claim directly.
- [ ] One-token answers (no decode-read effect on their only score), multi-token answers, EOS conventions and exact answer boundaries.
- [ ] Padding, attention masks, positions and batch size one versus multiple examples in the integrated evaluator.
- [ ] Fresh cache per example, order-independence checks and no cross-item contamination.
- [ ] Golden scoring fixture/independent check for off-by-one errors.
- [ ] Generation uses the same cache policy and tokenization as scored evaluation; unsupported generation modes fail explicitly.
- [ ] Compare instrumented and uninstrumented computation on fixed tokens; ensure instrumentation itself is neutral.
- [ ] Result records and errors satisfy results/README.md.

Both authors sign off by recording the reports, configuration and remaining limits in DECISIONS.md. Do not treat local unit tests as GPU validation.

## Local automated checks

```bash
python3 -m unittest discover -s tests -v
```

The dependency-free tests cover gate regressions (bad baseline, missing reads, nonfinite scores, cancelling token differences, identity mismatch, and unchanged scores with instrumented quantization), plus record validation. They do not exercise Torch, Transformers, CUDA or real model inference.
