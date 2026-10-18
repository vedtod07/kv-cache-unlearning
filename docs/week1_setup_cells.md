# Week-one setup — candidate, not GPU validated

Use an isolated Python 3.11 environment on the intended GPU runtime. Run commands from the project root unless stated otherwise. Do not share credentials or commit model weights.

```bash
nvidia-smi
python --version
pip install -r requirements-week1.txt
pip freeze > results/environment-candidate.txt
```

The requirements pin the inspected Transformers API but are not a complete runtime lock. Resolve any compatibility errors explicitly; preserve the failed command/error and final dependency list. Select FP16 on T4/P100 rather than assuming CUDA means BF16. The diagnostic defaults to FP16 on CUDA and FP32 on CPU, using SDPA.

## Fixed-token diagnostic

Resolve and record the model's immutable Hugging Face revision. Replace MODEL_COMMIT_SHA below; it is not an executable default.

```bash
python scripts/test_kv_scoring_path.py \
  --revision MODEL_COMMIT_SHA --nbits 4 --backend quanto \
  --residual_length 128 --output results/diagnostics/short-int4.json
```

Repeat with a new output path for a long fixture (`--filler_repeats 40`), INT2, and a smaller residual if supported. These are engineering fixtures, not a sweep for a desired research effect. Existing report paths are never overwritten.

Exit 0: preliminary diagnostic checks pass; exit 1: setup/runtime failure; exit 2: validation failure. Read the JSON rather than trusting an exit code alone. Unchanged quantized scores may pass if writes, reads and nonzero tensor reconstruction error are established. See VALIDATION.md before integrating with the evaluator.

## OpenUnlearning baseline

Clone [OpenUnlearning](https://github.com/locuslab/open-unlearning) separately and record its immutable commit. Inspect its requirements and configuration before installing into the chosen environment; do not silently overwrite the diagnostic environment's versions. Skip optional flash-attn on incompatible hardware.

The previous README-derived entry points were `pip install ".[lm-eval]"`, `python setup_data.py --eval`, and `python src/eval.py --config-name=eval.yaml experiment=eval/tofu/default`. Recheck them against the pinned upstream checkout. Configure model revision, SDPA and FP16 in the actual model config. Log the resolved Hydra configuration, not only CLI overrides.

Start with full, retain90 and one compatible unlearned checkpoint. Save actual benchmark IDs, rendered prompts, token IDs, generated outputs and scores. Synthetic diagnostic text is not a substitute for TOFU loading. Fail explicitly when benchmark data cannot be loaded.

Downloaded retain-model logs may reproduce the upstream stock evaluation, but they do not replace our matched transformed-reference runs. Confirm the same split, template, scoring and model revisions before comparing stock numbers.

Archive the successful `pip freeze`, Python/CUDA/GPU information, resolved configuration and code commits with each run batch. Lock the complete validated environment before confirmation.
