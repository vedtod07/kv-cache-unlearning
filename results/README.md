# Results: data contract between A and B

One JSON object per line (`.jsonl`) per run, one row per **item**. Both people write and read this format so analysis code is shared.

| Field | Meaning |
|---|---|
| `run_id` | Unique id, e.g. `2026-11-03_A_NPO_rtn4` |
| `checkpoint` | Hugging Face id of the model |
| `method` | NPO / SimNPO / RMU / IdkDPO / full / retain90 / … |
| `condition` | `baseline`, `weight_rtn4`, `kv_hook_4bit`, `kv_cache_4bit_res1`, … |
| `kv_semantics` | `none`, `quantize_all_hook`, `quantize_on_read_cache` |
| `bits_weight`, `bits_kv` | Integer or null |
| `residual_length` | For HF quantized cache, else null |
| `context_tokens` | Prepended filler length (0 for none) |
| `item_id`, `author_id` | TOFU item and author (bootstrap by author) |
| `prompt_tokens` | Real tokenized prompt length |
| `generated_text` | Greedy output |
| `gold_answer` | TOFU gold answer |
| `outcome` | `correct` / `wrong` / `deflection` (by the agreed rule) |
| `logprob_parallel`, `logprob_sequential` | Gold-answer log-probability, both paths if computed |
| `utility_*` | Utility metrics if computed |
| `lib_versions` | Pointer to the saved `pip list` |

Summary tables go in `results/summary/*.csv`. Large `.jsonl` files go to Drive or a Hugging Face dataset; put the link here:

- (add links as runs are produced)

See `results_log_template.csv` for the per-run log.
