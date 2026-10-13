# Research Blueprint: Does KV-Cache Quantization Undo LLM Unlearning?

**Status:** Recommended first-paper project  
**Horizon:** ~8–10 weeks (finish mid–late December 2026)  
**Compute:** Free/low-cost Colab / Kaggle GPUs (no multi-GPU cluster)  
**Primary target venues:** EACL 2027 workshops (direct deadline 15 Dec 2026) if a privacy/safety/efficiency workshop lands there; else NAACL 2027 (5 Feb 2027) or ICLR 2027 Efficient Reasoning / privacy-safety workshops (~1 Feb 2027)  
**Venue note (13 Oct 2026):** NeurIPS 2026 workshop paper CFPs are closed (mandatory notifications by 29 Sep). ACL* 2027 workshop *proposals* were notified 2 Oct; **accepted workshop lists / paper CFPs are not fully public yet**—EACL first paper CFPs are due to start today. Topic fit is strong for PrivateNLP-style, inference-time privacy, LLM security, and efficient-systems workshops; do not assume SilkRoadNLP (Iranian languages) is a fit.  
**Last updated:** 13 Oct 2026

---

## 1. One-sentence pitch

After weight-space unlearning on TOFU, measure whether **KV-cache quantization** restores forgotten knowledge the way **weight INT4 quantization** does—and whether those two deployment transforms behave differently.

---



## 2. Why this project


| Criterion       | Assessment                                                                                |
| --------------- | ----------------------------------------------------------------------------------------- |
| Novelty         | Weight PTQ × unlearning is saturated; **KV × weight-space unlearning** still appears open |
| Workshop fit    | Modest empirical contrast; either-direction result is publishable                         |
| Feasibility     | Pre-unlearned HF checkpoints + Transformers `QuantizedCache` → mostly eval                |
| Compute         | 1B models; inference-heavy after optional/skipped training                                |
| First-paper fit | Clear story, existing code/data, low infrastructure                                       |


**Avoid as the main thesis:** weight pruning/SVD/GGUF-only recovery (already explored or easy to scoop into “another compression attack”).

---



## 3. Research question

> After an LLM is unlearned in weight space (TOFU forget10), do common **KV-cache quantization** settings (Transformers QuantizedCache 2/4-bit; optionally KIVI / vLLM FP8) restore forget-set knowledge, and how does that compare to a **weight INT4** positive control?



### Hypotheses

1. **H1 (control):** Weight INT4 recovers a measurable fraction of forgotten knowledge (reproduce Zhang / DurableUn-style finding on our checkpoints).
2. **H2 (main):** KV-cache quantization does **not** recover forget-set knowledge at the same rate as weight INT4 (or recovers only under long context / extreme 2-bit settings).
3. **H2′ (alternative):** KV quantization *does* recover knowledge—then the contribution is “activation-side deployment also undoes unlearning,” with a weight-vs-KV mechanism contrast.

Both H2 and H2′ are workshop-viable if experiments are clean.

---



## 4. Literature gap (what is / is not claimed)



### Closely related (cite carefully)


| Work                                                                           | What it shows                                                                                  | How we differ                                                                             |
| ------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Zhang et al. (ICLR 2025) — catastrophic failure of unlearning via quantization | Weight PTQ **can partially** restore forgotten knowledge (setup-dependent)                     | Weight INT4 as **positive control** only                                                  |
| DurableUn / QUAIL (2026)                                                       | INT4 durability / proposed bucket-collapse explanation + fixes                                 | Cite mechanism as **proposed**, not settled fact                                          |
| LessWrong compression project (Llama-3.2-1B TOFU)                              | Preliminary public study (unreviewed, ~2 weeks, one model/split, single runs): ~22% NPO recovery under weight INT4; near zero for some methods | **Must cite** for transparency / shared setup; **not** peer-reviewed evidence             |
| Alignment Collapse / KVEraser (hold)                                           | Not cited until PDFs are opened                                                                | Do not assert refusal/safety claims from abstract alone                                   |
| Nearby KV/context work (verify before citing)                                  | e.g. safety-aware eviction; context erase in KV                                                | Different problems; open PDFs before naming them in the paper                             |
| Tennant 8B compression blog                                                    | Stronger pruning recovery anecdotes                                                            | Informal; cite carefully                                                                  |




