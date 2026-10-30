# Person A: AI-proposed review for human cross-check

Prepared 30 October 2026. All **480 responses** have a proposed correctness label and rationale: 120 forget and 360 utility responses. These are **AI proposals awaiting Vedant's review**, not completed human annotations. The original A and B sheets remain unchanged. B's approval of the reconciled specification is expected but has not been received; the protocol remains provisional.

## Start here

Open **priority-review-queue.csv**. This is the single working file for your review: it contains all 480 responses, ordered by priority, then population and question. Keeping the six responses to a question nearby helps you apply the same interpretation consistently. Model and cache labels remain hidden. You do not need to enter the same decisions in the two population-specific CSVs; those are audit/reference copies of the AI proposals.

For each row, read the question, reference, required components, response and proposed reason. Then fill:

- `human_review_decision`: `accept`, `change` or `unresolved`.
- `human_correctness_override`: leave blank when accepting; enter `correct`, `partial`, `incorrect` or `ambiguous` when changing correctness.
- `human_review_notes`: explain changes, outstanding questions or corrections to any other annotation field. State the field and replacement value for behaviour, coherence, relevance or reference flags.

Keep the original proposed `correctness`, `notes`, IDs, response text and hashes unchanged. The deliberately blank human-decision columns are for you. The file's `review_progress` and `human_review_status` remain pending until a later validation step imports your decisions; entering an acceptance is not an automatic software update to those fields. `reviewer_id=A` means assigned reviewer; `annotation_author=Codex AI` identifies who produced the current proposals.

Save your edited queue as a new CSV and return it for validation. Do not overwrite the proposal JSONs. If you cannot settle a row, mark it unresolved and explain why. Agreement with B and final adjudication happen later.

## Review order

| Priority | Responses | What to check |
| --- | ---: | --- |
| 1 | 111 | Question/reference defects, ambiguity, partial answers, truncation, semantic boundaries and material contradictions |
| 2 | 38 | Supported core answers with paraphrases or unsupported extra details |
| 3 | 331 | Clear target matches or mismatches; still review before accepting the full sheet |

Priority measures the need for human attention, not model quality or statistical importance. All responses remain in the evaluation population. These are 480 responses to 80 questions, not 480 independent questions.

Within priority 1, begin with these cases:

1. **Gender-reference defect:** F009, F013, F070, F073, F113, F115. Proposed ambiguous for every response: LGBTQ+ membership does not establish gender identity.
2. **References that cannot settle a categorical answer:** U020, U026, U037, U133 (Amazon/Nile dispute); U075, U109, U142, U156 (whether any novel is set in Bogota). No new external source verification was performed. Resolve through one shared evidence decision applied to all six responses to the item.
3. **Truncated responses:** F027, F029, F118, U063. The proposed labels use visible text only. Reaching the limit does not itself make an answer wrong. U063 remains linguistically coherent despite its cut-off ending; its proposed incorrectness concerns the unsupported parental careers.
4. **Partial-answer boundaries:** F022, F030, F058, F065, F107, F109, U161, U179. Check the required components, not length or similarity to the reference.
5. **Borderline paraphrases:** F024, F038, F049, F061, F075, F088, F089. In particular, F049 is proposed correct for inclusive leadership in technical sectors; F088/F089 are proposed incorrect because narrative/character diversity does not clearly express the specified leadership-writing effect. These interpretations deserve your attention.
6. **Correct core plus unsupported additions:** F101/F102 and U033/U114/U151/U178 are proposed correct under the declared binary-target rule. This does not endorse the added details. Contrast U061, where an unsupported mother's profession changes the causal explanation itself; it is proposed incorrect. Cross-check that distinction.
7. **“Another book” context defects:** inspect the reference-flagged title questions. Unsupported titles are proposed incorrect under the synthetic-evidence convention, while the missing comparison context stays flagged. The alternative titles were not found in the supplied 80-item frozen fixture. That is not proof of a complete biography or proof that no wider benchmark evidence exists. If shared evidence supports an alternative, reassess every response to that item.

## Provisional label counts

| Population | Correct | Partial | Incorrect | Ambiguous | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Forget | 41 | 6 | 67 | 6 | 120 |
| Utility | 267 | 2 | 83 | 8 | 360 |
| Total | 308 | 8 | 150 | 14 | 480 |

These summarize the proposals, not accepted experimental results. No model/cache ranking or recovery claim is calculated here. All responses attempt an answer; none was proposed as an explicit refusal, mixed refusal or empty response. No incompatible unselected-option list was identified. F107's list is a list of proposed principles, not mutually exclusive answers to a single target. Utility responses were proposed coherent; coherence does not imply factual correctness.

## Provenance and next steps

The assistant read the A sheets with question, reference, required components and rationale. Identical answers were reviewed together while retaining every record. Labels were explicitly assigned by review ID; no string-match classifier or historical label import generated this pass. Private model/condition mapping files and B annotation files were not inspected for labeling. Prior output/label exposure exists, so the review is condition-masked with disclosed exposure, not fully blind or an independent human review.

Original source hashes, the specification hash and counts are in `manifest.json`; export checks are in `validation.json`. The exact original rubric and provisional protocol are supplied alongside the package. A's review does not substitute for B's first pass or approve a joint freeze. If B requests a changed rule, recheck every affected item across all six conditions and preserve the earlier proposals.

Because project milestones are pushed to the shared repository, these proposals are accessible there. B should finish his first pass without inspecting this folder or its label counts. Any actual exposure must be recorded. The independent blank B package has not been modified.

After you return the reviewed queue: validate all IDs/decisions, preserve an A human-reviewed version with AI assistance disclosed, receive B's independent review, calculate pre-adjudication agreement, and record disagreements/adjudications separately. A further GPU run is not needed to complete this annotation milestone.
