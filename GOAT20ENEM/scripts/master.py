import pandas as pd, json, re
cop=json.load(open('fontes/co_prova.json',encoding='utf-8'))
rows=[]
for a in range(2009,2026):
    f=f'fontes/itens/ITENS_PROVA_{a}.csv'
    try: d=pd.read_csv(f,sep=';',encoding='utf-8')
    except UnicodeDecodeError: d=pd.read_csv(f,sep=';',encoding='latin1')
    d.columns=[c.upper() for c in d.columns]
    d['ANO']=a
    d['DESC']=d['CO_PROVA'].map(lambda x: (cop.get(str(a),{}).get(str(x)) or [None,None])[1])
    rows.append(d)
d=pd.concat(rows,ignore_index=True)
d.to_csv('dados/itens_todos.csv',index=False,encoding='utf-8')
def app(desc):
    if desc is None or desc!=desc: return 'desconhecida'
    s=desc.lower()
    if 'libras' in s: return 'libras'
    if 'ledor' in s or 'braile' in s or 'braille' in s or 'adaptada' in s or 'ampliada' in s or 'especializado' in s: return 'adaptada'
    if 'digital' in s: return 'digital'
    if 'segunda' in s: return 'segunda'
    if 'bam2' in s: return 'bam2'
    if 'reaplica' in s or 'ppl' in s: return 'ppl'
    return 'regular'
d['APP']=d['DESC'].map(app)
ok=d[(d.IN_ITEM_ABAN!=1)&d.NU_PARAM_B.notna()]
pri={'regular':0,'ppl':1,'digital':2,'segunda':3,'bam2':4,'libras':5,'adaptada':6,'desconhecida':7}
ok=ok.assign(P=ok.APP.map(pri))
best=ok.sort_values(['P','CO_PROVA']).groupby(['CO_ITEM']).first().reset_index()
apps=ok.groupby('CO_ITEM').APP.apply(lambda s: sorted(set(s),key=pri.get)).rename('APPS')
best=best.merge(apps,on='CO_ITEM')
best['ANO_MIN']=ok.groupby('CO_ITEM').ANO.min().reindex(best.CO_ITEM).values
best=best.sort_values('NU_PARAM_B',ascending=False)
best.to_csv('dados/itens_unicos.csv',index=False,encoding='utf-8')
print(len(d),'linhas;',len(best),'itens unicos')
print(best.groupby('SG_AREA').size())
print(best.APP.value_counts())
for ar in ['CN','CH','LC','MT']:
    print('==',ar); print(best[best.SG_AREA==ar].head(12)[['ANO','CO_ITEM','APP','TX_COR','CO_POSICAO','NU_PARAM_A','NU_PARAM_B','NU_PARAM_C','TX_GABARITO','APPS']].to_string())
