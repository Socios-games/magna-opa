# Recorta uma questão do caderno (todas as colunas/páginas que ela ocupa) e empilha numa imagem.
import sys, os, re, io, pymupdf
from PIL import Image, ImageChops
sys.path.insert(0, os.path.dirname(__file__))
from extrair import linhas, HDR
LANG = re.compile(r'(INGL[ÊE]S|ESPANHOL)', re.I)
def _chave_linhas(L):
    """Mapeia cada linha -> chave de questão (mesma lógica de extrair.questoes) e devolve headers."""
    qs = {}; cur = None; lang = None; hdr = {}
    for r in L:
        ml = LANG.search(r[6])
        if ml and len(r[6]) < 120 and ('op' in r[6].lower() or 'estrangeira' in r[6].lower() or r[6].strip().upper() == ml.group(1).upper() or 'quest' in r[6].lower()):
            lang = 'ing' if ml.group(1).upper().startswith('INGL') else 'esp'
        m = HDR.match(r[6])
        if m:
            n = int(m.group(1)); key = n
            if n in qs or (lang and (n <= 5 or 91 <= n <= 95)):
                key = f'{n}-{lang or "x"}'
                if key in qs:
                    outra = {'ing': 'esp', 'esp': 'ing'}.get(lang)
                    key = f'{n}-{outra}' if outra and f'{n}-{outra}' not in qs else f'{n}-{lang or "x"}2'
            cur = key; qs[cur] = []; hdr[cur] = r; continue
        if cur is not None: qs[cur].append(r)
    return qs, hdr
def faixas(doc):
    """Por página: limite superior (fim do cabeçalho) e inferior (início do rodapé)."""
    out = {}
    for pi, pg in enumerate(doc):
        H = pg.rect.height; top, bot = 0.045*H, 0.955*H
        for b in pg.get_text('dict')['blocks']:
            if b['type'] != 0: continue
            for l in b['lines']:
                t = ''.join(s['text'] for s in l['spans']).strip()
                x0, y0, x1, y1 = l['bbox']
                if y1 < 0.08*H and re.search(r'p[áa]gina|caderno|\*\w+\*', t, re.I): top = max(top, y1+2)
                if y0 > 0.92*H and re.search(r'p[áa]gina|caderno|\*\w+\*', t, re.I): bot = min(bot, y0-2)
        out[pi] = (top, bot)
    return out
