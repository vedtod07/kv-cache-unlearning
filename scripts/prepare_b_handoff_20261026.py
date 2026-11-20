"""Prepare an allowlisted engineering handoff and deterministic parity subset."""
from pathlib import Path
import json,hashlib,shutil,zipfile,ast
ROOT=Path(__file__).resolve().parents[1]
D6=ROOT/'results/day6/day6_20261020T130635380188Z'
D7=ROOT/'results/day7/day7_20261021T101236202224Z'
RUN=ROOT/'results/int4-development/int4dev_20261025T142729681517Z'
OUT=ROOT/'results/handoff-20261026';OUT.mkdir(exist_ok=True)
B=OUT/'person-a-engineering-handoff';B.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def cp(src,dst):dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
fixtures=json.loads((RUN/'fixtures.json').read_text())
seed='kv-cache-unlearning-parity-20261026-v1'
rank=lambda f:hashlib.sha256((seed+'\n'+f['item_id']).encode()).hexdigest()
selected=[]
for split,n in [('forget10',5),('retain90',2),('real_authors',2),('world_facts',1)]:
 seen=set();chosen=[]
 for f in sorted([f for f in fixtures if f['dataset_config']==split],key=lambda f:(rank(f),f['item_id'])):
  if split=='retain90' and f['author_id'] in seen:continue
  chosen.append(f);seen.add(f.get('author_id'))
  if len(chosen)==n:break
 assert len(chosen)==n;selected+=chosen
write(B/'parity/fixtures.json',selected)
write(B/'parity/selection-record.json',dict(version='parity-20261026-v1',date='2026-10-26',status='fixed engineering subset for requested handoff; not joint scientific sign-off',seed=seed,algorithm='Within each split sort SHA256(seed + newline + item_id), tie-break item_id; retain90 requires distinct author_id.',allocation={'forget10':5,'retain90':2,'real_authors':2,'world_facts':1},source_fixtures_sha256=sha(RUN/'fixtures.json'),selected_fixtures_sha256=sha(B/'parity/fixtures.json'),item_ids=[f['item_id'] for f in selected],prior_exposure='Selected after A inspected development outputs. Algorithm uses input IDs and author IDs only, no outcomes. No claim of untouched data or pre-outcome preregistration.'))
# Selection is completed before any generated outputs are read.
expected=[];selected_by_id={f['item_id']:f for f in selected}
for role in ['full','retain90','simnpo_candidate']:
 for condition in ['ordinary','int4']:
  src=RUN/f'{role}-{condition}-items.jsonl'
  for r in map(json.loads,src.read_text().splitlines()):
   if r['item_id'] not in selected_by_id:continue
   f=selected_by_id[r['item_id']]
   expected.append(dict(model_role=role,condition=condition,item_id=r['item_id'],prompt_token_ids=r['prompt_token_ids'],reference_token_ids=f['answer_token_ids'],generated_token_ids=r['generated_token_ids'],source_file=src.name,source_sha256=sha(src),reference_provenance='Frozen in-context EOT-inclusive fixture; utility reference tokens are inputs, not previously scored utility results.'))
assert len(expected)==60
write(B/'parity/expected-token-ids.json',expected)
for label,src in [('day6',D6),('day7',D7),('int4',RUN)]:
 for name in ['pip-freeze.txt','environment.json','hardware.txt']:
  cp(src/name,B/'environments'/label/name)
# Runnable historical inputs: derived preparation manifests omit all annotation dependencies.
for label,src,names in [('day7',D7,['config.json','fixtures.json','previous-outputs.json','day7_baseline.py','day6_integration.py','validate_results.py']),('int4',RUN,['config.json','fixtures.json','day7-baseline.json','int4_development.py','day7_baseline.py','day6_integration.py','validate_results.py'])]:
 folder=B/'runnable'/label
 for name in names:cp(src/name,folder/name)
 old=json.loads((src/'preparation-manifest.json').read_text())
 new=dict(old);new['files']={n:sha(folder/n) for n in names};new['handoff_derivation']={'date':'2026-10-26','original_manifest_sha256':sha(src/'preparation-manifest.json'),'note':'New label-free engineering package; removed annotations and unused metadata dependencies. Source code/config/fixtures copied unchanged; this preparation manifest is derived, not the original GPU input manifest.'}
 write(folder/'preparation-manifest.json',new)
# Raw label-free engineering evidence, selected by explicit allowlist.
for name in ['checks.json','scores.json','generations.json','fixtures.json','manifest.json','runner.py','base-generation-config.json','generation-overrides.json','chat-template.txt','quantized-layer.py','llama-attention.py']:
 cp(D6/name,B/'evidence/day6'/name)
for role in ['full','retain90','simnpo_candidate']:
 for suffix in ['items.jsonl','manifest.json']:cp(D7/f'{role}-{suffix}',B/'evidence/day7'/f'{role}-{suffix}')
for name in ['manifest.json','effective-generation-config.json']:cp(D7/name,B/'evidence/day7'/name)
# Assert no correctness/behaviour annotations are concealed inside nested raw data.
def scan(x):
 if isinstance(x,dict):
  for k,v in x.items():
   if k in ['correctness','behavior','behaviour']:assert v in [None,'unscored'],(k,v)
   scan(v)
 elif isinstance(x,list):
  for v in x:scan(v)
for p in B.rglob('*'):
 if p.suffix=='.json':scan(json.loads(p.read_text()))
 if p.suffix=='.jsonl':
  for line in p.read_text().splitlines():scan(json.loads(line))
 if p.suffix=='.py':ast.parse(p.read_text())
(B/'README.md').write_text('''# Person A engineering handoff - 26 October 2026

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
''')
files={str(p.relative_to(B)):sha(p) for p in sorted(B.rglob('*')) if p.is_file() and p.name!='HANDOFF_MANIFEST.json'}
write(B/'HANDOFF_MANIFEST.json',dict(date='2026-10-26',kind='label-free engineering handoff, identities visible',files=files))
z=OUT/'person-a-engineering-handoff-20261026.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as archive:
 for p in sorted(B.rglob('*')):
  if p.is_file():archive.write(p,str(p.relative_to(OUT)))
write(OUT/'package-check.json',dict(zip_sha256=sha(z),payload_files=len(files),expected_pairs=60,items=[{'split':f['dataset_config'],'row_index':f['row_index'],'item_id':f['item_id']} for f in selected],validation='All JSON/JSONL label fields unscored/null; Python AST valid; source bytes and input manifest hashes checked. GPU not rerun.'))
print(json.dumps({'zip':str(z),'sha256':sha(z),'subset':[(f['dataset_config'],f['row_index']) for f in selected]},indent=2))
