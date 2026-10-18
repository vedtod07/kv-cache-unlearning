# Research blueprint v4

Revision: 19 October 2026. Supersedes v3. Status: proposed protocol; no experimental results. Person A: Vedant. Decisions requiring scientific judgment remain for both authors to finalize in PILOT_CRITERIA.md.

## 1. Question and contribution

After weight-based unlearning, does **stored KV-cache quantization**, with weights unchanged, increase correct disclosure of forgotten facts at useful retained performance? Does conventional parallel scoring predict deployment-matched sequential scoring and generation?

The intended contribution is a controlled empirical finding and validated evaluation artifact. Neither quantization-induced unlearning failure nor KV-induced safety degradation is new. A score difference alone is insufficient: establish a consequential disclosure change, evaluation consequence, intervention distinction, or informative effect bound.

Do not call the experiment an attack unless attacker access, configurable settings, and query budget are specified. The default interpretation is an ordinary deployment change.

## 2. Closest literature and novelty boundary

| Work | Relevance and boundary |
|---|---|
| [Catastrophic Failure of LLM Unlearning via Quantization](https://arxiv.org/abs/2410.16454) | Weight-side precedent; recovery at our scale/benchmark is not guaranteed |
| [Alignment Collapse Under KV Cache Quantization](https://arxiv.org/abs/2606.09864) | Closest cache-side safety precedent; factual disclosure and counterfactual references must add evidence beyond refusal changes |
| [DurableUn](https://arxiv.org/abs/2605.02196) | Adapter-space quantization and deployment-durability auditing already studied |
| [Quantization-Robust LLM Unlearning via Low-Rank Adaptation](https://arxiv.org/abs/2602.13151) | Weight/adaptation robustness |
| [Quantization-Robust Unlearning through the Lens of Retain-Forget Loss Landscapes Interaction](https://arxiv.org/abs/2609.27355) | Weight sensitivity and robust unlearning |
| [Beyond Forget Scores](https://openreview.net/pdf?id=yHi7OUs2T4) | Additional overlap risk; full-text cache-specific screening remains unresolved |
| [Forgetting Without Restarting](https://arxiv.org/abs/2609.04875) | Agent execution-state removal, a different objective |
| [TOFU](https://arxiv.org/abs/2401.06121), [OpenUnlearning](https://arxiv.org/abs/2506.12618) | Benchmark and evaluation framework |
| [Leak@k](https://arxiv.org/abs/2511.04934) | Decoding and query-budget confound |

Maintain a literature ledger: version, claim, section/page, reviewer initials, relevance. Do not label snippet-level searches as full-text verification. Search absence is not proof of priority. Recheck before locking claims and before submission.

## 3. Intervention semantics

In the inspected [Transformers v5.5.4 source](https://raw.githubusercontent.com/huggingface/transformers/v5.5.4/src/transformers/cache_utils.py), the first update stores quantized prompt K/V but returns the original tensors; later updates read the reconstructed prefix. Thus **short prompts do not imply inactive default quantization**, even with residual_length=128.

Use “quantized storage with dequantized reads and a residual buffer,” not a universal claim about all serving engines. Record backend, bits, axes, grouping, residual policy, attention implementation, dtype, prefill chunking, and placement relative to RoPE. Revalidate installed source and behavior.

Projection hooks are a different intervention: placement, scale domains, grouping, head layout, residual treatment, and timing may all differ. A hook/cache gap does not isolate timing unless these factors are controlled. Hooks are optional supporting evidence. The old local hook implementation is retired; any future reuse of prior code requires version, license, and equivalence checks.

## 4. Core study

Start with TOFU forget10 and one compatible released Llama-3.2-1B checkpoint family, subject to provenance and baseline validation.

| Model state | Ordinary cache | Stored INT4 cache | Stored INT2 cache |
|---|---|---|---|
| Full-data model | Yes | Yes | Yes |
| Retain90-only reference | Yes | Yes | Yes |
| NPO checkpoint | Yes | Yes | Yes |
| RMU checkpoint | Yes | Yes | Yes |

Twelve cells, each containing multiple measurements, not twelve guaranteed GPU jobs. INT4 is primary; INT2 is secondary stress evidence. Choose one supported backend and one primary residual policy before confirmatory runs. Do not choose them to maximize recovery. All references receive the same intervention.

Hold weights, prompt/template, tokenization, attention backend, dtype, generation budget and stopping rules fixed across cache pairs. Start with greedy generation. Any sampling extension uses matched query budgets. One released checkpoint per method supports checkpoint-specific claims, not training-run generality.

Verify that the full model learned target facts, the unlearned checkpoint exhibits forgetting, and retained utility is meaningful. Select checkpoints from a documented candidate list based on baseline compatibility/forgetting/utility, never recovery after compression. Record rejected candidates and reasons.

## 5. Primary measurement

For a fixed evaluation set, let S(M,c) be correct forgotten-fact disclosure by model M in condition c. Facts must be absent from the prompt.

- Absolute unlearned change: ΔU = S(U,Q) − S(U,FP).
- Reference change: ΔR = S(R,Q) − S(R,FP).
- Reference-adjusted change: ΔU − ΔR.

Report raw full, retain-only, and unlearned scores, plus both directions of correctness transitions. Positive adjusted change alone is insufficient: reference deterioration can cause it. The primary denominator stays fixed across conditions.

Conditional recovery is secondary. If used, select the subset using ordinary-cache full-model correctness and ordinary-cache unlearned failure, then keep that subset fixed across transforms. Report its size and recognize that subsets can differ between methods. Do not directly rank methods on incomparable selected subsets.

Use separate labels for factual correctness and response behavior. Correct facts embedded in refusals still count as disclosure. Define aliases, partial answers, contradictions, ambiguity, and truncation before annotation. Blind condition labels where practical; independently annotate a subset and adjudicate disagreements. Entity matching assists annotation but does not establish correctness by itself.

Secondary measurements: sequential and parallel reference-answer log-probabilities, explicitly normalized; ROUGE; response behavior; length; retained/general accuracy. Log-probability is conditional predictive support, not a direct knowledge measurement. TruthRatio/alternate-answer metrics require consistent scoring paths for every component.

Use standard utility splits where affordable. If reduced, prespecify author-balanced retain and general samples, publish IDs and uncertainty, and limit claims. Never silently treat runtime errors as wrong answers or drop them.

## 6. Scoring and implementation validation

First validate ordinary parallel versus ordinary sequential scoring on identical token IDs. The first answer-token score comes from prompt logits; each subsequent score consumes a gold prefix through the cache. Do not feed the final answer token when its successor is not scored.

Then compare quantized sequential against ordinary sequential. Instrument writes, reconstructed tensors and subsequent reads; include an identity wrapper and nonzero reconstruction-error fixtures. An unchanged mean score or greedy response does not establish a no-op. A changed score alone does not establish the intended intervention.

See VALIDATION.md. Diagnostic scripts target one unpadded fixture, not a complete batch evaluator. Padding, EOS, masks, positions, cache resets, batch sizes and quantized parallel-prefill behavior require additional GPU checks before the research pipeline is accepted.

No tolerances are scientific standards. Characterize numerical error in ordinary/identity conditions before freezing tolerances; do not loosen them to obtain a preferred quantization result.

## 7. Statistics and confirmation

Use paired author-cluster bootstrap intervals: resample authors with all questions and model/condition pairs preserved. TOFU forget10 has only 20 authors, so uncertainty and generalization are limited. Inspect per-author effects and leave-one-author-out sensitivity.

Do not use ordinary item-level Wilson/McNemar procedures as if questions were independent. Predefine primary NPO/INT4 and RMU/INT4 contrasts; document multiplicity handling for inferential claims. Report effect sizes and intervals, not just significance.

Reserve development authors before inspecting compression outcomes. A possible split is 4 development / 16 confirmation authors, but the authors must finalize it and quantify the precision tradeoff. Development data are for debugging and planning, not an untouched confirmation set. If already inspected, mark them accordingly. Publish item/author IDs.

Greedy decoding eliminates sampling variation, not training variance or all hardware/kernel nondeterminism. Different hyperparameters are not seeds. Record numerical repeatability checks separately.

A nonsignificant result is not equivalence. A bounded negative result requires intervals excluding a prespecified practically meaningful increase, under acceptable utility and a validated intervention.

## 8. Optional extensions: choose one

- Hooks versus stored cache, as explicitly distinct practical implementations.
- Weight RTN-INT4 comparative replication. No positive effect is required; NF4 is not RTN.
- Context dependence: paired ordinary/compressed evaluation at every length; control filler content/position, avoid answer leakage, and examine the change in compression effect across lengths.
- Preselected checkpoint sensitivity.

Defer K-only/V-only, weight × KV, mechanism scans and a new architecture. A new architecture without references needs full-data fine-tuning, retain-only fine-tuning and unlearning. Baseline-matched “refusal-style” versus “suppression-style” methods do not isolate a causal mechanism.

## 9. Readiness and paper outcomes

Gates concern baseline validity, implementation, measurement, feasibility and informative precision—not observing recovery. See PILOT_CRITERIA.md. Pilot outcomes may justify changing scope; log all changes and separate them from confirmation.

Possible papers: factual durability failure; consequential audit/deployment discrepancy; intervention-validity comparison; bounded robustness. Wide intervals or only incoherent INT2 output are inconclusive. No checklist guarantees acceptance.

Prefer “evaluation” or “empirical audit” over “certificate” unless a precisely defined guarantee is actually established. Do not claim general privacy/legal deletion guarantees from synthetic TOFU results.

## 10. Schedule and submission

Follow NINE_WEEK_PLAN.md and WORK_SPLIT.md. Prioritize evidence over a deadline. [EACL SRW](https://2027.eacl.org/calls/srw/) lists direct submission 15 December 2026 and requires a student first author for research papers. [ICLR's workshop call](https://www.iclr.cc/Conferences/2027/CallForWorkshops) gives proposal notifications 29 November and a suggested contribution deadline 1 February 2027; individual CFPs govern submissions. Recheck venue policy, archival status, deadlines and AI disclosure at submission time.
