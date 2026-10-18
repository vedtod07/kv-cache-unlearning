# Pilot and confirmation criteria — v4

Status: DRAFT. Jointly finalize before the corresponding research runs. Engineering fixtures are allowed now; they are not benchmark pilot results. Do not invent effect/utility thresholds on the authors' behalf.

## Engineering and pilot gates

| Gate | Evidence required | Owner |
|---|---|---|
| Baseline validity | Correct data/template, meaningful full-model learning, unlearned forgetting and retained utility | A |
| Cache implementation | Instrumented K/V writes/reads, reconstruction-error fixtures, ordinary and identity checks; additional evaluator tests in VALIDATION.md | B, checked by A |
| Measurement | Fixed correctness/behavior rubric, annotation checks, consistent scoring normalization | A, checked by B |
| Feasibility | Measured loading, generation, scoring and annotation costs; restartable outputs | Both |
| Informativeness | Planned effect/interval precision and utility evaluation justify the scope | A, agreed by both |

None requires weight-RTN recovery, KV recovery, significance in two methods, or a ranking reversal. A pilot can be flat with valid engineering. Diagnose actual failures; do not keep changing models to find a positive result.

## Freeze before confirmation

- [ ] Dataset revision and explicit development/confirmation author/item IDs.
- [ ] Checkpoint IDs/revisions and documented baseline selection rule.
- [ ] Backend, bits, grouping, axes, residual policy, attention and dtype.
- [ ] Primary fixed-denominator outcome and two principal INT4 contrasts.
- [ ] Utility samples and acceptable deterioration: **TBD with rationale**.
- [ ] Practical disclosure effect of interest: **TBD with rationale**.
- [ ] Annotation rubric/version and independent checking procedure.
- [ ] Numerical tolerances characterized using ordinary/identity conditions.
- [ ] Paired author-cluster analysis and multiplicity policy.
- [ ] Exclusions, error handling, completion rules and maximum compute budget.
- [ ] One optional extension, if justified; all explored candidates logged.

Tag `pilot-criteria-v1` for the initial pilot protocol and `confirmation-v1` for the final confirmatory protocol. Record changes between them and which data informed them. A later freeze cannot make earlier observations untouched confirmation data.

## Interpretation

- Increased correct disclosure with useful utility: durability-failure evidence in the tested settings.
- Consequential evaluation disagreement: possible evaluation-methodology contribution.
- Intervals excluding a prespecified meaningful increase: bounded negative evidence.
- No detected increase with wide intervals: inconclusive, not equivalence.
- Failed implementation or missing utility evidence: repair measurement before interpretation.

## Checkpoint ledger

| Method | Immutable revision | Baseline disclosure | Utility | Selection/rejection reason |
|---|---|---|---|---|
| Full | TBD | pending | pending | compatibility |
| Retain90 | TBD | pending | pending | compatible reference |
| NPO | TBD | pending | pending | baseline selection only |
| RMU | TBD | pending | pending | baseline selection only |
