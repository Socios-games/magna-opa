# Escolhe 1 caderno por (ano, aplicação, dia) e baixa prova + gabarito pareado.
import json, re, os, subprocess, collections
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36"
C=os.path.expanduser('~/AppData/Local/GOAT20ENEM_cache')
d=json.load(open('fontes/pdf_links.json',encoding='utf-8'))
bad=re.compile(r'ledor|ampliada|amplia|_sup|braile|braille|nvda|libras|_com_gab|SUPER',re.I)
def grupo(a,f):
    s=f.lower()
    if 'digital' in s: return 'digital'
    if 'ppl' in s or 'reaplicacao' in s: return 'ppl'
    if 'terceira' in s: return 'terceira'
    if s.startswith('p2_'): return 'p2'
    m=re.search(r'_d(\d)_',s)
    if a=='2025' and m and m.group(1) in '3456': return {'3':'bam2','4':'bam2','5':'ppl','6':'ppl'}[m.group(1)]
    return 'regular'
def dia(a,f):
    s=f.lower()
    m=re.search(r'_d(\d)_',s) or re.search(r'dia(\d)',s) or re.search(r'(\d)_?dia',s)
    if m: n=int(m.group(1)); return 1 if n%2==1 else 2
    if 'ch_cn' in s: return 1
    if 'lc_mt' in s: return 2
    m=re.search(r'_(\d\d)_',s) or re.search(r'cad_(\d)',s)
    if m: return 1 if int(m.group(1)) in (1,2,3,4,9,10) else 2
    return 0
esc={}
for a,l in d.items():
    for i,(u,t) in enumerate(l):
        if not t.startswith('Prova'): continue
        f=u.split('/')[-1]
        if bad.search(f) or 'Especializado' in t or 'Leitor' in t: continue
        gab=next((u2 for u2,t2 in l[i+1:i+2] if t2.startswith('Gabarito')),None)
        k=(a,grupo(a,f),dia(a,f))
        if 'espanhol' in f: continue
        esc.setdefault(k,[]).append((f,u,gab))
sel=[]
for k,v in sorted(esc.items()):
    v.sort(key=lambda x:(0 if 'azul' in x[0].lower() else 1))
    sel.append((k,v[0]))
os.makedirs(C+'/provas',exist_ok=True)
man=[]
for (a,g,di),(f,u,gab) in sel:
    fn=f'{C}/provas/{a}_{g}_d{di}__{f}'
    if not os.path.exists(fn): subprocess.run(['curl','-s','-m','300','-A',UA,'-o',fn,u])
    gf=f"{C}/gab/{a}__{gab.split('/')[-1]}" if gab else None
    man.append(dict(ano=int(a),grupo=g,dia=di,arquivo=fn,url=u,gab=gf,gab_url=gab))
    print(a,g,di,f,'| gab:',gab.split('/')[-1] if gab else None)
json.dump(man,open('dados/provas_sel.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
