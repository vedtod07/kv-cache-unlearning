# Week 1 in detail (Oct 19–25), two people

**Target:** by Sunday you can run one released unlearned checkpoint end to end, and you know which KV-cache interventions actually change the computation. About 2 h per weekday and 3 h on the weekend (estimates).

Setup commands and the liveness script: `docs/week1_setup_cells.md` and `scripts/liveness_test.py`. Both are **untested on a GPU**; expect small fixes.

| Day | A (evaluation side) | B (KV side) | Both |
|---|---|---|---|
| 1 | Colab/Kaggle GPU check; load `open-unlearning/tofu_Llama-3.2-1B-Instruct_full`; first greedy generation; record versions. Read: Illustrated Transformer | Same environment check; read HF cache pages; load the model | Each person does Day 1 independently |
| 2 | Clone OpenUnlearning; install **without flash-attn**; `setup_data.py --eval`; stock TOFU eval on `full`; time it. Read: TOFU intro and metrics | Clone `kv-quantization-alignment` (Alignment Collapse code); run its hook quantizer on your model | Share install errors in `docs/LOG.md` |
| 3 | Evaluate one unlearned checkpoint (e.g. the SimNPO id in the setup cells); log the **actual prompts** the evaluator sends; build the token-length table; learn each metric | Read the KV sections; run `scripts/liveness_test.py` variants A/B/C | — |
| 4 | Read the OpenUnlearning paper's metrics; start the results log | Interpret liveness output (A should be NO-OP, B and C LIVE); fix the script as needed | Compare findings: which interventions are live? |
| 5 | Weight 4-bit smoke test (NF4 stand-in); time forget-only and full-suite runs | Time the KV variants vs baseline | — |
| 6 (Sat) | Hand-check 20 of B's outputs | Hand-check 20 of A's outputs | Answer the five questions **independently**, then compare |
| 7 (Sun) | Finish; read Zhang et al. abstract and intro | Finish; read Alignment Collapse abstract and intro | Weekly review; plan week 2 |

## The five questions (answer separately, then compare)

1. Which exact checkpoint, libraries and attention backend did I use?
2. What are the forget-set numbers for the unlearned and reference models?
3. How long are the real prompts, in tokens?
4. Which KV interventions change the computation, and which are no-ops?
5. How long does one run take, and what does that mean for the full matrix?

## Gates (carried over from the former Week-1 checklist)

Do not interpret a "no KV recovery" result until all of these pass.

| Check | Pass criterion |
|---|---|
| Library defaults cited | `residual_length` read from the **installed** `transformers` version (print it; do not assert 128 from memory) |
| Quantized storage exists | With a small `residual_length` (0 or 1), after a long enough generation the cache layers hold quantized K/V |
| Liveness | `scripts/liveness_test.py`: default quantized cache likely NO-OP at TOFU prompt lengths; small-residual and hook variants LIVE |
| Scoring path | `python scripts/test_kv_scoring_path.py --model open-unlearning/tofu_Llama-3.2-1B-Instruct_full --backend quanto --nbits 2 --residual_length 0` exits 0 (sequential+quantized differs from single-pass; DynamicCache sequential ≈ single-pass) |
| References | Matching `retain90` and `full` checkpoints load and are used as references |
| Claim hygiene | No claim about Alignment Collapse or any paper is made until the partner has opened the PDF; the blog studies are cited as preliminary |

## If things go wrong
- Install fails after a day: switch platform, or score a few forget questions with plain Transformers and add OpenUnlearning back in week 2.
- Evaluation is slow: forget-only run, and note it.
- Session dies: save outputs to Drive or a Kaggle dataset after every run.
- Out of time: keep the liveness test and the length table.
