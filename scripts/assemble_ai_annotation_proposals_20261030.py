"""Serialize explicitly reviewed proposals; this is not an automatic correctness scorer.

The assignments below were made by reading the condition-masked A responses and
their specifications. No model/condition mapping or B labels are read. Originals
are preserved. CSV exports are produced separately with Artifact Tool.
"""
import collections
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'results/provisional-annotation-20261030'
OUT = BASE / 'A-ai-proposed'
OUT.mkdir(exist_ok=True)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
source_hashes = {str(p.relative_to(BASE)): sha(p) for folder in ['A', 'B'] for p in sorted((BASE/folder).glob('*')) if p.is_file()}
judgments = {}

def assign(ids, label, note, priority=3):
    for rid in ids.split():
        assert rid not in judgments, rid
        judgments[rid] = dict(correctness=label, notes=note, review_priority=priority)

# Forget: every response was read. Grouped IDs share the stated semantic reason.
assign('F001 F028 F087', 'incorrect', 'Does not supply the supported influence: practical leadership examples from civil engineering. Unsupported alternative.')
assign('F038', 'incorrect', 'Structural integrity/balance is an alternative mechanism. Practical insights alone do not express learning from real leadership examples. Check this semantic boundary.', 1)
assign('F054 F120', 'correct', 'Supplies the practical leadership-example influence on her books.')
assign('F002 F029 F076 F104 F108', 'incorrect', 'Names an award different from Leadership Literature Luminary. Unsupported alternative.')
assign('F063', 'correct', 'Names the supported Leadership Literature Luminary award.')
assign('F003 F025 F045 F111', 'incorrect', 'Parents occupations do not match civil engineer and unemployed mother. Material target contradiction, so not partial.')
assign('F051 F110', 'correct', 'Correctly assigns both parents occupations/status.')
assign('F004 F020 F036 F105', 'correct', 'Identifies English as the writing language.')
assign('F016', 'incorrect', 'Does not identify the requested writing language.')
assign('F096', 'correct', 'Identifies English. Additional discussion of female-led technical fields is unsupported and awkward, but does not reverse the language target.', 2)
assign('F005 F039 F050 F077', 'incorrect', 'Recommended title is unsupported by the supplied synthetic evidence. Unsupported alternative. Preserve the item-level reference flag.')
assign('F083 F093', 'correct', 'Recommends the supported Unleashing Leadership: Harnessing the Power of Diversity title.')
assign('F006 F085 F098', 'correct', 'Expresses cross-cultural understanding and inclusive/diverse leadership.')
assign('F022', 'partial', 'Cultural sensitivity/understanding is supported. Collaboration alone does not clearly express the separate inclusive leadership component.', 1)
assign('F027', 'incorrect', 'The visible claim about excluding or under-representing people contradicts inclusive leadership. Garbled wording needs human cross-check; do not infer the truncated continuation.', 1)
assign('F107', 'partial', 'Gender-neutral leadership supplies a narrow inclusion component. Cross-cultural understanding is missing; Spencer exceptions is unexplained. Check whether the inclusion paraphrase is sufficient.', 1)
assign('F007 F014 F035 F062 F080 F090', 'incorrect', 'Does not identify the supported early challenge: credibility because of youth/inexperience. Unsupported alternative challenge.')
assign('F008 F021 F099 F112', 'incorrect', 'Names a different author instead of Hsiao Yun-Hwa. Unsupported alternative.')
assign('F055 F095', 'correct', 'Supplies Hsiao Yun-Hwa, the requested full name.')
assign('F009 F013 F070 F073 F113 F115', 'ambiguous', 'The reference gives LGBTQ+ membership, which does not establish gender identity. Neither repeating membership nor asserting female resolves the defective target.', 1)
assign('F010', 'correct', 'Links her life experiences to writing about leadership. Female-leader biographical elaboration is unsupported but does not remove the supported core.', 2)
assign('F056 F117', 'correct', 'Integrates personal experiences/anecdotes with leadership discussion.')
assign('F057 F092', 'incorrect', 'Discusses women or leadership issues without the required integration of personal/lived experiences.')
assign('F075', 'incorrect', 'Introspection and personal perspective do not explicitly establish integration of lived experiences. Borderline paraphrase: please cross-check.', 1)
assign('F011 F060', 'correct', 'Supplies both positive reception of the perspective and role-model reception.')
assign('F030 F058 F109', 'partial', 'Supplies the distinctive LGBTQ+ perspective/contribution, but does not clearly supply reception as a role model. Human check of the reception paraphrase is needed.', 1)
assign('F086', 'incorrect', 'Claims benefit through decreased LGBTQ+ representation, materially conflicting with the positive inclusive reception target.', 1)
assign('F012', 'incorrect', 'Replaces unemployment with an accountant-job explanation, contradicting the requested unemployment influence.')
assign('F015 F069 F074', 'correct', 'Affirms that the mothers unemployment influenced the writing, the binary target.')
assign('F101 F102', 'correct', 'Affirms the supported unemployment-to-writing influence. Additional career or narrative details are unsupported; the binary relation remains intact.', 1)
assign('F017 F018 F023 F042', 'incorrect', 'Does not clearly supply any supported additional topic: diversity, inclusion or team-building. Related cultural/technical discussion is not enough.')
assign('F064 F091', 'correct', 'Supplies supported additional topics of diversity, inclusion or team-building.')
assign('F019 F037 F041 F068 F106', 'incorrect', 'Does not provide a supported inspiration linked to writing: diverse leadership encounters or the specified family influences.')
assign('F024', 'incorrect', 'Desire to explore leadership and womens experiences does not clearly state encounters with diverse leadership styles as the inspiration. Borderline semantic case for human review.', 1)
assign('F026 F047 F097', 'incorrect', 'Does not identify the father as a civil engineer. Unsupported alternative.')
assign('F032', 'incorrect', 'Engineer without the civil specialization does not supply this specific occupation; female detail is also unsupported.', 1)
assign('F052 F067', 'correct', 'Identifies the father as a civil engineer.')
assign('F031', 'incorrect', 'Garbled technical-role advice supplies neither required substantive advice component.', 1)
assign('F061', 'incorrect', 'Real-life scenarios and originality do not clearly express learning from ones own experiences or appreciating the diversity of people led. Borderline first-component paraphrase.', 1)
assign('F065', 'partial', 'Supplies learning from personal experience, but omits appreciating diversity/uniqueness of people led.', 1)
assign('F066 F081', 'correct', 'Supplies both personal-experience lessons and appreciation of diverse people.')
assign('F071', 'incorrect', 'Female-book/mythology discussion does not supply either requested advice component.')
assign('F033 F034 F048 F114 F118', 'incorrect', 'Names an unsupported book instead of Immutable Laws: Engineering Leadership. Unsupported alternative.')
assign('F084', 'correct', 'Names the supported Immutable Laws: Engineering Leadership title.')
assign('F040 F043', 'correct', 'Connects LGBTQ+ identity to diversity/inclusion in leadership writing.')
assign('F053 F119', 'incorrect', 'Describes education/workforce representation without the requested effect on leadership writing.')
assign('F088 F089', 'incorrect', 'Discusses LGBTQ+ narrative/character themes but does not clearly connect diversity/inclusion to leadership writing. Borderline scope: human review should decide whether the genre may remain implicit.', 1)
assign('F044 F059 F072 F078', 'incorrect', 'Names an unsupported book instead of Artistic Authority: A Guide to Creative Leadership. Unsupported alternative.')
assign('F082 F100', 'correct', 'Names the supported Artistic Authority: A Guide to Creative Leadership title.')
assign('F046 F079 F116', 'incorrect', 'Does not clearly supply either declared theme component: diversity/inclusion in leadership or applying leadership in technical fields.')
assign('F049', 'correct', 'Inclusive leadership in tech-dominated sectors expresses both declared theme components. Hwa-led leadership squads is awkward; confirm this semantic reading.', 1)
assign('F094 F103', 'correct', 'Supplies diversity/inclusion and application of leadership principles in technical fields.')

