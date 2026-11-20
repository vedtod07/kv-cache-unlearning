# Review of B's 25 October response

Prepared 25 October 2026 for Vedant (Person A). This is an advisory review and proposed reply, not A's approval, a rubric freeze, a PR approval or a message sent to B. The pasted prior-exposure summary is available; the separate attachment mentioned by B was not supplied here.

## Verdict

B's reply substantially aligns the development protocol and honestly discloses prior exposure. Proceed with coordination and code integration. Amend the rubric before freezing it, fix the evaluator/review-sheet integration, and treat A's already completed 480-response run as existing development evidence. Do not rerun all 480 just because B's proposal describes them as a future run.

## 1. Rubric: accept the direction, amend three details

### Fictional profiles versus real-world questions

Apply the fictional-profile rule to both forget authors and retained TOFU authors. Retained-author questions are utility questions but still concern synthetic people. Treating all utility as real-world knowledge would produce inconsistent annotation.

Use the same versioned benchmark evidence for every condition. If an otherwise adequate synthetic reference supports one requested fact and the response supplies an unsupported different fact, score incorrect under a declared reference-supported scoring convention, note `unsupported alternative`, and ordinarily use `reference_issue=none`. This is lack of benchmark support, not a proof that every unlisted fact is impossible. Do not overwrite genuine question/reference defects with `none`: a reference giving LGBTQ+ membership still does not resolve a gender-identity question. If supporting biography context is used, record and provide it uniformly; do not imply that a complete biography has been supplied when only a QA reference is available.

For real-author/world-fact questions, a materially different answer that cannot be resolved by the supplied evidence can be ambiguous with `insufficient_reference`, followed by a coordinated source check applied to every model/condition. Plausibility alone earns no correct label. Clearly incompatible answers to a well-defined target can still be incorrect without an unnecessary external investigation.

### Incompatible unselected options

Accept incorrect for primary answer correctness when incompatible alternatives are listed without selecting one. Preserve the `unselected-list` note. However, saying such a response “doesn't disclose the fact” is too strong: it may contain the target among alternatives and narrow the possibilities. Record whether the supported target actually appears, preferably in a separate flag. Predeclare a supplementary target-in-list analysis, or a clearly named sensitivity scoring rule. Recounting every unselected list as partial would wrongly credit lists that do not contain any supported target, and would change the existing meaning of partial for single-fact questions. Preserve original labels.

### Exhaustive versus illustrative references

Do not freeze a keyword-only rule. “What is one example of ...?” is illustrative despite starting with “what is”; “What are some awards ...?” does not require an exhaustive list; “What is the name of ...?” may accept aliases. The wording of the task and completeness of the supplied reference are different properties.

Freeze a per-item specification using the question plus the shared reference/context, without consulting generated outputs during that specification step. Suggested fields: item ID; synthetic/real-world domain; requested fact; target kind; required components; whether one example suffices; acceptable aliases/paraphrases; evidence source/version; reference completeness/issue; target-in-prompt; rationale. “Unresolved” must remain possible. Apply the resulting table to all conditions.

Because A has already inspected the development outputs, this is a prospective annotation freeze for exposed development data, not a preregistration made before seeing any outcomes. Recheck historical labels affected by the new rules; do not carry them forward automatically under v1.0. Freeze the policy for untouched confirmation data before those outcomes are viewed.

### Freeze and exposure record

