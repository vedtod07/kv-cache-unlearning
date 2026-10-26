# Week one — Person A and Person B

Goal: establish trustworthy baselines and characterize the implementation, not demonstrate recovery. As of 21 October 2026, Person A's selected development baseline and review are completed, and limited-scope cache/GPU evidence is available. Independent B review and joint protocol/confirmation decisions remain open. See [WEEK1_REVIEW.md](WEEK1_REVIEW.md) for the actual goal, importance, method and result of each completed stage.

The table below is the original planned task allocation. The seven actual notebook stages expanded the setup, utility and cache-integration checks; their completion does not imply every joint sign-off has occurred.

| Day | A (Vedant) | B | Output |
|---|---|---|---|
| 1 | Record candidate checkpoint/data revisions; load full model on actual GPU | Same environment and hardware inventory | Environment record, first generation |
| 2 | Inspect OpenUnlearning configs and prompt/scoring code; run small full/retain baseline | Inspect pinned cache implementation and run instrumented diagnostic | Actual prompts, tokens, diagnostic reports |
| 3 | Add one unlearned checkpoint; check factual outputs and template compatibility | Repeat diagnostic for short/long fixtures and supported cache settings | Small baseline table; recorded engineering issues |
| 4 | Draft separate correctness/behavior rubric; define results manifest | Validate ordinary/identity paths and investigate tolerance | Rubric and validation evidence |
| 5 | Measure forget/utility runtime and annotation cost | Measure sequential scoring cost and cache behavior | Budget from measurements |
| 6 | Check partner outputs and diagnostic evidence | Check A's labels and baseline outputs | Independent review log |
| 7 | Draft primary metrics and development/confirmation allocation | List remaining pipeline tests | Joint next-week plan |

Ask: Which exact data, model, prompt, dtype and backend were used? Did the full model learn the facts? Is forgetting measurable? Are quantized writes and reads verified? Are the scoring boundaries correct? What is the measured cost?

Do not expect default residual=128 to be inert. Do not change methods until weight recovery appears. Do not classify unchanged answers as a no-op. See VALIDATION.md for engineering acceptance requirements.
