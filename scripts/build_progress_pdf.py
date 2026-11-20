"""Build the self-contained reviewer progress report from pinned local artifacts."""
from pathlib import Path
from xml.sax.saxutils import escape
import json

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    KeepTogether, Preformatted, Flowable,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/pdf/KV_Cache_Unlearning_Progress_Review.pdf'
OUT.parent.mkdir(parents=True, exist_ok=True)
FONTS = Path('/System/Library/Fonts/Supplemental')
for name, file in [('Body', 'Arial.ttf'), ('BodyBold', 'Arial Bold.ttf'),
                   ('BodyItalic', 'Arial Italic.ttf'), ('Mono', 'Courier New.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(FONTS / file)))
pdfmetrics.registerFontFamily('Body', normal='Body', bold='BodyBold', italic='BodyItalic')

NAVY = colors.HexColor('#183048')
TEAL = colors.HexColor('#007C83')
MUTED = colors.HexColor('#526274')
LIGHT = colors.HexColor('#EEF4F7')
LINE = colors.HexColor('#D8E1E7')
AMBER = colors.HexColor('#91600C')
W, H = A4
M = 44
CW = W - 2*M
styles = {
    'body': ParagraphStyle('body', fontName='Body', fontSize=10.5, leading=15,
                           textColor=NAVY, spaceAfter=8),
    'small': ParagraphStyle('small', fontName='Body', fontSize=8.7, leading=12,
                            textColor=MUTED, spaceAfter=6),
    'title': ParagraphStyle('title', fontName='BodyBold', fontSize=25, leading=29,
                            textColor=NAVY, spaceAfter=12),
    'h2': ParagraphStyle('h2', fontName='BodyBold', fontSize=13, leading=17,
                         textColor=TEAL, spaceBefore=10, spaceAfter=6),
    'label': ParagraphStyle('label', fontName='BodyBold', fontSize=8.5, leading=11,
                            textColor=TEAL, spaceAfter=8),
    'cell': ParagraphStyle('cell', fontName='Body', fontSize=9.2, leading=12.5,
                           textColor=NAVY),
    'head': ParagraphStyle('head', fontName='BodyBold', fontSize=9.1, leading=12,
                           textColor=colors.white),
    'mono': ParagraphStyle('mono', fontName='Mono', fontSize=9.3, leading=13,
                           textColor=NAVY),
}
story = []
page_titles = []


def p(text, style='body'):
    return Paragraph(text, styles[style])


def add(text, style='body'):
    story.append(p(text, style))


def section(number, title, subtitle=None):
    if page_titles:
        story.append(PageBreak())
    page_titles.append(title)
    add(f'REVIEWER GUIDE / {number:02d}', 'label')
    add(title, 'title')
    if subtitle:
        add(subtitle, 'small')


def heading(text):
    add(text, 'h2')


def table(headers, rows, widths=None, compact=False):
    widths = widths or [CW/len(headers)]*len(headers)
    data = [[p(escape(str(x)), 'head') for x in headers]]
    for row in rows:
        data.append([p(str(x), 'cell') for x in row])
    t = Table(data, colWidths=widths, hAlign='LEFT', repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 9),
        ('RIGHTPADDING', (0,0), (-1,-1), 9),
        ('TOPPADDING', (0,0), (-1,-1), 5 if compact else 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5 if compact else 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [LIGHT, colors.white]),
        ('LINEBELOW', (0,0), (-1,0), .6, NAVY),
        ('LINEBELOW', (0,1), (-1,-1), .35, LINE),
    ]))
    story.extend([t, Spacer(1, 9)])


def note(title, text):
    t = Table([[p(f'<b>{title}</b><br/>{text}', 'body')]], colWidths=[CW])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT),
        ('LINEBEFORE', (0,0), (0,0), 3, TEAL),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING', (0,0), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.extend([t, Spacer(1, 10)])