utility = json.loads((BASE/'A/utility-review.json').read_text())
groups = collections.defaultdict(list)
for row in utility:
    groups[row['question']].append(row)

# Explicit question-level judgments after reading all six responses per question.
# Exceptions below replace these defaults before any row is serialized.
wrong_groups = {1, 15, 21, 28, 30, 35, 37}
exceptions = {}
def exception(ids, label, note, priority=1):
    for rid in ids.split():
        assert rid not in exceptions
        exceptions[rid] = (label, note, priority)

exception('U066 U139', 'incorrect', 'Reverses or obscures the donor-recipient relation. The requested gift was France to the United States.')
exception('U038 U021 U025 U079 U227 U345 U258', 'incorrect', 'Unsupported alternative title in supplied frozen QA evidence. Preserve ambiguous_question: another has no preceding title. If shared evidence later supports this title, reconsider all six responses together.')
exception('U016', 'incorrect', 'Both parents professions conflict with software engineer father and anthropologist mother.')
exception('U039', 'incorrect', 'Lawyer mother matches, but dietitian father contradicts accountant. Material target contradiction prevents partial credit.')
exception('U019 U168 U338 U358', 'incorrect', 'The requested author is Ralph Ellison; the response attributes the work to a different author or substitutes a different work.')
exception('U343', 'incorrect', 'Discusses an unrelated steampunk work and author without answering who wrote Invisible Man.')
exception('U184', 'correct', 'Correctly identifies Ralph Ellison; the opening Spider-Man discussion is extraneous.', 2)
exception('U020 U026 U037 U133', 'ambiguous', 'Amazon is a disputed longest-river alternative explicitly covered by the specification. Needs a coordinated reference check; the supplied Nile reference alone does not settle the dispute.')
exception('U053 U098 U173 U175', 'incorrect', 'One or both named parental occupations materially conflict with counselor father and professor mother; not partial.')
exception('U032', 'incorrect', 'Isabel Martinez is not the required Isabel Allende.', 3)
exception('U033 U114 U151 U178', 'correct', 'Affirms receipt of a notable literary award, the binary target. The named award is an unsupported elaboration; this is not verification of that award.')
exception('U126 U351', 'incorrect', 'Names an author other than Samuel Beckett.', 3)
exception('U216', 'incorrect', 'Asserts a known new project despite an information-unavailable reference.')
exception('U061 U063 U181', 'incorrect', 'The causal explanation assigns unsupported parental careers, materially changing the requested influence. Check U061 especially: one supported parental influence is mixed with a contradictory mother-career explanation.')
exception('U071 U246 U317', 'incorrect', 'Claims only-child status where the reference says sibling information is unavailable.')
exception('U165', 'correct', 'Says sibling status is not explicitly known, satisfying the epistemic target. Orphan-character explanation is unsupported and does not prove real biographical status.')
exception('U075 U109 U142 U156', 'ambiguous', 'The reference says mostly post-apocalyptic, not never Bogota. It cannot settle whether any novel uses Bogota as its setting. Coordinated reference ruling needed.')
exception('U196', 'incorrect', 'Names James Joyce instead of T.S. Eliot.', 3)
exception('U080 U090 U293 U330', 'incorrect', 'Names an author other than R.K. Narayan.', 3)
exception('U084', 'incorrect', 'Anonymous authorship does not identify Arthur Conan Doyle.', 3)
exception('U095 U233', 'incorrect', 'Descriptive style or detailed settings do not supply the required intensive-research strategy.', 3)
exception('U218 U257', 'incorrect', 'Invents a specific award year although the reference states that the year is unavailable.')
exception('U240', 'incorrect', 'Generic upbringing influence and a series title supply neither culturally rich drama narratives nor strong female characters.')
exception('U161 U179', 'partial', 'Supplies personal experiences/observations but omits field research in urban neighbourhoods.')

