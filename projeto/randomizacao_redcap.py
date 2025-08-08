import pandas as pd
import random
import openpyxl

# ====================================================================================#
# Configurações iniciais
# ====================================================================================#
# Semente para reprodutibilidade (42 e 81)
# semente =81
semente = 42 
random.seed(semente)

# ====================================================================================#
# Centros e metas (total por centro)
# ====================================================================================#
estrato_centros = [1,2,3,4,5,6,7,8,9,10]  # Lista de centros (códigos dos centros - REDCAP DAGs)
meta_participantes_por_centro = {
    1:12,
    2:8,
    3:16,
    4:8,
    5:12,
    6:12,
    7:8,
    8:8,
    9:8,
    10:12
}

# ====================================================================================#
# Braços do estudo
# ====================================================================================#
bracos = ['1', '2']  # Braços do estudo
# Braços com códigos específicos 1: '2506091'/ Oxandrolona, 2: '2506092'/Placebo

# ====================================================================================#
# Gênero dos participantes
# ====================================================================================#
generos = ['1', '2']  # Gêneros dos participantes
# Gêneros com códigos específicos 1: '1'/ Feminino, 2: '2'/ Masculino

# ====================================================================================#
# Função: Gerar etiquetas

## Regras:
### 1. Etiquetas: gerar listas por centro e por braço, SEM sobreposição
### 2. Regra: Distribuição será dada por braço em cada centro, consome 3/4 * meta etiquetas(porque em cada braço metade dos participantes; e dentro do braço 1:1 sexo; homens consomem 2 cada e mulheres 1 cada → n_homens*2 + n_mulheres*1 = 3/4 * meta)
# ====================================================================================#

def gerar_etiquetas_por_centro(etiqueta_inicio: int) -> dict[int, list[int]]:
    atual = etiqueta_inicio
    etiquetas = {}
    for centro in estrato_centros:
        meta = meta_participantes_por_centro[centro]
        quantidade = (3 * meta) // 4  # etiquetas por braço neste centro
        faixa = list(range(atual, atual+quantidade))
        random.shuffle(faixa)
        etiquetas[centro] = faixa
        atual += quantidade
    return etiquetas

# ====================================================================================#
# gerando as etiquetas
# ====================================================================================#
etiquetas_por_centro = {
    "1": gerar_etiquetas_por_centro(1), # Inicia em 1
    "2": gerar_etiquetas_por_centro(109), # Inicia em 109
}

# ====================================================================================#
# Checagem de duplicadas dentro de cada braço
# ====================================================================================#
for braco in ["1", "2"]:
    duplicata = [x for c in estrato_centros for x in etiquetas_por_centro[braco][c]]
    assert len(duplicata) == len(set(duplicata)), f"Duplicatas encontradas no braço {braco}: {duplicata}"

# ====================================================================================#
# Permutação em blocos: sequência (gênero e braço) por centro
# cada bloco deverá conter: 1 homem para o braço 1, 1 homem para o braço 2, 1 mulher para o braço 1 e 1 mulher para o braço 2
# ====================================================================================#

def permutacao_blocos(meta: int):
    if meta % 4 != 0:
        raise ValueError(f"Meta {meta} não é múltiplo de 4, não é possível fazer permutação em blocos.")
    blocos = meta // 4
    sequecncia = []
    base = [
        ("2", "1"),
        ("2", "2"),
        ("1", "1"),
        ("1", "2"),
    ]
    for _ in range(blocos):
        bloco = base[:] # copia
        random.shuffle(bloco)  # embaralha a ordem dentro do bloco
        sequecncia.extend(bloco)
    return sequecncia

