import re

DESCRICAO = """
Estrutura do dicionário Python:
    'INFO'
        'FILE_NAME'                     Nome do arquivo importado
        'BASE_NAME'                     Nome base anotado no RNXS
        'QTD_BRANCHS'                   Quantidade de branchs
        'QTD_GRUPS'                     Quantidade de grupos
        'INT_GRUPS'                     Intervalos dos grupos
        'TIPO'                          O valor pode ser 'Simples' / 'Alterável' / 'Queimável'
        'TIPOS_XS'                      O valor pode ser ['MACRO'] se for "Simples"/'Alterável' ou ['MACRO', 'MICRO'] quando for tipo "Queimável"
        'TIPOS_ALTERAÇÕES_MACRO'        O valor pode ser ['BASE']  se for "Simples"/'Queimável' ou ['BASE', 'CR']     quando for tipo "Alterável"
        'TIPOS_XS_MACRO'                Lista de todos tipos de seção de choque macroscópicas listadas conforme abaixo
        'TIPOS_XS_MICRO'                Lista de todos tipos de seção de choque microscópicas listadas conforme abaixo (só existe para tipo 'Queimável')
        'QTD_QUEIMA'                    Quantidade de passos de queima (só existe para tipo 'Queimável')
        'PASSOS_QUEIMA'                 Lista de todos passos de queima (só existe para tipo 'Queimável')
        'LISTA_NUCLIDEOS'               Lista de todos nuclídeos conforme listados abaixo (só existe para tipo 'Queimável')
        Pode adicionar outras informações a respeito da Estrutura se achar necessário
        Os fatores de descontinuidade deixa para uma próxima etapa

    MACRO
        BASE
            INV_SPD
            SIG_TRP
            SIG_ABS
            SIG_SP0
            SIG_KCS
            (Somente existem as chaves abaixos se for tipo "queimável")
            ABS_FREE
            FIS_FREE
            NFS_FREE
            KFS_FREE
            KCS_FREE
            SP0_FREE
        
        CR (somente existe essa chave e as que estão dentro para o tipo "Alterável")
            INV_SPD
            SIG_TRP
            SIG_ABS
            SIG_SP0
            SIG_KCS


            Para cada uma de todas das chaves acima (chaves que estão dentro de BASE e/ou CR):
                XS (valores basicos de seção de choque)
                    *lista baseadas em passos de queima*
                        Dentro deve conter uma lista de valores baseadas nos grupos de energia.
                BRANCH (variações baseadas em branch calculations)
                    *lista baseadas em passos de queima*
                        Dentro deve conter uma lista de branch, dentro contendo listas de valores baseadas nos grupos de energia.



    MICRO (somente existe no tipo queimável)
        U234
        U235
        U236
        U237
        U238
        U239
        NP237
        NP238
        NP239
        PU238
        PU239
        PU240
        PU241
        PU242
        AM241
        AM242
        AM242M
        AM243
        CM242
        CM243
        CM244
        RU105
        RH105
        CD113
        I135
        XE135
        BA140
        LA140
        ND147
        ND148
        ND149
        PM147
        PM148
        PM148M
        PM149
        SM147
        SM148
        SM149

        Para cada uma das chaves acima:
            SIG_ABS
            SIG_FIS
            SIG_NFS
            SIG_KFS
            SIG_CPTG
            SIG_CPT2N

            Para cada uma das chaves acima:
                XS (valores basicos de seção de choque)
                    *lista baseadas em passos de queima*
                        Dentro deve conter uma lista de valores baseadas nos grupos de energia.
                BRANCH (variações baseadas em branch calculations)
                    *lista baseadas em passos de queima*
                        Dentro deve conter uma lista de branch, dentro contendo listas de valores baseadas nos grupos de energia.
"""

