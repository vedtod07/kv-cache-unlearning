# Work split — v4

**Person A: Vedant. Person B: collaborator (name to record).** Both own scientific decisions. Nine weeks is a planning budget, not a promise of completion or publication.

| Responsibility | A: measurement and analysis | B: cache and evaluation implementation |
|---|---|---|
| Baselines | Own OpenUnlearning setup, provenance, checkpoint selection, full/retain-only/unlearned baseline table | Independently reproduce a small sample |
| Protocol | Own fixed populations, outcomes, annotation rubric, utility samples, statistical plan | Review implementability and cost |
| Cache | Review instrumentation and paired outputs | Own exact backend, writes/reads, reconstruction fixtures, identity checks |
| Scoring | Specify boundaries/normalization and audit outputs | Own sequential scoring, parallel comparison, batching/masking/reset tests |
| Results | Own schema, validation, annotation and paired author-cluster analysis | Emit conforming records and failure logs |
| Optional work | Weight RTN only if jointly selected | Hook comparison or context implementation only if jointly selected |
| Writing | Introduction, related work, evaluation, analysis | Intervention details, validation, artifact and limitations |

## A's first deliverables

1. Immutable dataset/model manifest and baseline selection ledger.
2. Actual prompts, tokens and outputs for full, retain-only and one unlearned checkpoint.
3. Correctness and behavior rubric with ambiguous/refusal-with-fact examples.
4. Fixed-denominator effect definitions and development/confirmation plan.
5. Schema checks and analysis tests for zero effect, known improvement and author-concentrated effects.
6. Runtime/annotation budget and review of B's validation handoff.

Weight quantization is not A's first priority and is not a required positive control.

## B's handoff before A interprets quantized results

- Exact configuration, code/library/model revisions, hardware and dtype.
- Cache write/read and reconstruction-error evidence for all layers.
- Ordinary parallel/sequential and identity comparisons with justified tolerance.
- Quantized versus ordinary sequential comparisons on the same tokens.
- Tests for fresh caches, boundaries, masks, positions, EOS and batching.
- Common prompt/generation settings, conforming output records and explicit errors.
- Remaining limitations; the single-fixture diagnostic is not full pipeline validation.

## Shared workflow

Meet twice weekly. Keep LOG.md append-only. Both agree on pilot criteria, confirmation freeze, scope changes, framing and claims. Each checks at least 20 partner outputs weekly when outputs exist; record run IDs and findings. Neither author approves their own scientific evidence alone.

Use one shared implementation/configuration set across GPU accounts. Split compute only after both environments pass the same checks. Differences in dtype/backend/hardware must be recorded and investigated before pooling.

The other person reviews each PR; citation claims are checked against primary sources by the partner. AI can assist code and writing; authors own hypotheses, thresholds, annotations and claims. Record AI-assisted commits and follow venue disclosure rules.

Follow NINE_WEEK_PLAN.md. New architecture training, K-only/V-only and weight × KV are deferred, not hidden mandatory tasks.
