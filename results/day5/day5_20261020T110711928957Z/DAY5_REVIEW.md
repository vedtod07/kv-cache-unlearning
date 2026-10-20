# Day-five artifact review

Reviewed 20 October 2026. Reviewer: Codex-assisted verification. Human acceptance and Person B's independent sign-off are not inferred from receiving this archive.

**Outcome: the limited source-helper integration completed and its saved records are internally consistent. A mask convention changes outputs and must be fixed across future experimental conditions. This run contains no cache quantization.**

The original archive was extracted without modifying its files. `artifact-review.json` records the archive/input checksums, independently recomputed summaries and outstanding decisions. The raw manifest intentionally remains `integration_complete_review_pending`; the review is a separate artifact.

## Verification

- All 60 expected model–item pairs are present, unique and successful: 20 items for each of full, retain90 and the SimNPO development candidate.
- The input-bundle SHA256 matches the frozen preparation bundle. All 13 bundled upstream source/config/license hashes match that bundle at OpenUnlearning commit `b29929067732c40ee4ca58d5cc1d3c11fcf37de1`.
- Core environment matches the earlier baseline: Tesla T4, Torch 2.11.0+cu130, Transformers 5.5.4, FP16 and SDPA. This observed environment differs from the repository's provisional Torch 2.9.1 candidate requirements; the real quantization backend still needs compatibility validation.
- Checkpoint IDs and immutable revisions, questions, references and prompt IDs match earlier fixtures.
- All 60 all-ones-mask generations match the prior day-two/day-three outputs in both decoded text and exact generated token IDs. Earlier annotations remain applicable to those identical outputs.
- Both masks extract the intended gold answer for all 60 records. Prompt labels are ignored; answer labels equal the answer input IDs. The labeled EOS convention is consistent across all 20 token traces.
- Scores are finite; all saved summary statistics recompute from the item records. No numerical pass tolerance was chosen after observing the results.
- Of 120 generations, 119 end with an EOS. The SimNPO all-ones output at zero-based item 5 reaches the 64-token limit, reproducing its earlier truncation. Keep that record and flag; do not silently extend only that answer.

These checks validate archived consistency and input boundaries. Saved logits are not available for a fresh local cross-entropy recomputation, and this review did not rerun GPU inference.

## Mask finding

The upstream preprocessor creates an all-ones mask for real tokens. The inspected collator subsequently reconstructs it using:

```python
attention_mask = input_ids.ne(tokenizer.pad_token_id)
```

Here `pad_token_id == eos_token_id == 128009`, representing `<|eot_id|>`. These batch-size-one inputs contain no padding. Nevertheless, the collator zero-masks two real prompt tokens: the system and user end-of-turn markers. For the first example those positions are 31 and 65, counting from zero. The scoring sequence also zero-masks the final assistant end-of-turn marker, which remains a labeled prediction target.

An attention mask controls whether a token position can be attended to. It is distinct from the loss labels: a zero attention-mask entry does not itself remove a label from the scoring denominator. The final EOS is predicted from the preceding position; masking its own position does not mean that prediction was omitted. The earlier real prompt markers can affect later token predictions.

Only the mask differs between these paired arms. The saved generation differences are:

| Model | Changed response text | All-ones output tokens match prior run |
|---|---:|---:|
| Full | 5/20 | 20/20 |
| Retain90 | 14/20 | 20/20 |
| SimNPO candidate | 19/20 | 20/20 |

These are response-change counts, not changed-correctness counts. Paraphrases, different hallucinations and genuine factual changes all count as changed text. No new accepted factual annotations have been assigned to the stock-mask variants. Do not carry earlier labels across a changed response or interpret 19/20 as knowledge recovery.

The observation is specific to this pinned source, tokenizer configuration and execution path. It does not establish the behavior of every OpenUnlearning configuration or a new attack.

## Scores

For each item, probability is `exp(-mean target-token cross entropy)`, including the labeled EOS. The table averages that quantity across items. It is a geometric mean of token probabilities within an answer, not the answer's full-sequence probability or percentage of correct answers.

