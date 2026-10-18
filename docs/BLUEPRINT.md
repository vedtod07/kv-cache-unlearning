# Research Blueprint (v3): Does KV-Cache Compression Undo LLM Unlearning?

**Revision:** v3, 20 Oct 2026. Supersedes v1 (13 Oct) and v2 (17 Oct), which were removed from the repo (still in git history).
**Team:** two people (see `WORK_SPLIT.md`). **Schedule:** 9 weeks, Oct 19 → Dec 20, 2026 (see `NINE_WEEK_PLAN.md`).
**Compute:** free Colab/Kaggle GPUs; eval-only on released checkpoints, plus one possible small fine-tune. Optional $300 Google Cloud credit (GPU quota is not available on a free-trial account; plan without it).

**Label key:** **[F]** checked against a primary source (paper full text, library source, official page) during planning; **[I]** inference; **[S]** suggestion; **(v2, unverified)** carried over from the v2 blueprint and not independently checked. Nothing here is an acceptance prediction.

---

## 1. What changed from v2, and why

| # | v2 | v3 |
|---|---|---|
| 1 | "arXiv search for KV cache AND unlearning: 0 results" | **[F]** The query returns 1 result on 20 Oct: arXiv 2609.04875 (agent *execution-state* unlearning; treats the KV cache as state to roll back). Adjacent, not the same question. Re-run searches before locking a title. |
| 2 | Cache-invariance ("probability audits are blind to cache transforms") stated as general | **[F][I]** True for quantize-on-read cache objects: in HF `QuantizedLayer.update`, prefill quantizes into storage but returns the original full-precision K/V. **Not** true for Alignment Collapse's hooks, which quantize K/V before attention in the same forward pass. Two semantics must be defined and compared (§5.1). |
| 3 | Venue: EACL 2027 workshops ~15 Dec | **[F]** The joint 2027 workshop-proposal call closed 4 Sep (notified 2 Oct); I found no EACL workshop paper deadlines. ICLR 2027 workshops: suggested paper deadline 1 Feb 2027, authors notified by 26 Feb, workshop list announced 29 Nov. AAAI-27 workshop papers ~20 Nov (too early). |
| 4 | "One small training run" for a non-Llama checkpoint | **[I]** It is three jobs: fine-tune the base model on TOFU `full`, a `retain90` reference, then the unlearning run. A 1–1.5B full AdamW fine-tune does not fit a 16 GB T4 (no native bf16): use LoRA or a ~0.5B model, and say so in the paper. |
| 5 | 32–48 runs × 30–60 min | **[I]** Unproven. The full TOFU utility suite and a token-by-token scoring path may be much slower. Time one forget-only and one full run in week 1 and size the matrix from measurements. |
| 6 | Recovery measured against full-precision references | **[F][I]** Zhang et al. show quantizing the *original* model already lowers scores (BOOKS verbatim 99.8 → 85.3 at 4-bit). Use the *matched transformed* original and retain-only models as references. |
| 7 | Outcome = overlap / log-prob | **[S]** Separate **correct disclosure**, wrong answer, and deflection; a refusal turning into fluent text is not recovery. |
| 8 | Scope: arms A–K | **[S]** Core vs tier-2 split (§6.2). |
| 9 | Preliminary "independent replication" wording for the blog | Call them preliminary public studies (two exist; see §4.3). |

---

## 2. Question and hypotheses

> After weight-space unlearning on TOFU forget10, do cache-side deployment transforms (integer KV quantization) restore **correct** forget-set disclosure — how does that compare to weight INT4 on the same checkpoints — and do standard audits predict the deployed behaviour?

- **H0 (audit validity):** Parallel-forward probability metrics are insensitive to *quantize-on-read* cache transforms but are sensitive to *quantize-all* hook transforms; sequential decoding through the cache is sensitive to both. The gap is itself a measurement. *Expected by construction for quantize-on-read; the consequence (do verdicts or rankings change?) is the real question.*
- **H1 (control):** Weight RTN-int4 recovers some forgotten knowledge on Llama-3.2-1B TOFU forget10 (extension of Zhang et al., MUSE/RWKU 7B, to a new benchmark and scale). Two preliminary public studies suggest effects are method-dependent and often modest.
- **H2:** KV quantization changes **behaviour** (stops deflecting) more readily than **knowledge** (correct disclosure rises). *Speculative.*
- **H3:** Refusal-style unlearning (IdkDPO/IdkNLL) behaves more like safety refusals under KV noise than suppression-style (NPO/SimNPO/RMU). *Speculative; motivated by Alignment Collapse's refusal-subspace account.*
- **H4:** Recovery grows with context length. **[F]** Neither anchor paper tests input-length sweeps.