def recortar(pdf, chave, dpi=170, larga_forcada=False):
    doc = pymupdf.open(pdf)
    L = linhas(doc)
    qs, hdr = _chave_linhas(L)
    k = int(chave) if str(chave).isdigit() else chave
    if k not in qs: raise KeyError(chave)
    fx = faixas(doc)
    # ordem global das linhas para achar o próximo header
    keys = list(qs.keys()); i = keys.index(k)
    h0 = hdr[k]; h1 = hdr[keys[i+1]] if i+1 < len(keys) else None
    segs = []
    # percorrer (pág, col) do header atual até o próximo header
    def pos(r): return (r[0], r[1], r[2])
    start = pos(h0); end = pos(h1) if h1 else (len(doc)-1, 1, 1e9)
    # colunas que contêm linhas da questão
    WM = re.compile(r'^(do Ensino M[ée]dio|Exame Nacional|enem|\d{1,2}|20\d\d|\*.*\*|.*P[áa]gina \d+.*)$', re.I)
    WM2 = re.compile(r'Exame Nacional|do Ensino M[ée]dio|(ENEM\s?20\d\d\s*){2,}', re.I)
    ql = [r for r in qs[k] if not WM.match(r[6].strip()) and not WM2.search(r[6])]
    seq = [(p, c) for p in range(len(doc)) for c in (0, 1)]
    i0 = seq.index((h0[0], h0[1]))
    allowed = set(seq[i0:i0+3])
    cols = sorted(set((r[0], r[1]) for r in ql if (r[0], r[1]) in allowed) | {(h0[0], h0[1])})
    feitas_largas = set()
    for (pg, col) in cols:
        page = doc[pg]; W = page.rect.width; mid = W/2
        if pg in feitas_largas: continue
        lp = [r for r in ql if r[0] == pg]
        larga = larga_forcada or sum(1 for r in lp if r[3] < mid-20 and r[4] > mid+20 and (r[4]-r[3]) > 0.6*W) >= 2
        if larga:
            feitas_largas.add(pg)
            top, bot = fx[pg]
            y0 = h0[5] + 1 if pg == h0[0] else top
            y1 = (h1[2] - 2) if (h1 and h1[0] == pg and h1[2] > y0) else min(bot, max(r[5] for r in ql if r[0] == pg) + 8)
            pix = page.get_pixmap(clip=pymupdf.Rect(18, y0, W-18, y1), dpi=dpi)
            im = Image.open(io.BytesIO(pix.tobytes('png'))).convert('RGB')
            if any(m in os.path.basename(pdf) for m in MARCADOS): im = sem_verde(im)
            segs.append(apara(im)); continue
        top, bot = fx[pg]
        y0 = h0[5] + 1 if (pg, col) == (h0[0], h0[1]) else top
        x0, x1 = (18, mid - 2) if col == 0 else (mid + 2, W - 18)
        cl = [r for r in L if r[0] == pg and r[1] == col and top <= r[2] <= bot and (r[4]-r[3]) > 0.5*(mid-30)]
        if cl:
            x0 = max(x0, min(r[3] for r in cl) - 6); x1 = min(x1, max(r[4] for r in cl) + 6)
        if h1 and (pg, col) == (h1[0], h1[1]):
            y1 = h1[2] - 2
        else:
            ys = [r[5] for r in ql if (r[0], r[1]) == (pg, col)]
            last = max(ys) if ys else y0
            figs = [pymupdf.Rect(d['rect']) for d in page.get_drawings()] + [pymupdf.Rect(d['bbox']) for d in page.get_image_info()]
            for f in figs:
                if f.x1 > x0 and f.x0 < x1 and f.y0 >= y0 - 2 and f.y0 < last + 20 and f.y1 < bot and f.height < 0.8*page.rect.height:
                    last = max(last, f.y1)
            ylast = max([r[5] for r in ql if (r[0], r[1]) == (pg, col)] or [y0])
            y1 = max(min(bot, last + 8), ylast + 3)
        stop = [r[2] for r in L if r[0] == pg and r[1] == col and y0 < r[2] < y1 and re.search(r'^Quest[õo]es de \d|^Exame Nacional|^LINGUAGENS, C[ÓO]DIGOS|^CI[ÊE]NCIAS (HUMANAS|DA NATUREZA) E SUAS|^MATEM[ÁA]TICA E SUAS', r[6].strip(), re.I)]
        if stop: y1 = min(stop) - 4
        if y1 - y0 < 8: continue
        clip = pymupdf.Rect(x0, y0, x1, y1)
        pix = page.get_pixmap(clip=clip, dpi=dpi)
        im = Image.open(io.BytesIO(pix.tobytes('png'))).convert('RGB')
        if any(m in os.path.basename(pdf) for m in MARCADOS): im = sem_verde(im)
        segs.append(apara(im))
    segs = [s for s in segs if s is not None]
    if not segs: raise ValueError('sem segmentos')
    Wd = max(s.width for s in segs); Ht = sum(s.height for s in segs) + 24*(len(segs)-1)
    out = Image.new('RGB', (Wd + 40, Ht + 40), 'white'); y = 20
    for s in segs: out.paste(s, (20, y)); y += s.height + 24
    return out
MARCADOS = ['2010_ppl_d1__', '2010_ppl_d2__', '2013_regular_d1__']
def sem_verde(im):
    import numpy as np
    a = np.asarray(im).astype(int)
    g = (a[:,:,1] - np.maximum(a[:,:,0], a[:,:,2])) > 40
    a[g] = 255
    return Image.fromarray(a.astype('uint8'))
def apara(im):
    bg = Image.new('RGB', im.size, 'white')
    diff = ImageChops.difference(im, bg).convert('L').point(lambda p: 255 if p > 25 else 0)
    bb = diff.getbbox()
    if not bb: return None
    return im.crop((max(0, bb[0]-6), max(0, bb[1]-6), min(im.width, bb[2]+6), min(im.height, bb[3]+6)))
if __name__ == '__main__':
    pdf, chave, out = sys.argv[1:4]
    recortar(pdf, chave).save(out)
