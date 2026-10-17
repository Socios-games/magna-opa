# Extrai ITENS_PROVA_<ano>.csv do zip de microdados do INEP via range requests (curl).
import io, subprocess, sys, zipfile, os
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36"
class CurlIO(io.RawIOBase):
    def __init__(s, url):
        s.url = url; s.pos = 0
        h = subprocess.run(["curl","-sI","-m","60","-A",UA,url],capture_output=True,text=True).stdout
        s.size = int([l for l in h.splitlines() if l.lower().startswith("content-length")][-1].split(":")[1])
    def seekable(s): return True
    def readable(s): return True
    def tell(s): return s.pos
    def seek(s, off, wh=0):
        s.pos = off if wh==0 else s.pos+off if wh==1 else s.size+off
        return s.pos
    def read(s, n=-1):
        if n is None or n < 0: n = s.size - s.pos
        if n == 0 or s.pos >= s.size: return b""
        end = min(s.size, s.pos+n) - 1
        for _ in range(4):
            d = subprocess.run(["curl","-s","-m","300","-A",UA,"-r",f"{s.pos}-{end}",s.url],capture_output=True).stdout
            if len(d) == end-s.pos+1: break
        s.pos += len(d); return d
    def readinto(s, b):
        d = s.read(len(b)); b[:len(d)] = d; return len(d)
ano = sys.argv[1]; out = sys.argv[2]
url = f"https://download.inep.gov.br/microdados/microdados_enem_{ano}.zip"
z = zipfile.ZipFile(io.BufferedReader(CurlIO(url), buffer_size=1<<20))
names = [i.filename for i in z.infolist()]
alvo = [n for n in names if "ITENS_PROVA" in n.upper() and n.lower().endswith(".csv")]
print(ano, "->", alvo or [n for n in names][:30])
for n in alvo:
    with open(os.path.join(out, f"ITENS_PROVA_{ano}.csv"), "wb") as f: f.write(z.read(n))