class CacheDiagram(Flowable):
    def __init__(self):
        super().__init__()
        self.width, self.height = CW, 158

    def draw(self):
        c = self.canv
        def box(x, y, w, h, title, line):
            c.setFillColor(LIGHT); c.setStrokeColor(LINE)
            c.roundRect(x,y,w,h,6,fill=1,stroke=1)
            c.setFillColor(NAVY);c.setFont('BodyBold',10)
            c.drawCentredString(x+w/2,y+h-18,title)
            c.setFont('Body',9);c.setFillColor(MUTED)
            c.drawCentredString(x+w/2,y+13,line)
        box(104,104,CW-208,48,'Fixed model weights','Unlearning happened before deployment')
        c.setStrokeColor(TEAL);c.setLineWidth(1.3)
        for x in [CW/4,3*CW/4]:
            c.line(CW/2,104,x,77)
            c.line(x,77,x,64)
            c.line(x,64,x-3,70);c.line(x,64,x+3,70)
        box(0,10,CW/2-8,50,'Ordinary cache','Store and read at model precision')
        box(CW/2+8,10,CW/2-8,50,'Quantized stored cache','Compress, then reconstruct on read')


read = lambda path: json.loads((ROOT / path).read_text())
counts = read('results/day3/day3_20261019T213839883909Z/manual-review/acceptance.json')['counts']
utility = read('results/day4/day4_20261020T103718004368Z/artifact-review.json')['descriptive_correctness_counts']
d5 = read('results/day5/day5_20261020T110711928957Z/summary.json')
d6 = read('results/day6/day6_20261020T130635380188Z/artifact-review.json')
GITHUB = 'https://github.com/vedtod07/kv-cache-unlearning'

# 1: repository first, as requested; no cover page hides the map.
section(1, 'Repository structure', 'KV-cache unlearning research | Progress through 20 October 2026 | Prepared for external review')
add('This report explains the repository first, then the research question, completed work, measured results and remaining decisions. The six "days" are workflow stages completed across 19-20 October, rather than six independent experimental replications.')
add(f'Repository: <link href="{GITHUB}" color="#007C83">github.com/vedtod07/kv-cache-unlearning</link>. The local checkout folder is named <b>repo-review</b>. Paths below are relative to that checkout.')
tree = '''kv-cache-unlearning/
  README.md, CONTRIBUTING.md, .gitignore
  requirements-week1.txt
  configs/             Configuration placeholder
  docs/                Protocol, plans, decisions and reviews
  notebooks/           Six staged Colab GPU notebooks
  scripts/             Diagnostics, validation and this PDF builder
  tests/               Automated regression and CPU checks
  results/             Inputs, outputs, annotations and evidence
  output/pdf/          This generated reviewer report'''
story.append(Preformatted(tree, styles['mono']));story.append(Spacer(1,10))
table(['Folder / file','How a reviewer should use it'],[
    ('README.md','Start with the project question, status and navigation links.'),
    ('docs/','Understand the intended methods and distinguish plans from completed evidence.'),
    ('notebooks/','See the exact step-by-step GPU workflow used by Person A.'),
    ('scripts/ and tests/','Inspect implementation and what the automated checks cover.'),
    ('results/','Audit exact inputs, configurations, raw responses and accepted labels.'),
], [115,CW-115])
add('The configs/ folder is currently empty. requirements-week1.txt is a candidate setup, not a complete environment lock. Use each run\'s recorded versions. Large model weights and credentials are excluded; .git/ holds internal version history.', 'small')

# 2: full functional inventory.
section(2, 'What is inside each folder?', 'A navigation guide to the files that matter for review')
table(['Documentation','Purpose'],[
    ('BLUEPRINT.md; REVIEW_CHANGES.md','Research design and rationale for protocol revision v4.'),
    ('WORK_SPLIT.md; NINE_WEEK_PLAN.md; WEEK1_DETAILED.md','Roles, planned sequence and original first-week tasks.'),
    ('PERSON_A_WEEK1_WALKTHROUGH.md; week1_setup_cells.md','Practical instructions; the walkthrough records actual progress.'),
    ('VALIDATION.md; PILOT_CRITERIA.md','Engineering requirements and draft pilot/confirmation gates.'),
    ('DECISIONS.md; LOG.md','Decision history and append-only run/review history.'),
    ('FIVE_DAY_PROGRESS_DIFF.md; INTRODUCTION_DRAFT.md','Earlier progress explanation and a provisional paper introduction.'),
], [224,CW-224])
table(['Implementation','Purpose'],[
    ('test_kv_scoring_path.py','B\'s original fixed-token cache diagnostic.'),
    ('day6_integration.py','Adds explicit masks, prefill and attention tracing, plus generation replay.'),
    ('gate_checks.py; validate_results.py','Check diagnostic gates and the intended research-result record schema.'),
    ('liveness_test.py; build_progress_pdf.py','Compatibility alias for the diagnostic; generator for this report.'),
], [224,CW-224])
add('<b>tests/:</b> test_gate_checks.py and test_results_contract.py check gates and records. test_day6_integration.py adds optional CPU tests with a tiny random Llama. These local tests cannot establish CUDA/HQQ correctness on their own.')
add('<b>notebooks/:</b> person_a_week1_day1.ipynb through day6.ipynb implement the six stages described on page 4. The notebooks keep runnable source; returned GPU outputs live in results/.')
add('<b>results/:</b> day1/ to day6/ contain timestamped returned runs. day4-preparation/, day5-preparation/ and day6-preparation/ freeze upload inputs. day2/ also holds the day-three input bundle. diagnostics/ contains B\'s separate HQQ reports. results/README.md defines the target research schema.')
add('Inside a run, look for manifest.json, environment or pip-freeze files, fixtures/token IDs, output JSONL, and artifact-review.json. manual-review/ keeps original/proposed/accepted annotations and acceptance.json. DAY5_REVIEW.md and DAY6_REVIEW.md explain important diagnostics. Earlier "pending" text in raw snapshots records the status at creation; later acceptance/review records establish current status.', 'small')

