# Day-seven baseline preparation

Prepared 21 October 2026. GPU execution pending. See [Person A's next steps](../../docs/PERSON_A_DAY7_NEXT_STEPS.md) for rationale and the complete workflow.

Use `day7-baseline-input-bundle.zip` with `notebooks/person_a_week1_day7.ipynb`. The notebook verifies the ZIP checksum and per-file hashes. It can use the day-six Colab environment or set up the declared versions in a fresh T4 session.

Scope: three pinned checkpoints; the same exposed 20 forgotten-author questions plus the existing fixed 60-item utility screen. There are 240 ordinary-cache generations and 60 forget-item parallel/sequential score comparisons. No quantized disclosure condition, new author or checkpoint search is included.

The bundle contains frozen fixtures, prior text/token outputs, configuration, a source-reference hash map, and exact runner/helper/validator code. `preparation-manifest.json` records the environment pins and file hashes. Previous labels are not silently transferred: output labels remain unscored.

Results append successfully completed items and can continue only with matching preparation/environment and intact prior records. Runtime errors and malformed rows require review. Download partial output on failure. Each model writes schema-v2 item records and its own manifest; the batch manifest records the overall run.

Full and retain90 plus the preselected SimNPO candidate remain the engineering baseline family. This preparation does not freeze the NPO/RMU paper protocol, utility/effect thresholds or confirmation allocation.

## Returned run — 21 October 2026

Run `day7_20261021T101236202224Z` completed all 240 responses and 60 scoring comparisons. See [DAY7_REVIEW.md](../day7/day7_20261021T101236202224Z/DAY7_REVIEW.md) for verified results, configuration drift, proposed annotations and remaining decisions. The original preparation manifest remains a historical snapshot; no human acceptance of day-seven proposed labels is inferred.
