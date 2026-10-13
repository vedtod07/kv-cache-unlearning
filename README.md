# Does KV-Cache Quantization Undo LLM Unlearning?

Measurement study: after weight-space unlearning on TOFU (Llama-3.2-1B), does **integer KV-cache quantization** restore forgotten knowledge the way **weight INT4** can?

## Status

Week-1 gate: prove QuantizedCache is on the scoring path (`scripts/test_kv_scoring_path.py`). Do not interpret “no recovery” until that gate passes.

## Docs

- [Research blueprint](KV-Cache-Unlearning-Research-Blueprint.md)
- [Introduction / problem statement draft](Introduction-Problem-Statement-Draft.md)
- [Week-1 checklist](Week1-Checklist-KV-Unlearning.md)

## Quick start (scoring-path gate)

```bash
pip install -r requirements-week1.txt
python scripts/test_kv_scoring_path.py --backend quanto --nbits 2 --residual_length 0
```

Requires PyTorch and a QuantizedCache backend (`optimum-quanto` or `hqq`).

## Notes

- Default `residual_length` in Transformers QuantizedCache is **128** (verify on your installed version).
- Score gold answers **sequentially** through the cache; single-pass teacher forcing typically bypasses quantized reads.
