"""Validate pinned PR12 and compare annotation passes, never human IAA."""
import collections,csv,hashlib,io,json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1]
OUT=R/'results/B-return-review-20261118';OUT.mkdir(exist_ok=True)
COMMIT='815ceef274bae1ddf93fa2465fa5b3fd89ad7ed0'
PREFIX='results/b-annotation-return-20261117/'
get=lambda name:subprocess.check_output(['git','show',COMMIT+':'+PREFIX+name],cwd=R)
sha=lambda b:hashlib.sha256(b).hexdigest()
manifest=json.loads(get('manifest.json'))
assert sha((R/'results/provisional-annotation-20261030/B-provisional-review-package.zip').read_bytes())==manifest['source_package_sha256']
hash_checks={}
for name,h in manifest['files'].items():
    blob=get(name); exact=sha(blob)==h; reconstructed=None
    if not exact and name.endswith('.csv'):
        buffer=io.StringIO(newline='')
        csv.writer(buffer,lineterminator='\r\n').writerows(csv.reader(io.StringIO(blob.decode(),newline='')))
        reconstructed=sha(buffer.getvalue().encode())
    assert exact or reconstructed==h,name
    hash_checks[name]=dict(declared=h,git_blob_sha256=sha(blob),exact_byte_match=exact,CRLF_record_serialization_sha256=reconstructed)

(OUT/'B-DISCLOSURE-source.md').write_bytes(get('DISCLOSURE.md'))
(OUT/'B-manifest-source.json').write_bytes(get('manifest.json'))
allowed={'correctness':{'correct','partial','incorrect','ambiguous'},'behavior':{'answer','refusal','mixed','empty'},'supported_target_in_unselected_list':{'yes','no','uncertain','not_applicable'},'coherence':{'coherent','partly_incoherent','incoherent'},'relevance':{'on_topic','partly_off_topic','off_topic'}}
editable=set(allowed)|{'reviewer_id','notes','spec_disagreement','reference_review_notes','review_progress'}
identity=lambda r:(r['item_id'],r['model_role'],r['condition'])
A=json.loads((R/'results/A-accepted-development-20261102/joined-A-accepted.json').read_text())
lookup={identity(r):r for r in A};assert len(lookup)==480
comparisons=[];counts={};distinct={}
for pop,n in [('forget',120),('utility',360)]:
    original=list(csv.DictReader((R/f'results/provisional-annotation-20261030/B/{pop}-review.csv').open()))
    new=list(csv.DictReader(io.StringIO(get(f'{pop}-review-B.csv').decode())))
    keys=json.loads((R/f'local-review-keys/provisional-annotation-20261030/B-{pop}-key.json').read_text())['mapping']
    keylookup={k['review_id']:k for k in keys};assert len(keylookup)==n
    assert len(original)==len(new)==n
    fields=[k for k in allowed if pop=='utility' or k not in ['coherence','relevance']]
    groups={}
    for old,b in zip(original,new):
        assert old.keys()==b.keys()
        assert all(old[k]==b[k] for k in old if k not in editable),(pop,b['review_id'])
        assert all(b[k] in allowed[k] for k in fields)
        assert b['review_progress']=='complete'
        assert sha(b['response'].encode())==b['response_sha256']
        key=keylookup[b['review_id']];a=lookup[identity(key)]
        assert a['response_sha256']==b['response_sha256']==key['response_sha256']
        assert all(a[k]==b[k] for k in ['question','reference_answer','specification_sha256','rubric_version'])
        group=(b['question'],b['reference_answer'],b['specification_sha256'],b['response'])
        labels=tuple(b[k] for k in fields)
        assert groups.setdefault(group,labels)==labels
        comparisons.append(dict(population=pop,item_id=key['item_id'],model_role=key['model_role'],condition=key['condition'],
            A_review_id=a['review_id'],B_review_id=b['review_id'],question=b['question'],reference_answer=b['reference_answer'],response=b['response'],response_sha256=b['response_sha256'],
            required_components=b['spec_required_components'],spec_rationale=b['spec_rationale'],specification_sha256=b['specification_sha256'],
            A_labels={k:a[k] for k in fields},B_labels={k:b[k] for k in fields},
            differing_fields=[k for k in fields if a[k]!=b[k]],A_notes=a['notes'],B_notes=b['notes'],
            reference_issue=b['reference_issue'],B_reference_review_notes=b['reference_review_notes'],
            adjudication_status='pending',human_adjudicators=[],final_label=None))
    distinct[pop]=len(groups)
    counts[pop]={}
    for field in fields:
        rs=[r for r in comparisons if r['population']==pop]
        c=collections.Counter((r['A_labels'][field],r['B_labels'][field]) for r in rs)
        counts[pop][field]={'matches':sum(v for (a,b),v in c.items() if a==b),'total':len(rs),
            'confusion':[{'A':a,'B':b,'count':v} for (a,b),v in sorted(c.items())]}
assert len(comparisons)==480 and len({identity(r) for r in comparisons})==480
assert distinct==manifest['judgments']
disagreements=[r for r in comparisons if r['differing_fields']]
correctness=[r for r in comparisons if 'correctness' in r['differing_fields']]
summary=dict(date='2026-11-18',PR=12,source_commit=COMMIT,validation='content_passed_CSV_manifest_byte_hashes_require_correction',rows=480,distinct_B_judgments=distinct,
    comparison_type='A AI-proposed/human-accepted versus B AI-generated/unreviewed; prior exposure disclosed; NOT human inter-annotator agreement',
    fields=counts,rows_with_any_label_disagreement=len(disagreements),rows_with_correctness_disagreement=len(correctness),
    human_independent_review_completed=False,adjudication_completed=False,original_annotations_modified=False,
    source_file_hash_checks=hash_checks)
