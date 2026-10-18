# Research Blueprint: Cache-Invariant Audits — Does KV-Cache Compression Undo LLM Unlearning?

**Status:** Recommended first-paper project — design revised after full-text read of both anchor papers
**Horizon:** ~9 weeks (finish mid-December 2026)
**Compute:** Free/low-cost Colab / Kaggle GPUs. Eval-only *plus one small training run* (see §6.1 — this is a change from v1)
**Primary target venues:** EACL 2027 workshops (projected ~15 Dec 2026, **unverified**); ICLR 2027 workshops (projected ~1 Feb 2027, **unverified**)
**Revision:** v2, 17 Oct 2026 (supersedes v1 of 12 Oct 2026)

---

## 0. What changed in this revision, and why

v1 was built on a reading list that had not been read in full. Full-text verification of both anchor papers on 17 Oct 2026 produced three corrections that change the design, not just the prose:

| # | v1 assumption | Verified reality | Consequence |
|---|---|---|---|
| C1 | Zhang et al. established weight-PTQ recovery **on TOFU**; our Arm B "reproduces" it | Zhang et al. used **MUSE (NEWS/BOOKS) and RWKU** on **LLaMA-2 7B / ICLM-7B**. TOFU appears only as a motivational aside about small learning rates. No TOFU, no Llama-3.2, no GGUF, no bitsandbytes, no 2-bit | Arm B is a **transfer to a new benchmark and a 3.5× smaller model**, not a reproduction. Higher risk, slightly higher novelty. §4 table rewritten |
| C2 | `cache_implementation="quantized"` is the KV intervention the literature uses | Alignment Collapse uses **custom forward hooks** that quantize-dequantize K/V before attention (plus KIVI and real vLLM FP8). It does **not** use HF `QuantizedCache` | Our planned arm was a **strictly weaker intervention** than anything published. Combined with `residual_length=128` (see F1), Arms C/D would return bit-identical output to Arm A. §6.2 rebuilt around hooks |
| C3 | Llama-3.2-1B checkpoints are sufficient | Alignment Collapse's own data shows **LLaMA-3.1-8B is the most resistant of 11 models** (0.8% refusal flip at 4-bit vs Qwen-2.5-7B at 90.3%) | A 4-bit Llama-only null is **uninterpretable**. One non-Llama checkpoint must be trained (§6.1) |

Also added: the cache-invariance finding (F2) is promoted from a bug to the **paper's spine**, because it is publishable even if the KV result is null. Topic #2 (SkillsBench) is deferred out of this document.

---

## 1. One-sentence pitch

Standard TOFU unlearning audits compute probability metrics with a single parallel forward pass that never re-reads the KV cache, so they are **structurally blind to every cache-side deployment transform**; when we measure correctly, we find how much forgotten knowledge KV-cache compression restores relative to weight INT4 — and whether the two act on the same narrow subspace.

---

## 2. Why this project

| Criterion | Assessment |
|---|---|
| Novelty | **[F]** Verified open 17 Oct 2026: arXiv API `abs:"KV cache" AND abs:"unlearning"` → **0 results**. No citing paper of either anchor mentions KV/activation quantization. Full LaTeX source of 2606.09864 has zero hits for "unlearn", "TOFU", "forget set", "GDPR" |
| Novelty (caveat) | **[I]** Method novelty is **unavailable** — Alignment Collapse already ships critical-layer scans, channel-level PCR with a formal bound, K-vs-V ablations, and a mitigation, all MIT-licensed. The finding must carry the paper |
| Null-safety | **[S]** The cache-invariance result (§5.1) stands independently of the KV outcome. This is the main reason to prefer this framing over v1's |
| Feasibility | **[F]** 398 pre-unlearned Llama-3.2-1B forget10 checkpoints exist. One extra training run needed for architecture sensitivity |
| Compute | **[I]** ~32–48 runs × 30–60 min on a T4 ≈ 16–48 GPU-hours. Fits Kaggle's 30 h/week with margin |
| First-paper fit | Clear story, existing code/data, and a contribution that survives a negative result |

**Avoid as the main thesis:** weight pruning/SVD/GGUF-only recovery, and *anything* framed as weight quantization. **[F]** The weight-side neighborhood produced five papers in Sept 2026 alone (TULIP 2609.34591, 2609.27355, 2609.10439, GROM 2608.05783, DurableUn 2605.02196). Drifting there means being sixth.

---

## 3. Research question

> After weight-space unlearning on TOFU forget10, do cache-side deployment transforms (KV quantization, and optionally KV eviction) restore forget-set knowledge — how does that compare to weight INT4 on the same checkpoints, and are standard unlearning metrics even capable of detecting it?

### Hypotheses

- **H0 (audit validity, primary):** TOFU probability metrics computed via parallel forward pass are **invariant** to cache-side transforms; metrics computed via sequential decode are not. *Predicted: confirmed by construction, quantified empirically.*
- **H1 (control):** Weight **RTN** int4 recovers a measurable fraction of forgotten knowledge on Llama-3.2-1B TOFU forget10, extending Zhang et al.'s MUSE/RWKU finding to a new benchmark and scale.
- **H2 (main):** KV quantization recovers **behavior** (the model stops deflecting and emits the entity) more readily than it recovers **knowledge** (teacher-forced log-prob of the gold answer rises).
- **H3 (mechanism):** The unlearning subspace is at least as noise-fragile as the safety subspace, i.e. α_unlearn ≤ α_safety ≈ 10⁻³–10⁻², so collapse onsets at a bit-width predictable from α before running the sweep.
- **H4 (scaling):** Recovery increases with context length. **[F]** Neither anchor paper tests this; Alignment Collapse is single-turn only.

