"""Replace client names in RightCapital PDFs with avatar labels.
Line-level: remove the original text run, re-insert the edited line in Helvetica sized to fit.
"""
import fitz, re, sys, os

SRC = sys.argv[1]      # folder with originals
OUT = sys.argv[2]      # output folder
os.makedirs(OUT, exist_ok=True)

JOBS = {
 'Shabnam_Nejati_HighIncome_Drs_With_Business.pdf': ('HiNetWorth-Drs-Business_Avatar_HighIncome_Drs_With_Business.pdf', [
    ('Mehrdad (Mike) Nejati', 'Dr-With-PrivatePractices Avatar'),
    ('Shabnam Nejati', 'HiNetWorth-Drs-Business Avatar'),
    ('Mehrdad (Mike)', 'Dr-With-PrivatePractices Avatar'),
    ('(Mike)', ''),
    ('Mehrdad', 'Dr-With-PrivatePractices Avatar'),
    ('Mike', 'Dr-With-PrivatePractices Avatar'),
    ('Shabnam', 'HiNetWorth-Drs-Business Avatar'),
    ('Nejati', ''),
 ]),
 'Kollen_Glynn_HighIncome_HightNetwortj_Single.pdf': ('HiNetWorthHiIncome-Millennial_Avatar_HighIncome_HighNetworth_Single.pdf', [
    ('Kollen Glynn', 'HiNetWorthHiIncome-Millennial Avatar'),
    ('Whisler Family Trust', 'Family Trust'),
    ('Kollen', 'HiNetWorthHiIncome-Millennial Avatar'),
    ('Whisler', 'Family Trust'),
    ('Glynn', ''),
 ]),
 'Corey_Mailloux_Milleneal_HDW_Business.pdf': ('HiIncome-Business-Millennial_Avatar_Millennial_HDW_Business.pdf', [
    ('Corey Mailloux', 'HiIncome-Business-Millennial Avatar'),
    ('Nicky Mailloux', 'Spouse-W2 Avatar'),
    ('Corey', 'HiIncome-Business-Millennial Avatar'),
    ('Nicky', 'Spouse-W2 Avatar'),
    ('Mailloux', ''),
 ]),
 'Eddie_Martinez_HighIncome_Legacy_Plan.pdf': ('BabyBoomer-W2-and-Business_Avatar_HighIncome_Legacy_Plan.pdf', [
    ('Eddie Martinez', 'BabyBoomer-W2-and-Business Avatar'),
    ('Isabel Martinez', 'Spouse-W2 Avatar'),
    ('Martinez Family Trust', 'Family Trust'),
    ('Eddie', 'BabyBoomer-W2-and-Business Avatar'),
    ('Isabel', 'Spouse-W2 Avatar'),
    ('Martinez', ''),
 ]),
 'Chris_Arbogast_HighIncome_ModerateNetworth_Family.pdf': ('HiIncome-MedNetWorth-Millennial_Avatar_HighIncome_ModerateNetworth_Family.pdf', [
    ('Chris Arbogast', 'HiIncome-MedNetWorth-Millennial Avatar'),
    ('Kylee Arbogast', 'Spouse-W2 Avatar'),
    ('Chris', 'HiIncome-MedNetWorth-Millennial Avatar'),
    ('Kylee', 'Spouse-W2 Avatar'),
    ('Arbogast', ''),
 ]),
}

FONTS = {
    'Arial':  {'file': 'C:/Windows/Fonts/arial.ttf',   'obj': fitz.Font(fontfile='C:/Windows/Fonts/arial.ttf')},
    'ArialB': {'file': 'C:/Windows/Fonts/arialbd.ttf', 'obj': fitz.Font(fontfile='C:/Windows/Fonts/arialbd.ttf')},
}

def make_rx(rules):
    pats = sorted(rules, key=lambda r: -len(r[0]))
    rx = re.compile(r'(?<![A-Za-z])(' + '|'.join(re.escape(p) for p, _ in pats) + r')(?![A-Za-z])')
    lut = dict(pats)
    return rx, lut

def replace_text(txt, rx, lut):
    out = rx.sub(lambda m: lut[m.group(1)], txt)
    out = re.sub(r'[ \t]{2,}', ' ', out)
    out = re.sub(r'�(?=s\b)', "'", out)             # unmapped glyph before "s" is an apostrophe
    out = re.sub(r' � ', ' · ', out)            # unmapped glyph between spaces is a middle dot
    out = out.replace('�', "'")
    out = re.sub(r'^\s*&\s*$', '&', out)
    return out.strip() if out.strip() != txt.strip() else out