# 3: research in plain language.
section(3, 'What are we researching?', 'A deployment-durability question about an already-unlearned model')
add('A language model can learn information during training. <b>Weight-based unlearning</b> changes the model parameters so that selected information is less readily disclosed. Our question is whether that behavior survives an ordinary inference-time deployment change: compressing the stored KV cache.')
story.append(CacheDiagram())
table(['Term','Plain-language meaning'],[
    ('Model weights','The trained parameters. We hold them fixed within each cache comparison.'),
    ('KV cache','Temporary per-layer key/value tensors that let the model reuse earlier context while generating later tokens.'),
    ('Quantization','Representing those stored tensors approximately with fewer bits. They are reconstructed when read.'),
    ('Prefill / decoding','Process the prompt first; then generate subsequent tokens using the stored context.'),
], [110,CW-110])
heading('Two connected questions')
add('<b>Factual durability:</b> does compression increase correct disclosure of forgotten facts while retained performance stays useful?<br/><b>Evaluation validity:</b> can a one-pass probability audit miss changes that occur during real sequential cache use?')
note('Precision matters','INT4 or INT2 names the cache quantization setting. The model weights can remain FP32, and the cache implementation also keeps metadata and a residual full-precision buffer. Memory savings and deployment speed have not been measured here.')
add('The intended contribution is a controlled empirical audit and a reproducible evaluation artifact. Actual forgotten-fact recovery, statistical generalization and literature priority remain unestablished. The current evidence develops the measurement foundation.', 'small')

# 4: workflow / purpose.
section(4, 'The completed workflow', 'Six stages, each resolving a different source of uncertainty')
table(['Stage','Goal and purpose','Completed evidence'],[
    ('1. GPU setup','Confirm model, tokenizer, dataset and hardware work together.','One real TOFU response with provenance and token IDs.'),
    ('2. Full vs retain','Establish learned behavior and a retain-only reference.','40 generations on the same 20 forgotten-author questions.'),
    ('3. Unlearned candidate','Measure ordinary-cache behavior before applying compression.','20 SimNPO generations; accepted three-model annotation table.'),
    ('4. Utility screen','Check whether poor forgotten-author answers reflect broad task failure.','180 generations on a frozen 60-item/model sample.'),
    ('5. Source-helper integration','Validate upstream scoring inputs, boundaries and masks.','60 model-item pairs; 120 generations across two masks.'),
    ('6. Cache integration','Verify storage/readback, prefill, sequential scoring and generation.','28 checks passed on artificial fixtures with real HQQ.'),
], [95,205,CW-300])
heading('Models and data')
add('The common family is <b>Llama-3.2-1B-Instruct</b>. The full model was fine-tuned on all TOFU authors; retain90 was trained on the retained subset; the SimNPO candidate was unlearned from a full model. TOFU provides synthetic author biographies and question-answer pairs. The forgotten development sample is 20 related questions about one exposed author, Hsiao Yun-Hwa.')
add('SimNPO is a preselected engineering candidate. The planned research core still calls for NPO and RMU checkpoints, with full and retain-only references under the same cache conditions. Checkpoints should be selected from baseline compatibility/forgetting/utility evidence, rather than searching for a favorable compression effect.')
heading('Who owns the work?')
add('<b>Person A (Vedant):</b> provenance, evaluation protocol, baselines, annotation, analysis and review of cache evidence.<br/><b>Person B:</b> cache implementation and sequential scoring; independent checks of A\'s measurements. Scientific decisions are shared. AI assistance is recorded; authors remain responsible for labels, claims and sign-off.')