**[S]** H0 + H2 + H4 are the load-bearing claims. H1 is a control. H3 is the payoff if time allows. Unlike v1, there is no "either direction is publishable" hedge — a bare null with no mechanism is not publishable, and H0 is what protects against that.

---

## 4. Verified literature landscape

### 4.1 Anchor A — Zhang et al., *Catastrophic Failure of LLM Unlearning via Quantization* (ICLR 2025, arXiv:2410.16454) **[F, full text read]**

- **Benchmarks:** MUSE NEWS (BBC) and BOOKS (Harry Potter forget / FanWiki retain); RWKU top-200 people (Appendix F). **Not TOFU.**
- **Models:** LLaMA-2 7B (NEWS), ICLM-7B (BOOKS). RWKU base unnamed (unverified).
- **Unlearning methods:** retrained by the authors — GA, GA_GDR, GA_KLR, NPO, NPO_GDR, NPO_KLR (AdamW, lr 1e-5, 10 epochs NEWS / 5 BOOKS, α ∈ {2,5,10,100,300}); Appendix J adds RMU and RMU_LAT; RWKU adds GA, NPO, RT.
- **Quantizers:** RTN int8 and int4 (Table 1); GPTQ 4-bit and AWQ 4-bit (Table 2, NEWS). **2-bit explicitly excluded** for utility collapse. Library unstated (unverified).
- **Headline:** forgotten knowledge retained **21% → 83%** at 4-bit (utility-constrained methods, average).
- **Key cells (MUSE BOOKS, M1 VerMem / M2 KnowMem, ROUGE):** GA_KLR 13.0/15.1 → **75.6/34.6**; NPO_KLR 12.4/13.7 → 70.9/34.2; NPO_GDR 0.4/13.4 → 66.0/31.9; GA_GDR 0.0/2.9 → 17.9/33.7. **RMU 14.2/0.0 → 50.5/29.3**; RMU_LAT 11.7/0.0 → 43.0/27.4.
- **Int8 barely moves:** GA_KLR BOOKS 13.0 → 12.4 (M1), 15.1 → 10.1 (M2). GPTQ/AWQ ≈ RTN (GA_KLR NEWS: AWQ 33.7/49.8, GPTQ 33.2/49.3, RTN 33.8/50.9).
- **Metrics:** M1 VerMem and M2 KnowMem are **free-generation ROUGE**; M3 PrivLeak is Min-K% MIA AUC. **No gold-answer log-probability metric, no TruthRatio.** Recovery claims therefore rest on generation, not probability.
- **Mechanism (§5):** bucket collapse. Unlearning under utility constraints makes minimal weight changes, so Q(f_unlearn) ≈ Q(f_target). With max|w| = 200, Δ_int4 = 25, so Δθ must exceed **12.5** to survive int4 vs **0.78** for int8. Semi-quantitative; **no per-layer or outlier-weight analysis**; the phrase "bucket collapse" does not appear.
- **Defense:** **SURE** — large lr (grid 5e-5 / 1e-4 / 2e-4) restricted to modules above a ‖∇θᵢL_forget‖ saliency threshold (γ ∈ 90th/95th/99th pct). SURE + 4-bit: GA_KLR BOOKS M1 75.6 → 16.4; NPO_KLR 70.9 → 16.1. Admitted "highly sensitive to hyperparameter selection, leading to an unstable unlearned model"; full-precision GA_GDR+SURE on NEWS *degrades* (M1 0.0 → 23.5).
- **Honest controls they ran:** quantizing the *target* model also degrades it (BOOKS M1 99.8 → 85.3 at 4-bit), and a retrained-model 4-bit control barely moves (14.3 → 13.6) — so recovery is specific to unlearned models. **This is the noise-floor discipline our §6.3 must match.**
- **KV cache:** **zero mentions** across v1/v2/v3. Weight-only PTQ throughout.
- **Threat model (Appendix L):** GDPR right-to-be-forgotten deployment framing; explicitly *not* an adversarial attack. Notes Lynch et al. attack-based recovery reaches only ~10%, no attack above 20% — so quantization is a much stronger recovery route than any attack.
- **Citations:** heavily cited (Google Scholar ≈110; Semantic Scholar indexes ≈45). **None** of the citing abstracts mentions KV-cache or activation quantization.

**How we differ:** we work on TOFU (not MUSE/RWKU), at 1B scale, with probability *and* generation metrics, and on the activation side. We cite SURE as the weight-side defense and do not claim to improve it.

### 4.2 Anchor B — Xu et al., *Alignment Collapse Under KV Cache Quantization* (arXiv:2606.09864) **[F, full LaTeX source read]**

