"""Build a complete, unblinded paired-answer report from archived run records."""
from pathlib import Path
import json, hashlib, re
from collections import OrderedDict
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'results/int4-development/int4dev_20261025T142729681517Z'
SRC=RUN/'manual-review/paired-responses.json'
OUT=ROOT/'output/pdf/KV_Cache_Unlearning_INT4_All_Paired_Answers.pdf'
QA=ROOT/'tmp/pdfs/int4-paired-report'; QA.mkdir(parents=True,exist_ok=True)
pdfmetrics.registerFont(TTFont('Arial','/System/Library/Fonts/Supplemental/Arial.ttf'))
pdfmetrics.registerFont(TTFont('ArialB','/System/Library/Fonts/Supplemental/Arial Bold.ttf'))
rows=json.loads(SRC.read_text()); groups=OrderedDict()
for r in rows: groups.setdefault(r['item_id'],[]).append(r)
groups=OrderedDict(sorted(groups.items(),key=lambda kv: ['forget10','retain90','real_authors','world_facts'].index(kv[1][0]['split'])))
assert len(rows)==240 and len(groups)==80
assert all(len(v)==3 and len({r['model'] for r in v})==3 for v in groups.values())
for group in groups.values():
    assert len({r['question'] for r in group})==len({r['reference'] for r in group})==1
W,H=595.276,841.89; margin=43; width=W-2*margin
c=canvas.Canvas(str(OUT),pagesize=(W,H));c.setTitle('KV-cache unlearning: all 240 ordinary / INT4 comparisons');c.setAuthor('Research working report - prepared with AI assistance')
page=0; checks=[]
def P(s,size=10,lead=None,color='#203149',bold=False):
    return Paragraph(s,ParagraphStyle('p',fontName='ArialB' if bold else 'Arial',fontSize=size,leading=lead or size*1.34,textColor=colors.HexColor(color),spaceAfter=7))
def txt(s):return escape(str(s)).replace('\n','<br/>')
def render(title,items,bookmark=None):
    global page
    page+=1
    c.setFillColor(colors.HexColor('#16324f'));c.rect(0,H-16,W,16,fill=1,stroke=0)
    c.setFont('Arial',8);c.drawString(margin,H-36,'KV-CACHE UNLEARNING  /  PAIRED DEVELOPMENT REVIEW')
    c.setFont('ArialB',17);c.drawString(margin,H-64,title)
    if bookmark:c.bookmarkPage(bookmark);c.addOutlineEntry(title,bookmark,0,False)
    y=H-84
    for flow in items:
        _,h=flow.wrap(width,y-52)
        if y-h<52:raise ValueError(f'Overflow on page {page}: {title}, y={y}, h={h}')
        flow.drawOn(c,margin,y-h);y-=h+getattr(flow,'spaceAfter',0)
    c.setStrokeColor(colors.HexColor('#ccd5df'));c.line(margin,39,W-margin,39)
    c.setFont('Arial',7);c.setFillColor(colors.HexColor('#52647b'));c.drawString(margin,26,'25 October 2026 | Development evidence | Model identities visible | Not a blinded annotation sheet')
    c.drawRightString(W-margin,26,f'{page} / 84')
    checks.append({'page':page,'bottom_content_y':y});c.showPage()
