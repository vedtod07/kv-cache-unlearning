# Does Forgetting Survive KV-Cache Compression?

A planned measurement study of **weight-based LLM unlearning under stored KV-cache quantization**. We hold model weights fixed and ask whether correct forgotten-fact disclosure changes, and whether parallel scoring predicts deployment-matched evaluation.

## Status

Protocol v4; development progress updated 21 October 2026. **Person A's seven setup/baseline stages have run on a T4 and the day-seven annotations are A-accepted. Limited FP32/HQQ cache integration checks passed; B's separate diagnostics are preserved.** The next same-run ordinary/INT4 development notebook is prepared but has not run. Independent review, final scientific choices and the main quantized disclosure experiment remain unfinished.

Person A is **Vedant**: measurement protocol, baselines, annotation, statistics, and independent validation. Person B owns cache implementation and sequential scoring. Both review the other's evidence.

## Start here

- [Blueprint v4](docs/BLUEPRINT.md): core design, metrics, scope and claim limits
- [Week-one review](docs/WEEK1_REVIEW.md): goal, importance, method and result of each stage; completion and remaining joint work
- [Next paired ordinary/INT4 notebook](notebooks/person_a_week2_int4_development.ipynb) and [run instructions](results/int4-development-preparation/README.md)
- [Five-day progress diff and results review](docs/FIVE_DAY_PROGRESS_DIFF.md): what changed, why, measured results, problems and next steps
- [Person A/B work split](docs/WORK_SPLIT.md)
- [Person A week-one walkthrough](docs/PERSON_A_WEEK1_WALKTHROUGH.md) and [day-one GPU notebook](notebooks/person_a_week1_day1.ipynb)
- [Week-one tasks](docs/WEEK1_DETAILED.md) and [setup instructions](docs/week1_setup_cells.md)
- [Engineering validation](docs/VALIDATION.md)
- [Pilot and confirmation criteria](docs/PILOT_CRITERIA.md)
- [Results data contract](results/README.md)
- [Nine-week plan](docs/NINE_WEEK_PLAN.md)
- [Introduction draft](docs/INTRODUCTION_DRAFT.md)
- [Changes from v3](docs/REVIEW_CHANGES.md), [decisions](docs/DECISIONS.md), [log](docs/LOG.md)
- [Contribution workflow](CONTRIBUTING.md)

## Local checks (no model downloads)

```bash
python3 -m unittest discover -s tests -v
```

## GPU diagnostic (partial evidence available)

Use a dedicated environment. Resolve the immutable model commit before substituting the placeholder:

```bash
pip install -r requirements-week1.txt
python scripts/test_kv_scoring_path.py \
  --revision MODEL_COMMIT_SHA \
  --backend quanto --nbits 4 --residual_length 128 \
  --output results/diagnostics/short-int4.json
```

The requirements are a **candidate environment**, not a complete tested lock. The command above is an example; B's T4 attempt with Quanto failed to build its extension, while HQQ ran. See [the actual reports](results/diagnostics/) and [five-day review](docs/FIVE_DAY_PROGRESS_DIFF.md) before selecting a backend/environment. A's ordinary baseline used a different Torch version and FP16; do not pool these configurations. Archive `pip freeze`, hardware details, and the JSON report. `scripts/liveness_test.py` is now an alias for this fixed-token diagnostic; its previous free-generation comparison has been retired.

A pass demonstrates preliminary engineering checks on one artificial fixture. It is not a recovery result or sufficient validation of the eventual batched evaluator. Equal quantized and ordinary scores are allowed when the cache intervention is independently verified.