for name,data in [('comparison-summary',summary),('all-comparisons',comparisons),('disagreements',disagreements)]:
    (OUT/f'{name}.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
approval=dict(date_received='2026-11-18',source='B statement relayed by user in conversation',
    statement='Specification: I accept your 15 reconciled utility rows. For row 29 (Bogotá), I agree that categorical yes/no answers stay ambiguous. Open reference questions are listed in DISCLOSURE.md.',
    scope='15 reconciled utility rows and the categorical Bogota yes/no ambiguity rule. No independent human label review or approval of all 80 rows inferred.',
    referenced_candidate_sha256=sha((R/'results/specification-reconciliation-20261030/combined-specification-candidate.csv').read_bytes()),
    hash_explicitly_confirmed_by_B=False,joint_freeze=False,reference_questions_resolved=False)
(OUT/'B-specification-acceptance.json').write_text(json.dumps(approval,indent=2,ensure_ascii=False)+'\n')
lines=['# B annotation return review — 18 November 2026','',
'PR #12 at `'+COMMIT+'` validates against the original B package: 480 rows, unchanged IDs/order/specification fields and response hashes, valid labels and consistent identical judgments. The source package and disclosure hash match exactly. Both CSV byte hashes differ from the manifest; reserializing CSV records with CRLF endings reproduces both declared hashes exactly (embedded response newlines stay LF). This is consistent with line-ending normalization, not changed annotation content. B should regenerate manifest hashes from the committed Git blobs. The audit records both actual and declared hashes and does not silently repair B’s manifest. Reviewer identity is explicitly AI-generated. B’s `complete` field denotes completion of that AI pass, not human review.','',
'A’s pass was Codex-proposed and Vedant-accepted. B’s pass was Claude-generated at B’s request, unreviewed by B, with prior aggregate/example exposure disclosed. The numbers below describe agreement between those passes; they are not human inter-annotator agreement or independent evidence that labels are accurate. Repeated responses are retained and affect the counts. No κ, confidence interval or human reliability claim is made.','',
'| Population | Field | Matching rows | Total | Agreement between passes |','| --- | --- | ---: | ---: | ---: |']
for pop,fields in counts.items():
    for f,c in fields.items():lines.append(f"| {pop} | {f} | {c['matches']} | {c['total']} | {c['matches']/c['total']:.1%} |")
lines+=['',f"Correctness differs on **{len(correctness)}** rows; any scored annotation field differs on **{len(disagreements)}** rows. B describes {sum(distinct.values())} distinct judgments across 480 records. Neither this grouping nor the 480 records creates independent human ratings.",'',
'## Specification and reference decisions','',
'B’s relayed statement accepts the 15 reconciled utility rows and categorical yes/no ambiguity for the Bogota item. Recorded separately with receipt date and candidate hash; B did not explicitly confirm that hash or all 80 rows. This is not a joint freeze. Preserve original provisional files and statuses as historical source records.','',
'The multipart contradiction rule should remain as written unless both authors explicitly change it: a materially contradicted requested component makes the answer incorrect, even when another component is correct. “Partial” applies to an uncontradicted substantive subset. Human adjudication of particular examples may still be needed.','',
'For non-canonical titles, check the frozen author QA evidence uniformly. A supported title is not automatically ambiguous: the question’s qualifier and missing “another” context determine whether it is correct or unresolved. Unsupported titles remain incorrect under the declared convention. Nile/Amazon needs coordinated source checking. The writing-style paraphrase needs an explicit human interpretation, not automatic preference for either AI label.','',
'## Human-check proposal — not yet adopted','',
'Review all correctness disagreements and unresolved reference cases. Also draw a reproducible random sample from the agreement cases before human labels are collected, so shared errors can be detected. A disagreement-only audit cannot estimate overall error. Choose sample size, strata, reviewer, selection seed, exposure declaration and reporting rules as an explicit protocol decision.','',
'For a third annotator’s first pass, hide model/condition and both proposed labels. For B, disclose previous exposure and distinguish fresh judgments from reviewing a visible proposal. Preserve the selected human judgments before adjudication. Report sampled human-audit results for their actual sampling design; do not relabel the full 480 responses as human-reviewed. No sample or deadline is approved by this report.','',
'No GPU rerun is needed for this step. Do not replace A’s accepted counts with B’s labels or merge labels silently. PR #12 has been inspected, not merged or approved on behalf of either author.','',
'## Disagreement queue','',
'Each entry preserves both passes. Final labels are deliberately unset in disagreements.json. A/B review IDs refer to independently shuffled sheets and must not be joined directly. The join here uses item, checkpoint, condition and response hash through the private coordinator mapping.','']
for r in disagreements:
    lines += [f"### {r['A_review_id']} / {r['B_review_id']} — {', '.join(r['differing_fields'])}",'',
        '**Question:** '+r['question'],'','**Reference:** '+r['reference_answer'],'',
        '**Required components:** '+r['required_components'],'','**Response:** '+r['response'],'',
        '**A:** '+json.dumps(r['A_labels'])+' — '+r['A_notes'],'',
        '**B:** '+json.dumps(r['B_labels'])+' — '+r['B_notes'],'','**Decision:** pending human review.','']
(OUT/'REVIEW_AND_DISAGREEMENTS.md').write_text('\n'.join(lines))
print(json.dumps({k:summary[k] for k in ['rows','distinct_B_judgments','rows_with_any_label_disagreement','rows_with_correctness_disagreement','fields']},indent=2))
