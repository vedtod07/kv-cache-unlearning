# Contributing (two-person workflow)

## Branches and reviews
- `main` always runs. Don't commit experimental code to it directly.
- Work on a branch: `a/<topic>` or `b/<topic>` (e.g. `b/seq-decode`, `a/rtn-control`).
- Open a pull request; **the other person reviews and merges**. Small PRs, merged within 1–2 days.
- Tag decision points: `pilot-criteria-v1` (before any pilot run), `pilot-gate`, `framing-v1`.

## What goes in the repo
- Code, configs (YAML), small CSV/JSON summaries, docs, figures used in the paper.
- **Not** in the repo: model weights, checkpoints, large raw outputs, API keys, tokens. (`.gitignore` already blocks common weight formats.) Put large files in Drive or a Hugging Face dataset and link them from `results/README.md`.

## Reproducibility rules
- Every run writes one row to the results log and per-item records following `results/README.md`.
- Record library versions (`pip list` output) with each batch of runs.
- Greedy decoding: seeds don't matter; do not report "3 seeds". Variation comes from items, authors and checkpoints.
- Freeze settings in a config file before running a confirmatory batch.

## Commit messages
- Short imperative subject; body says what and why.
- If AI wrote or substantially edited the change, say so in the body.
