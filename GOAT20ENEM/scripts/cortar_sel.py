# Uso: python cortar_sel.py <disciplina> item1 item2 ...  -> img/<item>.webp + dados/sel_<disc>.json
import sys, os, json, pandas as pd
sys.path.insert(0, os.path.dirname(__file__))
from recorte import recortar
C = os.path.expanduser('~/AppData/Local/GOAT20ENEM_cache/provas/')
disc = sys.argv[1]; items = [int(x) for x in sys.argv[2:]]
df = pd.read_json('dados/pool_cls.json').set_index('item')
out = []
OV = json.load(open('dados/overrides.json', encoding='utf-8')) if os.path.exists('dados/overrides.json') else {}
for it in items:
    r = df.loc[it]
    ov = OV.get(str(it), {})
    im = recortar(C + r.arquivo, ov.get('chave', r.chave), dpi=220, larga_forcada=ov.get('larga', False))
    for bx in ov.get('blank', []):
        from PIL import ImageDraw; ImageDraw.Draw(im).rectangle(bx, fill='white')
    if 'bottom' in ov: im = im.crop((0, ov.get('top', 0), im.width, ov['bottom']))
    if im.width > 1400: im = im.resize((1400, int(im.height*1400/im.width)))
    im.save(f'img/{it}.webp', 'WEBP', quality=80, method=6)
    im.save(os.path.expanduser(f'~/AppData/Local/GOAT20ENEM_cache/teste/{it}.png'))
    out.append(dict(item=it, ano=int(r.ano), grupo=r.grupo, desc=r.desc, cor=r.cor, n=int(r.n), chave=str(r.chave), area=r.area, disc=disc,
                    gab=r.gab, a=float(r.a), b=float(r.b), c=float(r.c), hab=None if pd.isna(r.hab) else int(r.hab), url=r.url, gab_url=r.gab_url, arquivo=r.arquivo, w=im.width, h=im.height))
    print(it, r.ano, r.grupo, r.n, r.gab, im.size, os.path.getsize(f'img/{it}.webp')//1024, 'KB')
json.dump(out, open(f'dados/sel_{disc}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
