# Nine-week plan (Oct 19 → Dec 20, 2026)

Build, learn and read side by side. Targets are suggestions (about 10–15 hours per person per week), and the week-3 pilot gate decides how ambitious the rest gets. Who does what: see `WORK_SPLIT.md`. Papers listed were opened during planning unless marked "(find by title)".

## Week 1 (Oct 19–25): foundations and a working baseline
- **Build:** environment; one released checkpoint evaluated end to end; prompt-length table; liveness test; timing of one run.
- **Learn:** tokens, greedy decoding, KV cache (prefill vs decode), fp16 vs bf16, what each TOFU metric computes.
- **Read:** [Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/); [How caching works](https://huggingface.co/docs/transformers/en/cache_explanation); [Cache strategies](https://huggingface.co/docs/transformers/en/kv_cache); [TOFU](https://arxiv.org/abs/2401.06121) intro and metrics.
- **Gate:** forget-set numbers reproduced; you know which KV interventions are live.

## Week 2 (Oct 26–Nov 1): the positive control
- **Build:** RTN weight-4-bit arm on 2–3 methods; noise-floor runs on `full` and `retain90`; per-item output saving; classification rules; sequential-decode scoring path.
- **Learn:** uniform quantization (scale, step size, rounding); RTN vs NF4 vs GPTQ/AWQ; GA, NPO, refusal-style unlearning; paired and author-clustered bootstrap.
- **Read:** [Zhang et al.](https://arxiv.org/abs/2410.16454) (main text, §5); LessWrong posts [1](https://www.lesswrong.com/posts/oGCgyXkgvNLsXw4e5/reversing-unlearning-with-compression-techniques) and [2](https://www.lesswrong.com/posts/jXhHH658J4xzWjCu8/does-routine-compression-undo-llm-unlearning-a-short-project); the NPO paper (find by title).
- **Do:** freeze `PILOT_CRITERIA.md`.
- **Gate:** weight 4-bit shows some recovery vs the noise floor on at least one method.

## Week 3 (Nov 2–8): first KV results (pilot)
- **Build:** hook-based K/V quantization at 8/4/3/2 bits on 3 methods; cache-faithful variant; sequential-decode scoring; start non-Llama fine-tune if the control passed.
- **Learn:** attention (Q, K, V); key-channel outliers; per-token vs per-channel; simulated vs real quantization; "write vs read" cache semantics.
- **Read:** [Alignment Collapse](https://arxiv.org/abs/2606.09864) §1–5 and appendix A.1; [KIVI repo](https://github.com/jy-yuan/KIVI).
- **Gate:** apply the frozen pilot criteria.

## Week 4 (Nov 9–15): context and refusal-vs-suppression
- **Build:** context-length sweep (~0.1k / 1k / 4k, neutral filler); K-only vs V-only; refusal-style vs suppression-style comparison with matched checkpoints.
- **Learn:** effect sizes, Wilson intervals, pre-registration, threats to validity.
- **Read:** [Unlearning Isn't Deletion](https://arxiv.org/pdf/2505.16831); [Do Unlearning Methods Remove Information…](https://arxiv.org/pdf/2410.08827); [Existing Evaluations Are Inconclusive](https://arxiv.org/pdf/2506.00688); [QUAIL](https://arxiv.org/pdf/2601.15538).

## Week 5 (Nov 16–22): generalization and interaction
- **Build:** non-Llama results; weight × KV 2×2; scoop check #2.
- **Learn:** interaction effects (additive vs super-additive); LoRA fine-tuning basics.
- **Read:** [DurableUn](https://arxiv.org/pdf/2605.02196); [2609.27355](https://arxiv.org/pdf/2609.27355); [FRAG](https://arxiv.org/abs/2608.25429); [J-Access](https://arxiv.org/abs/2608.11408).
- **Decide:** framing (narrow transfer / evaluation study / broader).

## Week 6 (Nov 23–29): mechanism and freeze
- **Build:** freeze confirmatory settings; fill gaps; optional critical-layer scan.
- **Learn:** low-dimensional "refusal direction" idea; activation outliers.
- **Read:** Alignment Collapse appendices; [AnchorKV](https://arxiv.org/pdf/2606.17872); [Faithfulness Is Not Free](https://arxiv.org/abs/2608.30996); [2609.04875](https://arxiv.org/abs/2609.04875) (adjacent).
- **Nov 29:** ICLR 2027 workshop list announced; shortlist 2–3 venues and read their CFPs.

## Week 7 (Nov 30–Dec 6): analysis and figures
- **Build:** final tables with intervals; main figure (where the audit and deployed disclosure diverge, at acceptable utility); related-work table.
- **Learn:** claims-to-evidence mapping; writing limitations.
- **Read:** 2–3 accepted papers from the target workshop's previous edition.

## Week 8 (Dec 7–13): full draft
- Complete draft; rerun weak cells; red-team review; one outside reader.

## Week 9 (Dec 14–20): finish
- Appendix, code/result release, reproducibility pass, AI-use disclosure if required. Submit when the target CFP opens (suggested ICLR 2027 workshop deadline: Feb 1, 2027).

## Buffers and cuts
If behind, cut in this order: optional mechanism work, the 2×2, K-only/V-only. Never cut the noise-floor controls or the liveness checks. Dec 21–Jan is spare buffer.