| Model | Stock-mask mean probability | All-ones mean probability | Stock ROUGE-L recall | All-ones ROUGE-L recall |
|---|---:|---:|---:|---:|
| Full | 0.92590 | 0.91953 | 0.87686 | 0.84466 |
| Retain90 | 0.09948 | 0.10139 | 0.38033 | 0.40504 |
| SimNPO candidate | 0.04223 | 0.04831 | 0.33292 | 0.32936 |

Full > retain90 > SimNPO holds for these aggregate scores under both masks. That ordering is descriptive for one exposed development author. Low reference probability and ROUGE alone do not establish successful unlearning, privacy or recovered factual knowledge. ROUGE measures lexical overlap.

The maximum absolute difference between stock helper mean NLL and the independent score calculation is 0.00021230 for full, 0.00142431 for retain90 and 0.00362587 for SimNPO. The stock helper applies its loss calculation to FP16 logits; the independent calculation promotes logits/reductions to FP32. This is consistent with a precision contribution. It is not a comparison with an FP32-weight model, nor an independently established tolerance for later sequential scoring. Correct boundaries and identical scored token counts give no evidence here of a token-shift or omitted-EOS error.

## Timing and scope

Reported model load times: full 43.27 s; retain90 130.26 s; SimNPO 88.79 s. Summed per-item diagnostic loop times: 43.20 s, 40.40 s and 45.50 s respectively. Together these total approximately 6.52 minutes, excluding setup, downloads outside the measured calls, packaging and unmeasured overhead. Each item runs multiple scoring/generation arms. These are diagnostic timings, not an estimate for the full research matrix or sequential quantized evaluation. Peak memory was not measured.

This is integration of the actual upstream preprocessing/collation and probability/ROUGE helper functions through a direct harness. It is not full Hydra CLI reproduction, official `model_utility`, truth-ratio/forget-quality evaluation, or a full-dataset benchmark.

## Recommended next protocol and day-six handoff

Keep every genuine prompt token visible in the main experimental path. For these unpadded batch-size-one fixtures, use an explicit all-ones mask. For future padded batches, build masks from true sequence lengths or tokenizer padding metadata so genuine EOS/turn markers stay visible and only inserted padding is masked. Keep the unchanged stock-collator condition as an explicitly named compatibility diagnostic. Do not silently patch its archived source or pool its outputs with the main path.

Use one mask policy across ordinary and quantized conditions, all three model roles, generation and scoring. For new reference-score measurements, use FP32 log-softmax/reductions over the declared target tokens; preserve the stock-FP16 helper as a separately labeled comparator. A batch-padding/position test is required before moving beyond batch size one. Joint confirmation protocol choices remain to be recorded before confirmation data or quantized outcomes are inspected.

Person A's next task is reviewing cache-path evidence with Person B, using the engineering contract in `docs/VALIDATION.md` and `scripts/test_kv_scoring_path.py`. Begin with artificial fixed-token fixtures, not new forget authors:

1. Record the exact compatible quantization backend/version with the observed T4 environment. Preserve setup failures. Avoid replacing Torch merely to make it match the earlier provisional requirements.
2. Compare ordinary parallel scoring, ordinary sequential scoring and identity-wrapper sequential scoring on identical tokens. Characterize ordinary numerical repeatability before judging transformed scores. Preserve token boundaries and EOS policy.
3. Run the real stored-cache intervention, initially INT4. Inspect per-layer K/V writes, decode reads, storage and finite reconstruction errors, and verify reconstructed values feed attention. Instrumentation must itself be neutral.
4. Extend to INT2 and short/long prompts, residual boundaries, one-token versus multiple-token answers, fresh-cache/order checks and an explicit empty-QuantizedCache prefill comparison. The current script does not cover all these checks; a successful exit alone does not complete the contract.
5. Review and archive the reports, including failures. Proceed to a small paired development disclosure comparison only when the required evidence is satisfied. No gate requires positive recovery or changed aggregate NLL.

No new manual correctness sheet is needed to establish this engineering result. Existing accepted labels remain usable for the identical all-ones outputs. If stock-mask factual disclosure becomes a reported comparison, its changed responses need separately reviewed labels under the existing rubric. Independent B review remains pending.

The research question remains whether **stored KV quantization changes factual disclosure from weight-unlearned models, and whether the evaluation path detects that change**. Mask handling is a control needed to attribute an effect to compression. The SimNPO checkpoint remains an engineering candidate; it does not replace the planned NPO/RMU core.
