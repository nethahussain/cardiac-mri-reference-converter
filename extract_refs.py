#!/usr/bin/env python3
"""Extract all CMR reference-range tables from the Raisi-Estabragh appendix .docx
into a structured JSON:  REFS[eth][sex][seg][index][canonKey] = {ageGroup:[lo,hi]}
Also captures per-parameter unit labels and validates smooth+BSA against the
existing smooth_bsa_reference_ranges.json.
"""
import zipfile, re, html, json, sys, os

APPENDIX = 'appendix raisi-estabragh-et-al-2024-cardiovascular-magnetic-resonance-reference-ranges-from-the-healthy-hearts-consortium.docx'
AGES = ['18-29', '30-39', '40-49', '50-59', '60-69', '70+']
SEG_MAP = {'smooth': 'smooth', 'papillary': 'papillary', 'anatomical': 'anatomical', 'anatomic': 'anatomical'}
IDX_MAP = {'body surface area': 'bsa', 'height': 'height'}
ETH_CANON = {'White': 'White', 'Black': 'Black', 'South Asian': 'South Asian',
             'Chinese': 'Chinese', 'Mixed/Other': 'Mixed/Other'}

def para_text(p):
    return html.unescape(re.sub(r'<[^>]+>', '', p)).strip()

def cells_of_table(tbl_xml):
    rows = []
    for tr in re.findall(r'<w:tr\b.*?</w:tr>', tbl_xml, re.S):
        cells = []
        for tc in re.findall(r'<w:tc\b.*?</w:tc>', tr, re.S):
            t = re.sub(r'</w:p>', ' ', tc)
            t = re.sub(r'<[^>]+>', '', t)
            cells.append(html.unescape(t).strip())
        if cells:
            rows.append(cells)
    return rows

def canon_key(label):
    """'LVEDVi (ml/m2)' -> 'LVEDVi' ; 'LA max i (ml/m)' -> 'LA max i'"""
    return re.sub(r'\s*\(.*$', '', label).strip()

def unit_of(label):
    m = re.search(r'\(([^)]*)\)', label)
    return m.group(1).strip() if m else ''

def parse_heading(t):
    m = re.match(r'Supplemental Table (\d+)\.\s*CMR metrics in (women|men) of (.+?) ethnicity '
                 r'using (\w+) segmentation, indexed by (.+)', t)
    if not m:
        return None
    num, sexword, eth, seg, idx = m.groups()
    sex = 'F' if sexword == 'women' else 'M'
    eth = eth.strip()
    seg = SEG_MAP.get(seg.strip().lower())
    idx = IDX_MAP.get(idx.strip().lower().rstrip('.'))
    if eth not in ETH_CANON or not seg or not idx:
        return None
    return int(num), eth, sex, seg, idx

RANGE_RE = re.compile(r'\[\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*\]')

def main():
    z = zipfile.ZipFile(APPENDIX)
    xml = z.read('word/document.xml').decode('utf-8', errors='ignore')
    tokens = [(m.start(), 'p', m.group(0)) for m in re.finditer(r'<w:p\b.*?</w:p>', xml, re.S)]
    tokens += [(m.start(), 'tbl', m.group(0)) for m in re.finditer(r'<w:tbl\b.*?</w:tbl>', xml, re.S)]
    tokens.sort()

    REFS = {}
    UNITS = {}          # UNITS[index][canonKey] = unit string
    pending = None      # heading parsed, waiting for its table
    count = 0
    for off, kind, content in tokens:
        if kind == 'p':
            t = para_text(content)
            if t.startswith('Supplemental Table'):
                ph = parse_heading(t)
                pending = ph
        elif kind == 'tbl' and pending:
            num, eth, sex, seg, idx = pending
            rows = cells_of_table(content)
            node = REFS.setdefault(eth, {}).setdefault(sex, {}).setdefault(seg, {}).setdefault(idx, {})
            # Determine which age group each column maps to by reading the header row.
            col_ages = None
            for r in rows:
                if r and r[0].strip().lower().startswith('variable'):
                    col_ages = [re.sub(r'\s+', '', c) for c in r[1:]]
                    break
            if col_ages is None:
                col_ages = AGES[:]  # fallback
            for ag in col_ages:
                if ag not in AGES:
                    print(f'  WARN unexpected age label {ag!r} in table {num}', file=sys.stderr)
            for r in rows:
                label = r[0].strip()
                if not label or label.lower().startswith('variable') or label.startswith('N ') \
                   or label.lower() in ('left ventricle', 'right ventricle', 'left atrium', 'right atrium'):
                    continue
                key = canon_key(label)
                unit = unit_of(label)
                if unit:
                    UNITS.setdefault(idx, {}).setdefault(key, unit)
                agevals = {}
                for ci in range(1, len(r)):
                    if ci - 1 >= len(col_ages):
                        break
                    ag = col_ages[ci - 1]
                    m = RANGE_RE.search(r[ci])
                    if m:
                        lo, hi = float(m.group(1)), float(m.group(2))
                        lo = int(lo) if lo == int(lo) else lo
                        hi = int(hi) if hi == int(hi) else hi
                        agevals[ag] = [lo, hi]
                if agevals:
                    node[key] = agevals
            count += 1
            pending = None

    print(f'Parsed {count} tables.', file=sys.stderr)
    json.dump({'REFS': REFS, 'UNITS': UNITS}, open('cmr_reference_ranges.json', 'w'),
              ensure_ascii=False, separators=(',', ':'))
    sz = os.path.getsize('cmr_reference_ranges.json')
    print(f'Wrote cmr_reference_ranges.json ({sz} bytes)', file=sys.stderr)

    # ---- Validation against existing smooth + BSA JSON ----
    old = json.load(open('smooth_bsa_reference_ranges.json'))
    mism = 0
    checked = 0
    for grp, gd in old.items():
        eth, sex = grp.split('|')
        params = gd['parameters']
        for pname, ages in params.items():
            key = canon_key(pname)
            try:
                new = REFS[eth][sex]['smooth']['bsa'][key]
            except KeyError:
                print(f'  MISSING new: {eth}|{sex} smooth bsa {key}', file=sys.stderr)
                continue
            for ag, rng in ages.items():
                if rng is None:
                    continue
                if ag in new:
                    checked += 1
                    a = [round(float(x)) for x in rng]
                    b = [round(float(x)) for x in new[ag]]
                    if a != b:
                        mism += 1
                        if mism <= 20:
                            print(f'  MISMATCH {eth}|{sex} {key} {ag}: old={rng} new={new[ag]}', file=sys.stderr)
    print(f'Validation: checked {checked} cells, {mism} mismatches.', file=sys.stderr)

    # ---- Coverage summary ----
    seg_set, idx_set, key_set = set(), set(), set()
    for eth in REFS:
        for sex in REFS[eth]:
            for seg in REFS[eth][sex]:
                seg_set.add(seg)
                for idx in REFS[eth][sex][seg]:
                    idx_set.add(idx)
                    key_set.update(REFS[eth][sex][seg][idx].keys())
    print('segmentations:', sorted(seg_set), file=sys.stderr)
    print('indexings:', sorted(idx_set), file=sys.stderr)
    print('param keys:', sorted(key_set), file=sys.stderr)

if __name__ == '__main__':
    main()