Pilot go/no-go criteria: `PILOT_CRITERIA.md` (freeze end of week 2).

---

## 3. Verified literature landscape

### 3.1 Zhang et al., *Catastrophic Failure of LLM Unlearning via Quantization* (ICLR 2025, arXiv:2410.16454) **[F, full text read]**
- Benchmarks: MUSE NEWS (LLaMA-2 7B) and BOOKS (ICLM-7B); RWKU in an appendix. **No TOFU, no 1B model, no KV cache.**
- Methods retrained by the authors: GA, GA_GDR, GA_KLR, NPO, NPO_GDR, NPO_KLR; RMU and RMU_LAT in Appendix J.
- Quantizers: RTN int8/int4; GPTQ and AWQ 4-bit (NEWS). 2-bit excluded.
- Headline: retained forgotten knowledge 21% → 83% at 4-bit (utility-constrained methods, average). Int8 ≈ full precision. GPTQ/AWQ ≈ RTN.
- Example (BOOKS KnowMem): GA_KLR 15.1 → 34.6; original 59.4; retrained 28.9. RMU verbatim 14.2 → 50.5.
- Controls: quantizing the original lowers its scores; the retrained model barely moves (verbatim 14.3 → 13.6), so recovery is specific to unlearned models.
- Mechanism: informal step-size argument (small weight changes fall in the same quantization interval). Not a proof.
- Mitigation SURE (large learning rate with module-level saliency mask) is unstable by the authors' admission; in Table 3 GA_GDR+SURE keeps forgetting but truthfulness/factuality fall to ~0.2/0.0.
- Metrics are ROUGE-based generation metrics and a Min-K% privacy score; no gold-answer log-probability metric.

### 3.2 Xu et al., *Alignment Collapse Under KV Cache Quantization* (arXiv:2606.09864 v2) **[F, text read; appendices partly]**
- 11 instruction-tuned models (3.8B–72B), five benchmarks (1,894 prompts), greedy decoding, WildGuard classifier. Metric: ConditionalFlip (fraction of FP16 refusals that become compliance).
- Quantization: weights FP16; **forward hooks** quantize-dequantize K/V (per-token asymmetric for deployment, per-tensor symmetric for mechanism) before attention; cross-checked with KIVI and vLLM FP8; a real-dtype INT8 head-to-head gave identical flip counts (1/19).
- Results: Qwen-2.5-7B 90.3% flip at 4-bit; Mistral-7B 15.2% at 4-bit with 1.03× perplexity; **LLaMA-3.1-8B 0.8% at 4-bit and 58.1% at 2-bit**; Gemma-2-9B 91.8% at 2-bit. No universal safe bit-width. vLLM FP8 e5m2: 30.3% flip on Qwen. Key quantization accounts for 76–102% of damage in 8 of 9 primary models.
- Mechanism: safety features in a low-dimensional subspace (energy ratio α ≈ 1e-3–1e-2); PCR diagnostic; 35-GPU-minute mitigation (up to ~97% recovery).
- **No mention of unlearning** (text search). Future work lists pruning, eviction, low-rank compression, rotation-based quantizers.
- MIT-licensed code: github.com/Adarsh321123/kv-quantization-alignment. Companion ICML 2026 listings by the same group: "A 35-Minute Audit…" and "The Channel Geometry of Refusal…" (not read).
- Single-group preprint, not peer reviewed.

