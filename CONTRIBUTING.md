# Contributing (two-person workflow)

## Branches and reviews
- The default branch (`master` in this repository) should remain reviewable; GPU validation status must be explicit. Do not commit experimental code to it directly.
- Work on a branch: `a/<topic>` or `b/<topic>` (e.g. `b/seq-decode`, `a/rtn-control`).
- Open a pull request; **the other person reviews and merges**. Small PRs, merged within 1–2 days.
- Tag decision points: `pilot-criteria-v1` (before benchmark pilot runs), `confirmation-v1` (before untouched confirmatory evaluation), `framing-v1`.

## What goes in the repo
- Code, configs (YAML), small CSV/JSON summaries, docs, figures used in the paper.
- **Not** in the repo: model weights, checkpoints, large raw outputs, API keys, tokens. (`.gitignore` already blocks common weight formats.) Put large files in Drive or a Hugging Face dataset and link them from `results/README.md`.

## Reproducibility rules
- Every run writes one row to the results log and per-item records following `results/README.md`.
- Record library versions (`pip list` output) with each batch of runs.
- Do not report repeated greedy decoding as independent training seeds. Characterize numerical repeatability separately; inferential variation includes authors and checkpoints.
- Freeze settings in a config file before running a confirmatory batch.

## Commit messages
- Short imperative subject; body says what and why.
- If AI wrote or substantially edited the change, say so in the body.