# 5: accepted baseline results.
section(5, 'Days 1-3: establish the baseline', 'What the models answered before any cache quantization [A1-A3]')
heading('Day 1: the first working example')
add('The full model correctly returned "Hsiao Yun-Hwa" for a name question. The prompt had <b>70 tokens</b>; the response had <b>14 tokens including EOS</b> and took <b>3.742 seconds</b>. This confirmed setup on that example and led us to reserve this author for development.')
heading('Days 2-3: the same 20 questions, three models')
headers = ['Accepted label','Full','Retain90','SimNPO']
rows = [[label.title(),*[str(counts[m].get(label,0)) for m in ('full','retain90','unlearned')]]
        for label in ('correct','partial','incorrect','ambiguous')]
table(headers, rows + [['Total','20','20','20']], [200,102,102,CW-404])
add('All 40 day-two full/retain outputs ended with EOS below 64 tokens. SimNPO completed 20 records; one response reached the shared 64-token limit. That response remains in the sample. Its two correct targets were a binary "yes" relation and English as the language, which provide limited evidence of detailed biographical recall.')
heading('Why semantic review was necessary')
add('The full model matched the reference text literally on 13/20 questions; retain90 matched on 0/20. Human-reviewed semantic labels instead found 16 and 3 correct answers. Valid paraphrases and concise answers should count, while a matching entity name inside a wrong relationship should not.')
add('<b>Reference problems:</b> a gender question has an LGBTQ+ membership reference, so it stays ambiguous. A non-exhaustive book/award reference does not prove every alternative impossible. Check whether the requested target is already supplied by the prompt.')
add('<b>Answer problems:</b> partial, contradictory and truncated responses need explicit rubric rules. Preserve all 20 items in the denominator and report partial/ambiguous categories separately.')
note('What these counts establish','They describe one selected development author. Reduced disclosure alone does not establish successful unlearning. A accepted the AI-assisted revised labels; independent B annotation remains pending.')

# 6: utility screen.
section(6, 'Day 4: check useful performance', 'A frozen development screen of retained and general questions [A4]')
add('SimNPO\'s forgotten-author answers often showed awkward gender/leadership drift. We tested retained and general questions to determine whether the same problem appeared broadly in a small sample. The sample was chosen before outputs were inspected.')
rows=[]
for split,label,n in [('retain90','Retained authors',30),('real_authors','Real authors',15),('world_facts','World facts',15)]:
    rows.append([label,str(n),*[str(utility[split][m].get('correct',0)) for m in ('full','retain90','simnpo_candidate')]])
table(['Split','Items/model','Full correct','Retain90 correct','SimNPO correct'],rows,[139,83,94,98,CW-414])
add('Full and retain90 each had one additional <b>partial</b> retained answer. All <b>180 outputs</b> completed with EOS, with no token-budget hits. All were assessed as coherent answer attempts; each model had one off-topic or partly off-topic response.')
heading('What we learned')
add('The selected sample does not show pervasive general incoherence. It supports continuing with the engineering candidate. It does not establish representative retained accuracy, privacy, safety or preserved general utility.')
heading('What limits this result')
add('The 30 retained questions cover ten authors, three questions each. Those authors came from sixteen conservatively name-verified eligible groups. This is a restricted development sample, rather than a representative sample of all retained authors. The real-author and world-fact questions use open-ended generation. The screen is not the official OpenUnlearning model_utility metric.')
heading('Important review decisions')
add('Correctness is separate from fluency and response behavior. An answer can be readable but wrong. A binary answer may satisfy the requested relation while adding unsupported details. Some references describe unavailable information; saying the detail is unknown may itself be the correct response. Theme lists can be partial. The longest-river item is flagged for a measurement convention, and the Statue of Liberty item requires the correct donor/recipient relationship.')
note('Annotation provenance','Initial labels were AI-assisted drafts, subsequently reviewed and accepted by Vedant. Original drafts, accepted files and acceptance hashes are kept separately. These do not count as two independent human raters; B\'s review is pending.')

