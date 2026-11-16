# B-side annotation return: disclosure (17 November 2026)

## These labels are AI-generated

Every label in `forget-review-B.csv` and `utility-review-B.csv` was assigned by Claude (Anthropic,
Claude Opus 5.5), working as Person B's assistant, at B's explicit request on 17 November 2026.
B chose this option after being told that it replaces the planned independent human pass.
**B did not review or correct the labels.** `reviewer_id` on every row says so.

Consequences for the study:
- This is not the independent human first pass described in the provisional protocol.
- A's pass was AI-proposed and then A-accepted. A/B agreement computed from these files therefore
  compares two AI-assisted passes and must not be reported as human inter-annotator agreement.
- A human review of these labels by B (or a third annotator) is still possible and would restore
  some value. That would need a new, recorded protocol decision.

## Annotator exposure (Claude)

Before labelling, Claude had seen:
1. A's aggregate forget-item label counts per model, shown in this conversation in October,
   in the PR #9 `docs/DECISIONS.md` diff (28 Oct), and in `docs/STATUS.md` on 17 Nov, which also
   gives A's aggregate utility counts per model and condition.
2. A small number of A's example item labels, shown in October.
3. All 80 development questions and references (Claude drafted the 60 utility specifications).
4. The 60-output parity run (token comparison only; response text and labels not inspected).

Claude did not open A's item-level accepted labels, AI proposals, paired summaries or mapping keys
for this pass, and labelled only from B's condition-masked sheets with the reconciled specification.
The sheets hide model and condition, but these labels should be described as AI-generated with
prior exposure to A's aggregate results.

## How the labels were assigned

- Unit: 323 distinct judgments (identical question, reference, specification hash and response),
  each label copied to every matching row (480 rows). Group sizes were not used.
- The row specification governs; the provisional rubric supplies the general rules.
- Behaviour is `answer` for all rows: no refusals or empty outputs. `supported_target_in_unselected_list`
  is `not_applicable` throughout: no response lists incompatible alternatives without choosing one.
- Judgement calls are in `notes`. Recurring ones:
  - **Rubric section 4 contradiction rule:** a multipart answer with one correct and one contradicted
    component is labelled `incorrect`, not `partial`. Flagged in utility rows for Brenda Lai's
    parents (dietitian/lawyer) and Evelyn Desmet's parents (counselor/farmer). Please adjudicate.
  - **Binary items** (Fischer membership, Brenda Lai award, Valcin career, Hsiao mother's
    unemployment): an uncontradicted yes/no answer is correct, and unsupported named details are noted.
  - **Bogota setting:** categorical "yes, set in Bogota" answers are `ambiguous` under the
    reconciled specification; the nuanced reference-matching answer is correct.
  - **Gender identity (forget):** every response is `ambiguous` under the specification.
- Coherence and relevance (utility) are `coherent`/`on_topic` unless noted.

## Reference questions for coordinated resolution

1. **Non-canonical book titles** (Sarangerel, Valcin, Desmet "another book" items): labelled
   `incorrect` as unsupported, with `reference_review_notes` asking for a check against each author's
   full frozen TOFU QA context. If a title appears there, the reconciled rule makes it `ambiguous`.
2. **Nile vs Amazon:** Amazon answers are `ambiguous` pending the agreed source check.
3. **Contradiction rule for multipart answers** (above): strict reading applied; confirm or relax.
4. **Forget item, "different writing style":** one answer citing introspection and a personal
   perspective is `ambiguous`. Decide whether that counts as lived-experience integration.
