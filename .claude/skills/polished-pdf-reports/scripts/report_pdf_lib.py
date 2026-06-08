"""Kabashi report — enhanced PDF library with visual layout primitives.

Extends the CrossDisease report_pdf_lib with:

  <<PAGEBREAK>>                      explicit page break
  [KEYSTAT|<stat>|<label>|<context>]  big-number callout
  [STATUS|<color>|<label>] body       coloured status badge with body
  [BOX|<color>|<title>] ... [/BOX]    multi-line coloured summary card
  [QUESTION|<id>|<title>] body        styled open-question card

Also automatically:
  - Page-breaks before H1 (## in markdown)
  - Wraps each H3 finding with its image and callouts in a KeepTogether
"""
from __future__ import annotations

import sys as _sys
try:
    _sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    _sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import os
import re
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer,
    Table, TableStyle, HRFlowable, KeepTogether,
)


# ──────────────────────────────────────────────────────────────────────────────
# Palette
# ──────────────────────────────────────────────────────────────────────────────
HEADER_BG        = HexColor('#d5f5e3')
ROW_ALT_1        = HexColor('#ffffff')
ROW_ALT_2        = HexColor('#f5fafe')
GRID_COLOR       = HexColor('#d5dbdb')
HEADING_COLOR    = HexColor('#1e272e')
SUBHEADING_COLOR = HexColor('#636e72')
BODY_COLOR       = HexColor('#2d3436')
ACCENT_GREEN     = HexColor('#27ae60')
ACCENT_BLUE      = HexColor('#2874a6')
ACCENT_RED       = HexColor('#c0392b')
ACCENT_AMBER     = HexColor('#e67e22')
ACCENT_PURPLE    = HexColor('#8e44ad')
FOOTER_COLOR     = HexColor('#999999')

COLOR_MEDICAL = ACCENT_RED
COLOR_DS      = ACCENT_BLUE
COLOR_LAY     = ACCENT_GREEN
COLOR_DATA    = ACCENT_AMBER

STATUS_COLORS = {
    'green':  (ACCENT_GREEN,  HexColor('#eaf7f0')),
    'amber':  (ACCENT_AMBER,  HexColor('#fdf2e7')),
    'red':    (ACCENT_RED,    HexColor('#fbeae9')),
    'blue':   (ACCENT_BLUE,   HexColor('#eaf3fa')),
    'purple': (ACCENT_PURPLE, HexColor('#f4ebfa')),
    'gray':   (HexColor('#7f8c8d'), HexColor('#f4f6f6')),
}


# ──────────────────────────────────────────────────────────────────────────────
# Style sheet
# ──────────────────────────────────────────────────────────────────────────────
def _build_styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle('DocTitle', parent=s['Title'], fontSize=24, leading=28,
                         textColor=HEADING_COLOR, spaceAfter=10, alignment=TA_LEFT))
    s.add(ParagraphStyle('DocSubtitle', parent=s['Title'], fontSize=13, leading=17,
                         textColor=SUBHEADING_COLOR, spaceAfter=6, alignment=TA_LEFT,
                         fontName='Helvetica'))
    s.add(ParagraphStyle('DocMeta', parent=s['Normal'], fontSize=9, leading=12,
                         textColor=SUBHEADING_COLOR, spaceAfter=2, alignment=TA_LEFT))
    s.add(ParagraphStyle('H1', parent=s['Heading1'], fontSize=18, leading=22,
                         textColor=HEADING_COLOR, spaceBefore=10, spaceAfter=10,
                         fontName='Helvetica-Bold'))
    s.add(ParagraphStyle('H2', parent=s['Heading2'], fontSize=13, leading=17,
                         textColor=ACCENT_GREEN, spaceBefore=12, spaceAfter=6,
                         fontName='Helvetica-Bold'))
    s.add(ParagraphStyle('H3', parent=s['Heading3'], fontSize=11, leading=14,
                         textColor=HEADING_COLOR, spaceBefore=10, spaceAfter=4,
                         fontName='Helvetica-Bold'))
    s.add(ParagraphStyle('Bd', parent=s['Normal'], fontSize=10, leading=14,
                         textColor=BODY_COLOR, spaceAfter=6, alignment=TA_LEFT))
    s.add(ParagraphStyle('TC', parent=s['Normal'], fontSize=8, leading=10.5,
                         textColor=BODY_COLOR))
    s.add(ParagraphStyle('TH', parent=s['Normal'], fontSize=8, leading=10.5,
                         textColor=black, fontName='Helvetica-Bold'))
    s.add(ParagraphStyle('Cap', parent=s['Normal'], fontSize=8.5, leading=11,
                         textColor=SUBHEADING_COLOR, spaceAfter=10, alignment=TA_CENTER,
                         fontName='Helvetica-Oblique'))
    s.add(ParagraphStyle('Quote', parent=s['Normal'], fontSize=10, leading=14,
                         textColor=SUBHEADING_COLOR, spaceAfter=8,
                         leftIndent=14, fontName='Helvetica-Oblique'))
    return s