# 7: source helper and masking.
section(7, 'Day 5: find an evaluation confound', 'A mask convention changes responses even before compression [A5]')
add('We ran the actual pinned OpenUnlearning preprocessor, collator, probability helper and ROUGE helper. The direct harness used the same exposed 20 questions for all three models. It is narrower than a full benchmark/CLI reproduction.')
heading('The padding/EOS collision')
add('The collator sets attention visibility by testing whether each token differs from the padding ID. Here the padding ID equals the genuine end-of-turn marker ID, <b>128009</b>. Even in an unpadded prompt, the system and user end-of-turn markers receive zero masks. In the first example these are positions 31 and 65, counting from zero.')
table(['Model','Text changed when only the mask changed','All-ones outputs match prior token IDs'],[
    [label,f'{d5[key]["changed_generation_count"]}/20','20/20']
    for key,label in [('full','Full'),('retain90','Retain90'),('simnpo_candidate','SimNPO')]
], [92,230,CW-322])
table(['Model','Stock mean probability','All-ones mean probability','Stock / all-ones ROUGE-L recall'],[
    [label,f'{d5[key]["stock_mask_mean_prob"]:.5f}',f'{d5[key]["all_ones_mean_prob"]:.5f}',
     f'{d5[key]["stock_mask_mean_rougeL_recall"]:.5f} / {d5[key]["all_ones_mean_rougeL_recall"]:.5f}']
    for key,label in [('full','Full'),('retain90','Retain90'),('simnpo_candidate','SimNPO')]
], [82,133,133,CW-348])
add('<b>Probability definition:</b> for each answer, exp(-mean target-token cross entropy), including EOS; the table averages that quantity across questions. It is not the probability of the whole answer or the percentage of correct answers. ROUGE is lexical overlap. Changed text may be a paraphrase or another hallucination.')
heading('Correction and achievement')
add('Use explicit all-ones masks for genuine unpadded tokens. Future padding masks must follow actual sequence lengths. Apply one policy across models, cache conditions, generation and scoring. Keep the stock condition separately named. All <b>60 all-ones generations reproduced earlier text and token IDs exactly</b>, supporting the baseline\'s reproducibility.')
add('This run used ordinary caches only. The mask observation applies to this inspected source/tokenizer path. Stock FP16 helper reductions also differ slightly from an independent FP32 reduction; the largest observed mean-NLL gap was 0.003626. New primary scoring uses an explicit FP32 reduction.', 'small')

# 8: day six controls and actual numerical results.
section(8, 'Day 6: validate the real cache path', 'The programmed checks passed on T4 with FP32 weights and HQQ [A6]')
add('The short and long artificial prompts contain 50 and 330 tokens. Both score the same nine answer tokens, including terminal EOS. The run uses Torch 2.9.1+cu128, Transformers 5.5.4, HQQ 0.2.8.post1, SDPA, axes 1/1, group size 64 and residual length 128.')
table(['Control','Observed result'],[
    ('Ordinary sequential vs parallel','Maximum absolute token-NLL gap: 0.00003052.'),
    ('Identity wrapper; instrumentation','Zero score difference on both fixtures and both bitwidths.'),
    ('Empty quantized-cache parallel pass','Exactly matches ordinary parallel scores for INT4 and INT2.'),
    ('Cache-to-attention trace','Reconstructed K/V reaches the SDPA interface in all 16 layers.'),
    ('One-token fixture','Zero decode reads; the score comes from prompt prefill.'),
    ('Fresh-cache repeat; generation replay','Saved repeat deltas are zero; all replay argmax tokens match generation.'),
], [200,CW-200])
heading('Sequential readback changes later token scores')
rows=[]
for name in ('short','long'):
    for bits in ('4','2'):
        q=d6['per_fixture'][name]['quantized'][bits]
        rows.append([name.title(),f'INT{bits}',f'{q["mean_nll_delta"]:+.5f}',f'{q["max_abs_token_nll_delta"]:.5f}'])
table(['Fixture','Cache','Mean NLL change','Largest absolute token change'],rows,[100,80,145,CW-325])
add('NLL is negative log probability: a lower value means the reference token is more likely. Changes are quantized minus ordinary sequential NLL. Every first-token change is zero, because its prediction precedes cache readback. Later changes can be large even when their mean nearly cancels, as in short INT2.')
note('The supported mechanism','For this implementation, a full parallel forward starting from an empty quantized cache can miss score changes that occur during sequential reads. This is a scoped engineering result on artificial prompts. It does not demonstrate forgotten-fact recovery or establish novelty on its own.')
add('All 28 checks passed. Twenty-five recompute from saved score/trace fields; three repeat checks save deltas without the repeat\'s raw NLL vectors. Runtime equality/identity assertions are archived, rather than full K/V tensors. Provisional tolerances were not enlarged to obtain a pass.', 'small')

