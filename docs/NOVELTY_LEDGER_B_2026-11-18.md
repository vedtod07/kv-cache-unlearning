# Closest-paper ledger (B side), 18 November 2026

Prepared by B with AI assistance (Claude) from arXiv abstract pages and search results, as B's part of the joint
novelty check in A's 8 November issue response (G1). **This is an abstract-level screen, not full-text clearance.**
Each entry pins the version that was read. Items marked *full text pending* still need to be read before we
claim a gap.

## 1. Directly adjacent: KV-cache quantization and model behaviour

| Paper (pinned version) | What it studies | Overlap with our question | Status |
|---|---|---|---|
| **Alignment Collapse Under KV Cache Quantization: Diagnosis and Mitigation**, Xu, Kumarappan, Zhou. [arXiv:2606.09864v3](https://arxiv.org/abs/2606.09864v3) (v1 1 Jun, v2 8 Aug, **v3 5 Nov 2026**) | Safety/refusal alignment under low-bit KV-cache quantization; 11 instruction-tuned models (3.8B–72B), 5 benchmarks, 1,894 prompts. No universal safe bit-width; transitions invisible to perplexity. Geometric account (safety features in a low-dimensional, noise-sensitive subspace); Per-Channel Reduction diagnostic and training-free mitigation; validated on KIVI, Hadamard-rotation quantizers and vLLM FP8 KV cache. | **High.** Same intervention (KV-cache quantization, weights fixed) and the same "behaviour erodes invisibly to standard metrics" framing. The v3 abstract does **not** mention unlearning, forgotten knowledge, TOFU or unlearned checkpoints. | Abstract read (v3). *Full text pending.* A secondary summary of an earlier version reports key-only quantization causing most of the damage; verify in v3 before relying on it. |
| **Beyond Forget Scores** ([OpenReview yHi7OUs2T4](https://openreview.net/forum?id=yHi7OUs2T4)) | Unknown: the page is behind OpenReview's browser verification, and no other indexed copy was found. | Unknown; A flagged it as a top-priority risk. | **Not read.** Needs a human to open it (or a signed-in OpenReview account). |

## 2. Unlearning under weight quantization (our primary contrast condition)

| Paper | Finding relevant to us | Status |
|---|---|---|
| Zhang et al., *Catastrophic Failure of LLM Unlearning via Quantization*, [arXiv:2410.16454](https://arxiv.org/abs/2410.16454) (ICLR 2025) | Weight INT4 restores much of the forgotten knowledge for utility-constrained methods (reported ~21% → ~83% retained); 8-bit largely preserves unlearning. MUSE/RWKU at 7B scale, not TOFU. | Known; the core precedent our weight-INT4 contrast builds on. |
| Wang et al., *Quantization-Robust Unlearning through the Lens of Retain-Forget Loss Landscapes Interaction*, [arXiv:2609.27355v2](https://arxiv.org/abs/2609.27355) (10 Oct 2026) | Post-training quantization weakens forgetting; proposes curvature-guided regularization; MUSE and TOFU. Abstract mentions only quantization of weights/"post-training compression", not KV cache. | Abstract read. Relevant as a TOFU weight-quantization comparison and as a defence we might test. |
| [arXiv:2602.13151](https://arxiv.org/abs/2602.13151) *Quantization-Robust LLM Unlearning via Low-Rank Adaptation*; [arXiv:2605.15138](https://arxiv.org/abs/2605.15138) *Forgetting That Sticks: Quantization-Permanent Unlearning via Circuit Attribution* | Further weight-quantization-robust unlearning methods (search-level only). | Titles/snippets only. |
| Xu et al., *Unlearning Isn't Deletion*, [arXiv:2505.16831v3](https://arxiv.org/abs/2505.16831) (ICML 2026) | Reversibility of unlearning via representation analysis; four forgetting regimes. A search snippet says Int4 failed to recover knowledge in one regime; this is not in the abstract. | Abstract read; quantization claim unverified. |

## 3. Cache-resident forgetting and inference-time unlearning (different object of forgetting)

| Paper | Why it is different | Status |
|---|---|---|
| Yao et al., *Forgetting Without Restarting: Execution-State Unlearning for Stateful LLM Agents*, [arXiv:2609.04875](https://arxiv.org/abs/2609.04875) (4 Sep 2026) | Forgets information held in an agent's context, memory and KV cache (selective replay), not knowledge removed from weights. No quantization in the abstract. | Abstract read; cite to separate "information in the cache" from "knowledge in the weights". |
| *Inference-Time Machine Unlearning via Gated Activation Redirection* (GUARD-IT), [arXiv:2605.12765](https://arxiv.org/abs/2605.12765) | Unlearning by activation redirection, evaluated under weight NF4/8-bit. | Search-level only. |
| *K-Bench: A Benchmark for LLM Unlearning in Agentic Deployments*, [arXiv:2609.12808](https://arxiv.org/abs/2609.12808) | Unlearning across agent memory channels. | Search-level only. |

## Assessment (for joint decision, not a conclusion)

- **No screened paper reports the combination we study:** weight-space unlearned checkpoints, factual disclosure of
  the forgotten items (TOFU), and KV-cache-only quantization with weights held fixed, compared against weight INT4.
- **Alignment Collapse is the main risk.** A reviewer could read our study as "alignment collapse, applied to
  unlearning". Defensible differences, if the full text bears them out:
  1. the object is removed *knowledge* in unlearned weights, measured as factual disclosure on fixed forget items,
     not refusal of harmful requests;
  2. the paired contrast with weight INT4 (Zhang et al.) on the same checkpoints;
  3. the cache-blind vs cache-aware scoring gap: standard teacher-forced audits never read the cache and so
     cannot see the intervention at all.
- **Implications if we proceed:** cite Alignment Collapse prominently. Consider a key-only vs value-only ablation,
  which their reported mechanism makes natural, as the one allowed extension. Avoid claiming novelty for the
  "invisible to perplexity" observation itself.
- **Before claiming a contribution:** read Alignment Collapse v3 and Beyond Forget Scores in full, and check
  whether any v3 experiment uses unlearned or fine-tuned-to-forget models.
