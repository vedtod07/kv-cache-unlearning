"""Render the 23 October repository audit from its Markdown source."""
from pathlib import Path
import re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate,Paragraph,Table,TableStyle,Spacer,KeepTogether,PageBreak

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'docs/REPOSITORY_PROGRESS_REVIEW_2026-10-23.md'
OUT=ROOT/'output/pdf/KV_Cache_Unlearning_Repository_Review_2026-10-23.pdf'
OUT.parent.mkdir(parents=True,exist_ok=True)
fontdir=Path('/System/Library/Fonts/Supplemental')
for name,file in [('Review','Arial.ttf'),('ReviewBold','Arial Bold.ttf'),('ReviewItalic','Arial Italic.ttf'),('ReviewMono','Courier New.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(fontdir/file)))
pdfmetrics.registerFontFamily('Review',normal='Review',bold='ReviewBold',italic='ReviewItalic')
navy=colors.HexColor('#193149');teal=colors.HexColor('#007D83');muted=colors.HexColor('#536474')
light=colors.HexColor('#EFF5F7');line=colors.HexColor('#D9E3E8')
W,H=A4;M=45;CW=W-2*M
styles={
    'title':ParagraphStyle('title',fontName='ReviewBold',fontSize=23,leading=28,textColor=navy,spaceAfter=12),
    'h2':ParagraphStyle('h2',fontName='ReviewBold',fontSize=14,leading=18,textColor=teal,spaceBefore=13,spaceAfter=8,keepWithNext=True),
    'body':ParagraphStyle('body',fontName='Review',fontSize=10.1,leading=14.1,textColor=navy,spaceAfter=8),
    'small':ParagraphStyle('small',fontName='Review',fontSize=9,leading=12.5,textColor=muted,spaceAfter=8),
    'cell':ParagraphStyle('cell',fontName='Review',fontSize=9.0,leading=11.8,textColor=navy),
    'head':ParagraphStyle('head',fontName='ReviewBold',fontSize=9.0,leading=11.8,textColor=colors.white),
}


def html(text):
    text=text.replace('\u2011','-').replace('\u2013','-').replace('\u2014','-')
    text=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',lambda m:m[1],text)
    text=escape(text)
    text=re.sub(r'`([^`]+)`',r'<font name="ReviewMono" size="8.8">\1</font>',text)
    return re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',text)


def para(text,style='body'):
    return Paragraph(html(text),styles[style])


def make_table(lines):
    rows=[[x.strip() for x in ln.strip().strip('|').split('|')] for ln in lines]
    rows=[row for row in rows if not all(re.fullmatch(r'[-: ]+',x) for x in row)]
    cols=len(rows[0])
    if cols==2:widths=[CW*.35,CW*.65]
    elif cols==3:widths=[CW*.42,CW*.29,CW*.29]
    elif cols==4:widths=[CW*.40]+[CW*.20]*3
    elif cols==5:widths=[CW*.36]+[CW*.16]*4
    else:widths=[CW/cols]*cols
    data=[[para(x,'head' if i==0 else 'cell') for x in row] for i,row in enumerate(rows)]
    table=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
    table.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),navy),('ROWBACKGROUNDS',(0,1),(-1,-1),[light,colors.white]),
        ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
        ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
        ('LINEBELOW',(0,0),(-1,-1),.35,line),
    ]))
    return table


def body_flow(lines):
    result=[];i=0
    while i<len(lines):
        s=lines[i].strip()
        if not s:i+=1;continue
        if s.startswith('|'):
            tablelines=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                tablelines.append(lines[i]);i+=1
            result.extend([make_table(tablelines),Spacer(1,9)]);continue
        if s.startswith('- '):result.append(para('- '+s[2:]));i+=1;continue
        paragraph=[s];i+=1
        while i<len(lines) and lines[i].strip() and not lines[i].strip().startswith(('|','- ')):
            paragraph.append(lines[i].strip());i+=1
        text=' '.join(paragraph)
        result.append(para(text,'small' if text.startswith('Prepared ') else 'body'))
    return result


lines=SOURCE.read_text().splitlines();story=[]
assert lines[0].startswith('# ')
story.append(para(lines[0][2:],'title'))
end=next(i for i,line in enumerate(lines[1:],1) if line.startswith('## '))
story+=body_flow(lines[1:end])
i=end
while i<len(lines):
    assert lines[i].startswith('## ')
    title=lines[i][3:];i+=1;start=i
    while i<len(lines) and not lines[i].startswith('## '):i+=1
    flows=[para(title,'h2')]+body_flow(lines[start:i])
    if not title.startswith('1. '):story.append(PageBreak())
    story+=flows


def page(canvas,doc):
    canvas.saveState();canvas.setStrokeColor(line);canvas.setLineWidth(.5)
    canvas.line(M,H-33,W-M,H-33);canvas.line(M,33,W-M,33)
    canvas.setFont('Review',8);canvas.setFillColor(muted)
    canvas.drawString(M,H-24,'KV CACHE UNLEARNING | REPOSITORY REVIEW')
    canvas.drawRightString(W-M,H-24,'23 OCTOBER 2026')
    canvas.drawString(M,21,'Evidence review | Remote cf5c7f3 + identified local artifacts')
    canvas.drawRightString(W-M,21,str(doc.page));canvas.restoreState()

doc=SimpleDocTemplate(str(OUT),pagesize=A4,leftMargin=M,rightMargin=M,topMargin=48,bottomMargin=45,
    title='KV Cache Unlearning - Repository Progress Review',author='Vedant; Codex-assisted preparation',
    subject='Repository structure, achievements, verified results, methodological review and next work')
doc.build(story,onFirstPage=page,onLaterPages=page)
print(OUT)
