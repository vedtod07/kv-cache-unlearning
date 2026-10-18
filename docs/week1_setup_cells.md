# Week 1 — Day 1–2 setup cells (Colab / Kaggle)

Status: **not yet run on a GPU.** Commands marked (verified) were read from the OpenUnlearning README
on 2026-10-19; everything else is a suggestion to check against your environment.

## Day 1 — environment and a first generation

```python
# Cell 1: what GPU do I have?
!nvidia-smi
import torch, sys
print(sys.version)
print(torch.__version__, torch.cuda.is_available())
# T4 / P100 have no native bf16 -> use float16 (the checkpoints are stored in bf16).
```

```python
# Cell 2: minimal generation with a released checkpoint (no OpenUnlearning needed yet)
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

model_id = "open-unlearning/tofu_Llama-3.2-1B-Instruct_full"   # (verified name, from README)
tok = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id, dtype=torch.float16, attn_implementation="sdpa").cuda().eval()

msgs = [{"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Who wrote the book 'Principles of Fiction'?"}]
inp = tok.apply_chat_template(msgs, add_generation_prompt=True,
                              return_tensors="pt", return_dict=True).to("cuda")
out = model.generate(**inp, do_sample=False, max_new_tokens=60)
print(tok.decode(out[0, inp["input_ids"].shape[1]:], skip_special_tokens=True))
```

Day-1 done when: you can explain why the output is the same every time with `do_sample=False`.

```bash
# Cell 3: record versions (paste into your results log)
pip list 2>/dev/null | grep -i -E "^(torch|transformers|accelerate|bitsandbytes|datasets|optimum|hqq) "
```

## Day 2 — OpenUnlearning stock evaluation

```bash
# Cell 4 (verified from README, with one change: flash-attn skipped for T4/P100)
git clone https://github.com/locuslab/open-unlearning.git
cd open-unlearning
pip install ".[lm-eval]"
# README also lists: pip install --no-build-isolation flash-attn==2.8.3   <- SKIP on T4/P100
python setup_data.py --eval        # downloads retain-model logs into saves/eval (verified)
```

Notes before you run the evaluation:
- The README asks for Python 3.11; Colab/Kaggle may ship a newer one. If install fails on version
  pins, note the exact error — this is the day-1/2 risk the plan budgets time for.
- The repo pins `transformers==5.5.4`, `torch==2.9.1`; `optimum-quanto` and `hqq` are NOT in its
  requirements (from the earlier blueprint check) — install them separately for the cache tests.
- Open `configs/model/Llama-3.2-1B-Instruct.yaml` and look for the attention-implementation and dtype
  fields. Set attention to `sdpa` (not flash-attention) and dtype to float16 on a T4. (Exact key names
  not verified — read the file.)

```bash
# Cell 5: stock TOFU evaluation of the released FULL model (verified command shape from README)
model=Llama-3.2-1B-Instruct
python src/eval.py --config-name=eval.yaml experiment=eval/tofu/default \
  model=${model} \
  model.model_args.pretrained_model_name_or_path=open-unlearning/tofu_${model}_full \
  retain_logs_path=saves/eval/tofu_${model}_retain90/TOFU_EVAL.json \
  task_name=WEEK1_FULL
```

Then repeat with ONE unlearned checkpoint, e.g.
`open-unlearning/unlearn_tofu_Llama-3.2-1B-Instruct_forget10_SimNPO_lr2e-05_b4.5_a1_d1_g0.125_ep10`
(verified to exist), changing `task_name=WEEK1_SIMNPO`. Time both runs (`time python ...`).

Day-2 done when: you have a results JSON for `full` and for one unlearned checkpoint, plus the
wall-clock time of each run. Find where the JSON was written (the README does not say; check
`saves/eval/<task_name>/`).

## Day 4 — liveness test

```bash
python liveness_test.py --model open-unlearning/unlearn_tofu_Llama-3.2-1B-Instruct_forget10_SimNPO_lr2e-05_b4.5_a1_d1_g0.125_ep10 --tofu
pip install optimum-quanto   # if variant A/B report an ERROR about the backend
```

Expected if the library default is inert at TOFU prompt lengths: variant A = NO-OP, variants B and C = LIVE.
If B is also NO-OP, something is wrong with the install or the cache config — fix that before anything else.

## Day 4b — scoring-path gate (second script, from the earlier session)

```bash
pip install -r requirements-week1.txt
python scripts/test_kv_scoring_path.py \
  --model open-unlearning/tofu_Llama-3.2-1B-Instruct_full \
  --backend quanto --nbits 2 --residual_length 0
```

Exit code 0 = gate passed (sequential+quantized scoring differs from single-pass). Exit 2 = no measurable
KV effect: do not trust any "no recovery" result until this is fixed. This script has also not been run
by the person who wrote this note; run it and record the output in `docs/LOG.md`.
