# Extrai questões (texto + regiões) de um caderno do ENEM. Uso como módulo.
import pymupdf, re, unicodedata
HDR = re.compile(r'^\s*QUEST[ÃA]O\s*(\d{1,3})\s*$', re.I)
def norm(s): return unicodedata.normalize('NFC', s)
def linhas(doc):
    """Retorna lista de (pg, col, y0, x0, x1, y1, texto) em ordem de leitura."""
    out = []
    for pi, pg in enumerate(doc):
        W = pg.rect.width; mid = W/2
        d = pg.get_text('dict')
        for b in d['blocks']:
            if b['type'] != 0: continue
            for l in b['lines']:
                t = norm(''.join(s['text'] for s in l['spans'])).strip()
                if not t: continue
                x0, y0, x1, y1 = l['bbox']
                col = 0 if (x0+x1)/2 < mid else 1
                if x0 < mid-20 and x1 > mid+20: col = 0  # linha que atravessa
                out.append((pi, col, y0, x0, x1, y1, t))
    out.sort(key=lambda r: (r[0], r[1], r[2], r[3]))
    # junta 'Questão' + número que vieram em linhas separadas (cadernos 2009-2010)
    usados = set(); res = []
    for i, r in enumerate(out):
        if i in usados: continue
        if re.fullmatch(r'QUEST[ÃA]O', r[6].strip(), re.I):
            cand = [j for j, s2 in enumerate(out) if j not in usados and j != i and s2[0] == r[0] and s2[1] == r[1]
                    and abs(s2[2]-r[2]) < 14 and 0 <= s2[3]-r[3] < 140 and re.fullmatch(r'\d{1,3}', s2[6].strip())]
            if cand:
                j = min(cand, key=lambda j: abs(out[j][2]-r[2])); s2 = out[j]; usados.add(j)
                r = (r[0], r[1], r[2], r[3], max(r[4], s2[4]), max(r[5], s2[5]), r[6].strip()+' '+s2[6].strip())
        res.append(r)
    res = [x for k, x in enumerate(res)]
    # remove números usados que ficaram antes na lista
    ids = set(id(out[j]) for j in usados)
    res = [x for x in res if id(x) not in ids]
    return res
def questoes(path):
    doc = pymupdf.open(path)
    L = linhas(doc)
    qs = {}; cur = None; lang = None
    LANG = re.compile(r'(INGL[ÊE]S|ESPANHOL)', re.I)
    for r in L:
        ml = LANG.search(r[6])
        if ml and len(r[6]) < 120 and ('op' in r[6].lower() or 'estrangeira' in r[6].lower() or r[6].strip().upper() == ml.group(1).upper() or 'quest' in r[6].lower()):
            lang = 'ing' if ml.group(1).upper().startswith('INGL') else 'esp'
        m = HDR.match(r[6])
        if m:
            n = int(m.group(1))
            key = n
            if n in qs or (lang and (n <= 5 or 91 <= n <= 95)):
                key = f'{n}-{lang or "x"}'
                if key in qs:
                    outra = {'ing': 'esp', 'esp': 'ing'}.get(lang)
                    key = f'{n}-{outra}' if outra and f'{n}-{outra}' not in qs else f'{n}-{lang or "x"}2'
            cur = key; qs.setdefault(cur, {'n': n, 'lang': lang if isinstance(key, str) else None, 'linhas': [], 'pags': set()}); continue
        if cur is not None:
            qs[cur]['linhas'].append(r); qs[cur]['pags'].add(r[0])
    for q in qs.values():
        q['texto'] = '\n'.join(r[6] for r in q['linhas'])
        q['pags'] = sorted(q['pags'])
    capa = '\n'.join(doc[0].get_text().split('\n')[:80])
    return doc, qs, capa
