# Changes from v3 to v4 — 19 October 2026

This revision implements the repository methodology review. It does not claim GPU validation or finalize scientific thresholds for the authors.

| Review issue | Change |
|---|---|
| Default residual cache incorrectly called inactive on short prompts | Corrected every active plan and retired the old expectation from diagnostics |
| Scoring gate confounded parallel/sequential numerical differences with quantization | Separate ordinary baseline, identity and quantized-sequential comparisons; finite token-level checks |
| Liveness inferred solely from changed output | Added per-layer write/read/storage/reconstruction instrumentation; equal output scores allowed |
| Unclear recovery denominator | Fixed-population absolute effects primary; reference adjustment and conditional recovery secondary |
| Positive-result gates | Replaced with implementation, measurement, feasibility and precision gates |
| Hooks treated as a controlled timing-only comparison | Hooks optional; document all intervention differences |
| Unclustered tests alongside clustered benchmark | Paired author-cluster inference primary; no item-independence claims |
| Confirmation after repeated inspection | Explicit development/confirmation allocation and dated protocol versions |
| Broad drifting environment and BF16-on-any-CUDA | Pinned inspected Transformers API, explicit dtype/SDPA; candidate dependencies still need GPU lock |
| Scope and ownership inconsistent | 12-cell core; A is Vedant and owns measurement; one optional extension |
| Outcome labels conflate refusal and correctness | Separate fields and expanded provenance/error contract |
| No recorded GPU results | Kept status explicit; added local gate and record-validation regression tests |

Outstanding: actual GPU/backend validation; complete environment lock; immutable study manifests; integrated OpenUnlearning evaluator; annotation rubric and author split; authors' practical thresholds; analysis implementation and independent verification; closest-paper full-text screening. These are research work, not completed by this documentation/code revision.