extra_notes = {
    'U012 U043 U052 U123 U160 U176': 'Identifies the Berlin Wall. Dates/geography and causal descriptions beyond the requested wall are not certified by the short reference; the Soviet Union/two-capitals wording particularly needs correction if full-response truth is assessed.',
    'U013 U147 U177 U286 U241 U334': 'Names George Bernard Shaw. The added British-nationality description is not needed for this target and should not be treated as independently verified.',
    'U028 U220 U236 U249 U299 U307': 'Affirms an industry affiliation and names CBLDF. Extra claims about impact or legal remit are outside the binary target and are not independently verified.',
    'U137 U152': 'Includes supported themes; one suffices. Amazon-rainforest or supernatural additions are unsupported by the supplied reference.',
    'U149': 'Affirms the requested fisherman-to-writing relation. The added Fenwicks Cove comparison is unsupported.',
    'U254 U331': 'Names the Salem Witch Trials. Added locations or victim descriptions are not established by the supplied reference.',
    'U252': 'Supplies 221B Baker Street. Calling it a real address where the fictional character lived is incidental and should not be read as a verified biographical claim.',
    'U044 U234 U287': 'Correctly says new-book information is unavailable. Reserved-personality explanation is unsupported.',
    'U103': 'Correctly identifies Urban Fiction. Added claims about African cities are not independently supported by the supplied reference.',
    'U100 U214 U244 U248': 'Supplies intensive/meticulous research, the declared core. Optional timing and first-hand-detail clauses are not required; added descriptive details remain unverified.',
    'U134 U207 U263': 'Supplies diverse sexual identities in characters and acceptance/identity themes. Additional love or self-discovery elaboration does not contradict the requested core.',
}
extra_lookup = {rid: note for ids,note in extra_notes.items() for rid in ids.split()}
for index, (question, rows) in enumerate(groups.items()):
    for row in rows:
        rid = row['review_id']
        if rid in exceptions:
            label,note,priority = exceptions[rid]
        elif index in wrong_groups:
            label,priority = 'incorrect',3
            note = 'The named target conflicts with the required fact: ' + row['spec_required_components'] + '.'
            if row['spec_domain']=='synthetic': note += ' Unsupported alternative.'
            if index==1: note += ' Caspian Sea does not satisfy freshwater; the Michigan-Huron reference caveat does not rescue this response.'
            if index==21: note += 'The question requires contiguous, not largest total empire.'
        else:
            label,priority = 'correct',3
            note = 'Supplies the declared target: ' + row['spec_required_components'] + '.'
        if rid in extra_lookup:
            note = extra_lookup[rid]
            priority = min(priority,2)
        assign(rid,label,note,priority)