- **Claim:** low-bit KV quantization silently destroys safety refusals while perplexity stays near baseline. Metric = **ConditionalFlip**, the fraction of FP16 refusals that flip to compliance, classified by WildGuard (93.0% agreement with Llama-Guard-3, κ=0.840; human audit κ=0.89/0.86).
- **Headline:** Mistral-7B loses **15.2%** of refusals at 4-bit and **1.03× PPL** (AdvBench, 50/328 flipped, CI [11.8, 19.5]).
- **Models:** 11 instruction-tuned, **3.8B–72B** (Mistral-7B-v0.2, Mixtral-8x7B, Qwen-2.5-7B, Yi-1.5-9B, DeepSeek-7B, LLaMA-3.1-8B, Gemma-2-9B, Mistral-Small-24B, Phi-3.5-mini; supplementary Qwen-2.5-72B, Yi-1.5-34B; held-out OLMo-2-7B).
- **Quantization:** post-training, inference-time only, weights stay FP16. **Custom forward hooks quantize-dequantize K and V before attention.** Per-token asymmetric for deployment, per-tensor symmetric for mechanism, plus per-channel and Group-64. Bit-widths 8/6/4/3/2 and FP8 (e4m3/e5m2). Cross-validated against **KIVI** and **vLLM v0.13.0** on an RTX 3090. **Not Transformers QuantizedCache** (unverified whether tested).
- **Per-model ConditionalFlip at 4/3/2-bit:** Qwen-2.5-7B **90.3**/80.6/80.2; Phi-3.5-mini 4.8/43.7/**98.0**; DeepSeek-7B 3.7/51.6/85.5; Mistral-7B 15.2/17.1/80.2; Yi-1.5-9B 5.4/20.1/83.1; Gemma-2-9B 0.2/0.8/**91.8**; **LLaMA-3.1-8B 0.8/1.7/58.1**. Collapse onset spans four bit-widths (6-bit Qwen → 2-bit Gemma).
- **Production numbers:** vLLM FP8 `e5m2` → 30.3% flip on Qwen; `e4m3` → 7.1% vs 0.2% for simulated INT8.
- **Mechanism:** safety occupies a low-dimensional subspace with energy-concentration ratio **α ≈ 10⁻³–10⁻²**, making it **10²–10³× more vulnerable** to quantization noise than the full space (SNR_S = α·SNR_full). Localized at three levels:
  - **Layer:** quantize one layer alone at 3-bit → critical layer + flip rate. Qwen L0 = 68.8% ("concentrated"); Gemma-2 L1 = 5.4%; Mistral L3 = 34.2% ("distributed, 12L"); Yi L31 = 23.5% ("broad, 33L"); Phi L12; Mistral-Small L14. **Not always early.** Mixtral: 19/32 layers >10%, peak 21.9%, no dominant layer.
  - **Channel:** PCR = 1 − FlipRate_per-channel / FlipRate_per-tensor at the critical layer → three failure modes: outlier-crushes-safety (Gemma PCR=100%, DeepSeek 87.5%, Mixtral 88.9%), outlier-as-safety (low PCR), multi-layer dilution (LLaMA, Group-64 makes it **worse**, −45.8%). Proposition 1 (Channel-Geometry Bound): PCR_MSE = 1 − mean(R_S²)/R².
  - **Token:** first-divergence. Qwen's 465 flipped prompts diverge at **token 1 (mean 1.00, 100%)**; Mistral's 50 spread over positions 1–31 (mean 7.58, median 6, 74% early).
- **K vs V:** **K-only accounts for 76–102% of damage in 8 of 9 primary models**; K MSE is 4–87× V MSE. (At 3-bit K-only can exceed K+V — shown to be a WildGuard artifact: K-only responses are coherent, PPL 2.7 vs 15.2, ~15× longer. **Lesson: validate your classifier.**)
- **System prompt:** its own KV entries get quantized. At 2-bit it *helps* distributed-safety models (Mistral −34.96pp, Mistral-Small −32.72pp) and *hurts* concentrated ones (Qwen +10.54pp, LLaMA +16.32pp). PCR predicted mitigation direction on **9/9 primary + 1 held-out** from only 20 calibration prompts.
- **Context length:** **no dedicated study.** All single-turn, chat template, greedy, `max_new_tokens=256`. Only length-adjacent results: 256 vs 512 output tokens gave identical classifications (0/50 changed); multi-turn adversarial history quantized (Qwen flips 75% at 4-bit; Mistral 0%). Main text asserts results are "deterministic across seeds, context lengths, and hardware" — **asserted, not measured.** No input-length sweep, no residual-window analysis, no position-dependent quantization.
- **Mitigation:** training-free, PCR-prescribed, ~35 GPU-min/model. Qwen FP16-protect L0–1 → **97.8% recovery at 7% memory**; Gemma-2 Group-64 at 2-bit 92.0% → 2.7%; Mistral Group-64 52.0%; KIVI cross-quantizer up to 97.2% (OLMo-2, PCR=100%, L13). Attention-based layer selection was **never** best (Qwen attn top-2: 1.5%).
- **Benchmarks (1,894 prompts):** custom 63 (refusal 19 / privacy 21 / jailbreak 23), AdvBench 520, HarmBench 320 (direct subset), XSTest 450, IFEval 541. XSTest dual degradation at 2-bit (Yi-9B false refusal 2.0% → 85.2%). IFEval Qwen strict pass 69.5% → 16.8% at 6-bit.
- **Unlearning:** **zero mentions.** Verified by grepping main.tex, appendix.tex, all figure .tex files and nat.bib. Related work covers KV compression, weight-quantization safety (Egashira, QReSafe), refusal-direction geometry (Arditi, Pan, Qi) — no unlearning literature. Future work names "pruning, eviction, low-rank compression, rotation-based quantizers" — still no unlearning.
- **Admitted limitations:** "PCR predicts direction, not always magnitude… does not fully account for inter-layer interactions" (LLaMA PCR 70% predicts Group-64 helps, yet −45.8%); SmoothQuant and QuaRot-style rotations untested; Mixtral/Yi-34B need 50 calibration prompts not 20. Not stated but evident: no long-context study, no latency benchmarks, **no weight-quantization interaction**, no unlearning.
- **Code:** 63 files, MIT license — `run_kivi.py`, `run_vllm_deployment.py`, `run_multi_turn.py`, `run_protection_sweep.py`, benchmark CSVs, WildGuard classifier. **No unlearning code.**

### 4.3 Neighbourhood (corrected)

| Work | What it actually shows | How we differ |
|---|---|---|
| Zhang et al. 2410.16454 (ICLR 2025) | Weight RTN/GPTQ/AWQ int4 restores forgotten knowledge on **MUSE/RWKU**, 7B, via free-generation ROUGE; proposes SURE | We are on **TOFU, 1B, activation side**, with probability + generation metrics; weight int4 is only our control |
| **DurableUn 2605.02196** | **Adapter-space** INT4 in the NF4+LoRA regime; Sharpness-Aware Forgetting defense | This — not Zhang — is the TOFU+INT4 antecedent. We do not touch adapters |
| QUAIL 2601.15538 | Bucket-collapse explanation + weight-PTQ fix | Weight side only |
| Alignment Collapse 2606.09864 | KV quant destroys **safety refusals**; PCR mechanism + mitigation | We measure **TOFU forget-set recovery**, not refusal flips. We reuse their harness and their α/PCR machinery, and we test the axis they left open (context length) |
| AnchorKV 2606.17872 | Safety-aware KV **eviction** with a refusal anchor | Eviction ≠ bit-width; no unlearning |
| KVEraser 2606.17034 | Erase spans **inside** the KV cache | Context unlearning ≠ weight-unlearning durability |
| Leak@k 2511.04934 | Unlearning fails under **probabilistic decoding** | A **confound for us**, not just a bonus metric — see §6.4 |
| Unlearning Isn't Deletion 2505.16831 | Forgetting is often reversible | Motivation for the "suppression, not deletion" reading of our H2 |
| TULIP 2609.34591 / 2609.10439 / 2609.27355 / GROM 2608.05783 | Layer-selective and quantization-robust **weight-space** unlearning (all Sept 2026) | Weight side is crowded; we stay off it. Their layer-selectivity results are useful priors for our critical-layer scan |
| Gated Activation Redirection 2605.12765 | Inference-time unlearning via **activation steering** | Activation-space unlearning as a *method*; we study activation-space *degradation* of weight unlearning |
| Bits and Memories 2607.25451 | Verbatim extraction across **weight** quantization | Weight side; check whether it covers TOFU before claiming our control is novel |

### 4.4 Claimed gap (re-verified 17 Oct 2026)

No work found that (1) starts from TOFU weight-unlearned checkpoints, (2) evaluates cache-side compression recovery of forget-set metrics, and (3) contrasts it with weight int4 on the same checkpoints. Additionally, **no work points out that standard probability-based unlearning metrics are cache-invariant** — which is the more durable half of the contribution.

**Re-run before locking the title**, and again the week of submission:
- arXiv API: `abs:"KV cache" AND abs:"unlearning"`; `all:"QuantizedCache" AND all:"TOFU"`; `all:"FP8 KV" AND all:"forget set"`
- Semantic Scholar citation graphs of 2410.16454 and 2606.09864
- OpenReview for EACL/ICLR 2027 workshop submissions once visible

---

## 5. Proposed contribution

### 5.1 Primary — audit validity (**[S]** this is what makes the paper null-safe)

**[F]** In OpenUnlearning (commit 17cbbc8, 2026-09-29), the metrics `forget_Q_A_Prob`, `forget_Truth_Ratio`, `forget_quality` (KS test over those), `privleak`, `extraction_strength` and all six MIA attacks are computed from **forward-pass log-probabilities**. Only the ROUGE-family metrics (`forget_Q_A_ROUGE`, `model_utility` via `hm_aggregate`) call `model.generate`, from a single site: `eval_text_similarity`, `src/evals/metrics/utils.py:294`, batch 32, greedy, `max_new_tokens: 200`.

**[I]** A single parallel forward pass **writes** the KV cache and never **reads** it back. Quantizing a cache that is never re-read is a mathematical no-op. Therefore every log-probability-based unlearning audit is **structurally incapable** of detecting any cache-side deployment transform — KV quantization, KV eviction, prefix caching, cache offloading, speculative decoding.

**Deliverable:** a corrected audit protocol that reports parallel-forward and sequential-decode log-probabilities side by side. The *difference between them* is the measurement. This generalizes well past quantization, which is why it should survive review and get cited.

Note this does **not** invalidate Zhang et al. — their recovery claims rest on free-generation ROUGE, which does decode. It does bear on every TOFU paper reporting probability metrics.

### 5.2 Secondary — empirical matrix
Unlearning method × weight-RTN-int4 × KV bit-width × quantization implementation × context length, with knowledge and behaviour reported **separately**.

### 5.3 Tertiary — mechanism
Estimate α for the unlearning direction and compare to the published α for refusal directions on the same models; run a critical-layer scan; test whether their PCR-guided FP16-layer protection also protects unlearning.

### 5.4 Deployment framing
Unlearning audits at BF16 with a full-precision cache are incomplete for production serving — and the incompleteness is invisible to the standard metric suite.

---

## 6. Experimental design

### 6.1 Models and checkpoints **[F, verified against `huggingface.co/api/models?author=open-unlearning` — 474 models, 398 matching `unlearn_tofu_*`]**

**Available pre-unlearned (download, do not retrain):** `open-unlearning/unlearn_tofu_Llama-3.2-1B-Instruct_forget10_<Method>_<hparams>`
- Methods: NPO (54 ckpts), AltPO (54), **RMU (54)**, UNDIAL (54), IdkDPO (54), SimNPO (48), GradDiff (40), IdkNLL (40)
- Example: `open-unlearning/unlearn_tofu_Llama-3.2-1B-Instruct_forget10_SimNPO_lr2e-05_b4.5_a1_d1_g0.125_ep10`
- **Not available:** GA, plain DPO, CEU, SatMarker, WGA, PDU. **forget10 only** — no forget05/forget20. **No 3B unlearned checkpoint** (only `tofu_Llama-3.2-3B-Instruct_{full,retain90/95/99}`).
- Reference models: `tofu_Llama-3.2-1B-Instruct_{full, retain90, retain95, retain99}` — **use `full` and `retain90` as noise-floor controls in every arm.**

**Selection [S]:** run **NPO, SimNPO, RMU**. **Drop GradDiff** — weak and noisy; a null there is uninformative. **RMU is the highest-value checkpoint**: Zhang et al. saw RMU go 14.2/0.0 → 50.5/29.3 under int4, i.e. it is the method whose suppression is most aggressively installed and therefore most plausibly disrupted.

**Must train (new in v2) [S]:** one NPO checkpoint on a **noise-sensitive architecture** — Qwen2.5-1.5B-Instruct or Gemma-3-1B-Instruct — using OpenUnlearning's own recipe.
- **Why:** **[F]** LLaMA-3.1-8B is the *most resistant* of 11 models in Alignment Collapse (0.8% flip at 4-bit, 58.1% only at 2-bit), attributed to multi-layer dilution. A Llama-only study at 4-bit cannot distinguish "unlearning is robust" from "we picked the resistant architecture."
- **Cost [I]:** TOFU forget10 = 400 samples; 5 epochs at 1–1.5B is a few T4-hours. Cheapest de-risking spend in the project.
- Kick this off in week 3 and run Llama arms while it trains.

**Deferred:** 3B (requires training; v1's "1B→3B" strength bar was unreachable with released checkpoints), MUSE, WMDP.

### 6.2 Conditions

**[F] Critical implementation fact:** HF `QuantoQuantizedLayer`/`HQQQuantizedLayer` default to `nbits=4, residual_length=128`, gated by
```python
if self.keys.dim() == 4 and self.keys.shape[-2] + 1 >= self.residual_length:
```
Below that length, K/V stay full precision. **[F]** TOFU forget10 questions average 12.4 words (5–39 words, ~20 tokens); OpenUnlearning prepends `"You are a helpful assistant."` plus the Llama-3.2 chat template (~25–35 tokens) → **prompts are ~55 tokens**; probability metrics concatenate question+answer (~45 more) → ~105; TruthRatio with options → ~120–140. **At defaults, essentially nothing is quantized.**

| Arm | What to run | Role |
|---|---|---|
| A | FP16/BF16, `DynamicCache` | Baseline |
| B1 | Weight **RTN int4** | **Primary positive control** — matches Zhang et al.'s strongest quantizer |
| B2 | Weight NF4 (bitsandbytes `load_in_4bit`) | Secondary. **[S]** NF4 is a much better quantizer than RTN and may **under-recover**; do not let a B2 null fail the week-2 gate |
| **C** | **Hook-based quantize-dequantize on K and V, per-token asymmetric, 4-bit** | **Primary KV arm.** Literature-comparable with Alignment Collapse. Reuse their MIT code |
| D | Same, **2-bit** | Stress. **[F]** Even LLaMA-3.1-8B flips 58.1% here |
| E | HF `cache_implementation="quantized"` at `residual_length ∈ {128 (default), 32, 1}` × `nbits ∈ {4,2}` | Shows the shipped default is **inert** at TOFU prompt lengths — a finding in itself, and a direct check on F1 |
| F | C/D with **K-only** vs **V-only** | **[F]** K-only = 76–102% of alignment damage. Does unlearning behave the same? If V matters more, the two subspaces differ |
| G | C/D at input context ≈ 0.1k / 1k / 4k tokens | **H4 — promoted from "bonus" to primary.** The only regime where the effect has room to grow, and the realistic RAG/agent threat model |
| H | B1 × C jointly | Real serving does both (4-bit weights + FP8 KV). Neither anchor tests the combination. Additive / subadditive / superadditive? |
| I (optional) | KIVI as a third quantizer | Cross-quantizer validity, as Alignment Collapse did |
| J (optional) | KV **eviction** (H2O / SnapKV / StreamingLLM) | Tests whether the mechanism is subspace fragility rather than quantization noise. **[S]** Powerful but scope creep — hold as the follow-up paper |
| K (optional) | PCR-guided FP16-layer protection applied to unlearning | Does their 97.8%-recovery mitigation also make unlearning durable? Only if weeks 1–5 go well |

**Axes [F]:** `axis-key`/`axis-value` = **0 for quanto, 1 for hqq**. Wrong axes materially change results; v1 omitted this.
**Attention [S]:** `sdpa` on free GPUs; flash-attn pins break T4/P100. **[F]** QuantizedCache supports neither sliding-window layers, offloading, nor `torch.compile` — so there is no OOM fallback.

### 6.3 Metrics

**[F]** Default-enabled in `configs/eval/tofu.yaml`: `forget_Truth_Ratio`, `forget_quality`, `forget_Q_A_Prob`, `forget_Q_A_ROUGE`, `model_utility`, `privleak`, `extraction_strength`. Commented out: `exact_memorization`, six MIA attacks, `forget_Q_A_gibberish`. Handlers: `probability`, `probability_w_options`, `rouge` (`rouge1_recall`, `rougeL_f1`, `rougeL_recall`), `truth_ratio`, `ks_test`, `hm_aggregate`, `privleak`.

**Report two axes separately [S]:**
- **Knowledge** — teacher-forced log-prob of the gold answer, TruthRatio, `forget_Q_A_Prob`. Compute **both** parallel-forward and sequential-decode. The gap between them is contribution §5.1.
- **Behaviour** — `forget_Q_A_ROUGE`, entity-emission rate (does the model produce the name *at all*, correct or not), deflection/refusal rate, `model_utility`.

**Controls [S]:**
- **Noise floor, mandatory.** Run every arm on `tofu_Llama-3.2-1B-Instruct_full` and `_retain90`. Report recovery as a **relative** effect: how much more does the metric move on the unlearned model than on a never-unlearned one? If equal, it is degradation, not recovery. Zhang et al. ran exactly this control (target 99.8 → 85.3; retrained 14.3 → 13.6) and it is why their result is credible.

**Statistics [S]:**
- **Delete "≥3 seeds."** Under `do_sample=False` there is no stochasticity to average; three seeds give three identical runs. The only variance source is the **item** distribution (400 forget10 rows). Use **paired bootstrap CIs over items** plus per-item McNemar tests on recovery.
- **[F]** forget10 = 400 rows; questions 5–39 words (mean 12.4), answers mean ~182 chars (max 400). Tokenize the real templated prompts in week 1 and record exact lengths — do not trust the char/4 heuristic.

### 6.4 Confounds to control explicitly

| Confound | Why it bites | Control |
|---|---|---|
| **Leak@k (2511.04934)** | Unlearning fails under probabilistic decoding *regardless* of quantization. A reviewer will attribute any recovery to this | Stay greedy throughout (cleanest), or report Leak@k on Arm A and show the **incremental** effect of quantization above it |
| **Uniform degradation** | Any perturbation moves all log-probabilities | Noise-floor controls on `_full`/`_retain90` (§6.3) |
| **Architecture resistance** | Llama is the most resistant model tested | Train one Qwen/Gemma NPO checkpoint (§6.1); push to 2-bit |
| **Inert intervention** | `residual_length=128` > prompt length | **Liveness assertion** (§7); Arm E quantifies the default's inertness |
| **Classifier artifact** | **[F]** Alignment Collapse found K-only appearing worse than K+V was a WildGuard artifact (K-only responses coherent, PPL 2.7 vs 15.2, ~15× longer) | Manually inspect a sample of flipped generations; report PPL and length alongside any classifier judgement |
| **Metric disagreement** | Probability and generation metrics can diverge (they do in Zhang et al.) | Report both; never claim recovery from one axis alone |

### 6.5 What counts as a meaningful result

- **Minimum (publishable):** §5.1 cache-invariance demonstrated and quantified; weight RTN int4 shows recovery on TOFU 1B; KV C/D reported on ≥2 methods **including one non-Llama model**, with paired bootstrap CIs and noise-floor controls; knowledge vs behaviour separated.
- **Strong:** contrast holds across 3 methods and 2 architectures; context-length curve (Arm G) shows a trend; K-vs-V asymmetry result; weight×KV interaction (Arm H).
- **Bonus:** α_unlearn estimated and compared to published α_safety; critical-layer scan; PCR-guided protection transfers to unlearning (Arm K).

---

## 7. Implementation path

### Stack
1. Fork **locuslab/open-unlearning** — TOFU eval. **[F]** `requirements.txt` pins `transformers==5.5.4`, `torch==2.9.1`, `bitsandbytes==0.49.2`, `accelerate==1.13.0`, `datasets==3.0.1`, `hydra-core==1.3`, `rouge-score==0.1.2`, `scikit-learn==1.5.2`, `deepspeed==0.15.4`. **`optimum-quanto` and `hqq` are absent — install and verify against Transformers v5**, where `QuantoQuantizedCache` was refactored into `QuantizedLayer` classes and the quanto backend may be broken or dropped.
2. Clone **Adarsh321123/kv-quantization-alignment** (MIT, 63 files) for the hook-based quantizer, layer/channel scans and PCR — do not reimplement.
3. **RTN int4** for the primary weight control (quanto/torchao weight quantization), bitsandbytes NF4 secondary.
4. `sdpa` attention throughout.

### Patch points **[F]**
- **One** `model.generate` call site: `src/evals/metrics/utils.py:294` (`eval_text_similarity`).
- Probability utilities: `evaluate_probability`, `tokenwise_vocab_logprobs` — add a **sequential-decode** path alongside the existing parallel one.
- `src/model/__init__.py::get_model` passes `model_args` verbatim to `from_pretrained`, so weight `quantization_config` can be injected by config with no code change.
- Generation defaults live in `configs/generation/default.yaml`; eval config in `configs/experiment/eval/tofu/default.yaml`.
- **[S]** Wire everything through Hydra config, not a bolt-on script. v1 was right about this.

### The liveness assertion — do this before anything else **[S]**
```python
# Fails loudly if the KV intervention is inert (residual_length > prompt length).
fp16_logits = run(model, prompt, cache=None)
kv_logits   = run(model, prompt, cache=make_quantized_cache(nbits=4, residual_length=1))
assert not torch.allclose(fp16_logits, kv_logits, atol=1e-4), \
    f"KV arm is a no-op: prompt_len={prompt_len}, residual_length={rl}"
```
Print tokenized prompt length, cache length, and the fraction of positions actually quantized for every run. **Do not scale to the matrix until this passes on every arm.** This single check is what separates a real null from a silent misconfiguration.

### Minimal KV arm
```python
out = model.generate(
    **inputs, do_sample=False, max_new_tokens=200,
    cache_implementation="quantized",
    cache_config={"nbits": 4, "backend": "quanto",
                  "residual_length": 1, "axis-key": 0, "axis-value": 0},
)
```
Prefer the **hook-based** quantizer (Arm C) as primary; treat the above as Arm E.

### Week-1 smoke test
1. Install `optimum-quanto` + `hqq` against `transformers==5.5.4`; confirm the quanto backend works in v5.
2. Load `unlearn_tofu_Llama-3.2-1B-Instruct_forget10_NPO_*`; run stock TOFU eval; record exact tokenized prompt lengths.
3. **Pass the liveness assertion** for Arms C and E.
4. Add the sequential-decode logprob path; confirm it differs from the parallel path under quantization and matches it under FP16.
5. Run weight **RTN** int4 → confirm recovery signal.
6. Only then scale.

---

## 8. Timeline (9 weeks)

| Week | Focus | Decision gate |
|---|---|---|
| 1 | Env, deps, liveness assertion, sequential-decode path, exact prompt lengths | **Liveness assertion passes on Arms C and E**; sequential vs parallel paths differ under quantization |
| 2 | Reproduce weight **RTN int4** recovery on NPO + RMU; noise-floor controls on `_full`/`_retain90` | **Must** see recovery. If not, debug — do not continue |
| 3 | Launch Qwen/Gemma NPO training (background). Run Llama Arms A/B/C/D/E on 3 methods | **HARD KILL GATE:** if RTN int4 shows no recovery on *any* checkpoint, stop and re-select methods/bit-widths. A broken control invalidates everything downstream |
| 4 | Arm F (K-only vs V-only), Arm G context-length sweep on Llama | Context-length curve has a direction |
| 5 | Arm G + C/D on the non-Llama checkpoint; Arm H (weight × KV) | **Go/no-go:** if nothing moves at 2-bit on a sensitive architecture, the paper becomes §5.1 + a bounded negative result. Decide now, not in week 8 |
| 6 | Mechanism: critical-layer scan, α estimate, optional Arm K | Story locked |
| 7 | Analysis, figures, paired bootstrap CIs, related-work table from §4 | Draft outline |
| 8 | Writing (workshop length) | Complete draft |
| 9 | Gap runs, null-result framing if needed, polish, submit | Submission |

**Contingencies [S]:**
- **Scooped on KV × unlearning** → lead harder with §5.1 (audit validity), which is orthogonal and harder to scoop, and fold in Arm J (eviction) to broaden beyond quantization.
- **Weight-RTN control fails** → try weaker unlearning methods (IdkNLL, GradDiff) or a coarser bit-width. Zhang et al.'s mechanism predicts recovery depends on Δθ vs the bucket threshold, which shifts with model scale — 1B may need a different operating point than 7B.
- **quanto broken in Transformers v5** → use `hqq` (supports int2/4/8) or the hook-based quantizer exclusively; Arm E becomes hqq-only.

---

## 9. Venue strategy

| Venue | Timing | Notes |
|---|---|---|
| AAAI-27 workshops | ~20 Nov 2026 (**unverified**) | Only if the week-5 minimal set lands early |
| **EACL 2027 workshops** | ~15 Dec 2026 (**projected, not announced**) | Best near-term NLP target |
| **ICLR 2027 workshops** | ~1 Feb 2027 (**projected**) | Best buffer; themes TBD after main decisions |
| NAACL / COLING / ACL 2027 | Jan–Apr 2027 | Fallbacks |

**[S]** Every date above is a projection. Verify against official CFPs — workshop calls typically post Oct–Nov. Target tracks: trustworthy ML, evaluation methodology, negative results (ICBINB-style), LLM reliability, privacy. **§5.1 makes this an evaluation-methodology paper as much as a quantization paper, which widens the set of suitable workshops.**

---

## 10. Risks and mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| **Inert KV intervention** (`residual_length` > prompt length) | **Certain if unaddressed** | Liveness assertion (§7); Arm E quantifies it; hook-based Arm C as primary |
| **Probability metrics are cache-blind** | **Certain** | This is §5.1, the contribution — not a bug to hide |
| **Llama-only null is uninterpretable** | High | Train one Qwen/Gemma NPO checkpoint (§6.1); report 2-bit |
| Reviewers say "another quantization paper" | Moderate | Title and abstract lead with **cache-invariant audits**, not "we quantized" |
| No method novelty (their machinery is MIT-licensed) | **Certain** | Claim the finding and the audit protocol, never the method |
| Weight-side drift | Moderate | §4.3 lists five Sept-2026 weight papers; stay on the activation side |
| Scooping | Moderate | Re-run §4.4 searches weekly; §5.1 is the moat |
| No weight-RTN recovery at 1B | Low–moderate | Week-3 hard kill gate; swap methods or bit-width |
| Leak@k explains the recovery | Moderate | Greedy throughout, or report incremental effect above Arm A |
| `optimum-quanto` broken in Transformers v5 | Moderate | hqq fallback, or hook-based quantizer only |
| QuantizedCache ≠ production FP8 | **Certain** | Disclose; Arm I (KIVI) and optional vLLM FP8 later |
| OOM with no offloading fallback | Low at 1B | QuantizedCache cannot offload; use hook-based quantization if needed |
| Classifier artifact inflates behaviour recovery | Moderate | Manual inspection + report PPL and generation length (§6.4) |
| Colab/Kaggle disconnects | High | Checkpoint per-item results to Drive incrementally; run arms as independent jobs |

---

## 11. Explicitly out of scope (v1)

- Training large models from scratch (the single 1–1.5B NPO run in §6.1 is the only training)
- 3B / 8B unlearned checkpoints — **none exist**; would require training
- MUSE, WMDP, forget05/forget20 — no released checkpoints for the latter
- Adapter/LoRA quantization (DurableUn's territory)
- Proposing a new unlearning method or improving SURE
- Arm J (eviction) and Arm K (protection transfer) unless weeks 1–5 go well
- Multimodal memory deletion
- Claiming "first quantization undoes unlearning" (**false** — weight PTQ already did, on MUSE/RWKU)
- SkillsBench / OpenHands (former Topic #2) — deferred entirely; see §12

---

## 12. Alternate topics (if this dies)

**#3 — GGUF / imatrix calibration vs unlearning.** Whether imatrix calibrated on the forget domain vs WikiText changes recovery under Q4_K_M/Q2_K. Good *ablation* of the weight arm; weak as a sole thesis. **[F]** Mind the Gap (2505.23786) already attacks GGUF security, so the space is partly occupied.

**#4 — KV eviction generality (promoted from Arm J).** If H3 holds — the mechanism is subspace fragility, not quantization noise — then H2O/SnapKV/StreamingLLM eviction should also recover forgotten knowledge. **[F]** Alignment Collapse's own future work names eviction, pruning, low-rank and rotation-based quantizers as untested. Broader and more interesting than #1, but a second paper's scope.

**#2 — SkillsBench on local ≤8B.** Removed from active consideration. Docker-per-task, long timeouts, large context; higher engineering risk with no eval-only path.

---

## 13. Minimum publishable experiment set

1. §5.1 **cache-invariance demonstrated**: parallel-forward vs sequential-decode log-probs, quantified, on ≥2 methods.
2. ≥2 unlearning methods on Llama-3.2-1B TOFU forget10 (released checkpoints) **plus 1 trained non-Llama checkpoint**.
3. Weight **RTN int4** positive control with visible recovery, and a noise-floor control on `_full`/`_retain90`.
4. Hook-based KV quantization at 4-bit and 2-bit, **liveness-asserted**.
5. Knowledge and behaviour metrics reported **separately**.
6. Context-length sweep (Arm G) at ≥3 lengths.
7. **Paired bootstrap CIs over items** — not seeds.
8. Related-work table (§4.3) correctly separating weight PTQ, KV-safety, adapter-quant, and this gap.

**Only if time:** K-vs-V ablation, weight×KV interaction, KIVI arm, critical-layer scan, α estimate, protection transfer, eviction arm, Leak@k sweep, 3B.

---

## 14. Key links

**Code and data**
- OpenUnlearning: https://github.com/locuslab/open-unlearning (commit 17cbbc8)
- TOFU unlearned models: https://huggingface.co/collections/open-unlearning/tofu-unlearned-models
- Org model index (JSON, reliable): https://huggingface.co/api/models?author=open-unlearning
- Alignment Collapse code (MIT, hook quantizer + PCR): https://github.com/Adarsh321123/kv-quantization-alignment
- Zhang et al. code: https://github.com/zzwjames/FailureLLMUnlearning
- KIVI: https://github.com/jy-yuan/KIVI
- Transformers KV/QuantizedCache docs: https://huggingface.co/docs/transformers/en/kv_cache

**Anchor papers**
- Zhang et al., weight PTQ undoes unlearning (MUSE/RWKU): https://arxiv.org/abs/2410.16454 · v3 HTML: https://arxiv.org/html/2410.16454v3 · OpenReview: https://openreview.net/pdf?id=lHSeDYamnz
- Xu et al., Alignment Collapse under KV quant: https://arxiv.org/abs/2606.09864
- TOFU: https://arxiv.org/abs/2401.06121 · https://locuslab.github.io/tofu/

**Weight-side neighbourhood (cite, do not compete)**
- DurableUn: https://arxiv.org/abs/2605.02196 · QUAIL: https://arxiv.org/abs/2601.15538 · TULIP: https://arxiv.org/abs/2609.34591 · Quantization-Robust Unlearning: https://arxiv.org/abs/2609.27355 · Layer-Selective Unlearning: https://arxiv.org/abs/2609.10439 · GROM: https://arxiv.org/abs/2608.05783

**Evaluation-validity**
- Leak@k: https://arxiv.org/abs/2511.04934 · Unlearning Isn't Deletion: https://arxiv.org/abs/2505.16831 · A Probabilistic Perspective: https://arxiv.org/abs/2410.03523 · Stress Testing Unlearning (WMDP++): https://arxiv.org/abs/2608.22527

**KV-side neighbourhood**
- AnchorKV: https://arxiv.org/abs/2606.17872 · KVEraser: https://arxiv.org/abs/2606.17034 · KVQuant: https://arxiv.org/abs/2401.18079 · vLLM FP8 KV: https://docs.vllm.ai/en/latest/features/quantization/quantized_kvcache/

**Inference-time unlearning (adjacent framing)**
- Gated Activation Redirection: https://arxiv.org/abs/2605.12765

---

## 15. Decision checklist (start of Week 1)

- [ ] Install `optimum-quanto` and `hqq` against `transformers==5.5.4`; confirm the quanto backend is not broken in Transformers v5
- [ ] Clone OpenUnlearning; run stock TOFU eval on `unlearn_tofu_Llama-3.2-1B-Instruct_forget10_NPO_*` with `sdpa`
- [ ] **Record exact tokenized prompt lengths** for forget10 under the real chat template (do not trust char/4)
- [ ] Clone the Alignment Collapse repo; get the hook-based quantizer running on the same model
- [ ] **Pass the liveness assertion** for Arms C and E — hard blocker
- [ ] Add the sequential-decode logprob path; verify it matches the parallel path at FP16 and diverges under KV quantization
- [ ] Confirm weight **RTN int4** recovery (not NF4 first)
- [ ] Freeze model IDs, bit-widths, `residual_length` values, quantization axes, and metric list in a config YAML
- [ ] Re-run the §4.4 novelty searches; log the date and results
- [ ] Verify EACL/ICLR workshop dates against official CFPs — the dates in §9 are projections
- [ ] Pick venue track (EACL Dec vs ICLR Feb) based on week-5 progress

---

## Label key

- **[F]** Fact verified against primary source (paper full text, library source, HF API, repo file) on 17 Oct 2026
- **[I]** Inference from that evidence
- **[S]** Strategic recommendation for a first-time, low-compute workshop paper
- **unverified** — could not confirm; check before relying on it

**Recommendation [S]:** Execute with §5.1 (cache-invariant audits) as the spine, Arms A–H as the matrix, and the hook-based quantizer — not HF `QuantizedCache` at defaults — as the primary KV intervention. Train one non-Llama NPO checkpoint in week 3. Hold eviction (Arm J) and protection transfer (Arm K) as the follow-up.
