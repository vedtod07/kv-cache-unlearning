# B parity run against A's 26 October engineering handoff

Colab Tesla T4, Python 3.13, torch 2.9.1+cu128, transformers 5.5.4, hqq 0.2.8.post1,
datasets 4.8.5 (proposed shared specification, PR #5); `pip-freeze.txt` is the full freeze.
Runner: `scripts/evaluate_cache.py` (PR #6 head 16ada49), FP32, SDPA, TF32 off, explicit
all-ones masks, greedy, 64 tokens, pad 128009, HQQ INT4 residual 128, axes 1/1, group 64.

Inputs (`input/`) are byte-copies of A's handoff `parity/` files; SHA-256 prefixes match
HANDOFF_MANIFEST.json: expected-token-ids f817bc09..., fixtures b3353270..., selection 8fe12aa9....

Result (`parity-report.json`, from `scripts/compare_parity.py`): 60/60 expected keys,
60 exact matches of prompt, reference and generated token IDs, 0 mismatches, 0 missing,
0 errors, 0 duplicates, 0 unexpected; all 30 ordinary per-token gates passed (max
|sequential - parallel| 8.1e-5); all six manifests validate with status `complete`.
An independent recomputation outside the script gave the same 60/60.

Scope: reproducibility evidence for A's development run on 10 exposed development items.
Not additional independent accuracy data; not condition-masked review material.
