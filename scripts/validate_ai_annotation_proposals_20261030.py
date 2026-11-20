"""Check proposal coverage, source preservation, CSV exports and review status."""
import collections
import csv
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'results/provisional-annotation-20261030'
OUT=BASE/'A-ai-proposed'
manifest=json.loads((OUT/'manifest.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for path,digest in manifest['source_sha256'].items():
    assert sha(BASE/path)==digest, ('source changed',path)
rows=[]
editable={'correctness','behavior','supported_target_in_unselected_list','notes','spec_disagreement','review_progress','reference_issue','reference_review_needed','reference_review_notes','coherence','relevance'}
for population,n in [('forget',120),('utility',360)]:
    original=json.loads((BASE/f'A/{population}-review.json').read_text())
    proposed=json.loads((OUT/f'{population}-ai-proposed.json').read_text())
    assert len(original)==len(proposed)==n
    for a,b in zip(original,proposed):
        for key,value in a.items():
            if key not in editable: assert b[key]==value,(b['review_id'],key)
        assert hashlib.sha256(b['response'].encode()).hexdigest()==b['response_sha256']
        assert b['correctness'] in {'correct','partial','incorrect','ambiguous'}
        assert b['behavior'] in {'answer','refusal','mixed','empty'}
        assert b['supported_target_in_unselected_list'] in {'yes','no','uncertain','not_applicable'}
        assert b['review_priority'] in {1,2,3}
        assert b['notes'] and b['priority_reason']
        assert b['human_review_status']=='pending'
        assert b['annotation_author']=='Codex AI'
        assert b['review_progress']=='ai_proposed_human_review_pending'
        assert not any(b[k] for k in ['human_review_decision','human_correctness_override','human_review_notes'])
        assert not any(k in b for k in ['condition','model_role','item_id','run_id'])
        if population=='utility':
            assert b['coherence'] in {'coherent','partly_incoherent','incoherent'}
            assert b['relevance'] in {'on_topic','partly_off_topic','off_topic'}
    rows.extend(proposed)
assert len({r['review_id'] for r in rows})==480
for name in ['forget-ai-proposed','utility-ai-proposed','priority-review-queue']:
    j=json.loads((OUT/f'{name}.json').read_text())
    with (OUT/f'{name}.csv').open(newline='') as f: c=list(csv.DictReader(f))
    assert len(j)==len(c)
    for a,b in zip(j,c):
        assert set(a)==set(b)
        for k,v in a.items():
            expected=str(v).lower() if isinstance(v,bool) else str(v)
            assert b[k]==expected,(name,a['review_id'],k)
queue=json.loads((OUT/'priority-review-queue.json').read_text())
assert {r['review_id'] for r in queue}=={r['review_id'] for r in rows}
lookup={r['review_id']:r for r in rows}
for r in queue:
    for k,v in lookup[r['review_id']].items(): assert r[k]==v
assert [r['review_priority'] for r in queue]==sorted(r['review_priority'] for r in queue)
# Identical responses to the same target must receive identical substantive labels.
duplicates=collections.defaultdict(set)
for r in rows:
    duplicates[(r['question'],r['response'])].add(tuple(r.get(k) for k in ['correctness','behavior','coherence','relevance','supported_target_in_unselected_list']))
assert all(len(v)==1 for v in duplicates.values())
assert dict(collections.Counter(str(r['review_priority']) for r in rows))==manifest['priorities']
assert sum(r['reached_token_budget'] and not r['ended_with_eos'] for r in rows)==4
result=dict(status='passed',responses=480,unique_questions=len({r['question'] for r in rows}),
    source_A_and_B_files_unchanged=True,response_hashes_preserved=True,
    identical_response_labels_consistent=True,csv_json_values_match=True,
    all_human_decisions_pending=True,B_approval_received=False,
    output_sha256={p.name:sha(p) for p in sorted(OUT.iterdir()) if p.suffix in {'.json','.csv','.md'} and p.name!='validation.json'})
(OUT/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='output_sha256'},indent=2))
