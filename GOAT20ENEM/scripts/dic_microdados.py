# Baixa o dicionário (xlsx/ods) dos microdados via range requests.
import sys, os, zipfile, io
sys.path.insert(0, os.path.dirname(__file__))
from itens_microdados_lib import CurlIO
ano, out = sys.argv[1], sys.argv[2]
z = zipfile.ZipFile(io.BufferedReader(CurlIO(f"https://download.inep.gov.br/microdados/microdados_enem_{ano}.zip"), buffer_size=1<<20))
for i in z.infolist():
    n = i.filename
    if "dicion" in n.lower() and n.lower().endswith((".xlsx", ".ods", ".xls")):
        open(os.path.join(out, f"dic_{ano}{os.path.splitext(n)[1]}"), "wb").write(z.read(n)); print(ano, n)
