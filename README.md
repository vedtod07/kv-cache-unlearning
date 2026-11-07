# Does Forgetting Survive KV-Cache Compression?

A planned measurement study of **weight-based LLM unlearning under stored KV-cache quantization**. We hold model weights fixed and ask whether correct forgotten-fact disclosure changes, and whether parallel scoring predicts deployment-matched evaluation.

## Status

Updated **8 November 2026**. **The paired FP32 ordinary/HQQ INT4 development experiment has run: 480 responses, three checkpoints, one forget author and a 60-question utility screen.** A accepted the AI-proposed annotations on 2 November; B's independent review remains pending. B's separate evaluator reproduces 60/60 parity outputs. The multi-author confirmation experiment, final criteria and joint freeze remain unfinished. See [current status](docs/STATUS.md) for evidence, limits and the next actions.

Person A is **Vedant**: measurement protocol, baselines, annotation, statistics, and independent validation. Person B owns cache implementation and sequential scoring. Both review the other's evidence.

## Start here

- [Current status](docs/STATUS.md): completed evidence, unresolved work and next actions
- [Response to the external issue register](docs/ISSUE_REGISTER_RESPONSE_2026-11-08.md): all 44 concerns checked against repository artifacts
- [A-accepted paired development results](results/A-accepted-development-20261102/NEXT_STEPS_AND_PAIRED_REVIEW.md): ordinary/INT4 correctness transitions and provisional interpretation
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

The requirements are a **candidate environment**, not a complete tested lock. The command above is a historical diagnostic example; B's T4 attempt with Quanto failed to build its extension, while HQQ ran. Current paired evidence uses torch2.9.1+cu128, Transformers5.5.4, HQQ0.2.8.post1 and FP32. Earlier FP16/torch2.11 baselines stay separately identified. See [current run evidence](results/int4-development/int4dev_20261025T142729681517Z/artifact-review.json) and [validation coverage](docs/VALIDATION.md). Archive `pip freeze`, hardware details and reports. `scripts/liveness_test.py` aliases the fixed-token diagnostic.

A pass of that historical diagnostic demonstrates preliminary checks on one artificial fixture. Later real-prompt validation is linked above. Neither proves all batched/deployment modes valid. Equal quantized and ordinary scores are allowed when the cache intervention is independently verified.
