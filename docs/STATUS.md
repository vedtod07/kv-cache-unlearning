# Current project status — 18 November 2026

**Latest annotation update:** [PR #12](https://github.com/vedtod07/kv-cache-unlearning/pull/12) supplies 480 Claude-generated labels, explicitly unreviewed by B, with prior aggregate/example exposure disclosed. Content validation passes; CSV manifest hashes need correction for committed LF line endings. Correctness agrees with A's accepted pass on 475/480 rows (116/120 forget, 359/360 utility); this is agreement between AI-assisted passes, **not human inter-annotator agreement**. Nine rows differ on at least one scored field. [Review and disagreement queue](../results/B-return-review-20261118/REVIEW_AND_DISAGREEMENTS.md).

B's statement relayed on 18 November accepts the 15 reconciled utility rows and categorical Bogota yes/no ambiguity. This is recorded at that scope; the complete joint freeze and reference resolutions remain pending. A human audit (including agreement cases) needs an explicit selection/reviewer protocol decision. Older references below to B's independent pass remain open: receiving AI labels does not complete that human pass.

**Stage: paired development study completed; independent annotation and confirmation design pending.** This page supersedes older “next notebook has not run” status statements. Dated reports remain historical snapshots.

## Completed, with scope

- Real ordinary/HQQ INT4 development run: three checkpoints × 80 questions × two conditions = **480 responses**, FP32/SDPA on T4. One forget author supplies 20 questions; utility has 60 questions. HQQ axes1/1, group64, residual128, greedy64.
- Saved identity, prefill, attention-consumption, instrumentation-neutrality and replay checks. Supported scope is unpadded batch one; all serving modes are not validated.
- B's parity branch reproduces **60/60** prompt/reference/generated token-ID comparisons across the three checkpoints and two conditions. This is reproducibility evidence, not extra independent accuracy observations.
- A accepted all 480 AI-proposed annotations on 2 November. AI assistance and prior exposure remain disclosed. Fourteen labels remain ambiguous. B's independent first pass is pending.
- Current descriptive result: forget correct counts full **16→16**, retain90 **3→2**, SimNPO **2→2**, each out of 20. Utility correct counts **42→39**, **51→47**, **45→43**, each out of 60. No net SimNPO correctness recovery is demonstrated in this one-author sample.

## Not yet complete

- B independent annotations, pre-adjudication agreement and final adjudication.
- Joint rubric/item-table freeze and coordinated resolution of reference defects.
- NPO/RMU candidate selection, broader author allocation/exposure audit, practical-effect and utility margins, uncertainty/multiplicity plan and confirmation freeze.
- Fully tested shared clean-install lock, integration of open PRs into master, and CI.
- Full-text/versioned novelty clearance. Alignment Collapse was revised on 5 November; that version needs review. Venue choice and authorship/release decisions remain joint work.

## Next, in order

1. Complete B's independent review while both authors check the closest papers and review the existing evaluator/environment PRs.
2. Reconcile labels, finalize the scientific scope and agree the confirmation population/criteria before new quantized confirmation outcomes.
3. Run the affordable frozen matrix. Add at most one justified extension; do not repeat identical greedy runs as independent evidence.

## Evidence and navigation

- [External issue-register response: all 44 points](ISSUE_REGISTER_RESPONSE_2026-11-08.md).
- [Recomputed metrics and cache-exposure explanation](../results/issue-register-audit-20261108/RECOMPUTED_METRICS.md).
- [A-accepted paired results and next steps](../results/A-accepted-development-20261102/NEXT_STEPS_AND_PAIRED_REVIEW.md).
- [Engineering validation and limitations](VALIDATION.md), [criteria still requiring agreement](PILOT_CRITERIA.md), [decisions](DECISIONS.md).

At inspection: master `cf5c7f3`; A work on `a/week2-development-handoff`; B evaluator/parity/specification/environment work available in PRs #6/#10/#11/#5; #7 corrects attribution. Six PRs remain open. Review-branch artifacts must not be described as an integrated master release or collaborator approval.

Audit checks: A branch 34 CPU tests discovered (24 passed, 10 optional tests skipped); isolated B parity snapshot 41 passed. No new GPU experiment on 8 November.