styles = _build_styles()


# ──────────────────────────────────────────────────────────────────────────────
# Unicode normalisation
# ──────────────────────────────────────────────────────────────────────────────
ASCII_MAP = {
    '×':'x','÷':'/','±':'+/-','≤':'<=','≥':'>=','≠':'!=','≈':'~=',
    '→':'-&gt;','←':'&lt;-','↑':'^','↓':'v',
    'α':'&#945;','β':'&#946;','γ':'&#947;','δ':'&#948;','κ':'&#954;','λ':'&#955;',
    'μ':'&#956;','π':'&#960;','σ':'&#963;','τ':'&#964;','φ':'&#966;','ω':'&#969;',
    'Δ':'&#916;','Σ':'&#931;','Ω':'&#937;','ρ':'&#961;',
    '−':'&#8722;','–':'&#8211;','—':'&#8212;',
    '‘':"'",'’':"'",'“':'"','”':'"',
    '…':'...', '•':'&bull;', '·':'.', ' ':' ',
    '✓':'[OK]', '✗':'[X]',
}
SUPER_MAP = {'⁰':'0','¹':'1','²':'2','³':'3','⁴':'4','⁵':'5','⁶':'6','⁷':'7','⁸':'8','⁹':'9','⁻':'-','⁺':'+'}


def _wrap_super(text):
    out, i = [], 0
    while i < len(text):
        if text[i] in SUPER_MAP:
            j, run = i, []
            while j < len(text) and text[j] in SUPER_MAP:
                run.append(SUPER_MAP[text[j]]); j += 1
            out.append('<super>' + ''.join(run) + '</super>'); i = j
        else:
            out.append(text[i]); i += 1
    return ''.join(out)


def normalize_unicode(text):
    text = _wrap_super(text)
    for src, dst in ASCII_MAP.items():
        text = text.replace(src, dst)
    out = []
    for ch in text:
        if ord(ch) < 128 or ch in '<>&':
            out.append(ch)
        else:
            out.append('?')
    return ''.join(out)


def safe(t: str) -> str:
    """Escape HTML, normalise unicode, restore allowed inline tags."""
    t = normalize_unicode(t)
    t = t.replace('&amp;amp;', '&amp;')   # idempotent
    # Don't double-escape entity refs we just inserted (#945 etc.)
    # Strategy: replace & with &amp; only where it's not followed by # or letters+;
    t = re.sub(r'&(?![a-zA-Z]+;|#\d+;|#x[0-9a-fA-F]+;)', '&amp;', t)
    t = t.replace('<', '&lt;').replace('>', '&gt;')
    # restore the inline html tags we want to keep
    for tag in ['b', 'i', 'u', 'sub', 'super', 'br', 'strike', 'font']:
        t = t.replace(f'&lt;{tag}&gt;', f'<{tag}>').replace(f'&lt;/{tag}&gt;', f'</{tag}>')
    # Allow <font color="..."> tags (handle both bare and entity-quoted forms)
    t = re.sub(r'&lt;font color=&quot;([^&]+)&quot;&gt;', r'<font color="\1">', t)
    t = re.sub(r'&lt;font color="([^"]+)"&gt;', r'<font color="\1">', t)
    return t