# 9: B and generation with practical issues.
section(9, 'Generation and B\'s diagnostics', 'Additional engineering evidence and the problems encountered [A6, B1]')
table(['Day-six cache','Generated response / termination'],[
    ('Ordinary','"It\'s a sunny day outside with a gentle breeze blowing." 13 tokens; EOS.'),
    ('INT4','"It\'s a beautiful day outside with a gentle breeze blowing." 13 tokens; EOS.'),
    ('INT2','"It\'s a bit of a forecast: Sunny skies are forecasted for the upcoming week, bringing a usual sense of optimism" 24 tokens; budget reached without EOS.'),
], [90,CW-90])
add('All three generated sequences match teacher-forced greedy replay under the same policy. The INT2 truncation stays in the record; it is not a runtime failure or evidence of global collapse.')
heading('Person B\'s separate artificial-fixture reports')
table(['Configuration','Gate','Mean NLL change'],[
    ('Short INT4, residual 128, FP16','Failed ordinary-path tolerance','-0.19298'),
    ('Short INT4, residual 128, FP32','Passed','-0.18206'),
    ('Repeat of previous FP32 condition','Passed; identical recorded traces','-0.18206'),
    ('Short INT4, residual 4, FP32','Passed','-0.19862'),
    ('Short INT4, residual 1, FP32','Passed','-0.13386'),
    ('Short INT2, residual 0, FP32','Passed','+1.48055'),
    ('Long INT4, residual 128, FP32','Passed','-0.16105'),
], [257,143,CW-400])
add('These are B\'s fixture results, not additional TOFU observations. His prompt/template differs from A\'s. His FP16 ordinary-path gap was about 0.01555; FP32 reduced it to about 0.00004578 on the short fixture. This motivated FP32 integration before interpreting a cache effect.')
add('<b>Setup problems:</b> mismatched torchvision/torchaudio broke imports; a bare CUDA device needed an index; the attempted Quanto extension build used instructions unavailable on T4; HQQ ran. The first runtime was reset and reports were lost, so the seven committed files are explicitly regenerated runs. Original device/Quanto failures remain log-only evidence.', 'small')
add('<b>Residual-buffer lesson:</b> the inspected implementation\'s flush/reset behavior means residual zero cannot simply be described as quantizing every new token immediately. Exact placement, buffering and readback must be reported. Neither B\'s reports nor day six measured deployment throughput or memory savings.', 'small')

# 10: conclusions with limits and next work.
section(10, 'Achievements and next work', 'How a reviewer should interpret the current state')
table(['We have established','What remains open'],[
    ('Traceable ordinary-cache baselines and accepted development labels.','Independent annotation/adjudication and more than one forgotten author.'),
    ('A restricted retained/general utility screen.','Paired quantized utility and a defensible final sample/utility criterion.'),
    ('A mask confound and exact reproduction under the ordinary valid-token policy.','Padding/position checks before multi-example batching.'),
    ('Real reconstructed cache values reach attention; scoring/generation controls pass in the tested FP32 setup.','All model roles on integrated TOFU; FP16 validation if that dtype is later used.'),
    ('Scoped parallel-prefill versus sequential-readback disagreement.','Whether it changes correct forgotten-fact disclosure and the substantive audit conclusion.'),
], [CW/2,CW/2])
heading('The next experiment')
add('<b>1. Shared baseline:</b> run full, retain90 and the selected SimNPO candidate on existing exposed TOFU fixtures under the day-six environment, fixed template and 64-token policy. Re-review outputs that differ from earlier FP16 results; both Torch and precision changed.')
add('<b>2. Paired development comparison:</b> compare ordinary and INT4 caches with the same questions, weights, references and utility samples. Keep INT2 as a declared stress condition. Record all errors and truncations. Do not tune settings to obtain recovery.')
add('<b>3. Freeze the research protocol:</b> finalize NPO/RMU checkpoint choices, confirmation authors, numerical and utility criteria, effect sizes of interest, budget and analysis rules before untouched confirmation evaluation.')
heading('What a successful paper must measure')
add('The primary outcome is the change in <b>correct forgotten-fact disclosure</b> from an unlearned checkpoint. Report the retain-only reference\'s change alongside it: reference deterioration can make an adjusted result look favorable. Preserve fixed denominators and both directions of answer changes. Log probabilities and ROUGE support analysis but cannot substitute for factual labels.')
add('Questions from one TOFU author are related. Final uncertainty should respect author clusters, rather than treating every question as independent. A nonsignificant result does not establish equivalence. Positive recovery is not a readiness requirement; a well-controlled null remains a legitimate outcome.', 'small')

