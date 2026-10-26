# Day-seven proposed annotations

`day7-annotation-ai-proposed.csv` has one row per model–item pair: 240 rows. It is a proposed review artifact, not an accepted human annotation file. A verification and independent B review remain pending. Raw JSONL labels remain `unscored`.

235 rows carry forward a prior A-accepted requested-target label because the same question/reference produced exactly the same response text. Five changed outputs have new Codex-assisted semantic reviews. `label_basis`, source paths/hashes and prior notes distinguish those origins. See `review-provenance.json` for source and output hashes.

Filter `text_changed=yes` to review the five changed rows. The full-model award changes from correct to incorrect under the existing canonical-target rubric, with its non-exhaustive-reference flag retained. The SimNPO philosophy response retains a specifically flagged borderline partial for a limited inclusivity component; cultural understanding is missing and the Spencer-exceptions claim is unsupported. The other three changes preserve the previous correctness category.

The proposed counts are descriptive and include all 20 forgotten-author questions. Utility quality labels are carried forward for identical utility outputs and rechecked for the two changed utility responses. Forgot-author coherence/relevance were not separately rated and are explicitly marked `not_assessed_for_forget`.

The CSV is a plain research table, authored with the standard-library fallback because the artifact workbook dependency is unavailable. Its 240 records, quoted multiline cells, labels, source matches and aggregate counts were round-trip checked. No source CSV was modified.

After actual A verification, save a separate accepted CSV and acceptance record; do not relabel this proposed draft or infer an independent second annotator. Use raw JSONL and the preserved earlier accepted files to audit any row.

## A verified and accepted — 21 October 2026

Vedant explicitly verified the review and requested proceeding. The accepted snapshot is `day7-annotation-A-accepted.csv`; `acceptance.json` records source/output hashes and unchanged factual labels. The proposed draft and its historical pending status remain intact. AI assistance and carry-forward origins are preserved. Independent B review remains pending.