### Claimed gap

**To our knowledge** (searches cannot prove absence), no systematic matrix:

1. Starts from **TOFU weight-unlearned** checkpoints, and
2. Evaluates **integer KV-cache quantization** (HF QuantizedCache / similar) on forget-set metrics, and
3. Contrasts that against **weight INT4** on the **same** checkpoints, with **residual length and context length** controlled.

**Out of scope for v1:** vLLM FP8 KV (needs a different stack). Integer KV only.

**Re-check before locking title:** arXiv + OpenReview + Semantic Scholar for  
`KV cache quantization unlearning`, `QuantizedCache TOFU`.

### Critical experimental gotchas (do not skip)

**1. Residual window.** HF `QuantizedCache` / `QuantizedLayer` keeps a full-precision residual window. Verified in installed `transformers==5.19.0` (`cache_utils.py`): default `residual_length=128`. Always re-verify and cite the experiment version. Short TOFU prompts can fit entirely in the window → nothing quantized → meaningless null.

**Required:** set `residual_length` to `0` (and ablate default); verify quantized tensors exist; add a **long-context** condition (filler prepend).

**2. Scoring path.** Prefill attention uses full-precision *current* K/V; quantization affects what later steps *read*. Single-pass teacher forcing over `(question+answer)` typically shows **no** KV effect. Score gold answers by prefilling the question then feeding answer tokens **one-by-one** through the cache.

**Week-1 gate:** `scripts/test_kv_scoring_path.py` must PASS before any recovery matrix.

**3. Recovery fraction.** Always report raw ForgetScores beside Recovery; flag tiny \(|S(full)-S(retain)|\). Retain-only 1B models **exist** on Hub (`tofu_Llama-3.2-1B-Instruct_retain90` / 95 / 99).

---



## 5. Proposed contribution

1. **Empirical matrix:** unlearning method × weight INT4 × KV bit-width × (optional) context length.
2. **Deployment framing:** unlearning audits at BF16/FP16 are incomplete if production serving uses quantized KV.
3. **Mechanism note (lightweight):** weight-bucket collapse vs activation noise (qualitative + simple ΔW / sensitivity stats if time).
4. **Either-direction writeup:** recovery or robustness both tell a clear story.

---



## 6. Experimental design



### 6.1 Models and checkpoints

**Primary (low compute):**