def infoRNXS(nodalXS=None):
    
    if nodalXS is None:
        print("Você deve passar como parâmetro para essa função um dicionário python estruturado.")
        print(DESCRICAO)

    else:
        # Acessar a INFO: Imprime TODAS as chaves e valores armazenados em 'INFO'
        print("\n\n\n\n\n=== INFORMAÇÕES DO ARQUIVO (INFO) ===")
        for chave, valor in nodalXS['INFO'].items():
            print(f"{chave}: {valor}")
        print("=====================================\n")

        # 1. Acessar XS Macro (Passo 0 -> Grupo 1 -> index 0)
        xs_abs_grupo1 = nodalXS['MACRO']['BASE']['SIG_ABS']['XS'][0][0]
        print(f"MACRO BASE SIG_ABS (Passo 0, Grupo 1): \nnodalXS['MACRO']['BASE']['SIG_ABS']['XS'][0][0] = {xs_abs_grupo1}\n")

        # 2. Acessar BRANCH Macro (Passo 0, Branch 0, Grupo 1)
        branch_abs = nodalXS['MACRO']['BASE']['SIG_ABS']['BRANCH'][0][0][0]
        print(f"MACRO BASE SIG_ABS (Passo 0, Branch 0, Grupo 1): \nnodalXS['MACRO']['BASE']['SIG_ABS']['BRANCH'][0][0][0] = {branch_abs}\n")

        # 3. Se for do tipo Alterável, acessar XS da Barra de Controle (CR)
        if nodalXS['INFO']['TIPO'] == 'Alterável':
            cr_abs_grupo1 = nodalXS['MACRO']['CR']['SIG_ABS']['XS'][0][0]
            print(f"MACRO CR SIG_ABS (Passo 0, Grupo 1): \nnodalXS['MACRO']['CR']['SIG_ABS']['XS'][0][0] = {cr_abs_grupo1}\n")

        # 4. Se for do tipo Queimável, acessar XS Micro do Urânio 235
        if nodalXS['INFO']['TIPO'] == 'Queimável':
            micro_u235_abs = nodalXS['MICRO']['U235']['SIG_ABS']['XS'][1][0]
            print(f"MICRO U235 SIG_ABS (Passo 1, Grupo 1): \nnodalXS['MICRO']['U235']['SIG_ABS']['XS'][1][0] = {micro_u235_abs}")


