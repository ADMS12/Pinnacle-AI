"""Redact / replace personal information in the two R-L tax return PDFs.
Usage: python redact_tax.py <src_dir> <out_dir>
Text is removed with PyMuPDF redaction (no fill, so form rules stay intact) and the edited
value is re-typed at the same spot in the matching base font.
"""
import fitz, re, os, sys

SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)

I = re.IGNORECASE
# (pattern, replacement, flags). Order matters: longer phrases first.
RULES = [
    # names
    (r'REMY J LEVINE', 'R J L', 0), (r'REMY LEVINE', 'R L', 0), (r'\bREMY J\b', 'R J', 0),
    (r'\bREMY\b', 'R', I), (r'\bLEVINE\b', 'L', I), (r'\bLEVI\b', 'L', 0),
    # entities
    (r'BUTTER LLC', 'B LLC', 0), (r'\bBUTT\b', 'B', 0),
    (r'VOLTAIC CONSTRUCTION LLC', 'V C LLC', 0), (r'VOLTAIC, LLC', 'V, LLC', 0), (r'\bVOLTAIC\b', 'V', 0),
    # rental property address -> generic label
    (r'2329 OCEAN AVE,? VENICE,? CA 90291', 'RENTAL PROPERTY', 0), (r'2329 OCEAN AVE', 'RENTAL PROPERTY', 0),
    # identifiers
    (r'\b048-94-4443\b', '', 0), (r'\b048944443\b', '', 0),
    (r'\b(86-3688216|90-0228797|88-1110109|82-3381550|26-2627205)\b', '', 0),
    (r'[\w.+-]+@[\w-]+\.\w+', '', 0),
    (r'\(\d{3}\) ?\d{3}-\d{4}', '', 0), (r'\b3107090059\b', '', 0),
    (r'\b09[/-]26[/-]1994\b', '', 0), (r'\b(92563|92617)\b', '', 0),
    (r'\bP00953907\b', '', 0), (r'\b960104202608200jyvl8\b', '', 0),
    (r'MICHELLE A\. TAYLOR', '', 0), (r'ZELADA & TAYLOR CPA, P\.C\.', '', 0),
    # addresses
    (r'700 BROADWAY(,? (Apt\.?|APT) 512)?(, SANTA MONICA CA 90401)?', '', 0),
    (r'SANTA MONICA(, CA 90401)?', '', 0),
    (r'1195 MIRAMAR DR(, VISTA CA 92081)?', '', 0), (r'\bVISTA( CA 92081)?\b', '', 0),
    (r'486 CARROLL? CT( VENICE CA 90291)?', '', 0), (r'\bVENICE( CA 90291)?\b', '', 0),
    (r'38087 OLD CREEK (CT|RD)', '', 0), (r'5300 CALIFORNIA AVE', '', 0),
    (r'732 N DIAMOND BAR BLVD STE 216( DIAMOND BAR CA 91765)?', '', 0), (r'DIAMOND BAR( CA 91765)?', '', 0),
    (r'\bMURRIETA\b', '', 0), (r'\bIRVINE\b', '', 0), (r'\bLOS ANGELES\b', '', I),
    (r',? ?\bCA (90401|90291|92081|91765)\b', '', 0),
]
# values that are removed only when the whole span is exactly this text
EXACT_REMOVE = {'90401', '90291', '92081', '91765', '44443', '01011', '88216', '960104', 'VISTA', 'VENICE', 'DIAMOND BAR', 'SANTA MONICA'}
COMPILED = [(re.compile(p, f), r) for p, r, f in RULES]

def apply(text):
    """Return edited text, or None when no rule touched it."""
    t = text
    for rx, rep in COMPILED:
        t = rx.sub(rep, t)
    if t == text: return None
    return re.sub(r'[ ]{2,}', ' ', t).strip()

ARIAL, ARIALB = 'C:/Windows/Fonts/arial.ttf', 'C:/Windows/Fonts/arialbd.ttf'
def font_for(name):
    n = name.lower()
    if 'courier' in n: return 'cour', None
    if 'bold' in n or '-bd' in n: return 'ArialB', ARIALB
    return 'Arial', ARIAL

def rgb(c): return ((c >> 16) & 255) / 255, ((c >> 8) & 255) / 255, (c & 255) / 255

for fname in sorted(os.listdir(SRC)):
    if not fname.lower().endswith('.pdf'): continue
    doc = fitz.open(os.path.join(SRC, fname))
    n_edit = 0
    for page in doc:
        d = page.get_text('dict')
        spans = [s for b in d['blocks'] for l in b.get('lines', []) for s in l['spans'] if s['text'].strip()]
        has_broadway = any('700 BROADWAY' in s['text'] for s in spans)
        # SSN printed in three separate boxes: 048 | 94 | 4443 on one baseline
        ssn_parts = set()
        for s4 in spans:
            if s4['text'].strip() == '4443':
                ssn_parts.add(id(s4))
                for s in spans:
                    if s['text'].strip() in ('048', '94') and abs(s['origin'][1] - s4['origin'][1]) < 2 and 0 < s4['bbox'][0] - s['bbox'][0] < 120:
                        ssn_parts.add(id(s))
        jobs = []
        for s in spans:
            txt = s['text']; stripped = txt.strip()
            if stripped in EXACT_REMOVE or (stripped == '512' and has_broadway) or id(s) in ssn_parts:
                new = ''
            else:
                new = apply(txt)
                if new is None: continue
            jobs.append((fitz.Rect(s['bbox']), new, s))
        if not jobs: continue
        for r, new, s in jobs:
            rr = fitz.Rect(r); rr.y0 += 0.3; rr.y1 -= 0.3
            page.add_redact_annot(rr, fill=False)
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)
        for r, new, s in jobs:
            n_edit += 1
            if not new: continue
            fname_, ffile = font_for(s['font'])
            page.insert_text((r.x0, s['origin'][1]), new, fontname=fname_, fontfile=ffile, fontsize=s['size'], color=rgb(s['color']))
    out = os.path.join(OUT, fname)
    doc.save(out, garbage=3, deflate=True)
    # verification scan
    chk = fitz.open(out); full = '\n'.join(p.get_text() for p in chk)
    checks = ['048-94-4443', '048944443', 'REMY', 'LEVINE', 'BUTTER', 'VOLTAIC', 'TAYLOR', 'ZELADA', 'BROADWAY', 'MIRAMAR', 'OCEAN AVE', 'CARROL',
              'OLD CREEK', 'CALIFORNIA AVE', 'DIAMOND BAR', 'SANTA MONICA', 'VENICE', 'VISTA', 'MURRIETA', 'IRVINE', 'LOS ANGELES', '@gmail', '@zelada',
              '709-0059', '861-2689', '861-1865', '09/26/1994', 'P00953907', '86-3688216', '90-0228797', '88-1110109', '82-3381550', '26-2627205',
              '90401', '90291', '92081', '91765']
    left = {c: len(re.findall(re.escape(c), full, re.I)) for c in checks}
    left = {k: v for k, v in left.items() if v}
    print(f'{fname}: {n_edit} spans edited over {len(chk)} pages; leftovers: {left}')