render('All 240 ordinary / INT4 comparisons',[
 P('Purpose and scope',14,bold=True),
 P('This report contains every question, dataset reference and generated answer from the completed paired development run. There are <b>80 distinct dataset items x 3 checkpoints = 240 comparisons</b>, with two cache conditions per comparison: <b>480 generated answers</b>. Each question page groups all three checkpoints so readers can compare them without searching between sections.'),
 P('The 80 questions comprise 20 forget questions about one fictitious author, 30 retained-author questions, 15 real-author questions and 15 world-fact questions. These are previously exposed development items, not an untouched confirmation set.'),
 P('How to read the models',14,bold=True),
 P('<b>Full:</b> the checkpoint trained on the full TOFU training set. It provides a pre-unlearning reference, but need not answer every question correctly.<br/><b>Retain90:</b> the reference checkpoint trained on the retained portion. It was not trained on the designated forget portion.<br/><b>SimNPO candidate:</b> the selected weight-unlearned checkpoint. Its forget-answer behaviour is the main development case for testing robustness to cache compression.'),
 P('What changed between conditions',14,bold=True),
 P('Within each checkpoint, the loaded weights are unchanged. Ordinary uses the unquantized cache. INT4 uses HQQ 4-bit stored-cache quantization with axes 1/1, group size 64 and residual length 128. Model weights are FP32 in both conditions. The shared setup is a Tesla T4, Torch 2.9.1+cu128, Transformers 5.5.4, HQQ 0.2.8.post1, SDPA and TF32 disabled.'),
 P('Prompts, tokenizer, masks and generation settings are shared: fixed date 10 Apr 2025, helpful-assistant system prompt, greedy decoding, one beam and at most 64 new tokens. The question pages show the user question, not the repeated chat wrapper.'),
 P('<b>Review status:</b> complete engineering audit; new INT4 factual labels and independent review remain pending. Text-change flags are measured comparisons, not accuracy judgments. Model and cache identities are visible, so this report is for discussion and transparent review, not an independent blinded first pass.'),
], 'scope')
render('Why INT4 can sometimes answer better',[
 P('1. Numerical precision is not factual truth',13,bold=True),
 P('An ordinary cache preserves the model\'s computed key/value tensors at the selected precision. It does not correct incomplete learning, hallucinations, conflicting associations or damage from unlearning. Full-model errors are possible; forget-answer failures in retain90 and SimNPO are also consistent with the intended training objectives. A wrong answer alone does not prove successful or safe forgetting.'),
 P('2. Compression can change which continuation wins',13,bold=True),
 P('Quantization changes stored K/V values and their later readback. This can perturb attention and next-token scores. If two candidate tokens have close scores, the greedy winner can switch. Later generation then conditions on a different prefix, so a small early difference can produce a very different answer. The new path can be better or worse. This is a plausible mechanism; this run did not archive the full candidate-logit margins needed to establish it for every changed answer.'),
 P('3. The observed improvement is real in at least one clear case',13,bold=True),
 P('For full-model forget item 8 (report question 09), the ordinary answer names a "Mentor of the Year" award. INT4 names the reference\'s "Leadership Literature Luminary" award. Conversely, item 5 (question 06) changes from the reference-matching book and father\'s profession to a different book and mother\'s profession. These illustrate why both gains and losses must be counted. They are illustrative judgments, not a completed annotation of all outputs.'),
 P('4. Better utility and weaker forgetting are different outcomes',13,bold=True),
 P('A correct answer on retained, real-author or world-fact questions is a utility success. A newly correct forgotten fact from the unlearned model may indicate increased disclosure, which would weaken forgetting. The full model\'s award correction is not itself an unlearning failure because the full model was not unlearned. Retain90 changes help reveal generic quantization effects; they do not provide a perfect causal explanation for every SimNPO change.'),
 P('5. Check the reference and the denominator',13,bold=True),
 P('Semantic equivalence matters more than exact wording. Some references are incomplete or ambiguous: for example, LGBTQ+ membership does not specify a person\'s gender identity. A fluent, longer answer is not automatically correct. The browser initially shows changed outputs, which can make interesting improvements look more prevalent. Use all items, inspect both directions and keep splits and checkpoints separate.'),
], 'interpretation')
changes=[['Checkpoint','Forget','Retained','Real','World','All']]
for m,label in [('full','Full'),('retain90','Retain90'),('simnpo_candidate','SimNPO')]:
 a=[r for r in rows if r['model']==m]
 changes.append([label]+[f"{sum(r['changed'] for r in a if r['split']==s)}/{sum(r['split']==s for r in a)}" for s in ['forget10','retain90','real_authors','world_facts']]+[f"{sum(r['changed'] for r in a)}/80"])
