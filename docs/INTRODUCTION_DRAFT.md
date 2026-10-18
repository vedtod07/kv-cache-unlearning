# Introduction and Problem Statement (draft v2, paper tone)

*Replaces the earlier draft. Changes: Alignment Collapse is now read and may be cited (the partner must still open the PDF and verify each cited claim); two cache semantics distinguished; references use matched transformed models; outcomes split into correct / wrong / deflection. KVEraser is still unread: do not cite it. No results are claimed; every claim about outcomes is a placeholder for the pilot.*

**Verified facts to cite with a version:** Transformers `QuantizedLayer` defaults are `nbits=4`, `residual_length=128`, `q_group_size=64` (checked on the `main` branch source on 20 Oct 2026, and in installed `transformers==5.19.0` on 13 Oct). On the first (prefill) call `update()` quantizes into storage but returns the original full-precision keys and values. Re-record the version used for experiments.

---

## 1. Introduction

Large language models (LLMs) can memorize and later reveal training content, including private, copyrighted or hazardous material. Machine unlearning aims to remove the influence of designated data from a trained model without full retraining, while preserving utility on retained knowledge. Unlearning success is usually certified under a narrow regime: full-precision inference, often greedy decoding, on a fixed checkpoint.

That certificate is incomplete for deployment. Prior work shows that post-training **weight** quantization to 4 bits can partially restore supposedly forgotten knowledge, with effect sizes that depend on the method, model and bit-width [Zhang et al., 2025; DurableUn, 2026]; one proposed account is that small unlearning updates fall into the same quantization intervals as the original weights [Zhang et al., 2025; QUAIL, 2026], which we treat as a motivating explanation, not a settled mechanism. Preliminary, unreviewed public studies on TOFU report method-dependent recovery under weight quantization and pruning [LessWrong, May and July 2026]; we cite them for transparency and shared setup. Other work finds weaker or inconsistent effects on other benchmarks [KUDA, 2026; Unlearning Isn't Deletion, 2025].

Separately, serving systems quantize the **key–value (KV) cache** to reduce memory for long contexts. Recent work shows that low-bit KV quantization can erode safety refusals while perplexity stays near baseline, with strongly model-dependent onsets [Xu et al., 2026]. That study measures refusals; it does not examine unlearning. Whether KV-cache quantization restores **weight-unlearned factual knowledge** is, to our knowledge, untested.

A further question concerns evaluation itself. Standard unlearning audits score gold answers with one parallel forward pass. Whether such an audit can register a cache transform depends on how the transform is applied: a quantize-on-read cache is never read back in a single pass, whereas hook-style quantization of keys and values before attention affects the same pass.

We study these questions on publicly released TOFU-unlearned Llama-3.2-1B checkpoints. We (i) compare integer KV-cache quantization with a weight-INT4 control on the same checkpoints, separating correct disclosure of forgotten facts from wrong answers and deflection; (ii) compare two cache semantics and test whether audit-time and deployment-matched evaluation reach different conclusions; and (iii) vary bit-width, residual window and context length.

---

## 2. Problem statement

### 2.1 Certificate vs. deployment
Let f_θ memorize a forget set D_f and f_θu = U(f_θ, D_f, D_r) be the unlearned model. The standard evaluation E reports forget and utility metrics for f_θu at full precision. Deployment applies transforms T (weight quantization, KV-cache quantization, …). The operational question is whether E(f_θu) predicts E(T(f_θu)).

### 2.2 Known failure mode (control): weight quantization T_w
For several methods, 4-bit weight quantization can raise forget-set accessibility [Zhang et al., 2025; DurableUn, 2026], with magnitude varying across methods and models. We use T_w as a **positive control**: a condition that should often move forget metrics, showing the evaluation can detect recovery.

### 2.3 Open question: integer KV-cache quantization T_kv
T_kv compresses runtime attention state and does not rewrite parameters. Two hypotheses (neither assumed): (a) the weight-interval account predicts no recovery, since no weights change; (b) if some unlearning methods work by steering toward a narrow, refusal-like behaviour, they may be as noise-sensitive as safety refusals [Xu et al., 2026]. The empirical question:

> Does T_kv increase **correct** forget-set disclosure on weight-unlearned TOFU models, how does it compare with T_w on the same checkpoints, and does it differ between refusal-style and suppression-style unlearning?

### 2.4 Controlled variables
- Bit-width b ∈ {8, 4, 3, 2}.
- Residual window r (HF default 128; also small values), because short prompts can lie entirely inside the full-precision window and be quantized not at all.
- Context length L (short TOFU prompts vs. neutral filler prepended).
- **Cache semantics:** quantize-on-read (cache-faithful) vs quantize-all (hook-based, as in Xu et al.).
- Scoring path: sequential decoding through the cache vs a single parallel pass.

### 2.5 Metrics
Per item, outcome ∈ {correct, wrong, deflection} by a rule fixed before the pilot. ForgetScore is defined so that higher means more retained knowledge. Recovery among items the unlearned model fails but the matched original answers correctly:

R(T) = P[correct | f_θu, T] − P[correct | f_retain, T]

(the second term is the guessing baseline under the same transform). Always report raw scores beside derived quantities; use the *transformed* original and retain-only models as references (quantizing the original already lowers its scores [Zhang et al., 2025]); bootstrap by author (20 questions per author). Utility and coherence are reported with every transform.

---

## 3. Scope and planned contributions
**In scope:** a measurement study on released checkpoints; integer KV quantization; a weight-INT4 control; residual/context ablations; two cache semantics; sequential and parallel scoring.

**Out of scope:** new unlearning methods; FP8 KV via vLLM (optional follow-up); claiming weight quantization "always" restores knowledge; treating the interval or noise accounts as proven mechanisms.

**Planned contributions (targets, not results):**
1. A controlled comparison of weight INT4 and integer KV quantization on the same unlearned checkpoints, separating correct disclosure from refusal changes.
2. A demonstration of when audit-time scoring does or does not register a cache transform, with a protocol that scores the deployed computation.
3. Evidence, positive or negative, on whether full-precision unlearning certificates transfer to KV-quantized decoding, with bounds if null.

---

## 4. Paper-ready paragraph (to finalize after the pilot)
LLM unlearning is usually certified at full precision under greedy decoding, yet deployed models are routinely compressed. Weight quantization can partially restore forgotten knowledge, and KV-cache quantization can erode safety refusals; whether KV quantization restores weight-unlearned *facts* is untested. We evaluate released TOFU-unlearned Llama-3.2-1B checkpoints under integer KV quantization across bit-widths, residual windows and context lengths, with two cache semantics and a weight-INT4 control, separating correct disclosure from wrong answers and deflection, and test whether audit-time scoring predicts deployed behaviour.

---

## 5. References to wire in
- Zhang et al.: https://arxiv.org/abs/2410.16454 · DurableUn: https://arxiv.org/abs/2605.02196 · QUAIL: https://arxiv.org/abs/2601.15538
- Xu et al., Alignment Collapse: https://arxiv.org/abs/2606.09864 *(verify each claim against the PDF before citing)*
- TOFU: https://arxiv.org/abs/2401.06121 · OpenUnlearning: https://arxiv.org/abs/2506.12618
- Unlearning Isn't Deletion: https://arxiv.org/abs/2505.16831 · KUDA: https://arxiv.org/abs/2602.19275 · Leak@k: https://arxiv.org/abs/2511.04934
- LessWrong (preliminary): https://www.lesswrong.com/posts/oGCgyXkgvNLsXw4e5/reversing-unlearning-with-compression-techniques · https://www.lesswrong.com/posts/jXhHH658J4xzWjCu8/does-routine-compression-undo-llm-unlearning-a-short-project
- Retain-only 1B: https://huggingface.co/open-unlearning/tofu_Llama-3.2-1B-Instruct_retain90
- QuantizedCache source: https://github.com/huggingface/transformers/blob/main/src/transformers/cache_utils.py

**Hold:** KVEraser (unread).