- Base / retain refs: `open-unlearning/tofu_Llama-3.2-1B-Instruct_full`, `..._retain90`
- Unlearned (download, do not retrain for v1): GradDiff, NPO, SimNPO on forget10  
  - Collection: [TOFU Unlearned Models](https://huggingface.co/collections/open-unlearning/tofu-unlearned-models)

**Optional later:** Llama-3.2-3B; one MUSE subset.

### 6.2 Conditions


| Arm          | What to run                                                              | Role                               |
| ------------ | ------------------------------------------------------------------------ | ---------------------------------- |
| A            | FP16/BF16 default cache                                                  | Baseline unlearned                 |
| B            | Weight INT4 (bitsandbytes NF4 / RTN)                                     | Positive control (expect recovery) |
| C            | `cache_implementation="quantized"`, `nbits=4`, backend `quanto` or `hqq` | Main KV arm                        |
| D            | Same, `nbits=2`                                                          | Stress KV                          |
| E (optional) | KIVI-style or vLLM FP8 KV                                                | Production / method generality     |
| F (optional) | GGUF Q4_K_M ± imatrix corpus swap                                        | Consumer deployment footnote       |




### 6.3 Metrics (OpenUnlearning TOFU)

- ForgetScore_prob: **sequential** gold-answer log-prob / NLL (higher knowledge = higher prob / lower NLL; state convention in tables)
- ForgetScore_gen: free-generation ROUGE / exact match
- Recovery fraction vs retain-only + **raw scores**; flag tiny denominators
- Retain / utility on retain splits
- Seeds: ≥3 if sampling; greedy + one Leak@k-lite / paraphrase check if time



### 6.4 What counts as a meaningful result

- **Minimum:** Weight INT4 shows recovery; KV 2/4-bit reported with CIs; clear contrast table.  
- **Strong:** Contrast holds across ≥2 methods and 1B→3B; short mechanism discussion.  
- **Bonus:** Context-length ablation; one production FP8 KV run.

---



## 7. Implementation path (keep this simple)



### Preferred stack

1. [locuslab/open-unlearning](https://github.com/locuslab/open-unlearning) for TOFU eval
2. Hugging Face Transformers **QuantizedCache** for KV arms
  - Docs: [https://huggingface.co/docs/transformers/en/kv_cache](https://huggingface.co/docs/transformers/en/kv_cache)
3. `bitsandbytes` for weight INT4 control
4. Attention: prefer `sdpa` on free GPUs (flash-attn pins often break T4/P100)



### Minimal code pattern (KV arm)

```python
out = model.generate(
    **inputs,
    do_sample=False,
    max_new_tokens=64,
    cache_implementation="quantized",
    cache_config={"nbits": 4, "backend": "quanto"},  # or "hqq"
)
```

Wire this into OpenUnlearning’s generation path (do not only demo a toy script).

### Week-1 smoke test

1. Load one unlearned 1B checkpoint.
2. Run stock TOFU eval.
3. Run weight INT4 eval → confirm recovery signal.
4. Run QuantizedCache 4-bit eval → get first contrast number.
5. Only then scale to full matrix.

---



## 8. Timeline (10 weeks)


| Week | Focus                                                 | Decision gate                                       |
| ---- | ----------------------------------------------------- | --------------------------------------------------- |
| 1    | Env + OpenUnlearning eval on 1 HF unlearned model     | Eval metrics match published / docs                 |
| 2    | Reproduce **weight INT4 recovery** (positive control) | **Must** see recovery; else debug before continuing |
| 3–5  | KV 4-bit / 2-bit × GradDiff / NPO / SimNPO × seeds    | Main table filled                                   |
| 6    | Ablations: context length; optional 3B or KIVI        | Story locked                                        |
| 7    | Analysis + figures; mechanism notes                   | Draft outline                                       |
| 8    | Paper writing (workshop length)                       | Complete related work table                         |
| 9    | Gap runs + null-result framing if needed              | Camera-ready path                                   |
| 10   | Polish + submit (EACL WS) or bank for ICLR WS         | Submission                                          |


**Contingency:** If scooped on KV×unlearning → fold GGUF/imatrix arm and reframe as “deployment-stack durability audit,” or pivot to local SkillsBench (#2) only if time remains.

---



## 9. Venue strategy


| Venue                         | Paper timing          | Notes                                         |
| ----------------------------- | --------------------- | --------------------------------------------- |
| NeurIPS / ICML 2026 workshops | Closed                | Skip                                          |
| AAAI-27 workshops             | ~20 Nov 2026          | Only if compressed minimal set is ready early |
| **EACL 2027 workshops**       | ~15 Dec 2026          | Best near-term NLP target                     |
| **ICLR 2027 workshops**       | Suggested ~1 Feb 2027 | Best buffer; themes TBD after Nov 29          |
| NAACL / COLING / ACL 2027     | Jan–Apr 2027          | Fallbacks                                     |


Fit workshops that welcome: trustworthy ML, evaluation, negative results / ICBINB-style, LLM reliability, privacy.

---



## 10. Risks and mitigations


| Risk                                          | Likelihood   | Mitigation                                                    |
| --------------------------------------------- | ------------ | ------------------------------------------------------------- |
| Scooping (KV + safety is hot)                 | Moderate     | Lead with weight-vs-KV contrast; check arXiv weekly           |
| No weight-INT4 recovery on chosen checkpoints | Low–moderate | Swap hyperparameters / methods from HF collection             |
| Reviewers say “another quant paper”           | Moderate     | Title/abstract emphasize **KV vs weight**, not “we quantized” |
| QuantizedCache ≠ production FP8               | Certain      | Disclose; optional vLLM FP8 later                             |
| Prob vs generation metric disagreement        | Likely       | Report both; don’t overclaim                                  |
| OpenUnlearning env pain                       | Moderate     | `sdpa`, freeze deps, eval-only first                          |


---



## 11. Explicitly out of scope (v1)

- Training large models from scratch  
- Full SkillsBench / OpenHands Docker campaign (Topic #2) as main project  
- Multimodal MemLeak-style memory deletion  
- Claiming “first quantization undoes unlearning” (false; weight PTQ already did)

---



## 12. Alternate topics (if #1 dies)



### #2 — SkillsBench on local ≤8B (higher eng. risk)

Paired no-Skill vs curated-Skill on a SkillsBench subset with OpenHands + Ollama/vLLM, controlling serving-stack confounds ([arXiv:2609.26693](https://arxiv.org/html/2609.26693)).  
**Harder:** Docker per task, long timeouts, large context. Better as a second paper.

### #3 — GGUF / imatrix calibration vs unlearning (optional arm)

Test whether imatrix calibrated on forget-domain vs WikiText changes recovery under Q4_K_M/Q2_K.  
Good **ablation** for #1; weaker as sole thesis (easy to lump with weight PTQ).

---



## 13. Minimum publishable experiment set

1. ≥2 unlearning methods on Llama-3.2-1B TOFU forget10 (HF checkpoints OK).
2. Weight INT4 positive control with visible recovery.
3. KV QuantizedCache at 4-bit and 2-bit.
4. Forget + retain utility metrics.
5. ≥3 seeds **or** fully deterministic greedy + sensitivity note.
6. Clear related-work table separating weight PTQ, KV-safety, and this gap.

**Do only if time:** 3B replicate, MUSE, KIVI, vLLM FP8, GGUF/imatrix, Leak@k sweep, deep mechanism.

---



## 14. Key links

- OpenUnlearning: [https://github.com/locuslab/open-unlearning](https://github.com/locuslab/open-unlearning)  
- TOFU unlearned models: [https://huggingface.co/collections/open-unlearning/tofu-unlearned-models](https://huggingface.co/collections/open-unlearning/tofu-unlearned-models)  
- Transformers KV / QuantizedCache: [https://huggingface.co/docs/transformers/en/kv_cache](https://huggingface.co/docs/transformers/en/kv_cache)  
- Zhang et al. (weight PTQ undoes unlearning): [https://arxiv.org/abs/2410.16454](https://arxiv.org/abs/2410.16454)  
- Alignment Collapse (KV × refusals): [https://arxiv.org/abs/2606.09864](https://arxiv.org/abs/2606.09864)  
- SkillsBench (alt topic): [https://www.skillsbench.ai/](https://www.skillsbench.ai/)  
- Interactive ranking canvas (Cursor): `canvases/workshop-research-topics-2026.canvas.tsx`

---



## 15. Decision checklist (start of Week 1)

- [ ] Install transformers; record version; confirm `residual_length` default from that install  
- [ ] Run `scripts/test_kv_scoring_path.py` → GATE PASS (sequential ≠ single-pass under QuantizedCache)  
- [ ] Confirm retain90 Hub ID + weight INT4 positive control on one unlearned checkpoint  
- [ ] Freeze model IDs + bit-widths + residual/context + metric list in a config YAML  
- [ ] Re-run novelty search; if scooped, apply contingency  
- [ ] Pick venue only after matching workshop CFPs are listed (see venue note above)  

---



## Label key

- **[F]** Fact from literature / official docs / HF / GitHub  
- **[I]** Inference from that evidence  
- **[S]** Strategic recommendation for a first-time, low-compute workshop paper

**Recommendation [S]:** Execute Topic #1 with the eval-only + QuantizedCache path above. Treat GGUF as optional; defer full SkillsBench.