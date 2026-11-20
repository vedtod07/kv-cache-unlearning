# Next development experiment: paired ordinary and stored INT4 caches

Prepared 21 October 2026 after A explicitly accepted the day-seven review. GPU execution is pending. This is the next development stage after Person A's week-one baseline, not a completed week-one result or an untouched confirmation experiment.

## Goal, importance, method and output

- **Goal:** measure factual/utility behavior and scoring-path differences when only the stored-cache condition changes.
- **Why:** day seven provides the shared-environment ordinary baseline, but the research question needs paired compression outcomes and matching references.
- **How:** run ordinary and HQQ INT4 conditions on the same loaded FP32 model, for each of full/retain90/SimNPO. Use the existing 20 forget and 60 utility questions, exact masks/template/tokens, 64-token greedy budget and fresh cache per call. Trace the first forget item for every model and check instrumentation neutrality before the full loop.
- **Expected output:** 480 response records (3 models x 2 conditions x 80 items), reference scores on the 20 forget questions per condition/model, per-model trace reports, runtime/environment metadata and raw paired outputs ready for annotation. No result is claimed before execution and review.

## Run it

1. Open [person_a_week2_int4_development.ipynb](../../notebooks/person_a_week2_int4_development.ipynb) in Colab and select a T4.
2. Reuse the successful day-seven environment if available. Otherwise run the setup cell, restart if installation occurs, and continue with environment verification.
3. Upload `int4-development-input-bundle.zip` from this directory when prompted. The notebook verifies its checksum and all bundled file hashes.
4. Run the paired experiment. Preserve failures; do not change thresholds or checkpoints to obtain a desired effect.
5. Download and return the output ZIP, including partial output if execution fails. A continuation can use intact existing files under the same preparation/environment; failed or malformed rows require review.

The notebook is self-contained with its input ZIP; no new GitHub push is required to run it. The ZIP freezes the day-seven baseline, accepted annotations and acceptance record as provenance, plus exact runner/helper/validator sources.

## Controls and interpretation

- Weights stay FP32 and are identical between cache conditions within a model. Only the cache factory changes: ordinary DynamicCache versus HQQ QuantizedCache, INT4, axes 1/1, group64, residual128.
- Ordinary outputs are regenerated in the same run, rather than relying only on a historical baseline. Differences from day seven are recorded.
- Ordinary parallel/sequential scoring must agree within the inherited provisional rule. INT4 empty-cache parallel scoring and first-target behavior have separate controls. INT4 sequential scores are allowed to differ from parallel scores; equality is not an efficacy gate.
- A traced score probe and instrumented/plain comparison are run on the first exposed forget item for every model. Native quantized generation is also traced for that item. This does not mean every output is fully instrumented.
- No positive NLL, text or factual recovery effect is required. Native generation and reference scoring always use fresh cache objects.
- Utility questions use generation only. Factual labels remain unscored until the output review. Ordinary/INT4 differences in text alone are not factual disclosure changes.
- Record every error/truncation and keep paired fixed denominators. Model/condition manifests use distinct run IDs. General-split author-ID sentinels are not author clusters.
- Peak memory is reported for the combined probe and both conditions per model, not as a cache memory-savings estimate.

The scientific confirmation choices and independent B/joint review remain open. This limited development run keeps the existing exposed population and preselected engineering candidate; it does not replace the NPO/RMU paper core or introduce outcome-based checkpoint selection.