# ====================================================================================#
# Rodar distribuição em todos os centros e braços
# ====================================================================================#
resultado = []
for centro in estrato_centros:
    meta = meta_participantes_por_centro[centro]
    
    #Validação: etiquetas por braço no centro
    esperado_por_braco = (meta // 4) * 3  # 3/4 da meta por braço
    for braco in bracos:
        disposicao = len(etiquetas_por_centro[braco][centro])
        if disposicao < esperado_por_braco:
            raise ValueError(f"Etiquetas insuficientes no centro {centro} para o braço {braco}."
                             f"Esperado: {esperado_por_braco}, encontrado: {disposicao}")
    
    # Permutação por gênero e braço para o centro
    sequencia = permutacao_blocos(meta)
    
    # Distribuição das etiquetas conforme a sequência
    for genero, braco in sequencia:
        etiquetas = etiquetas_por_centro[braco][centro]
        if genero == '2': # Homem -> consome 2 etiquetas
            etiquetas = [etiquetas.pop(0), etiquetas.pop(0)]
            etiquetas_str = " / ".join(f"{x:03}" for x in etiquetas)
        else:  # Mulher -> consome 1 etiqueta
            etiquetas_str = f"{etiquetas.pop(0):03}"
        resultado.append([centro, genero, braco, etiquetas_str])
        

# ====================================================================================#
# Dataframe final
# ====================================================================================#

df_final = pd.DataFrame(resultado, columns = ["Centro", "Genero", "Braco", "Etiquetas"])
# mapeia renomes (corrigi "demogarfia" -> "demografia")
cols_map = {
    "Centro": "demografia_centro",
    "Genero": "demogarfia_sexo",
    "Braco":  "redcap_randomization_group",
    # "Etiquetas" já está ok
}

# renomeia e adiciona a coluna vazia
df_final = (
    df_final
      .rename(columns=cols_map)
      .assign(redcap_randomization_number=pd.NA)
)

df_final = df_final[["redcap_randomization_number", "redcap_randomization_group","demogarfia_sexo","demografia_centro", "Etiquetas"]]
df_randomizacao = df_final.copy()
df_randomizacao = df_randomizacao[["redcap_randomization_number", "redcap_randomization_group","demogarfia_sexo","demografia_centro"]]

# ====================================================================================#
# Dataframe etiquetas
# ====================================================================================#
df_etiquetas = df_final.copy()

df_etiquetas = df_etiquetas[["Etiquetas", "redcap_randomization_number","demogarfia_sexo","demografia_centro"]]
cols_map = {
    "Etiquetas": "redcap_randomization_number",
    "redcap_randomization_number": "redcap_randomization_group"
}

df_etiquetas = df_etiquetas.rename(columns=cols_map)


# ====================================================================================##
# Exportar os resultados para csv e excel - Randomização dos participantes
# ====================================================================================##

# Exportar para CSV na pasta csv
nome_arquivo_csv = f'randomizacao_imox_semente{semente}.csv'
df_randomizacao.to_csv(r'csv\{}'.format(nome_arquivo_csv), index=False, encoding='utf-8-sig')

# Exportar para Excel na pasta excel
nome_arquivo_excel = f'randomizacao_imox_semente{semente}.xlsx'
# Verifica se o diretório existe, caso contrário, cria
with pd.ExcelWriter(r'xlsx\{}'.format(nome_arquivo_excel), engine='openpyxl') as writer:
    df_randomizacao.to_excel(writer, index=False, sheet_name='Randomizacao Imox Semente {}'.format(semente))
    # Formatação da planilha
    planilha = writer.book
    abas = writer.sheets['Randomizacao Imox Semente {}'.format(semente)]
    for col in abas.columns:
        max_length = max(len(str(cell.value)) for cell in col)
        adjusted_width = (max_length + 2)
        abas.column_dimensions[col[0].column_letter].width = adjusted_width

# ====================================================================================##
# Exportar os resultados para csv e excel - distribuição das etiquetas
# ====================================================================================##

# Exportar para CSV na pasta csv
nome_arquivo_csv = f'randomizacao_imox_semente{semente}_etiquetas.csv'
df_etiquetas.to_csv(r'csv\{}'.format(nome_arquivo_csv), index=False, encoding='utf-8-sig')

# Exportar para Excel na pasta excel
nome_arquivo_excel = f'randomizacao_imox_semente{semente}_etiquetas.xlsx'
# Verifica se o diretório existe, caso contrário, cria
with pd.ExcelWriter(r'xlsx\{}'.format(nome_arquivo_excel), engine='openpyxl') as writer:
    df_etiquetas.to_excel(writer, index=False, sheet_name='Randomizacao Imox Semente {}'.format(semente))
    # Formatação da planilha
    planilha = writer.book
    abas = writer.sheets['Randomizacao Imox Semente {}'.format(semente)]
    for col in abas.columns:
        max_length = max(len(str(cell.value)) for cell in col)
        adjusted_width = (max_length + 2)
        abas.column_dimensions[col[0].column_letter].width = adjusted_width
        


#Exluir depois
# Exportar para CSV na pasta csv
nome_arquivo_csv = f'randomizacao_imox_semente{semente}_completo.csv'
df_final.to_csv(r'csv\{}'.format(nome_arquivo_csv), index=False, encoding='utf-8-sig')