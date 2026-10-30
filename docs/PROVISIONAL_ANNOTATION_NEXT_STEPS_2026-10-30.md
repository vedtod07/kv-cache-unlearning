# Provisional annotation started - 30 October 2026

Vedant authorized moving ahead because time is limited and B approval is expected. **B approval has not been received.** The current table is an A-authorized provisional working specification, not a joint freeze or final v1.0. The exact rubric/table hashes and authorization are recorded in results/provisional-annotation-20261030/PROVISIONAL_AUTHORIZATION.json.

## Completed next step

Prepared separate A and B review packages for the original480 responses:120 forget and360 utility each. Each package contains two CSVs, the rubric source and a protocol guide. Inputs are independently shuffled for each reviewer; model/cache fields and mapping keys are excluded. Prior exposure remains disclosed. Every row has provisional status, response hash, exact table hash, required components, aliases and full rationale. No factual labels have been assigned, no GPU work repeated and no historical labels inherited.

Both reviewers see the same population under the same provisional rule set. Two reviews do not double the number of experimental observations. The selection includes original responses even when identical across conditions. All four truncations remain represented through termination fields.

## Next actions

1. A uses A-provisional-review-package.zip; B uses B-provisional-review-package.zip. Do not send A's completed labels to B before his first pass. Do not inspect the paired browser or mappings while performing first-pass review.
2. Begin with the120 forget responses. Assess each against the question, required content and rationale, not exact-string equality. Fill correctness, behaviour and list-target-presence separately. Then complete360 utility responses, including coherence and relevance.
3. Keep unresolved reference cases ambiguous as specified; log needed source checks and specification disagreements. Do not quietly resolve a factual alternative for only one condition.
4. Return first-pass files with review IDs and response text/hash unchanged. Preserve original submissions. Join and calculate agreement only afterward, then record adjudications separately.
5. B can confirm the exact table hash or request changes while provisional work continues. Any rule change triggers a version bump and a recheck of every affected item across all models/conditions and both reviewers. Do not report final results or claim independent approval until the outstanding checks/sign-off are complete.

## Why labels are blank

The completed milestone is a validated annotation package, not a completed factual assessment. A's prior annotations were produced under earlier conventions. Carrying them forward wholesale would skip the newly agreed rules. Any future assistant-proposed labels must be marked AI-assisted and must not be represented as B's independent review.

## Mapping-key custody

Coordinator keys are stored locally under local-review-keys/provisional-annotation-20261030, excluded by .gitignore and excluded from reviewer ZIPs. Their hashes are in the manifest. Preserve a private backup. Public source outputs and the builder still exist, so this is procedural condition masking rather than an access-control guarantee or fully blind review.