def getRNXS(caminho_arquivo):
    """
    Lê um arquivo RNXS e converte todas as seções de choque e metadados para um dicionário Python estruturado.
    """
    with open(caminho_arquivo, 'r') as f:
        conteudo = f.read()

    nodalXS = {'INFO': {}, 'MACRO': {}}
    info = nodalXS['INFO']
    info['FILE_NAME'] = caminho_arquivo

    # 1. INFO Básica (Nome e Grupos)
    match_seg = re.search(r"'KEY_SEGMENT'\n'([^']+)'", conteudo)
    info['BASE_NAME'] = match_seg.group(1).strip() if match_seg else "Desconhecido"

    match_neu = re.search(r"'KEY_NEUGRP'\n\s*(\d+).*?\n([\s\S]*?)'KEY_STATE'", conteudo)
    if match_neu:
        info['QTD_GRUPS'] = int(match_neu.group(1))
        info['INT_GRUPS'] = [float(x) for x in match_neu.group(2).split()]
    else:
        info['QTD_GRUPS'] = 0
        info['INT_GRUPS'] = []
    num_grupos = info['QTD_GRUPS']

    # 2. Tipo de Arquivo
    if "'KEY_ACTIN'" in conteudo or "'KEY_ACTXS'" in conteudo:
        tipo = 'Queimável'
    elif "! CR tables" in conteudo or "'B4C_R" in conteudo:
        tipo = 'Alterável'
    else:
        tipo = 'Simples'

    info['TIPO'] = tipo
    info['TIPOS_XS'] = ['MACRO', 'MICRO'] if tipo == 'Queimável' else ['MACRO']
    info['TIPOS_ALTERAÇÕES_MACRO'] = ['BASE', 'CR'] if tipo == 'Alterável' else ['BASE']

    # 3. Mapeamento Global de Passos de Queima
    passos_queima = []
    for m in re.finditer(r"! Burnup \[MWd/kg\]:\s+([0-9\.E\+\-]+)", conteudo):
        bu = float(m.group(1))
        if bu not in passos_queima:
            passos_queima.append(bu)
            
    if not passos_queima:
        passos_queima = [0.0]

    info['QTD_QUEIMA'] = len(passos_queima)
    if tipo == 'Queimável':
        info['PASSOS_QUEIMA'] = passos_queima

    # Função central de inserção com pré-alocação indexada
    def adicionar_xs(match_obj, dic_alvo, set_tipos, bu_idx):
        tipo_xs = match_obj.group(1)
        valores = [float(v) for v in match_obj.group(2).split()]
        if not valores: return
        
        passo_tamanho = len(valores) // num_grupos
        qtd_branchs = passo_tamanho - 1
        if 'QTD_BRANCHS' not in info: 
            info['QTD_BRANCHS'] = qtd_branchs
        
        xs_base = valores[0::passo_tamanho][:num_grupos]
        branches = [valores[b+1::passo_tamanho][:num_grupos] for b in range(qtd_branchs)]
        
        # Pré-aloca a lista com "Nones" para garantir que o índice de queima sempre bata
        if tipo_xs not in dic_alvo:
            dic_alvo[tipo_xs] = {
                'XS': [None] * info['QTD_QUEIMA'],
                'BRANCH': [None] * info['QTD_QUEIMA']
            }
            
        dic_alvo[tipo_xs]['XS'][bu_idx] = xs_base
        dic_alvo[tipo_xs]['BRANCH'][bu_idx] = branches
        set_tipos.add(tipo_xs)

    # 4. Processamento MACRO
    nodalXS['MACRO']['BASE'] = {}
    if tipo == 'Alterável': 
        nodalXS['MACRO']['CR'] = {}
    tipos_macro = set()

    # Isola o texto puramente MACRO (Apaga blocos de Isótopos e FDF para não haver conflitos)
    texto_macro = re.sub(r"'KEY_ACTXS'[\s\S]*?(?='KEY_|$)", "", conteudo)
    texto_macro = re.sub(r"'KEY_SIDEFDF'[\s\S]*?(?='KEY_|$)", "", texto_macro)
    texto_macro = re.sub(r"'KEY_CORNFDF'[\s\S]*?(?='KEY_|$)", "", texto_macro)

    blocos_bu_macro = re.split(r"(! Burnup \[MWd/kg\]:\s+[0-9\.E\+\-]+)", texto_macro)
    for i in range(1, len(blocos_bu_macro), 2):
        bu_val = float(re.search(r"([0-9\.E\+\-]+)", blocos_bu_macro[i]).group(1))
        bu_idx = passos_queima.index(bu_val)
        texto_bu = blocos_bu_macro[i+1]
        
        # Divide BASE e CR
        if tipo == 'Alterável':
            partes = re.split(r"! CR tables", texto_bu)
            texto_base = partes[0]
            texto_cr = partes[1] if len(partes) > 1 else ""
        else:
            texto_base = texto_bu
            texto_cr = ""
            
        # Extrai MACRO BASE (! XS type:) -> Note que \s* não captura "Actinide"
        for m in re.finditer(r"!\s*XS\s+type:\s*(\w+)\s*\n([\s\S]*?)(?=\n!|\n'|$)", texto_base):
            adicionar_xs(m, nodalXS['MACRO']['BASE'], tipos_macro, bu_idx)
            
        # Extrai MACRO CR
        if texto_cr:
            for m in re.finditer(r"!\s*XS\s+type:\s*(\w+)\s*\n([\s\S]*?)(?=\n!|\n'|$)", texto_cr):
                adicionar_xs(m, nodalXS['MACRO']['CR'], tipos_macro, bu_idx)

    info['TIPOS_XS_MACRO'] = list(tipos_macro)

    # 5. Processamento MICRO (Apenas Queimável)
    if tipo == 'Queimável':
        nodalXS['MICRO'] = {}
        tipos_micro = set()
        lista_nuclideos = []
        
        def limpar_nome(nome):
            match = re.search(r"([A-Z]{1,2}\d{3}M?)", nome)
            return match.group(1) if match else nome.strip("'- ")

        # Lista de Nuclídeos
        for b in [r"'KEY_ACTIN'", r"'KEY_FP'"]:
            bloco = re.search(b + r"\n\s*\d+\n([\s\S]*?)(?:'KEY_|$)", conteudo)
            if bloco:
                lista_nuclideos.extend([limpar_nome(iso) for iso in re.findall(r"'([^']+)'", bloco.group(1))])
        info['LISTA_NUCLIDEOS'] = lista_nuclideos

        # Isola e processa o bloco Micro
        bloco_actxs = re.search(r"'KEY_ACTXS'([\s\S]*?)(?='KEY_SIDEFDF'|'KEY_CORNFDF'|'KEY_ENDFILE'|$)", conteudo)
        if bloco_actxs:
            fragmentos_iso = re.split(r"! Isotope:\s*", bloco_actxs.group(1))[1:]
            for frag in fragmentos_iso:
                nome_limpo = limpar_nome(frag.strip().split('\n')[0].strip())
                if nome_limpo not in nodalXS['MICRO']:
                    nodalXS['MICRO'][nome_limpo] = {}
                
                # Divide por passos de queima
                blocos_bu_iso = re.split(r"(! Burnup \[MWd/kg\]:\s+[0-9\.E\+\-]+)", frag)
                for i in range(1, len(blocos_bu_iso), 2):
                    bu_val = float(re.search(r"([0-9\.E\+\-]+)", blocos_bu_iso[i]).group(1))
                    bu_idx = passos_queima.index(bu_val)
                    
                    # Regex restrita APENAS para Micro (Actinide ou FP)
                    for m in re.finditer(r"!\s*(?:Actinide|FP)\s+XS\s+type:\s*(\w+)\s*\n([\s\S]*?)(?=\n!|\n'|$)", blocos_bu_iso[i+1]):
                        adicionar_xs(m, nodalXS['MICRO'][nome_limpo], tipos_micro, bu_idx)

        info['TIPOS_XS_MICRO'] = list(tipos_micro)

    return nodalXS


