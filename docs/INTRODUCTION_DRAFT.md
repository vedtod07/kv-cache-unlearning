# Introduction draft — v3 aligned with protocol v4

Status: planned study, not a results section. Replace future tense only after experiments. Avoid “certificate” unless a defined formal or empirical guarantee is actually established.

Language models can disclose information associated with their training data. Machine unlearning seeks to remove the influence of designated data while retaining useful behavior. Evaluation typically measures a particular checkpoint under a specified inference configuration; its conclusions need not transfer to a different deployed computation.

Prior research demonstrates that weight quantization can weaken unlearning in evaluated settings [Catastrophic Failure; DurableUn]. Quantization-robust unlearning methods further investigate this problem [Low-Rank Adaptation; Retain-Forget Loss Landscapes]. Separately, Alignment Collapse studies safety degradation under KV-cache quantization. These results motivate, but do not answer, whether changing stored attention state while keeping unlearned weights fixed increases correct disclosure of forgotten facts.

We plan to study this question using compatible full-data, retain-only and unlearned TOFU checkpoints. We will compare ordinary inference with a precisely specified stored-cache backend, measuring factual disclosure and retained utility. References will undergo the same cache transforms, and we will report both absolute within-checkpoint changes and reference-adjusted comparisons.

Evaluation semantics are a supporting question. In the inspected Transformers implementation, initial prefill stores quantized K/V while using original tensors for that call; later decoding reads the reconstructed prefix. A single parallel scoring pass therefore represents a different computation from sequential scoring with that cache policy. Our aim is to determine whether the difference has a consequential effect on evaluation, rather than merely documenting a numerical discrepancy.

Correct factual disclosure and response behavior will be annotated separately. We will estimate paired effects with author-clustered uncertainty and disclose the limited checkpoint and benchmark scope. Possible findings include recovery, evaluation disagreement, or bounded robustness; none is assumed in advance.

## Claim limits

- The weight-interval account does not predict that every other intervention must have no effect; it simply does not explain a cache-only effect by changed weights.
- “Refusal-style” and “suppression-style” are descriptive training-method labels, not established causal mechanisms.
- Projection hooks and stored-cache compression can differ in more than timing.
- Log-probability is not a direct measurement of latent knowledge.
- A stock evaluator of an uncompressed checkpoint is not necessarily defective because it does not assess a deployment transform.
- A null finding needs informative bounds, not merely a nonsignificant test.
- Closest-paper full-text screening, including Beyond Forget Scores, must finish before a novelty claim.

References and links are maintained in BLUEPRINT.md. The partner must check each final paper claim against the cited version and section. No “first” claim is currently established.