t=Table(changes,colWidths=[100,80,85,75,75,94]);t.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'Arial'),('FONTSIZE',(0,0),(-1,-1),10),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dce8f3')),('BOTTOMPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),8),('LINEBELOW',(0,0),(-1,-1),.4,colors.HexColor('#cbd5e1'))]))
render('What the returned run establishes',[
 P('480 / 480 responses completed, with no status errors. All 240 ordinary responses reproduce day seven exactly in text and tokens. This makes an accidental change of baseline less likely; it does not establish factual correctness.'),
 P('Exact generated-text changes',13,bold=True),t,Spacer(1,14),
 P('145 / 240 pairs changed and 95 did not. There are 47 changed forget responses and 98 changed utility responses. These numbers must not be presented as correct-answer gains.'),
 P('The saved ordinary sequential/parallel reference-score checks pass. Empty quantized-cache parallel scores equal no-cache parallel scores, and the first INT4 sequential reference-token score equals ordinary sequential scoring. First-item probes for each checkpoint show reconstructed quantized K/V reaching attention across all 16 layers. The probes cover the first item per checkpoint, not every item individually.'),
 P('Average reference-score effects',13,bold=True),
 P('Mean INT4-minus-ordinary sequential NLL changes, averaged equally over the 20 forget questions, are +0.016648 (full), +0.002018 (retain90) and +0.032497 (SimNPO). Positive means the fixed reference is less probable on average. These are not generated-answer accuracy scores; individual improvements and degradations can cancel, and reference likelihood need not track greedy answer correctness.'),
 P('Four visible answers reached the 64-token budget without EOS. They are flagged on their pages and retained in the denominator: full INT4 retained item 631, SimNPO ordinary forget item 5, and SimNPO INT4 forget items 8 and 18.'),
 P('Next analysis',13,bold=True),
 P('Apply one agreed semantic rubric to both conditions; record correct, partial, incorrect and ambiguous separately, including refusals that still disclose the fact. For each checkpoint and split, count correct-to-correct, correct-to-noncorrect, noncorrect-to-correct and noncorrect-to-noncorrect transitions, while preserving partial/ambiguous detail. Report net change as (gains minus losses) / the fixed number of evaluated items, with the ambiguity policy declared. Do not silently exclude difficult or truncated cases.'),
 P('Use paired comparisons and broader author coverage before generalizing. One exposed forget author cannot support a population-level author confidence interval. Repeating identical greedy runs tests reproducibility; it does not create independent evidence of accuracy. If explaining a specific gain, inspect token-score margins on the same prefix before divergence.'),
], 'evidence')
render('Reading guide and source record',[
 P('Question index',14,bold=True),
 P('<b>Questions 01-20 / pages 5-24:</b> forget10, one author.<br/><b>Questions 21-50 / pages 25-54:</b> retained-author utility screen.<br/><b>Questions 51-65 / pages 55-69:</b> real-author utility.<br/><b>Questions 66-80 / pages 70-84:</b> world-fact utility.'),
 P('Each page shows one question, its supplied dataset reference, and ordinary/INT4 answers for full, retain90 and SimNPO. Text is reproduced from the saved responses without factual correction. Generated-token counts include the recorded special tokens; the visible text omits those tokens. A changed flag means the two decoded strings differ. References should be assessed against the question rather than treated as an infallible answer key.'),
 P('Run and reproducibility',14,bold=True),
 P('Run: int4dev_20261025T142729681517Z<br/>Returned ZIP SHA256:<br/><font size="8">c5bb47659da4f1d5092895b5e4c41694ba3a63d32ef421231994782f4b7f846b</font><br/>The original 38 ZIP files were archived byte-for-byte. Config and child manifests record immutable checkpoint revisions. Local engineering review: INT4_DEVELOPMENT_REVIEW.md and artifact-review.json in the run folder.'),
 P('Checkpoint references',14,bold=True),
 P('Full: open-unlearning/tofu_Llama-3.2-1B-Instruct_full<br/><font size="8">88e31200b97e4c0c04ae0d2f0b591f427046d192</font><br/>Retain90: open-unlearning/tofu_Llama-3.2-1B-Instruct_retain90<br/><font size="8">7114300c0049527a71833f5683965c358ad9dcbf</font><br/>SimNPO: forget10, lr2e-05, b4.5, a1, d1, g0.125, ep10<br/><font size="8">444648425d9c8a3926683f1870e364c5fe0b1357</font>'),
 P('Background resources',14,bold=True),
 P('TOFU: A Task of Fictitious Unlearning for LLMs. The benchmark uses invented author profiles, so these author answers are evaluated within the synthetic dataset.<br/><link href="https://locuslab.github.io/tofu/" color="#12649c">https://locuslab.github.io/tofu/</link>'),
 P('Hugging Face: KV cache quantization. Background on stored-cache compression and residual caches; this report\'s exact implementation claims come from the archived run and probes.<br/><link href="https://huggingface.co/blog/kv-cache-quantization" color="#12649c">https://huggingface.co/blog/kv-cache-quantization</link>'),
 P('<b>Sharing note:</b> this document exposes model/condition identities and illustrative interpretations. It can be shared as a descriptive research report. Provide a separately shuffled, label-free package to anyone intended to perform a blinded first-pass annotation. No independent-review approval or final accuracy advantage is asserted.'),
], 'guide')
labels={'full':'FULL','retain90':'RETAIN90','simnpo_candidate':'SimNPO CANDIDATE'}
for n,(item,group) in enumerate(groups.items(),1):
 a=group[0]; split=a['split']; index=item.rsplit(':',1)[-1]
 items=[P(f"{txt(split)} | Dataset item {index} | Question {n:02d} of 80",9,color='#52647b'),P(txt(a['question']),12,bold=True),P('<b>DATASET REFERENCE</b><br/>'+txt(a['reference']),10),Spacer(1,4)]
 for r in group:
  status='TEXT CHANGED' if r['changed'] else 'IDENTICAL TEXT'
  items.append(P(labels[r['model']]+'  |  '+status,10,bold=True,color='#12649c'))
  for k,label in [('ordinary','ORDINARY CACHE'),('int4','INT4 CACHE')]:
   note=f"{r[k+'_tokens']} generated tokens"+(' | TOKEN LIMIT, NO EOS' if r[k+'_truncated'] else '')
   items.append(P(f'<b>{label}</b> <font color="#52647b" size="8">({note})</font><br/>'+txt(r[k]),11,14.5))
  items.append(Spacer(1,5))
 render(f'Question {n:02d} | {split}',items,f'q{n}')
assert page==84;c.save()
(QA/'layout-checks.json').write_text(json.dumps(checks,indent=2))
print(OUT)
print('Pages:',page,'minimum content bottom:',min(r['bottom_content_y'] for r in checks))