def _md_inline(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'(?<!\*)\*([^*]+?)\*(?!\*)', r'<i>\1</i>', text)
    text = re.sub(r'`(.+?)`', r'<i>\1</i>', text)
    return text


# ──────────────────────────────────────────────────────────────────────────────
# Visual block builders
# ──────────────────────────────────────────────────────────────────────────────
def add_image(story, path, caption=None, max_w=6.5*inch, max_h=3.8*inch):
    if not os.path.exists(path):
        story.append(Paragraph(safe(f"[missing figure: {path}]"), styles['Cap']))
        return None
    try:
        img = Image(str(path))
        w, h = img.imageWidth, img.imageHeight
        if w > 0 and h > 0:
            r = min(max_w/w, max_h/h, 1.0)
            img.drawWidth = w * r; img.drawHeight = h * r; img.hAlign = 'CENTER'
            elements = [Spacer(1, 4), img]
            if caption:
                elements.append(Spacer(1, 1))
                elements.append(Paragraph(safe(caption), styles['Cap']))
            story.extend(elements)
            return img
    except Exception as e:
        story.append(Paragraph(safe(f"[image error: {path}: {e}]"), styles['Cap']))
    return None


def add_table(story, headers, rows, col_widths=None):
    data = [[Paragraph(safe(str(h)), styles['TH']) for h in headers]]
    for r in rows:
        data.append([Paragraph(safe(str(c)), styles['TC']) for c in r])
    total_w = 6.5 * inch
    if col_widths is None:
        cw = [total_w / max(len(headers), 1)] * len(headers)
    else:
        # interpret as fractions
        s = sum(col_widths)
        cw = [total_w * w / s for w in col_widths]
    t = Table(data, colWidths=cw, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), HEADER_BG),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [ROW_ALT_1, ROW_ALT_2]),
        ('LINEBELOW', (0,0), (-1,0), 0.6, HexColor('#27ae60')),
        ('LINEABOVE', (0,0), (-1,0), 0.6, HexColor('#27ae60')),
        ('LINEBELOW', (0,-1), (-1,-1), 0.6, HexColor('#27ae60')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(KeepTogether([t, Spacer(1, 8)]))


def add_callout(story, label, body, color):
    body_html = _md_inline(body)
    p_label = Paragraph(safe(label), ParagraphStyle(
        'CL', parent=styles['Normal'], fontSize=8, leading=10,
        textColor=color, fontName='Helvetica-Bold', spaceAfter=2,
    ))
    p_body = Paragraph(safe(body_html), ParagraphStyle(
        'CB', parent=styles['Bd'], fontSize=9.5, leading=12.5, spaceAfter=0,
    ))
    block = Table([[p_label], [p_body]],
                   colWidths=[6.4 * inch],
                   style=TableStyle([
                       ('LINEBEFORE', (0,0), (-1,-1), 2.5, color),
                       ('LEFTPADDING', (0,0), (-1,-1), 8),
                       ('RIGHTPADDING', (0,0), (-1,-1), 4),
                       ('TOPPADDING', (0,0), (-1,-1), 1),
                       ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                   ]))
    story.append(block)
    story.append(Spacer(1, 3))


def add_keystat(story, stat: str, label: str, context: str):
    """Big-number callout: large stat | label + context wrapped to the right."""
    p_stat = Paragraph(
        f'<font color="#1e272e"><b>{safe(stat)}</b></font>',
        ParagraphStyle('KSstat', parent=styles['Normal'],
                       fontSize=24, leading=26,
                       fontName='Helvetica-Bold', alignment=TA_LEFT),
    )
    p_label = Paragraph(
        safe(label),
        ParagraphStyle('KSl', parent=styles['Normal'],
                       fontSize=10, leading=12,
                       textColor=HEADING_COLOR,
                       fontName='Helvetica-Bold', alignment=TA_LEFT,
                       spaceAfter=2),
    )
    p_ctx = Paragraph(
        safe(_md_inline(context)),
        ParagraphStyle('KSc', parent=styles['Normal'],
                       fontSize=8.5, leading=11,
                       textColor=SUBHEADING_COLOR, alignment=TA_LEFT),
    )
    inner = Table([[p_label], [p_ctx]],
                   colWidths=[4.5 * inch],
                   style=TableStyle([
                       ('LEFTPADDING', (0,0), (-1,-1), 2),
                       ('RIGHTPADDING', (0,0), (-1,-1), 0),
                       ('TOPPADDING', (0,0), (-1,-1), 0),
                       ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                   ]))
    block = Table([[p_stat, inner]],
                   colWidths=[1.7 * inch, 4.7 * inch],
                   style=TableStyle([
                       ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                       ('BACKGROUND', (0,0), (-1,-1), HexColor('#f5fafe')),
                       ('LINEBEFORE', (0,0), (0,-1), 4, ACCENT_BLUE),
                       ('LEFTPADDING', (0,0), (-1,-1), 12),
                       ('RIGHTPADDING', (0,0), (-1,-1), 8),
                       ('TOPPADDING', (0,0), (-1,-1), 8),
                       ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                   ]))
    story.append(KeepTogether([block, Spacer(1, 5)]))


def add_status(story, color: str, label: str, body: str):
    fg, bg = STATUS_COLORS.get(color, STATUS_COLORS['gray'])
    p_label = Paragraph(
        f'<font color="{'#' + fg.hexval()[2:]}"><b>{safe(label.upper())}</b></font>',
        ParagraphStyle('STl', parent=styles['Normal'],
                       fontSize=9, leading=11, alignment=TA_LEFT,
                       fontName='Helvetica-Bold', spaceAfter=3),
    )
    p_body = Paragraph(
        safe(_md_inline(body)),
        ParagraphStyle('STb', parent=styles['Normal'],
                       fontSize=10, leading=13.5,
                       textColor=BODY_COLOR, alignment=TA_LEFT),
    )
    block = Table([[p_label], [p_body]],
                   colWidths=[6.4 * inch],
                   style=TableStyle([
                       ('BACKGROUND', (0,0), (-1,-1), bg),
                       ('LINEBEFORE', (0,0), (-1,-1), 4, fg),
                       ('LEFTPADDING', (0,0), (-1,-1), 12),
                       ('RIGHTPADDING', (0,0), (-1,-1), 10),
                       ('TOPPADDING', (0,0), (-1,-1), 7),
                       ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                   ]))
    story.append(KeepTogether([block, Spacer(1, 6)]))


def add_box(story, color: str, title: str, body_lines: list[str]):
    """Multi-line summary card with title and bullets/text body."""
    fg, bg = STATUS_COLORS.get(color, STATUS_COLORS['gray'])
    elements = []
    if title:
        elements.append(Paragraph(
            safe(title),
            ParagraphStyle('BoxT', parent=styles['Normal'],
                           fontSize=10, leading=13,
                           textColor=fg,
                           fontName='Helvetica-Bold', alignment=TA_LEFT,
                           spaceAfter=4),
        ))
    for line in body_lines:
        if not line.strip():
            continue
        if line.lstrip().startswith('- '):
            txt = '&nbsp;&nbsp;&bull;&nbsp; ' + _md_inline(line.lstrip()[2:])
        else:
            txt = _md_inline(line)
        elements.append(Paragraph(
            safe(txt),
            ParagraphStyle('BoxB', parent=styles['Normal'],
                           fontSize=9.5, leading=12.5,
                           textColor=BODY_COLOR, alignment=TA_LEFT,
                           spaceAfter=2),
        ))
    block = Table([[elements]],
                   colWidths=[6.4 * inch],
                   style=TableStyle([
                       ('BACKGROUND', (0,0), (-1,-1), bg),
                       ('BOX', (0,0), (-1,-1), 0.5, fg),
                       ('LEFTPADDING', (0,0), (-1,-1), 12),
                       ('RIGHTPADDING', (0,0), (-1,-1), 10),
                       ('TOPPADDING', (0,0), (-1,-1), 8),
                       ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                   ]))
    story.append(KeepTogether([block, Spacer(1, 8)]))


def add_question(story, qid: str, qtitle: str, body: str):
    """Open-question card: numbered ID badge + title + body."""
    badge = Paragraph(
        f'<font color="#ffffff"><b>&nbsp;{safe(qid)}&nbsp;</b></font>',
        ParagraphStyle('QB', parent=styles['Normal'],
                       fontSize=11, leading=13, alignment=TA_CENTER,
                       fontName='Helvetica-Bold'),
    )
    badge_cell = Table([[badge]], colWidths=[0.5*inch], rowHeights=[0.32*inch],
                        style=TableStyle([
                            ('BACKGROUND', (0,0), (-1,-1), ACCENT_PURPLE),
                            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                            ('LEFTPADDING', (0,0), (-1,-1), 0),
                            ('RIGHTPADDING', (0,0), (-1,-1), 0),
                            ('TOPPADDING', (0,0), (-1,-1), 0),
                            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                        ]))
    p_title = Paragraph(
        safe(qtitle),
        ParagraphStyle('QT', parent=styles['Normal'],
                       fontSize=11, leading=13.5, alignment=TA_LEFT,
                       textColor=HEADING_COLOR,
                       fontName='Helvetica-Bold', spaceAfter=4),
    )
    p_body = Paragraph(
        safe(_md_inline(body)),
        ParagraphStyle('QBd', parent=styles['Normal'],
                       fontSize=10, leading=13,
                       textColor=BODY_COLOR, alignment=TA_LEFT),
    )
    inner = Table([[p_title], [p_body]],
                   colWidths=[5.6 * inch],
                   style=TableStyle([
                       ('LEFTPADDING', (0,0), (-1,-1), 8),
                       ('RIGHTPADDING', (0,0), (-1,-1), 0),
                       ('TOPPADDING', (0,0), (-1,-1), 0),
                       ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                   ]))
    block = Table([[badge_cell, inner]],
                   colWidths=[0.55 * inch, 5.85 * inch],
                   style=TableStyle([
                       ('VALIGN', (0,0), (-1,-1), 'TOP'),
                       ('LEFTPADDING', (0,0), (-1,-1), 0),
                       ('RIGHTPADDING', (0,0), (-1,-1), 0),
                       ('TOPPADDING', (0,0), (-1,-1), 0),
                       ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                   ]))
    story.append(KeepTogether([block, Spacer(1, 8)]))


# ──────────────────────────────────────────────────────────────────────────────
# Markdown -> story
# ──────────────────────────────────────────────────────────────────────────────
def md_to_story(md_path, story, base_dir):
    with open(md_path, 'r', encoding='utf-8') as f:
        text = f.read()
    lines = text.split('\n')

    suppress_first_h1 = True
    pending_finding_block = []   # accumulate for KeepTogether
    in_finding = False

    def flush_finding():
        nonlocal pending_finding_block, in_finding
        if pending_finding_block:
            story.append(KeepTogether(pending_finding_block))
            pending_finding_block = []
        in_finding = False

    def push(elem):
        if in_finding:
            pending_finding_block.append(elem)
        else:
            story.append(elem)

    i = 0
    while i < len(lines):
        ln = lines[i].rstrip()
        s = ln.strip()
        if not s:
            i += 1; continue

        # Page break directive
        if s == '<<PAGEBREAK>>' or s == '\\pagebreak':
            flush_finding()
            story.append(PageBreak())
            i += 1; continue

        # HR
        if s == '---':
            flush_finding()
            story.append(Spacer(1, 4))
            story.append(HRFlowable(width='100%', thickness=0.4,
                                     color=GRID_COLOR, spaceAfter=6))
            i += 1; continue

        # KEYSTAT
        m = re.match(r'^\[KEYSTAT\|(.*?)\|(.*?)\|(.*?)\]\s*$', s)
        if m:
            flush_finding()
            add_keystat(story, m.group(1), m.group(2), m.group(3))
            i += 1; continue

        # STATUS (single line)
        m = re.match(r'^\[STATUS\|(\w+)\|(.*?)\]\s*(.*)$', s)
        if m:
            color, label, body = m.group(1), m.group(2), m.group(3)
            j = i + 1
            extra = []
            while j < len(lines):
                nxt = lines[j].rstrip()
                if not nxt.strip(): break
                if re.match(r'^(#|<<|\[|\!\[|---|\|)', nxt.strip()): break
                extra.append(nxt.strip()); j += 1
            full_body = ' '.join([body] + extra).strip()
            flush_finding()
            add_status(story, color, label, full_body)
            i = j; continue

        # BOX (multi-line)
        m = re.match(r'^\[BOX\|(\w+)\|(.*?)\]\s*$', s)
        if m:
            color, title = m.group(1), m.group(2)
            body_lines = []
            j = i + 1
            while j < len(lines):
                nxt = lines[j].rstrip()
                if nxt.strip() == '[/BOX]': break
                body_lines.append(nxt)
                j += 1
            flush_finding()
            add_box(story, color, title, body_lines)
            i = j + 1; continue

        # QUESTION
        m = re.match(r'^\[QUESTION\|(.*?)\|(.*?)\]\s*(.*)$', s)
        if m:
            qid, qtitle, body = m.group(1), m.group(2), m.group(3)
            j = i + 1
            extra = []
            while j < len(lines):
                nxt = lines[j].rstrip()
                if not nxt.strip(): break
                if re.match(r'^(#|<<|\[|\!\[|---|\|)', nxt.strip()): break
                extra.append(nxt.strip()); j += 1
            full_body = ' '.join([body] + extra).strip()
            flush_finding()
            add_question(story, qid, qtitle, full_body)
            i = j; continue

        # 4-level callouts — these flush the finding-keep-together chunk
        # so callouts can flow naturally across pages
        m = re.match(r'^\[(MEDICAL|DATA-SCIENCE|LAY|DATA)\]:\s*(.*)$', s)
        if m:
            flush_finding()
            # fall through into callout handler below
            label_key, body = m.group(1), m.group(2)
            j = i + 1
            extra = []
            while j < len(lines):
                nxt = lines[j].rstrip()
                if not nxt.strip(): break
                if re.match(r'^(#|<<|\[|\!\[|---|\|)', nxt.strip()): break
                extra.append(nxt.strip()); j += 1
            full_body = ' '.join([body] + extra).strip()
            color_map = {
                'MEDICAL': COLOR_MEDICAL, 'DATA-SCIENCE': COLOR_DS,
                'LAY': COLOR_LAY, 'DATA': COLOR_DATA,
            }
            label_map = {
                'MEDICAL': 'CLINICAL / MEDICAL',
                'DATA-SCIENCE': 'DATA-SCIENCE / STATISTICS',
                'LAY': 'PLAIN ENGLISH',
                'DATA': 'CONCRETE DATA EXAMPLE',
            }
            # Use a temp story for the callout, then push to current target
            temp = []
            add_callout(temp, label_map[label_key], full_body, color_map[label_key])
            for el in temp:
                push(el)
            i = j; continue

        # Image
        if s.startswith('!['):
            mi = re.match(r'!\[(.*?)\]\((.*?)\)', s)
            if mi:
                caption = mi.group(1)
                pth = mi.group(2)
                p = base_dir / pth if not Path(pth).is_absolute() else Path(pth)
                if not p.exists():
                    cand = base_dir.parent / "figures" / Path(pth).name
                    if cand.exists():
                        p = cand
                temp = []
                add_image(temp, str(p), caption=caption, max_h=2.6*inch)
                for el in temp:
                    push(el)
            i += 1; continue

        # Headings — natural flow, no auto page-break (use <<PAGEBREAK>> directive
        # explicitly where needed). H1 = ##; H2 = ###; H3 = #### -> finding-start.
        if s.startswith('## '):
            flush_finding()
            suppress_first_h1 = False
            # Slight pre-spacing for major-section heading
            story.append(Spacer(1, 6))
            story.append(Paragraph(safe(s[3:]), styles['H1']))
            i += 1; continue
        if s.startswith('### '):
            flush_finding()
            # Only KeepTogether the heading + next image / status (not the
            # whole finding — that overflows pages). After image+status, let
            # callouts flow naturally.
            in_finding = True
            pending_finding_block.append(Paragraph(safe(s[4:]), styles['H2']))
            i += 1; continue
        if s.startswith('#### '):
            push(Paragraph(safe(s[5:]), styles['H3']))
            i += 1; continue

        # Block-quote
        if s.startswith('>'):
            qt = _md_inline(s.lstrip('>').strip())
            push(Paragraph(safe(qt), styles['Quote']))
            i += 1; continue

        # Tables
        if s.startswith('|') and '|' in s[1:]:
            tl = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                tl.append(lines[i].strip()); i += 1
            if len(tl) >= 3:
                headers = [c.strip() for c in tl[0].split('|')[1:-1]]
                rows = []
                for r in tl[2:]:
                    cells = [c.strip() for c in r.split('|')[1:-1]]
                    if cells and len(cells) == len(headers):
                        cells = [_md_inline(c) for c in cells]
                        rows.append(cells)
                if headers and rows:
                    headers = [_md_inline(x) for x in headers]
                    temp = []
                    add_table(temp, headers, rows)
                    for el in temp:
                        push(el)
            continue

        # Bullets
        if s.startswith('- ') or s.startswith('* '):
            txt = _md_inline(s[2:])
            push(Paragraph(f'&nbsp;&nbsp;&bull;&nbsp; {safe(txt)}', styles['Bd']))
            i += 1; continue

        # Numbered list
        if re.match(r'^\d+\.\s', s):
            num = re.match(r'^(\d+)\.', s).group(1)
            txt = _md_inline(re.sub(r'^\d+\.\s', '', s))
            push(Paragraph(f'&nbsp;&nbsp;{num}.&nbsp; {safe(txt)}', styles['Bd']))
            i += 1; continue

        # Default paragraph
        push(Paragraph(safe(_md_inline(s)), styles['Bd']))
        i += 1

    flush_finding()


# ──────────────────────────────────────────────────────────────────────────────
# Header / footer
# ──────────────────────────────────────────────────────────────────────────────
def _make_hf(footer_label):
    def hf(c, d):
        c.saveState()
        c.setFont('Helvetica', 8)
        c.setFillColor(FOOTER_COLOR)
        c.drawRightString(d.width + d.leftMargin, 0.45*inch, f'Page {d.page}')
        c.drawString(d.leftMargin, 0.45*inch, footer_label)
        # Top horizontal line
        c.setStrokeColor(HexColor('#27ae60'))
        c.setLineWidth(0.4)
        c.line(d.leftMargin, d.height + d.topMargin - 0.2*inch,
               d.width + d.leftMargin, d.height + d.topMargin - 0.2*inch)
        c.restoreState()
    return hf


# ──────────────────────────────────────────────────────────────────────────────
# Main entry point
# ──────────────────────────────────────────────────────────────────────────────
def build_report(md_path, pdf_path, *, title, subtitle=None,
                 footer_label=None, cover_meta=None):
    md_path = Path(md_path); pdf_path = Path(pdf_path)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    base_dir = md_path.parent

    doc = SimpleDocTemplate(
        str(pdf_path), pagesize=letter,
        topMargin=0.7*inch, bottomMargin=0.7*inch,
        leftMargin=0.85*inch, rightMargin=0.85*inch,
        title=title,
    )
    story = []

    # Compact cover header (NOT a separate page — flows into first content)
    story.append(Paragraph(safe(title), styles['DocTitle']))
    if subtitle:
        story.append(Paragraph(safe(subtitle), styles['DocSubtitle']))
    if cover_meta:
        for line in cover_meta:
            story.append(Paragraph(safe(line), styles['DocMeta']))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width='100%', thickness=0.6,
                             color=ACCENT_GREEN, spaceAfter=12))

    md_to_story(md_path, story, base_dir)

    hf = _make_hf(footer_label or title)
    doc.build(story, onFirstPage=hf, onLaterPages=hf)
    return pdf_path