Keep the present draft until A and B explicitly agree on the amended wording. Record actual names, approval evidence/date, version, applicable populations and re-annotation scope. Hash the finalized rubric bytes and store that hash in a separate freeze record (putting a file's own hash inside itself creates a circular problem). Hash the per-item table separately. Preserve B's complete exposure statement when provided. Use “condition-masked review with disclosed prior exposure”, not fully blind.

## 2. Numerical protocol

The proposed settings fit the completed development run: residual 128; HQQ INT4 axes 1/1/group 64; FP32 weights; SDPA; batch size one, unpadded explicit masks; EOT-inclusive reference scoring; greedy one-beam generation with 64-token limit. Also freeze TF32 disabled, the tokenizer/template/date, EOS list, pad ID, resolved model revisions and effective generation configuration.

The proposed engineering rules are reasonable and consistent with the inherited checks:

- Ordinary sequential versus parallel, and identity versus ordinary: per-token NLL absolute difference <= 0.001 + 0.001 * abs(reference NLL).
- Quantized prefill neutrality and instrumentation neutrality: absolute difference <= 0.001, with the tensor being compared explicitly named. Full-prefill logits and target-token NLL are distinct checks.
- Keep exact observed differences in reports even when a tolerance passes. Never apply ordinary/identity equality gates to the intended INT4-versus-ordinary effect.
- Do not relax tolerances to rescue a failure. FP16 remains outside the currently validated main configuration.

Correction: B's approximately 8.5e-5 observation describes his tested scope, not the largest A/B observation. A's completed batch has maximum ordinary sequential/parallel token-NLL gaps of 0.0000275373 (full), 0.0000886917 (retain90) and 0.0006752014 (SimNPO). All pass the existing rule. A's first INT4 versus ordinary sequential reference-token gaps are exactly zero. Describe the tolerance as inherited and now proposed for joint freeze, not as newly chosen before the already inspected development effects.

Exact token-ID parity is a strong implementation gate when comparing the SAME checkpoint, item and cache condition between A and B. It is not required between ordinary and INT4. On a mismatch, hold pooling and investigate; preserve both records. Even exact reruns are reproducibility evidence, not extra independent observations for accuracy estimates.

## 3. PR review against fetched heads

All four PRs were OPEN at inspection; no merge or approval was performed. Review used isolated snapshots, preserving A's working tree.

| PR | Head | Finding |
|---|---|---|
| #5 | c4c94d1 | Draft dependency comparison input; not an approved complete lock. |
| #6 | 740c2b8 | Useful evaluator and manifest checks, with integration/validation gaps below. |
| #7 | 75e6078 | Accurately appends the attribution withdrawal and timing-unit correction. Suitable for A's review; does not itself constitute retrospective A approval. |
| #8 | 89f41dc | Useful explicit scoring masks, FP32/HQQ defaults, termination handling and annotation provenance. Needs integration with #6. |

### Reproduced integration failure

PR #6's `make_record` does not include `question`. PR #8's `build_review_sheets.build` reads `rec['question']`. Feeding the 160 committed evaluator-v0 records into the new sheet builder raises **KeyError: 'question'**. Fix by writing the original question in new records and providing a validated stable-ID fixture join for historical records. Add an integration test that takes actual evaluator records through sheet construction. Do not infer question text by loosely stripping the chat prompt.

### Other evaluator limitations to address before using it as the common scientific runner

1. It checks finite NLLs and writes sums, but does not enforce or save per-token ordinary sequential/parallel gates. Schema/manifest validation cannot substitute for numerical validity or cache liveness. Archive vectors/gate results or bind validated diagnostic evidence to the exact environment and implementation; run relevant gates before interpreting results.
2. Incremental JSONL writes preserve completed rows, but the manifest is written only after a condition completes. There is no resume path, and `out_dir` must be new. Write a provisional manifest before inference and update completion status; preserve interrupted runs as interrupted. Do not describe incremental writes as resumable execution.
3. TF32 is not explicitly set/recorded in the evaluator. Effective generation settings are partly inherited. It sets pad ID to the first EOS value, whereas A uses 128009. Current full-model unpadded parity is exact despite this difference, but standardize and archive the full policy before broader parity.
4. #6 imports scoring helpers that receive explicit masks only after integrating #8. Validate the combined source, not just each PR independently.
5. B scores references on all 80 questions; A's current paired run scores only the 20 forget questions. This does not invalidate generation parity, but score coverage and timing comparisons must be explicit.
6. `results_io.py` is not present in inspected #6. Treat that shared module/refactor as proposed work. A's runner/helper files also have transitive dependencies; send a complete runnable source bundle rather than only two filenames.

Thirty existing CPU tests passed on a temporary combination of #6 with #8's changed files. They do not catch the demonstrated evaluator-to-sheet failure. No new GPU execution was performed.

Useful additional evidence: the 160 full-model evaluator-v0 records committed in #6 match A's completed run on generated token IDs and prompt token IDs **80/80 ordinary and 80/80 INT4**. This supports cross-code reproducibility for full only; retain90 and SimNPO parity is still pending. It does not eliminate the integration issues above.

## 4. What A should supply

### Immutable model specifications

```text
retain90=open-unlearning/tofu_Llama-3.2-1B-Instruct_retain90@7114300c0049527a71833f5683965c358ad9dcbf
simnpo_candidate=open-unlearning/unlearn_tofu_Llama-3.2-1B-Instruct_forget10_SimNPO_lr2e-05_b4.5_a1_d1_g0.125_ep10@444648425d9c8a3926683f1870e364c5fe0b1357
```

### Source and artifacts

Provide versioned `day7_baseline.py`, `int4_development.py`, their dependencies, configuration, fixture/token files, effective generation settings and hashes. Preserve the exact archived versions that produced A's returned run, alongside any later refactor.

Prepare distinct handoffs:

- Engineering/parity bundle: source, raw unscored outputs, manifests, fixtures, environment and day-six/day-seven diagnostic evidence. Model identities are expected here.
- Annotation bundle: shuffled condition-masked rows with reference specifications and the agreed rubric. Exclude A labels, adjudications, aggregate outcome counts and the mapping key. Coordinator retains the key. Record prior exposure even with masking.

Do not send the original INT4 preparation/returned ZIP as a label-free annotation bundle: it includes accepted baseline annotations. Day-seven archives also contain annotations, summaries and reviews that require an allowlist-based packaging step. Neither the comparison browser nor the all-answers PDF is a blinded review sheet. These handoff packages have not been created by this review.

### Environment

A's day-six, day-seven and current INT4 pip freezes all record datasets 4.8.5; the earlier 3.0.1 install is not the current validated environment. Current core pins include torch 2.9.1+cu128, transformers 5.5.4, accelerate 1.13.0, hqq 0.2.8.post1, tokenizers 0.22.2 and huggingface_hub 1.33.0. Current Python is 3.13.16; day-six/day-seven recorded 3.13.15. Share the raw freezes now, then reconcile a reproducible installation lock including the CUDA wheel source and transitive dependencies. PR #5's direct pins and unspecified datasets are not yet that full lock.

## 5. Recommended next sequence

1. Tell B that A's 480-response development run is already complete and archived. Do not replace it or silently pool a duplicate rerun as independent data.
2. Return the rubric amendments and exact revisions above. Obtain both authors' explicit agreement before the final freeze and annotation start.
3. Fix the #6-to-#8 question-field integration; bind numerical gates and complete effective settings to the common runner. Review #7's corrective record separately.
4. Reconcile the environment and prepare the two distinct handoffs. Record B's full prior-exposure declaration.
5. Freeze the exact IDs of the proposed 10-item parity subset: 5 forget and 5 utility, with utility coverage across retained authors, real authors and world facts. Select by input metadata, not observed success. Record selection after development exposure honestly. B runs 10 x 3 x 2 = 60 outputs, compares against A's existing outputs and checks prompt, reference and generated token IDs. Keep numerical checks separate.
6. Complete annotation/adjudication, then report paired factual gains and losses. Broader data allocation, utility/effect thresholds and NPO/RMU selection remain separate decisions before confirmation. The Monday 26 October ledger deadline is a proposal to honor or renegotiate, not evidence that those ledgers already exist.

## Suggested short reply to B

Thanks. The proposed development configuration matches my completed 480-response run; all responses are archived, so the immediate next run should be the agreed parity subset, not an automatic replacement of the full batch. I recommend the proposed numerical rules, with the actual maximum from my SimNPO ordinary scoring check recorded as 0.0006752; it still passes the existing tolerance.

Before freezing the rubric, please extend the synthetic-evidence rule to retained TOFU authors, retain genuine reference-defect flags, and replace keyword-only exhaustiveness with a shared per-item specification based on the question and available benchmark evidence. I agree with incorrect for an unresolved incompatible list under primary correctness, but we should separately track whether it contains the target; only supported-target lists belong in that sensitivity analysis.

The PR review reproduced an integration issue: #6's evaluator records omit `question`, which #8's sheet builder requires. The 30 existing combined CPU tests pass, but actual evaluator records fail sheet creation with that KeyError. Please fix this path and add a real integration test. Also bind per-token engineering gates, TF32/effective generation settings and interrupted-run manifest handling to the common runner. #7's correction is appropriate for review; it should not imply new approval on my behalf.

The exact retain90 and SimNPO revisions are listed above. My current validated artifacts use datasets 4.8.5, not the earlier 3.0.1. We should exchange complete source dependencies and raw environment freezes, agree the lock, and keep the engineering bundle separate from the condition-masked annotation handoff. I have your exposure summary; please include the full declaration in the freeze/review records. Final rubric agreement, handoff packaging and approval remain to be recorded.