def segments(line, gap_factor=1.5):
    """Split a line's spans into segments wherever there is a large horizontal gap (separate table cells)."""
    segs, cur = [], []
    for s in line['spans']:
        if cur:
            prev = cur[-1]
            gap = s['bbox'][0] - prev['bbox'][2]
            if gap > gap_factor * s['size']:
                segs.append(cur); cur = []
        cur.append(s)
    if cur: segs.append(cur)
    return segs

def int_rgb(c):
    return ((c >> 16) & 255) / 255, ((c >> 8) & 255) / 255, (c & 255) / 255

summary = []
ONLY = sys.argv[3] if len(sys.argv) > 3 else None
for src_name, (dst_name, rules) in JOBS.items():
    if ONLY and ONLY not in src_name: continue
    rx, lut = make_rx(rules)
    doc = fitz.open(os.path.join(SRC, src_name))
    # which Type3 fonts are the bold face: those used on big headings
    bold_fonts = set()
    for p in doc:
        for b in p.get_text('dict')['blocks']:
            for l in b.get('lines', []):
                for s in l['spans']:
                    if s['size'] >= 19 and s['text'].strip(): bold_fonts.add(s['font'])
    n_edits = 0
    for page in doc:
        d = page.get_text('dict')
        # obstacles for right-extension: every text span and every non-hairline drawing (cell fills, cover graphics)
        all_rects = [fitz.Rect(s['bbox']) for b in d['blocks'] for l in b.get('lines', []) for s in l['spans'] if s['text'].strip()]
        all_rects += [dr['rect'] for dr in page.get_drawings()
                      if dr['rect'].width > 4 and dr['rect'].height > 4 and dr['rect'].height < 450 and dr['rect'].width < 500]
        jobs = []
        for b in d['blocks']:
            for l in b.get('lines', []):
                for seg in segments(l):
                    txt = ''.join(s['text'] for s in seg)
                    if not rx.search(txt): continue
                    new = replace_text(txt, rx, lut)
                    rect = fitz.Rect(seg[0]['bbox'])
                    for s in seg[1:]: rect |= fitz.Rect(s['bbox'])
                    s0 = seg[0]
                    jobs.append(dict(rect=rect, text=new, size=s0['size'], color=int_rgb(s0['color']),
                                     bold=s0['font'] in bold_fonts, origin=s0['origin']))
        if not jobs: continue
        for j in jobs:
            r = fitz.Rect(j['rect']); r.y0 += 0.5; r.y1 -= 0.5
            page.add_redact_annot(r, fill=False)
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)
        for j in jobs:
            if not j['text']: continue
            font = 'ArialB' if j['bold'] else 'Arial'
            ffile = FONTS[font]['file']
            rect = j['rect']; fs = j['size']
            # free space on the row: right limit = next text/graphic to the right, left limit = nearest to the left
            right = page.rect.width - 40
            left = 40.0
            for o in all_rects:
                if o.y1 > rect.y0 + 1 and o.y0 < rect.y1 - 1:
                    if o.x0 > rect.x1 - 1: right = min(right, o.x0 - 8)
                    elif o.x1 < rect.x0 + 1: left = max(left, o.x1 + 8)
            right = max(right, rect.x1); left = min(left, rect.x0)
            w = FONTS[font]['obj'].text_length(j['text'], fontsize=fs)
            x = rect.x0
            if w > right - rect.x0:
                fs_keep = fs * (right - rect.x0) / w
                if fs_keep >= 0.6 * fs:
                    fs = fs_keep                       # modest shrink, keep the left edge
                else:                                  # too small: use the room on the left as well
                    fs = max(5.0, fs * (right - left) / w)
                    w = FONTS[font]['obj'].text_length(j['text'], fontsize=fs)
                    x = max(left, right - w)
            page.insert_text((x, j['origin'][1]), j['text'], fontname=font, fontfile=ffile, fontsize=fs, color=j['color'])
            n_edits += 1
    out_path = os.path.join(OUT, dst_name)
    doc.save(out_path, garbage=3, deflate=True)
    # verify
    chk = fitz.open(out_path)
    leftovers = {}
    for p in chk:
        t = p.get_text()
        for pat, _ in rules:
            k = len(re.findall(r'(?<![A-Za-z])' + re.escape(pat) + r'(?![A-Za-z])', t))
            if k: leftovers[pat] = leftovers.get(pat, 0) + k
    summary.append((src_name, dst_name, n_edits, leftovers, len(chk)))
    print(f'{src_name} -> {dst_name}: {n_edits} lines rewritten, pages {len(chk)}, leftovers {leftovers}')
