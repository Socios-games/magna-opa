import json, re, unicodedata, pandas as pd
df = pd.read_json('dados/pool.json')
def n(s): return unicodedata.normalize('NFKD', s).encode('ascii','ignore').decode().lower()
K = {
 'Física': r'velocidade|aceleracao|forca|energia cinetica|potencia|corrente eletrica|resistor|tensao|circuito|voltagem|\bohm|watt|joule|newton|onda|frequencia|comprimento de onda|lente|espelho|refracao|optica|temperatura|calor|dilatacao|pressao|empuxo|massa especifica|campo magnetico|campo eletrico|carga eletrica|atrito|movimento|trajetoria|gravidade|gravitacional|som|decibe|eficiencia|termodinamica|kwh|\bv\b|\bm/s|\bhz|ampere|capacitor|inducao|lampada|fusivel|choque eletrico|radiacao|luz',
 'Química': r'reacao|molecula|atomo|ion|ions|ph\b|acido|base|sal|oxidacao|reducao|eletrolise|pilha|equilibrio quimico|concentracao|mol\b|mols|g/mol|solucao|soluto|solvente|composto|organico|ligacao|polimero|hidrocarboneto|combustao|entalpia|catalisador|isomer|funcao organica|ester|alcool|cetona|aldeido|amina|carboxil|radioativ|meia-vida|elemento quimico|tabela periodica|precipit|estequiometr|titulacao|oxido|grupo funcional|formula estrutural|cloro|sodio|carbono|nitrogenio|enxofre|ferro',
 'Biologia': r'celula|gene|genetic|dna|rna|proteina|enzima|especie|ecossistema|ecologic|populacao|bacteria|virus|fungo|planta|vegetal|animal|organismo|evolucao|selecao natural|fotossintese|respiracao celular|hormonio|sangue|sistema imune|vacina|doenca|parasita|mitose|meiose|cromossomo|alelo|heranca|cadeia alimentar|bioma|nicho|mutacao|tecido|orgao|embriao|metabolismo|insulina|glicose|mosquito|inseto|vertebrado|fisiolog|anticorpo|antibiotico',
 'História': r'seculo|colonial|colonia|imperio|republica|revolucao|ditadura|regime militar|getulio|vargas|escravid|escravo|abolicao|monarquia|idade media|feudal|renascimento|iluminismo|guerra|grecia|roma|romano|medieval|absolutismo|nazis|fascis|guerra fria|independencia|cabanagem|canudos|sesmaria|bandeirante|jesuita|portugueses|metropole|oligarquia|coronelismo|era vargas|estado novo|constituicao de 18|tenentismo|cafe com leite|antiguidade|faraos|egito|mesopotamia|cruzadas',
 'Geografia': r'relevo|clima|climatic|bioma|bacia hidrografica|urbaniza|populacao|migracao|industria|agricult|agronegocio|globaliza|territori|cartograf|escala|mapa|latitude|longitude|fuso|placas tectonicas|erosao|solo|vegetacao|cerrado|caatinga|amazonia|desmatamento|rio|hidrograf|precipitacao|massa de ar|el nino|efeito estufa|aquecimento global|matriz energetica|geopolitic|fronteira|regiao|metropole|metropolizacao|demograf|economia|exportac|commodit|blocos economicos|mercosul|uniao europeia|transporte|ambiental|agua|aquifero|dessalinizacao',
 'Filosofia': r'filosof|platao|socrates|aristoteles|descartes|kant|hume|locke|hobbes|rousseau|nietzsche|sartre|hegel|spinoza|maquiavel|santo agostinho|tomas de aquino|epicuro|estoic|sofist|etica|moral|metafisic|epistemolog|razao|conhecimento|verdade|virtude|liberdade|existencialis|empiris|racionalis|ser humano|alma|logica|dialetica|heidegger|foucault|arendt|habermas|adorno|schopenhauer|pascal|montaigne|bacon|wittgenstein|kierkegaard|merleau',
 'Sociologia': r'sociolog|durkheim|weber|marx|bourdieu|bauman|giddens|sociedade|social|cidadania|movimentos sociais|desigualdade|classe social|trabalho|capitalismo|estratificacao|cultura|etnocentr|identidade|genero|raca|racismo|preconceito|discriminacao|direitos|democracia|estado|poder|ideologia|alienacao|industria cultural|mobilidade social|instituic|socializacao|fato social|anomia|burocracia|indigena|quilombol|feminis',
 'Literatura': r'poema|poeta|poesia|verso|estrofe|soneto|romance|narrador|personagem|conto|cronica|modernis|romantis|realismo|naturalismo|parnasian|simbolis|barroco|arcadismo|machado de assis|drummond|bandeira|guimaraes rosa|clarice|graciliano|jose de alencar|castro alves|cecilia meireles|vinicius|joao cabral|mario de andrade|oswald|lirico|eu lirico|literari|obra literaria|fragmento do romance|ficcao|escritor',
 'Artes': r'\barte\b|artista|pintura|quadro|tela|escultura|museu|obra de arte|instalacao|performance|danca|teatro|musica|cancao|cinema|fotografia|grafite|arquitetura|vanguarda|cubismo|surrealismo|impressionis|expressionis|dadais|pop art|bienal|exposicao|xilogravura|artes visuais|cenico|coreograf|composicao|ritmo|melodia|samba|espetaculo',
 'Educação Física': r'esporte|atividade fisica|exercicio fisico|corpo|corporal|jogo|ginastica|futebol|atleta|olimpi|luta|capoeira|treinamento|sedentar|lazer|danca|condicionamento',
 'Português': r'linguagem|lingua|variacao linguistica|norma|gramatic|verbo|substantivo|adjetivo|pronome|conjuncao|oracao|sintax|concordancia|regencia|coesao|coerencia|genero textual|argumenta|interlocutor|funcao da linguagem|metalinguag|ironia|ambiguidade|sentido|texto|campanha|propaganda|anuncio|charge|tirinha|cartum|infografico|redes sociais|internet|hipertexto|digital|neologismo|dicionario|palavra|expressao',
}
AR = {'CN':['Física','Química','Biologia'], 'CH':['História','Geografia','Filosofia','Sociologia'],
      'LC':['Português','Literatura','Artes','Educação Física'], 'MT':['Matemática']}
def classif(r):
    if r.area == 'MT': return 'Matemática'
    if r.area == 'LC' and r.lingua in (0,1) : return 'Inglês' if r.lingua == 0 else 'Espanhol'
    t = n(r.texto)
    sc = {d: len(re.findall(K[d], t)) for d in AR[r.area]}
    if r.area == 'LC' and r.hab:
        h = r.hab
        if 12 <= h <= 14: sc['Artes'] += 4
        elif 15 <= h <= 17: sc['Literatura'] += 4
        elif 9 <= h <= 11: sc['Educação Física'] += 4
        elif 5 <= h <= 8: sc['Português'] += 0
        else: sc['Português'] += 2
    best = max(sc, key=sc.get)
    return best
df['disc'] = df.apply(classif, axis=1)
df.to_json('dados/pool_cls.json', orient='records', force_ascii=False, indent=0)
print(df.groupby('disc').size())
