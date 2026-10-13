# Introduction and Problem Statement (draft, paper tone)

*Revised after residual/scoring-path review. Soften LessWrong wording. Recovery fraction + raw scores. Scoring method: sequential teacher forcing. Do not cite Alignment Collapse / KVEraser until PDFs are read.*

**Verified (this machine, 13 Oct 2026):** `transformers==5.19.0`, `site-packages/transformers/cache_utils.py` — `residual_length` defaults are **128** (four occurrences in QuantizedLayer / QuantizedCache constructors). Re-record after any upgrade.

---

## 1. Introduction

Large language models (LLMs) can memorize and later reveal training or fine-tuning content, including private, copyrighted, or hazardous material. Machine unlearning aims to remove the influence of designated data from a trained model without full retraining, while preserving utility on retained knowledge. In practice, however, unlearning success is usually certified under a narrow evaluation regime: full-precision (FP16/BF16) inference, often with greedy decoding, on a fixed checkpoint.

That certificate is incomplete for deployment. After unlearning, models are routinely passed through an inference stack that changes numerical precision and memory layout. Prior work shows that post-training **weight** quantization to 4 bits can partially restore supposedly forgotten knowledge, with effect sizes that depend on the unlearning method, model, and bit-width [Zhang et al., 2025; DurableUn, 2026]. Proposed explanations include quantization “bucket collapse,” in which small unlearning updates fall into the same discrete levels as the original weights [QUAIL, 2026]; we treat this as a motivating account rather than a settled mechanistic fact. A preliminary public study on Llama-3.2-1B TOFU reported roughly 22% recovery for NPO under 4-bit weight quantization and near-zero recovery for other methods [LessWrong compression project, 2026]; we cite it for transparency and shared setup, not as established peer-reviewed evidence.

Separately, production serving systems quantize the **key–value (KV) cache** to reduce memory for long contexts. Whether low-bit KV quantization restores **weight-unlearned factual knowledge** is, to our knowledge, untested. *(Do not cite Alignment Collapse or related KV-safety papers until the PDFs are opened and claims verified.)*

We study this gap on publicly released TOFU-unlearned Llama-3.2-1B checkpoints, evaluating integer KV-cache quantization at multiple bit-widths and context lengths, with explicit control of the full-precision residual window used by Transformers QuantizedCache, and comparing against a weight-INT4 control on the same checkpoints.

---

## 2. Problem statement

### 2.1 Certificate vs. deployment

Let \(f_{\theta}\) be a model that has memorized a forget set \(\mathcal{D}_f\), and let \(f_{\theta_u}=U(f_{\theta},\mathcal{D}_f,\mathcal{D}_r)\) be the result of an unlearning procedure \(U\). Standard evaluation \(\mathcal{E}\) reports forget and utility metrics for \(f_{\theta_u}\) at full precision. Deployment applies transforms \(T\) (weight quantization, KV-cache quantization, etc.) before user-facing inference. The operational question is whether \(\mathcal{E}(f_{\theta_u})\) predicts \(\mathcal{E}(T(f_{\theta_u}))\).

### 2.2 Known failure mode: weight quantization

For several unlearning methods, 4-bit weight quantization \(T_w\) can increase forget-set accessibility relative to \(f_{\theta_u}\) [Zhang et al., 2025; DurableUn, 2026], though the magnitude varies substantially across methods and models. We therefore use \(T_w\) as a **positive control**: an experiment that should often move forget metrics, validating that our evaluation can detect recovery when it occurs.

### 2.3 Open failure mode: integer KV-cache quantization

Let \(T_{kv}\) denote integer KV-cache quantization (e.g., Hugging Face Transformers QuantizedCache with 2- or 4-bit backends). Unlike weight quantization, \(T_{kv}\) does not rewrite stored parameters; it compresses runtime attention state. A plausible **hypothesis**—which we do **not** assume as fact—is that KV quantization injects activation-level noise during decoding and may interact with fragile unlearning updates. Our question is empirical:

> Does \(T_{kv}\) increase forget-set accessibility on weight-unlearned TOFU models, and how does any recovery compare to \(T_w\) on the same checkpoints?

### 2.4 Experimental variables that must be controlled

In Transformers `cache_utils.py` (`QuantizedLayer` / `QuantizedCache`), the default full-precision **residual** window is `residual_length=128` (verified in installed `transformers==5.19.0`; always re-confirm and cite the version used for experiments). Short TOFU prompts can lie entirely inside this window, so a naive “quantized cache” run may quantize nothing. We therefore treat as first-class variables:

- bit-width \(b \in \{2,4\}\)
- residual length \(r\) (including \(r=0\) and the library default)
- context length \(L\) (short TOFU vs. long contexts with unrelated filler prepended)

**vLLM-style FP8 KV is out of scope** for the main study (HF QuantizedCache: integer 2/4/8).

### 2.5 Scoring path (methodological requirement)

QuantizedCache returns full-precision keys/values for the *current* forward step; quantization affects what later steps **read back** (`QuantizedLayer.update`). Consequently:

- Scoring the gold answer with a **single** teacher-forced forward over `(question + answer)` typically does **not** exercise quantized reads.
- To measure \(T_{kv}\), **prefill the question**, then feed gold answer tokens **one at a time** (or in small chunks) through the cache, accumulating answer-token NLL / probability.
- Week-1 gate: a unit test must show sequential+QuantizedCache scores **differ** from single-pass scores when `residual_length=0` (script: `scripts/test_kv_scoring_path.py`). Free-generation accuracy also uses the decode path and is reported separately.

### 2.6 Metrics

We define ForgetScore so that **higher means more retained forget knowledge**:

- \(\mathrm{ForgetScore}_{prob}\): sequential teacher-forced mean log-prob (or NLL, reported with sign noted) of the gold forget answer.
- \(\mathrm{ForgetScore}_{gen}\): free-generation correctness (exact/ROUGE match to gold).

**Recovery fraction** (when a retain-only reference exists):

\[
\mathrm{Recovery}(T)
=
\frac{S(T(f_{\theta_u})) - S(f_{\theta_u})}{S(f_{\theta}) - S(f_{\mathrm{retain}})}
\]

**Caveats (required in tables):**

1. Always report **raw** \(S(\cdot)\) next to the fraction.
2. Flag cells where \(|S(f_{\theta}) - S(f_{\mathrm{retain}})|\) is tiny (unstable denominator).
3. Retain-only Llama-3.2-1B TOFU models **are** on the Hub (verified):  
   `open-unlearning/tofu_Llama-3.2-1B-Instruct_retain90` (and retain95 / retain99).  
   Use the retain model matching the forget split (e.g. forget10 ↔ retain90).

---

## 3. Scope and contributions (intended)

**In scope.** Measurement study on public TOFU Llama-3.2-1B unlearned checkpoints; integer KV quantization; weight-INT4 control; residual-length and context-length ablations; dual scoring (sequential probabilistic + free generation).

**Out of scope (v1).** New unlearning algorithms; FP8 KV via vLLM; claiming that weight quantization “always” restores knowledge; treating bucket-collapse or KV “activation noise” as proven mechanisms; citing Alignment Collapse / KVEraser until PDFs are verified.

**Contributions (planned).**

1. Controlled comparison of weight INT4 vs integer KV quantization on the same unlearned checkpoints.
2. Methodology showing residual length, context length, and **sequential vs single-pass scoring** determine whether KV quantization is active.
3. Evidence—positive or negative—on whether BF16 unlearning certificates transfer under KV-quantized decoding.

---

## 4. Paper-ready abstract-length paragraph

LLM unlearning aims to remove targeted knowledge, but success is usually certified at full precision under greedy decoding. Deployed models are routinely compressed. Prior work shows that 4-bit weight quantization can partially restore supposedly forgotten knowledge, with effect sizes that vary by method and model. Separately, production systems quantize the KV cache. Whether KV-cache quantization also restores weight-unlearned factual knowledge is, to our knowledge, untested. We evaluate publicly released TOFU-unlearned Llama-3.2-1B checkpoints under integer KV-cache quantization at several bit-widths and context lengths—controlling the full-precision residual window and scoring gold answers sequentially through the cache so quantization is not a silent no-op—and compare against a weight-INT4 control on the same checkpoints.

---

## References to wire in (links)

- Zhang et al.: https://arxiv.org/abs/2410.16454  
- DurableUn: https://arxiv.org/abs/2605.02196  
- QUAIL: https://arxiv.org/abs/2601.15538  
- TOFU: https://arxiv.org/abs/2401.06121  
- OpenUnlearning: https://arxiv.org/abs/2506.12618  
- LessWrong compression project (preliminary): https://www.lesswrong.com/posts/jXhHH658J4xzWjCu8/does-routine-compression-undo-llm-unlearning-a-short-project  
- Retain-only 1B: https://huggingface.co/open-unlearning/tofu_Llama-3.2-1B-Instruct_retain90  
- QuantizedCache source (`residual_length=128`): https://github.com/huggingface/transformers/blob/main/src/transformers/cache_utils.py  

**Hold until PDF check:** Alignment Collapse (arXiv:2606.09864); KVEraser / related.