### 3.3 Neighbourhood
| Work | What it shows | Difference |
|---|---|---|
| LessWrong 1 (28 May 2026), Llama-3.1-8B, TOFU forget10, GradDiff/SimNPO/RMU | NF4 4-bit: GradDiff forget-prob 0.028 → 0.672; 20% magnitude pruning restores nearly all; no KV | Preliminary, unreviewed, weight/pruning only |
| LessWrong 2 (20 Jul 2026), Llama-3.2-1B, TOFU forget10, NPO/SimNPO/IdkDPO | 4-bit: NPO 0.209 → 0.353 (~22%); others ≤ ~3%; pruning 20% ~42% for NPO; generation did not recover facts | Same checkpoints; one seed, no KV |
| DurableUn (2605.02196) | Adapter-space INT4 recovery on NF4+LoRA | Adapter quantization, not ours |
| QUAIL (2601.15538), 2609.27355 | Weight-quantization fixes and explanations | Weight side |
| Leak@k (2511.04934) | Unlearning leaks under probabilistic decoding | Confound: stay greedy or report incremental effect |
| Unlearning Isn't Deletion (2505.16831) | Forgetting often reversible; INT4 on Yi-6B recovered little | Motivation for "suppression, not deletion" |
| KUDA (2602.19275), full-stack study (2510.07626) | Weaker/inconsistent quantization effects on WMDP | The field disagrees on effect size |
| AnchorKV (2606.17872) | Safety-aware KV *eviction* | Eviction, safety only |
| Faithfulness Is Not Free (2608.30996) | INT4 KV hurts RAG faithfulness, Qwen2.5-7B | Not unlearning |
| 2609.04875 | Unlearning agent execution state (KV cache as state to roll back) | Different problem |
| GUARD-IT (2605.12765), MANSU (2605.15138) | Activation steering / circuit-based unlearning vs quantization | Methods, not durability audits of weight unlearning |

### 3.4 Claimed gap and how to re-check
No work found that (1) starts from TOFU weight-unlearned checkpoints, (2) measures forget-set recovery under KV-cache compression, and (3) contrasts it with weight INT4 on the same checkpoints. This is an absence in a snippet-level search, not proof. Re-run before fixing a title and again the week before submitting: arXiv (`KV cache` + `unlearning`, `QuantizedCache` + `TOFU`), Semantic Scholar citations of 2410.16454 and 2606.09864, and the Alignment Collapse group's ICML pages.

---

## 4. Contribution (target, not a result)

> We characterize when checkpoint-level unlearning evaluations fail to predict forgotten-fact disclosure under compressed-cache inference, and give a validated protocol for evaluating the deployed computation.

Linked pieces: (1) a concrete phenomenon (correct disclosure changes or not), (2) a measurement consequence (audit vs deployment-matched verdicts or rankings differ or not), (3) a practical protocol. Method novelty is unavailable: Alignment Collapse's machinery is public. Claim the finding and the protocol.

Anticipated reviewer objections and responses:
| Objection | Response |
|---|---|
| "Just refusal collapse again" | Separate correct / wrong / deflection; refusal-style vs suppression-style comparison with matched baselines |
| "Obviously an evaluator that doesn't run the transform can't see it" | The value is the *consequence* (changed verdicts/rankings) and the released protocol; also compare two cache semantics |
| "Only simulated" | Include a faithful quantize-on-read implementation; optionally KIVI |
| "Model is just broken" | Report utility and coherence alongside |
| "One peculiar checkpoint" | Several methods plus a non-Llama checkpoint |
| "Settings chosen post hoc" | Freeze confirmatory settings after the pilot |

---

## 5. Design

### 5.1 Two cache semantics (central methodological point)
- **Quantize-on-read (cache-faithful):** K/V of the current step are used at full precision and stored quantized; later steps read quantized values. HF `QuantizedLayer.update` behaves this way **[F]**. A single parallel teacher-forced pass over question+answer never reads the cache back, so it is insensitive.
- **Quantize-all (hooks):** K/V are quantized before attention in every forward pass, including the prompt. A parallel pass is sensitive. This is stricter than a real cache for the prefill tokens.
- Run both and report the gap. Which deployments an audit misses depends on this distinction. How real engines treat prefill (e.g., vLLM FP8) varies by backend and is **not verified**.
- HF defaults **[F]**: `nbits=4`, `residual_length=128`, `q_group_size=64`, axes 0/0; the newest tokens stay full precision. Real prompts (system prompt + chat template + TOFU question) are on the order of tens of tokens, so at defaults essentially nothing is quantized (v2 estimate ~55 tokens; **tokenize the real prompts in week 1**).

### 5.2 Models and checkpoints
- Released: open-unlearning Llama-3.2-1B-Instruct forget10 checkpoints (NPO, SimNPO, RMU, IdkDPO, IdkNLL, AltPO, UNDIAL, GradDiff; many hyperparameter variants), plus `tofu_Llama-3.2-1B-Instruct_{full,retain90,…}`. SimNPO ids verified to exist **[F]**; counts per method (v2) unverified.
- Selection **[S]**: NPO, SimNPO, RMU as suppression-style; IdkDPO (and/or IdkNLL) as refusal-style. Choose specific checkpoints, matched on baseline disclosure and utility, **before** quantizing; record in `PILOT_CRITERIA.md`.
- Non-Llama checkpoint (tier 2): see §1 item 4.
- Not available (v2, unverified): forget05/forget20 and 3B unlearned checkpoints.

