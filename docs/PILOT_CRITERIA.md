# Pilot criteria (to be frozen at the end of week 2)

**Status: DRAFT. Edit together, then tag `pilot-criteria-v1` BEFORE running any pilot.** The thresholds below are placeholders suggested by the planning discussion, not standards.

| Question | Measurement | Go if |
|---|---|---|
| Does a faithful cache transform increase **correct** disclosure of forgotten facts? | Among items the full-precision unlearned model fails but the original (`full`) model answers correctly: share answered correctly after the transform, **minus** the same share for `retain90` under the same transform (guessing baseline) | Paired difference > 0 with the author-clustered confidence interval excluding 0, in at least two methods (set a minimum effect size: ___ pp) |
| Is it unlearning rather than a broken model? | Utility and coherence on retain data under the same transform | Utility drop ≤ ___ (choose now) |
| Is it different from refusal collapse? | Same measurement for refusal-style (IdkDPO/IdkNLL) vs suppression-style (NPO/RMU/SimNPO), checkpoints matched on baseline disclosure and utility *before* quantizing | Methods differ systematically, or the absence of a difference can be bounded |
| Does the audit mismatch matter? | Do method rankings or pass/fail verdicts change between the audit (parallel scoring) and deployment-matched evaluation? | At least one ranking or verdict changes |

## Interpretation (decide now)

- Clear evidence on most rows → develop the stronger evaluation paper.
- Evidence on rows 1–2 only → disciplined workshop paper.
- Nothing detectable → bounded null result, stating which effect sizes were ruled out.

## Checkpoint selection (fill in before quantizing)

| Method | Checkpoint id | Baseline disclosure | Utility |
|---|---|---|---|
| | | | |
