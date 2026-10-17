# Extrai todas as provas selecionadas e casa cada (prova, área) com um CO_PROVA dos microdados.
import sys, os, json, re, unicodedata, pandas as pd, pymupdf
sys.path.insert(0, os.path.dirname(__file__))
from extrair import questoes
man = json.load(open('dados/provas_sel.json', encoding='utf-8'))
it = pd.read_csv('dados/itens_todos.csv')
def nc(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii','ignore').decode().upper()
    for c in ['AZUL','AMAREL','BRANC','ROSA','CINZA','VERDE','LARANJA','ROX']:
        if c in s: return c
    return s
it['COR'] = it.TX_COR.map(nc)
START_NEW = {'LC':1,'CH':46,'CN':91,'MT':136}
def nb(r):
    a, ar, p, l = r.ANO, r.SG_AREA, int(r.CO_POSICAO), r.get('TP_LINGUA')
    if a == 2017:
        if ar == 'LC':
            if p <= 5: return p
            if p <= 10 and l == 1: return p-5
            return p-5
        return START_NEW[ar] + p - 1
    if a == 2016:
        return {'CH':p-45,'CN':p-45,'LC':p+90,'MT':p}[ar]
    return p
it['NB'] = it.apply(nb, axis=1)
it.to_csv('dados/itens_todos_nb.csv', index=False, encoding='utf-8')
def cor_capa(t):
    t = unicodedata.normalize('NFKD', t).encode('ascii','ignore').decode().upper()
    m = re.search(r'CADERNO\W{0,6}\d{1,2}\W{0,6}(AZUL|AMAREL|BRANC|ROSA|CINZA|VERDE|LARANJA)', t) or \
        re.search(r'(?:COR DO SEU CADERNO[^\n]*?E\s*)(AZUL|AMAREL|BRANC|ROSA|CINZA|VERDE|LARANJA)', t) or \
        re.search(r'\b(AZUL|AMAREL[OA]|BRANC[OA]|ROSA|CINZA|VERDE|LARANJA)\b', t)
    return nc(m.group(1)) if m else None
def gab_parse(path):
    """número -> lista de letras na ordem em que aparecem (várias cores/idiomas)."""
    if not path or not os.path.exists(path): return {}
    toks = re.findall(r'\d{1,3}|[A-E]\b|Anulad[oa]', ' '.join(p.get_text() for p in pymupdf.open(path)))
    g = {}; i = 0
    while i < len(toks):
        t = toks[i]
        if t.isdigit() and 1 <= int(t) <= 185:
            j = i+1; ls = []
            while j < len(toks) and not toks[j].isdigit(): ls.append(toks[j]); j += 1
            if ls: g.setdefault(int(t), []).append(ls)
            i = j
        else: i += 1
    return g
AREA_D1_OLD = {(1,45):'CH',(46,90):'CN'}; AREA_D2_OLD = {(91,135):'LC',(136,180):'MT'}
def area_de(ano, n):
    if ano <= 2016: return ('CH' if n<=45 else 'CN') if n<=90 else ('LC' if n<=135 else 'MT')
    return ('LC' if n<=45 else 'CH') if n<=90 else ('CN' if n<=135 else 'MT')
res = []; texto = {}
for m in man:
    doc, qs, capa = questoes(m['arquivo'])
    cor = cor_capa(capa)
    g = gab_parse(m['gab'])
    key = os.path.basename(m['arquivo'])
    texto[key] = {str(n): {'t': q['texto'], 'p': q['pags']} for n, q in qs.items()}
    areas = sorted(set(area_de(m['ano'], q['n']) for q in qs.values()))
    for ar in areas:
        cand = it[(it.ANO==m['ano'])&(it.SG_AREA==ar)]
        best = []
        for cp, grp in cand.groupby('CO_PROVA'):
            gab = dict(zip(grp.NB, grp.TX_GABARITO))
            sc = 0; tot = 0
            for pos, letra in gab.items():
                if pos in g:
                    tot += 1
                    if any(letra in ls for ls in g[pos]): sc += 1
            best.append((sc, tot, cp, grp.DESC.iloc[0], grp.COR.iloc[0]))
        best.sort(key=lambda x: (-(x[0]), x[2]))
        # empates: preferir mesma cor e descrição coerente com o grupo
        top = [b for b in best if b[0]==best[0][0]] if best else []
        def app_ok(desc):
            s = str(desc).lower()
            if m['grupo'] == 'regular': return ('reaplica' not in s and 'digital' not in s and 'ppl' not in s and 'segunda' not in s)
            if m['grupo'] in ('ppl','p2','terceira'): return 'reaplica' in s or 'ppl' in s or s == 'nan'
            if m['grupo'] == 'digital': return 'digital' in s
            return True
        if not best or best[0][1] == 0 or best[0][0] < 0.8*best[0][1]:
            top = [b for b in best if b[4]==cor and app_ok(b[3])] or [b for b in best if b[4]==cor] or best
            top = [b for b in top if 'ledor' not in str(b[3]).lower() and 'adaptada' not in str(b[3]).lower()] or top
        pref = [b for b in top if b[4]==cor] or top
        ch = pref[0] if pref else None
        res.append(dict(arquivo=key, ano=m['ano'], grupo=m['grupo'], dia=m['dia'], cor=cor, area=ar,
                        co_prova=int(ch[2]) if ch else None, desc=ch[3] if ch else None, score=f'{ch[0]}/{ch[1]}' if ch else None,
                        n_empate=len(top), nq=len(qs), valido=bool(ch and ch[1]>=40 and ch[0]>=0.85*ch[1]), fallback=bool(ch and (ch[1]<40 or ch[0]<0.85*ch[1])), url=m['url'], gab_url=m['gab_url']))
        print(m['ano'], m['grupo'], m['dia'], cor, ar, res[-1]['co_prova'], res[-1]['desc'], res[-1]['score'], 'emp', len(top))
json.dump(res, open('dados/casamento.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(texto, open('dados/textos_pdf.json','w',encoding='utf-8'), ensure_ascii=False)
