# Junta seleções + explicações + fontes em app/data/questoes.json e copia imagens.
import json, os, glob, shutil
DISC = [('Matemática','MT'),('Física','CN'),('Química','CN'),('Biologia','CN'),('História','CH'),('Geografia','CH'),('Filosofia','CH'),('Sociologia','CH'),
        ('Português','LC'),('Literatura','LC'),('Artes','LC'),('Inglês','LC'),('Espanhol','LC'),('Lendárias','LEN')]
APP = {'regular':'Aplicação regular','ppl':'PPL / Reaplicação','p2':'2ª aplicação','terceira':'3ª aplicação','bam2':'2ª aplicação','digital':'ENEM Digital'}
fontes = json.load(open('dados/fontes.json', encoding='utf-8'))
labels = json.load(open('dados/rotulos.json', encoding='utf-8')) if os.path.exists('dados/rotulos.json') else {}
import pandas as pd
_pool = pd.read_json('dados/pool_cls.json').set_index('item')
_it = pd.read_csv('dados/itens_todos_nb.csv').drop_duplicates('CO_PROVA').set_index('CO_PROVA')
def cor_de(item):
    t = str(_it.loc[_pool.loc[item].co_prova].TX_COR).strip().lower()
    for a, b in [('azul','Azul'),('amarel','Amarelo'),('branc','Branco'),('rosa','Rosa'),('cinza','Cinza'),('verde','Verde'),('laranja','Laranja'),('rox','Roxo')]:
        if a in t: return b
    return t.title()
os.makedirs('app/img', exist_ok=True); os.makedirs('app/data', exist_ok=True)
qs = []; discs = []
for nome, area in DISC:
    f = f'dados/sel_{nome}.json'; e = f'explicacoes/{nome}.json'
    sel = json.load(open(f, encoding='utf-8')) if os.path.exists(f) else []
    ex = json.load(open(e, encoding='utf-8')) if os.path.exists(e) else {}
    pront = [s for s in sel if str(s['item']) in ex]
    discs.append({'id': nome, 'area': area, 'n': len(pront)})
    for s in sorted(pront, key=lambda s: -s['b']):
        k = str(s['item'])
        shutil.copy(f"img/{k}.webp", f"app/img/{k}.webp")
        qs.append({'id': k, 'disc': nome, 'area': area, 'ano': s['ano'], 'aplic': labels.get(k) or APP.get(s['grupo'], s['grupo']),
                   'cor': cor_de(s['item']), 'n': s['n'], 'gab': s['gab'],
                   'b': round(s['b'], 3), 'a': round(s['a'], 3), 'img': f"img/{k}.webp", 'w': s['w'], 'h': s['h'],
                   'tema': ex[k]['tema'], 'com': ex[k]['com'], 'fontes': fontes.get(k, []), 'prova': s['url'], 'gabUrl': s['gab_url']})
def _limpa(v):
    if isinstance(v, float) and v != v: return None
    if isinstance(v, dict): return {k: _limpa(x) for k, x in v.items()}
    if isinstance(v, list): return [_limpa(x) for x in v]
    return v
qs = _limpa(qs)
json.dump({'disciplinas': discs, 'questoes': qs}, open('app/data/questoes.json', 'w', encoding='utf-8'), ensure_ascii=False, allow_nan=False)
print({d['id']: d['n'] for d in discs}, len(qs))
# embute os dados na página (sem depender de fetch)
_h = open('app/index.html', encoding='utf-8').read()
import re as _re
_j = json.dumps({'disciplinas': discs, 'questoes': qs}, ensure_ascii=False, allow_nan=False).replace('</', '<\/')
_h = _re.sub(r'(<script id="dados" type="application/json">).*?(</script>)', lambda m: m.group(1) + _j + m.group(2), _h, flags=_re.S)
open('app/page.html', 'w', encoding='utf-8').write(_h)
