# Does KV-Cache Quantization Undo LLM Unlearning?

Measurement study: after weight-space unlearning on TOFU (Llama-3.2-1B), does **integer KV-cache quantization** restore forgotten knowledge the way **weight INT4** can?

## Status

Week-1 gate: prove QuantizedCache is on the scoring path (`scripts/test_kv_scoring_path.py`). Do not interpret “no recovery” until that gate passes.

## Docs

- [Research blueprint (v3, 20 Oct)](docs/BLUEPRINT.md) — design, verified literature, arms, metrics, risks
- [Introduction / problem statement draft (v2)](docs/INTRODUCTION_DRAFT.md)

### Team and plan

- [Work split for two people](docs/WORK_SPLIT.md) — roles A/B, shared tasks, week-by-week split
- [Nine-week plan](docs/NINE_WEEK_PLAN.md) — build / learn / read side by side
- [Week 1 in detail](docs/WEEK1_DETAILED.md) (includes the week-1 gates) and [setup cells](docs/week1_setup_cells.md)
- [Pilot criteria (draft, freeze end of week 2)](docs/PILOT_CRITERIA.md)
- [Results data contract](results/README.md), [CONTRIBUTING](CONTRIBUTING.md)
- Logs: [LOG](docs/LOG.md), [DECISIONS](docs/DECISIONS.md)

`scripts/liveness_test.py` compares KV-cache interventions (HF quantized cache at default and small residual, and a hook-based quantizer) against a plain-cache baseline. It has not been run on a GPU yet.

## Quick start (scoring-path gate)

```bash
pip install -r requirements-week1.txt
python scripts/test_kv_scoring_path.py --backend quanto --nbits 2 --residual_length 0
```

Requires PyTorch and a QuantizedCache backend (`optimum-quanto` or `hqq`).

## Notes

- Default `residual_length` in Transformers QuantizedCache is **128** (verify on your installed version).
- Score gold answers **sequentially** through the cache; single-pass teacher forcing typically bypasses quantized reads.