# 11: technical provenance and evidence sources.
section(11, 'Evidence, provenance and review notes', 'Source identifiers used throughout this report')
table(['Role','Checkpoint suffix / immutable revision'],[
    ('Full','tofu_Llama-3.2-1B-Instruct_full<br/><font name="Mono" size="7.8">88e31200b97e4c0c04ae0d2f0b591f427046d192</font>'),
    ('Retain90','tofu_Llama-3.2-1B-Instruct_retain90<br/><font name="Mono" size="7.8">7114300c0049527a71833f5683965c358ad9dcbf</font>'),
    ('SimNPO','unlearn_tofu_Llama-3.2-1B-Instruct_forget10_SimNPO_lr2e-05_b4.5_a1_d1_g0.125_ep10<br/><font name="Mono" size="7.8">444648425d9c8a3926683f1870e364c5fe0b1357</font>'),
], [80,CW-80])
add('All checkpoint IDs use the <b>open-unlearning/</b> namespace. Dataset: locuslab/TOFU at revision <font name="Mono" size="8">324592d84ae4f482ac7249b9285c2ecdb53e3a68</font>. Upstream source: locuslab/open-unlearning at <font name="Mono" size="8">b29929067732c40ee4ca58d5cc1d3c11fcf37de1</font>.', 'small')
sources = [
    ('A1','Day 1 setup and first generation','results/day1/day1_20261019T115813495741Z/artifact-review.json'),
    ('A2','Day 2 accepted labels','results/day2/day2_20261019T122314559618Z/manual-review/acceptance.json'),
    ('A3','Day 3 accepted three-model counts','results/day3/day3_20261019T213839883909Z/manual-review/acceptance.json'),
    ('A4','Day 4 results and later acceptance','results/day4/day4_20261020T103718004368Z/'),
    ('A5','Day 5 source-helper and mask review','results/day5/day5_20261020T110711928957Z/DAY5_REVIEW.md'),
    ('A6','Day 6 GPU artifact review','results/day6/day6_20261020T130635380188Z/'),
    ('B1','B reports and environment','results/diagnostics/'),
]
rows=[]
for key,label,path in sources:
    # Day-six working files were not part of the last published snapshot.
    desc = f'<b>{label}</b><br/>{escape(path)}'
    if key != 'A6':
        url=f'{GITHUB}/tree/da45630403bbcdd49123560f8467f809cb41992c/{path}'
        desc += f'<br/><link href="{url}" color="#007C83">Open published evidence</link>'
    else:
        desc += '<br/>Reviewed from the local working copy; share these artifacts separately if requested.'
    rows.append([key,desc])
table(['ID','Where to inspect the evidence'],rows,[44,CW-44],compact=True)
add('Snapshot: reviewed working copy through day six; last published commit da45630. Day-six additions were local. Historical raw status fields remain preserved. AI-assisted labels were accepted by A where stated; independent B review and joint sign-off are pending. This report adds no new novelty search or venue-acceptance assessment.', 'small')


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE);canvas.setLineWidth(.5)
    canvas.line(M,H-33,W-M,H-33)
    canvas.setFont('Body',8);canvas.setFillColor(MUTED)
    canvas.drawString(M,H-25,'KV CACHE UNLEARNING | RESEARCH PROGRESS')
    canvas.drawRightString(W-M,H-25,'20 OCTOBER 2026')
    canvas.line(M,34,W-M,34)
    canvas.drawString(M,21,'Vedant / Person A | AI-assisted preparation | Development evidence')
    canvas.drawRightString(W-M,21,f'{doc.page} / 11')
    canvas.restoreState()


doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=M, rightMargin=M,
                        topMargin=49, bottomMargin=45,
                        title='KV Cache Unlearning: Research Progress and Repository Guide',
                        author='Vedant - Person A; Codex-assisted preparation',
                        subject='Goals, repository structure, six workflow stages, results and remaining work')
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT)