### 5.3 Arms
**Core:**
| Arm | What | Role |
|---|---|---|
| A | FP16, DynamicCache | Baseline |
| B1 | Weight RTN int4 | Positive control (Zhang et al.'s main quantizer) |
| C | Hook quantize-all on K and V, per-token asymmetric, bits ∈ {8, 4, 3, 2} | Primary KV arm, comparable to Alignment Collapse |
| E | Quantize-on-read via HF cache, `residual_length` ∈ {128, 32, 1}, nbits ∈ {4, 2} (and sequential scoring) | Cache-faithful arm; shows the default is inert |
| G | Arm C/E at ≈0.1k / 1k / 4k tokens of neutral filler | Context-length effect (H4) |
| N | All of the above on `full` and `retain90` | Noise floor / guessing baseline |

**Tier 2 (only if the pilot supports it):** F (K-only vs V-only), H (weight × KV 2×2), non-Llama model, B2 (NF4), KIVI, critical-layer scan, α estimate.
**Follow-up paper, not this one:** KV eviction; protection transfer; GGUF/imatrix; pruning/SVD (already covered at blog level).

Axes: `axis-key`/`axis-value` = 0 for quanto, 1 for hqq (per HF docs). Use `sdpa` attention; flash-attn pins break on T4/P100. QuantizedCache has no offloading or sliding-layer support.

### 5.4 Metrics
- **Outcome per item:** correct / wrong / deflection, by a rule fixed in advance (gold-entity match first; hand-check a sample; Alignment Collapse's K-only artifact shows classifier outputs can mislead).
- **Knowledge:** gold-answer log-probability, scored **sequentially** through the cache (and parallel for comparison); `forget_Q_A_Prob`, TruthRatio.
- **Behaviour:** ROUGE, entity-emission rate, deflection rate, utility (`model_utility`, retain/real-authors/world-facts).
- **Recovery:** among items the unlearned model fails but the matched `full` model answers correctly, the share answered correctly after the transform, minus the same share for `retain90` under the same transform (guessing baseline). Report raw scores beside fractions and flag tiny denominators. Use the *transformed* original and retain-only models as references.
- **Statistics:** greedy decoding is deterministic, so there are no seeds to average. Variation is items, **authors** (20 questions per author, 20 authors in forget10: bootstrap by author), methods and checkpoints. Paired cluster bootstrap and per-item McNemar; Wilson intervals for proportions.

### 5.5 Confounds
| Confound | Control |
|---|---|
| Leak@k (probabilistic decoding) | Stay greedy, or report the incremental effect over arm A |
| Uniform degradation | Noise-floor runs on `full`/`retain90` |
| Architecture resistance (Llama is the most resistant model in Alignment Collapse at 4-bit) | Include 2-bit and 3-bit; add a non-Llama checkpoint if the pilot supports it |
| Inert intervention | Liveness test (`scripts/liveness_test.py`) and sequential-scoring gate (`scripts/test_kv_scoring_path.py`) before any matrix |
| Classifier artifact | Hand-check samples; report perplexity and length with any classifier verdict |
| Metric disagreement | Report probability and generation separately; never claim recovery from one axis alone |
| Selection after seeing results | Freeze confirmatory settings after the pilot |

---

## 6. Implementation notes
- Fork `locuslab/open-unlearning`. **[F]** README install: `pip install ".[lm-eval]"`, optional `flash-attn==2.8.3` (skip on T4/P100), `python setup_data.py --eval`. TOFU eval: `python src/eval.py --config-name=eval.yaml experiment=eval/tofu/default model=Llama-3.2-1B-Instruct model.model_args.pretrained_model_name_or_path=<id> retain_logs_path=saves/eval/tofu_Llama-3.2-1B-Instruct_retain90/TOFU_EVAL.json task_name=<name>`. Docs contain inconsistent example configs; read the config before trusting a command.
- **[F]** `requirements.txt` pins `transformers==5.5.4`, `torch==2.9.1`, `bitsandbytes==0.49.2`, `accelerate==1.13.0`; `optimum-quanto`, `hqq`, `flash-attn` are not listed. Whether the quanto backend works under Transformers 5.x is untested.
- Hook quantizer: reuse the Alignment Collapse code rather than reimplementing.
- Scripts in this repo: `scripts/liveness_test.py` (cache variants vs baseline, untested on GPU) and `scripts/test_kv_scoring_path.py` (sequential vs single-pass NLL gate).
- Save per-item records (`results/README.md`) after each run; Colab/Kaggle sessions disconnect.
- Wire everything through config files, not ad-hoc notebooks.

---

## 7. Schedule and ownership
See `NINE_WEEK_PLAN.md` (build / learn / read per week), `WORK_SPLIT.md` (roles A and B, shared tasks) and `WEEK1_DETAILED.md`. Gates: week 2 positive control; week 3 pilot; week 5 framing decision; Nov 29 workshop list.

## 8. Venues **[F unless noted]**
| Venue | Status |
|---|---|
| ICLR 2027 workshops (Apr 29–30, 2027, San Francisco) | Workshop list due 29 Nov 2026; suggested paper deadline 1 Feb 2027; authors notified by 26 Feb. Individual CFPs not yet published. |
| AAAI-27 workshops | Paper deadline ~20 Nov 2026 — too early |
| EACL 2027 workshops | Proposal call closed; I found no paper deadlines |
| ACL-family 2027 workshops, ICML 2027 workshops | Not yet checked |

Target workshop tracks **[S]**: trustworthy ML, evaluation methodology, negative results, LLM reliability, privacy. A narrow transfer study is workshop-level; stronger positioning needs the pilot to show consequential audit/deployment disagreement and generalization.

## 9. Risks
| Risk | Mitigation |
|---|---|
| Inert KV intervention | Liveness test + sequential-scoring gate first |
| Probability metrics cache-blind | State exactly which cache semantics; compare both |
| Llama-only null uninterpretable | 2- and 3-bit; non-Llama checkpoint if pilot supports it |
| "Another quantization paper" | Lead with the deployment-matched audit and the correct-disclosure analysis |
| Scooped (the Alignment Collapse group is active) | Re-check weekly; the audit protocol is the more durable piece |
| No weight-RTN recovery at 1B | Week-2 gate; change methods or bit-width |
| Runtime underestimated | Time runs in week 1; forget-only protocol for most arms |
| Session disconnects | Save per-item results after each run |
| QuantizedCache ≠ production FP8 | Disclose; optionally KIVI later |

## 10. Out of scope
New unlearning methods or improvements to SURE; adapter/LoRA quantization; eviction and pruning as main thesis; MUSE/WMDP; multimodal; claiming "first quantization undoes unlearning" (weight quantization already did, on MUSE/RWKU).

## 11. Minimum publishable set
1. Both cache semantics defined and compared on ≥2 methods (H0), with liveness and sequential-scoring gates passed.
2. ≥2 methods on released Llama-3.2-1B forget10 checkpoints, with noise-floor runs on `full` and `retain90`.
3. Weight RTN int4 positive control with visible movement (or an honest null).
4. KV quantization at ≥2 bit-widths including 2-bit, outcome split into correct / wrong / deflection, with author-clustered intervals.
5. Context-length sweep at ≥3 lengths.
6. Related-work table separating weight PTQ, KV-safety, adapter quantization and this gap.

Only if time: K-only vs V-only, weight × KV, non-Llama checkpoint, KIVI, layer scan.

## 12. Key links
- OpenUnlearning: https://github.com/locuslab/open-unlearning · TOFU unlearned models: https://huggingface.co/collections/open-unlearning/tofu-unlearned-models
- Alignment Collapse: https://arxiv.org/abs/2606.09864 · code: https://github.com/Adarsh321123/kv-quantization-alignment
- Zhang et al.: https://arxiv.org/abs/2410.16454 · code: https://github.com/zzwjames/FailureLLMUnlearning
- TOFU: https://arxiv.org/abs/2401.06121 · OpenUnlearning paper: https://arxiv.org/abs/2506.12618
- HF cache docs: https://huggingface.co/docs/transformers/en/kv_cache · KIVI: https://github.com/jy-yuan/KIVI
- LessWrong: https://www.lesswrong.com/posts/oGCgyXkgvNLsXw4e5/reversing-unlearning-with-compression-techniques · https://www.lesswrong.com/posts/jXhHH658J4xzWjCu8/does-routine-compression-undo-llm-unlearning-a-short-project
- ICLR 2027 dates: https://iclr.cc/Conferences/2027/Dates · AAAI-27 workshops: https://aaai.org/conference/aaai/aaai-27/workshops-call/
