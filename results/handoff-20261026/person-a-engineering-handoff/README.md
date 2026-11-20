# Person A engineering handoff - 26 October 2026

This package is label-free but NOT condition-masked: model/cache IDs, raw answers and expected generation tokens are visible. Do not use it as an independent annotation sheet. No accepted/proposed annotations, review PDFs or adjudications are included. B has disclosed prior exposure.

## Parity check (the next GPU job)

Use parity/fixtures.json with the updated evaluate_cache.py from PR #6. Use all three model IDs/revisions from runnable/int4/config.json, ordinary and quantized conditions, HQQ INT4 residual128 axes1/1 group64, FP32, SDPA, TF32 off, explicit masks, greedy, max64 and pad128009. Preserve the pinned full tokenizer/date/template. Expected output: six sets of 10 records, 60 total. Do not use --limit on the original 80 fixtures as a substitute.

Compare each record by (model_role, condition, item_id) against parity/expected-token-ids.json. Map B condition quantized to A int4; ordinary maps to ordinary. Require exactly the 60 unique keys, status ok, and exact prompt/reference/generated token lists. Check ordinary numerical gates and manifests separately. Missing, duplicate or mismatching records stop pooling; preserve the evidence. The reference tokens for utility items come from the frozen input fixtures; A did not score utility references in this batch.

The subset selection is recorded with hashes and the deterministic algorithm. It is selected after development exposure, not before outcomes existed. This is reproducibility evidence, not 60 new independent accuracy observations.

## Source reuse

runnable/day7 and runnable/int4 contain the archived source and full 80-item inputs required by the respective historical runner. Each includes day6_integration.py and validate_results.py. Source/config bytes are unchanged; preparation manifests are explicitly derived to remove annotation-file dependencies. These runners assert 80 items and are NOT the 10-item parity runner. They are provided for reproduction/refactoring, not a request to rerun all 480.

In a matching GPU environment, an example historical entry point is:

    python -c "import sys; sys.path.insert(0, 'runnable/int4'); from int4_development import main; main('runnable/int4', '/content/new-int4-output')"

For day seven use runnable/day7 and day7_baseline.main analogously, with a fresh output directory. Hugging Face checkpoint access is required. No credentials are included. GPU execution of this repackaged handoff has not been performed.

## Environment

Raw, unchanged freezes and hardware records are in environments/day6, day7 and int4. Current core: Torch2.9.1+cu128, Transformers5.5.4, HQQ0.2.8.post1, datasets4.8.5, accelerate1.13.0, tokenizers0.22.2, huggingface_hub1.33.0. Python changed from3.13.15 to3.13.16. These are observed full Colab snapshots, not a minimal agreed installer lock. Reconcile wheel index/CUDA and required transitive dependencies before adopting a shared lock; do not blindly reinstall every Colab system package.

## Integrity and review scope

HANDOFF_MANIFEST.json hashes every payload file (excluding itself). Original day-six/day-seven outputs remain unchanged in the repository. This package does not approve a PR, freeze the annotation rubric, or certify A/B scientific agreement. Build validation checks syntax, runnable dependencies, fixture counts/hashes and absence of factual labels; it does not rerun CUDA.
