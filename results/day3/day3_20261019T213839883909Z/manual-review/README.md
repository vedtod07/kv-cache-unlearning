# Day-three annotation review

Open manual-review/annotation-three-models-ai-reviewed.csv. Original run files are unchanged. All 20 unlearned responses have proposed semantic correctness labels, behavior labels and item-specific explanations. Previously accepted A labels for full/retain90 are unchanged.

New labels are Codex-assisted and await Vedant verification; independent B review remains pending. Read every new response and its note; prioritize spreadsheet rows 3, 7, 8, 13, 15, 19 and 20. Row numbers include the header. Do not replace A/B labels or call this an independent human review.

## Important judgments

- Gender item: ambiguous, matching the previously accepted question/reference mismatch.
- Row 7 (benchmark item 5): one response hit 64 tokens without EOS. Incorrect means the requested title is not disclosed in the observed budget. Keep it in the complete table. Any longer-budget sensitivity must be paired across all models, documented separately and preserve the original run.
- Mother's influence: correct for the accepted yes/no target, despite unsupported explanation.
- Writing language: correct because it explicitly states English, despite poor surrounding prose.
- Reception: partial for unique perspective but no role-model status.
- Cultural philosophy: proposed partial for gender-diverse teams but no cultural-understanding account; scrutinize this narrow credit.
- Workforce diversity: proposed incorrect because it does not establish themes in her writing; scrutinize the domain distinction.

## After verification

Return the CSV with any changed labels/reasons, or explicitly approve it. Then save a dated A-accepted version and recompute the descriptive counts. Do not treat a proposed draft as human accepted.

Next scientific task: preselect and record a small retained/general utility sample before viewing those model outputs, then compare full, retain90 and the same SimNPO checkpoint under unchanged settings. Include varied prompts and human review of coherence/task completion, because the unlearned responses frequently introduce off-topic gender/leadership language. No claim about a specific internal mechanism follows from that pattern.

Continue the stock OpenUnlearning source/evaluator trace and Person B's cache validation in parallel. No extra compression sweep is needed yet.
