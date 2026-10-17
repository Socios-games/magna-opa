import json, math, pandas as pd, re
it = pd.read_csv('dados/itens_todos_nb.csv')
cas = json.load(open('dados/casamento.json', encoding='utf-8'))
tx = json.load(open('dados/textos_pdf.json', encoding='utf-8'))
ok = {(c['co_prova']): c for c in cas if c['co_prova'] and (c['valido'] or c['fallback']) and not (c['ano']==2016 and c['grupo']=='ppl')}
it = it[(it.IN_ITEM_ABAN!=1) & it.NU_PARAM_B.notna()]
def P(a,b,c,th=2.0): return c + (1-c)/(1+math.exp(-1.7*a*(th-b)))
def limpa(t, arq):
    t = re.sub(r'(ENEM\s?20\d\d\s*){2,}', ' ', t)
    if arq.startswith('2014_terceira') or arq.startswith('2014_ppl'):
        def dec(w):
            if sum(1 for ch in w if 'a'<=ch<='z') > len(w)*0.5: return w
            return ''.join(chr(ord(ch)+29) if 0x21 <= ord(ch) <= 0x5D else ch for ch in w)
        t = ' '.join(dec(w) for w in t.split(' '))
    return t
rows = []
for item, g in it.groupby('CO_ITEM'):
    r0 = g.iloc[0]
    occ = [r for _, r in g.iterrows() if r.CO_PROVA in ok]
    if not occ: continue
    # preferir regular > ppl > outros
    pri = {'regular':0,'ppl':1,'p2':2,'terceira':2,'bam2':3,'digital':4}
    occ.sort(key=lambda r: pri.get(ok[r.CO_PROVA]['grupo'], 9))
    r = occ[0]; c = ok[r.CO_PROVA]
    nb = int(r.NB)
    lingua = r.get('TP_LINGUA')
    key = str(nb) if pd.isna(lingua) else f"{nb}-{'ing' if int(lingua)==0 else 'esp'}"
    q = tx[c['arquivo']].get(key)
    if not q: continue
    lingua = r.get('TP_LINGUA')
    rows.append(dict(item=int(item), ano=int(r.ANO), area=r.SG_AREA, grupo=c['grupo'], cor=c['cor'], co_prova=int(r.CO_PROVA), desc=c['desc'],
        n=nb, chave=key, arquivo=c['arquivo'], url=c['url'], gab_url=c['gab_url'], gab=r.TX_GABARITO, hab=None if pd.isna(r.CO_HABILIDADE) else int(r.CO_HABILIDADE),
        lingua=None if pd.isna(lingua) else int(lingua), a=float(r.NU_PARAM_A), b=float(r.NU_PARAM_B), c=float(r.NU_PARAM_C),
        p700=P(r.NU_PARAM_A, r.NU_PARAM_B, r.NU_PARAM_C), p500=P(r.NU_PARAM_A, r.NU_PARAM_B, r.NU_PARAM_C, 0.0), texto=limpa(q['t'], c['arquivo']), pags=q['p']))
df = pd.DataFrame(rows).sort_values('p700')
df.to_json('dados/pool.json', orient='records', force_ascii=False, indent=0)
print(len(df), df.groupby('area').size().to_dict())
print(df.groupby(['area']).p700.describe())