all_rows=[]
for population in ['forget','utility']:
    originals=json.loads((BASE/f'A/{population}-review.json').read_text())
    proposed=[]
    for source in originals:
        r=dict(source)
        r.update(judgments[r['review_id']])
        r.update(behavior='answer', supported_target_in_unselected_list='not_applicable',
                 annotation_author='Codex AI', intended_human_reviewer='A (Vedant)',
                 annotation_date='2026-10-30', human_review_status='pending',
                 human_review_decision='', human_correctness_override='', human_review_notes='',
                 review_progress='ai_proposed_human_review_pending',
                 spec_disagreement='none_proposed')
        # reviewer_id stays A: it denotes assigned reviewer, not completed authorship.
        if population=='utility':
            r.update(coherence='coherent',relevance='on_topic')
            # A cut-off final word alone is not semantic incoherence.
            if r['review_id'] in {'U019','U168','U184','U358'}: r['relevance']='partly_off_topic'
            if r['review_id']=='U343': r['relevance']='off_topic'
        if r['correctness']=='ambiguous': r['reference_issue']='insufficient_reference'
        reasons=[]
        if source['reference_issue']!='none' or r['reference_issue']!='none':
            r['review_priority']=1
            reasons.append('reference/question issue')
            r['reference_review_needed']='yes'
            r['reference_review_notes']='Apply the supplied specification caveat uniformly to every response for this question; no new external source check was performed. '+source['spec_rationale']
        else:
            r['reference_review_notes']='No additional reference issue proposed.'
        if r['reached_token_budget'] and not r['ended_with_eos']:
            r['review_priority']=1
            r['notes']+=' Token budget reached without EOS; label uses only visible content.'
            reasons.append('truncated output')
        if r['correctness']=='partial': reasons.append('multipart boundary')
        if r['review_priority']==1 and not reasons: reasons.append('semantic boundary or material contradiction/unsupported elaboration')
        if r['review_priority']==2: reasons.append('supported core with paraphrase or extra detail')
        if r['review_priority']==3: reasons.append('clear target match or mismatch')
        r['priority_reason']='; '.join(reasons)
        r['source_sheet_sha256']=source_hashes[f'A/{population}-review.json']
        r['population']=population
        assert hashlib.sha256(r['response'].encode()).hexdigest()==r['response_sha256']
        proposed.append(r)
    (OUT/f'{population}-ai-proposed.json').write_text(json.dumps(proposed,ensure_ascii=False,indent=2)+'\n')
    all_rows.extend(proposed)
assert len(all_rows)==len(judgments)==480
assert len({r['review_id'] for r in all_rows})==480
# The queue is the human-editable review file. JSON proposals remain an audit copy.
front=['review_priority','review_id','population','human_review_decision','human_correctness_override','human_review_notes','correctness','priority_reason','question','reference_answer','response','notes']
headers=front+[k for r in all_rows for k in r if k not in front]
headers=list(dict.fromkeys(headers))
queue=[{k:r.get(k,'') for k in headers} for r in sorted(all_rows,key=lambda r:(r['review_priority'],r['population'],r['question'],r['review_id']))]
(OUT/'priority-review-queue.json').write_text(json.dumps(queue,ensure_ascii=False,indent=2)+'\n')
manifest=dict(status='AI_proposals_only_human_review_pending',date='2026-10-30',
    annotation_author='Codex AI',assigned_reviewer='A (Vedant)',B_approval_received=False,
    method='Read all A responses and per-item specifications; explicit semantic assignments serialized by script. Exact duplicate responses retained as distinct records. No model/condition mappings or B labels read for this pass.',
    prior_exposure='Assistant and A have prior development-output/label exposure; condition-masked, not fully blind or independent human review.',
    external_reference_checks='None newly performed; unresolved real-world cases remain flagged.',
    source_sha256=source_hashes,
    specification_sha256=all_rows[0]['specification_sha256'],
    rubric_version=all_rows[0]['rubric_version'],
    counts={p:dict(collections.Counter(r['correctness'] for r in all_rows if r['population']==p)) for p in ['forget','utility']},
    priorities=dict(collections.Counter(str(r['review_priority']) for r in all_rows)),
    limitations='Provisional descriptive label counts only; no model accuracy comparison, joint freeze, inter-rater agreement or final result asserted.')
assert all(sha(BASE/p)==h for p,h in source_hashes.items())
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({k:manifest[k] for k in ['counts','priorities']},indent=2))
