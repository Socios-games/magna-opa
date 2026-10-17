# GOAT20ENEM

As **20 questões mais difíceis da história do ENEM** em cada uma das 13 disciplinas, mais **40 Lendárias**: 300 questões no total. Cada uma é um recorte do caderno oficial do INEP, com o gabarito oficial e uma explicação do porquê.

- **Modo estudo:** a resposta e a explicação aparecem ao marcar a alternativa.
- **Modo simulado:** a correção vem no fim, com "Refazer as que errei".
- Para abrir, use `index.html` (as questões já estão dentro da página). Fora do claude.ai, o histórico de tentativas fica no `localStorage` do navegador.

## Critério
- **Disciplinas (13 × 20):** maior parâmetro **b** da TRI, segundo os microdados do INEP de 2009 a 2025 (regular, PPL/reaplicação, 2ª aplicação, digital e Libras). É o mesmo critério dos rankings famosos, como o do Xeque-Mate. As questões citadas por cursinhos entram sempre e levam o selo "citada".
- **Lendárias (40):** menor taxa de acerto real (ranking do Akira ENEM, com dados do INEP), com foco em Matemática e Linguagens.
- Itens anulados ficam de fora. O PPL de 2016 não está nos microdados.

## Estrutura
- `index.html`, `img/`, `data/questoes.json`: o app.
- `explicacoes/<Disciplina>.json`: tema e comentário de cada questão.
- `dados/`: seleção por disciplina (`sel_*.json`), fontes das citadas, ajustes de recorte (`overrides.json`) e o casamento entre caderno e CO_PROVA.
- `scripts/`: o pipeline. Ele extrai os itens dos microdados por range request, baixa os cadernos e gabaritos do INEP, casa CO_PROVA com o caderno pelo gabarito, monta o pool por TRI, recorta as questões (PyMuPDF) e monta os dados.

Pipeline: `itens_microdados.py` → `dic_microdados.py` → `master.py` → `baixar_provas.py` → `casar.py` → `pool.py` → `classif.py` → `cortar_sel.py <Disciplina> itens...` → `montar.py`.
Os PDFs e microdados brutos não estão no repositório, porque são grandes. Os scripts baixam tudo de novo.
