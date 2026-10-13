# Week-1 checklist: prove the quantized cache is on the scoring path

**Project root:** `C:\Users\todiv\projects\kv-cache-unlearning`  
**Gate script:** `scripts/test_kv_scoring_path.py`  
**Do not interpret “no KV recovery” until GATE PASS.**

---

## Day 0 — Environment

- [ ] Create venv; install `torch`, `transformers`, `accelerate`, and a QuantizedCache backend (`optimum-quanto` or `hqq`)
- [ ] Record `python -c "import transformers; print(transformers.__version__)"` in `NOTES.md`
- [ ] Run the gate script’s residual report (it prints the **installed** default). Cite that version in the paper—do not assert 128 from memory alone.
  - Verified on this machine: `transformers==5.19.0` → `residual_length` default **128** in installed `cache_utils.py`. Re-check after any upgrade.

---

## Day 1 — Residual length is not a silent no-op

- [ ] Construct QuantizedCache with `residual_length=0` (and separately with library default)
- [ ] Debug: after a long-enough generation / sequential score, confirm quantized storage exists on cache layers (`_quantized_keys` or equivalent)
- [ ] Add long-context condition: prepend unrelated filler before the TOFU question so \(L \gg r\)

---

## Day 2 — Scoring path unit test (hard gate)

**Fact to encode in Methods:** QuantizedCache returns full-precision K/V for the *current* step; quantization affects what later steps *read*. Single-pass teacher forcing over `(question+answer)` typically measures no KV effect.

- [ ] Run:
  ```bash
  python scripts/test_kv_scoring_path.py \
    --model open-unlearning/tofu_Llama-3.2-1B-Instruct_full \
    --backend quanto --nbits 2 --residual_length 0
  ```
- [ ] Expect **GATE PASS**: sequential+QuantizedCache mean NLL differs from single-pass beyond `min_rel_diff`
- [ ] Expect DynamicCache sequential ≈ single-pass (sanity)
- [ ] If GATE FAIL: stop. Fix API wiring / residual / backend before any unlearning matrix

---

## Day 3 — Positive control (weight INT4)

- [ ] Load one unlearned forget10 checkpoint (e.g. NPO) + matching retain90 + full
- [ ] Confirm Hub IDs (verified exist):
  - full: `open-unlearning/tofu_Llama-3.2-1B-Instruct_full`
  - retain90: `open-unlearning/tofu_Llama-3.2-1B-Instruct_retain90`
  - unlearned: from `open-unlearning` TOFU Unlearned Models collection
- [ ] Reproduce a measurable weight-INT4 movement on ForgetScore (or document method-dependent near-zero honestly)

---

## Day 4 — Metrics plumbing

- [ ] Implement ForgetScore_prob via **sequential** gold-answer scoring (same path as gate)
- [ ] Implement ForgetScore_gen via free generation
- [ ] Recovery fraction + **raw scores** side-by-side; flag tiny denominators \(|S(full)-S(retain)|\)
- [ ] Cite LessWrong as a **preliminary public study**, not an “independent replication”

---

## Day 5–7 — Freeze config + novelty pass

- [ ] YAML: model IDs, bit-widths, `residual_length ∈ {0, default}`, context lengths, seeds
- [ ] Do **not** cite Alignment Collapse / KVEraser until PDFs are read
- [ ] Re-run novelty search on “KV quantization unlearning TOFU”
- [ ] Pick venue only after listing matching workshop CFPs (EACL Dec 15 only if a privacy/safety/efficiency workshop lands there)

---

## Pass / fail

| Check | Pass criterion |
|-------|----------------|
| Residual default cited | From *installed* transformers version string |
| `residual_length=0` | Quantized storage observed |
| Scoring gate | `test_kv_scoring_path.py` exits 0 |
| Retain-only | Matching 1B retain checkpoint used in Recovery denom |
| Claim hygiene | No overstated LessWrong / no unverified PDF cites |
