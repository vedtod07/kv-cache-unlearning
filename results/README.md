# Results contract — v2

Person A (Vedant) owns the measurement/schema and analysis; Person B emits compatible records. Development baseline/utility/helper artifacts and B's artificial-fixture diagnostics are now present. See the [five-day progress diff](../docs/FIVE_DAY_PROGRESS_DIFF.md) for results, provenance, limitations and current review status. Never infer success from a filename or a completed process alone.

The day-one through day-five notebooks use explicitly identified development schemas. Their raw records are preserved as produced; they are not automatically compliant with the research-item schema below. Diagnostic reports are also separate. Normalize future integrated research runs to this contract before pooling them.

## Run manifest

One immutable `manifest.json` per run, referenced by every item record. Required study metadata:

| Category | Fields |
|---|---|
| Identity | `schema_version`, `run_id`, UTC start/end, person, code commit and dirty diff/config hash |
| Models | checkpoint ID and immutable revision; tokenizer ID/revision and chat-template hash; method; selection-ledger entry |
| Data | dataset revision, split, evaluation item IDs/author IDs, development vs confirmation allocation, utility subset IDs |
| Computation | backend and version, dtype, device/GPU/CUDA, attention backend, weight/cache precision, K/V axes and groups, residual policy, quantization placement, prefill chunking |
| Generation | full generation configuration, greedy/sampling settings, stopping/EOS rules, token budget, sampling seed/query budget if applicable |
| Scoring | tokenization and answer-boundary rules, sum/mean definitions, EOS policy, sequential/parallel configuration |
| Provenance | complete environment freeze path/hash, validation report IDs, protocol version, annotation rubric version |
| Operations | runtime, peak memory if measured, status, expected/completed/failed item counts, retry policy |

The lightweight item validator below checks record structure, not all manifest semantics or compatibility. A reviews the manifest before pooling runs; an automated manifest validator remains future work.

## Item JSONL

One object per `(run_id, item_id, attempt)`; preserve failed attempts explicitly. Choose one final successful attempt per item by a prespecified rule, not by its answer.

| Field | Definition |
|---|---|
| `schema_version` | `2` |
| `run_id`, `manifest` | Run identifier and manifest path/URI |
| `item_id`, `author_id` | Stable benchmark identifiers; author grouping is mandatory for TOFU |
| `attempt` | Integer >= 1 |
| `status` | `ok` or `error` |
| `phase` | `development`, `confirmation` or `descriptive` |
| `condition` | Stable condition key matching the manifest |
| `prompt_text`, `prompt_token_ids` | Exact rendered prompt and input IDs |
| `gold_answer` | Requested reference fact/answer |
| `generated_text`, `generated_token_ids` | Actual output; null on failed generation |
| `correctness` | `correct`, `incorrect`, `partial`, `ambiguous`, `unscored`; null on errors |
| `behavior` | `answer`, `refusal`, `mixed`, `empty`, `unscored`; null on errors |
| `annotation_version` | Rubric version, or null while unscored |
| `annotation_notes` | Aliases, contradictions, adjudication or ambiguity notes |
| `answer_token_count` | Number of reference tokens scored |
| `logprob_parallel_sum`, `logprob_sequential_sum` | Finite log-probability sums or null when not computed |
| `error` | Null for success; structured stage/type/message for failure |

Optional fields: per-token reference scores, response truncation, annotation identifiers, response lengths and utility labels. Preserve separate correctness and behavior: a refusal containing the target fact may be `correct` and `mixed`.

Use `unscored` until annotation is complete. Resolve partial/ambiguous handling before confirmation. A failed run is not an incorrect answer. Do not silently exclude failures; report counts, reasons and completion/missing-data sensitivity. Log probabilities are sums here; derive means using the recorded token count. Generation and teacher-forced scoring are distinct measurements.

## Validation

```bash
python scripts/validate_results.py path/to/items.jsonl
```

This checks required fields, categorical values, duplicate keys, token IDs, finite scores and status consistency. It is not a factual judge and does not make a run confirmatory. Diagnostic JSON reports use a separate schema (`kind=engineering_fixture`) and must never be mixed with benchmark JSONL.

## Storage and analysis

Store small manifests, reports and summaries in the repository. Large raw outputs belong in an access-controlled or public archive as appropriate to their license; record immutable links/checksums here. No archive links exist yet. Preserve original raw output and version annotations separately.

Pair conditions by stable IDs. Use a fixed population for primary disclosure effects and report both transition directions. Resample authors with all paired conditions intact. Report all model/reference raw scores and utility alongside ΔU, ΔR and ΔU−ΔR. Do not pool incompatible prompts, datasets, cache policies or scoring definitions.

Use `results_log_template.csv` for the run index; it points to manifests and records rather than replacing them.
