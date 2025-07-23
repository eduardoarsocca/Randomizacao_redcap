import pandas as pd
import random
import openpyxl




# ====================================================================================#
# Configurações iniciais
# ====================================================================================#
# Semente para reprodutibilidade
random.seed(42)

#tamanho da amostra (n)
total_participantes = 160  

# Variáveis de interesse
# Estrato 1: Centros (Sites)
estrato_centros = [18,19,20,21,22,23,24,25,26,27]  # Lista de centros (códigos dos centros)

#Meta do total de participantes por centro
#Cade centro tem uma meta unica de participantes, mas o total de participantes no estudo (somando todos os centros) é fixo em total_participantes
meta_participantes_por_centro = {
    18: 16,
    19: 16,
    20: 16,
    21: 16,
    22: 16,
    23: 16,
    24: 16,
    25: 16,
    26: 16,
    27: 16
}

# os participentes serão alocados em cada centro de acordo com a meta de participantes por centro
numero_centros = len(estrato_centros)
# Verificar se a soma das metas de participantes por centro é igual ao total de participantes
assert sum(meta_participantes_por_centro.values()) == total_participantes, (
    f"A soma das metas de participantes por centro ({sum(meta_participantes_por_centro.values())})"
    f" deve ser igual ao total de participantes ({total_participantes})."
)

# Distribuição de participantes por centro
participantes_por_centro = total_participantes // numero_centros

# Estrato 2: Sexo
estrato_genero = ['Masculino', 'Feminino']

# Distribuição de participantes por genero por centro
# Cada Centro deverá ter 50% de participantes masculinos e 50% de participantes femininos
# Cada centro tem uma meta distinta de participantes (meta_participantes_por_centro), mas a distribuição de gênero é fixa
# Portanto, o número de participantes por gênero em cada centro será metade do total de participantes por centro
participantes_por_genero_por_centro = participantes_por_centro // 2



# ====================================================================================#
# Parâmetros de randomização em blocos (block randomization)
# ====================================================================================#
## Tamanho do bloco
tamanho_bloco = 4
assert participantes_por_genero_por_centro % tamanho_bloco == 0,(
    f"O número de participantes por gênero em cada centro ({participantes_por_genero_por_centro})"
    f" deve ser divisível pelo tamanho do bloco ({tamanho_bloco})."
)

# ====================================================================================#
# Randomização em blocos
# ====================================================================================#
# Função para criar blocos de randomização
def criar_blocos_randomizacao(tamanho_amostral: int, tamanho_bloco: int) -> list:
    assert tamanho_amostral % tamanho_bloco == 0,(
        f"{tamanho_amostral} não é divisivel por {tamanho_bloco}"
    )

    alocacao = []
    
    total_blocos = tamanho_amostral // tamanho_bloco
    print(total_blocos, type(total_blocos))
    for _ in range(total_blocos):
        bloco = (['2506091'] * (tamanho_bloco //2) + ['2506092'] * (tamanho_bloco //2))
        random.shuffle(bloco)
        alocacao.extend(bloco)
    return alocacao
   
# ====================================================================================#
# Construir registros estratificados por Centro → Gênero, considerando a meta de participantes por centro
# ====================================================================================#

registros = []

# Estrato 1: Alocar participantes por centro
for centro in estrato_centros:
    #1. Alocar Homens (estrato_2_a) e Mulheres (estrato_2_b) separadamente
    estrato_2_a = criar_blocos_randomizacao(
        participantes_por_genero_por_centro,
        tamanho_bloco
    )
    estrato_2_b = criar_blocos_randomizacao(
        participantes_por_genero_por_centro,
        tamanho_bloco
    )
    #Preencher os registros do estrato_2_a
    for braco in estrato_2_a:
        registros.append({
            'Centro': centro,
            'Gênero': 'Masculino',
            'Alocação': braco
        })
    #Preencher os registros do estrato_2_b
    for braco in estrato_2_b:
        registros.append({  
            'Centro': centro,
            'Gênero': 'Feminino',
            'Alocação': braco
        })

df_registros = pd.DataFrame(registros)
print(df_registros)
# ====================================================================================#
# Calcular quantas ampolas são necessárias por grupo e sexo (com desvio de + 50%)
# ====================================================================================#
# Neste estudo Homens receberão dois pellets (ampolas) e Mulheres receberão um pellet (ampola)
# As ampolas deverão ser catalogadas por centro e braco (exemplo: para as ampolas do centro 1 para o braco 2506092, o nome devera cer "centro_1_P001", "centro_1_P002", etc.)
# O número de ampolas por centro e braco será igual ao número previsto de participantes alocados no braco (com desvio de + 50%)

b1_estrato_2_a = sum(
    1 for r in registros
    if r['Gênero'] == 'Masculino' and r['Alocação'] == '2506091')*2
b1_estrato_2_b = sum(
    1 for r in registros
    if r['Gênero'] == 'Feminino' and r['Alocação'] == '2506091'
)
total_ampolas_2506091 = (b1_estrato_2_a  + b1_estrato_2_b)  # +50% de desvio

b2_estrato_2_a = sum(
    1 for r in registros
    if r['Gênero'] == 'Masculino' and r['Alocação'] == '2506092')*2

b2_estrato_2_b = sum(
    1 for r in registros
    if r['Gênero'] == 'Feminino' and r['Alocação'] == '2506092'
)

total_ampolas_2506092 = (b2_estrato_2_a + b2_estrato_2_b)  # +50% de desvio


total_geral = total_ampolas_2506091 + total_ampolas_2506092

print(b1_estrato_2_a, b1_estrato_2_b, total_ampolas_2506091)
print(b2_estrato_2_a, b2_estrato_2_b, total_ampolas_2506092)
print("Total de ampolas:", total_geral)
# ====================================================================================#
# Calcular a quantidade de ampolas necessárias por centro e braço
# ====================================================================================#
total_ampolas = {}

for centro in estrato_centros:
    for braco in ['2506091', '2506092']:
        # Contar quantos participantes masculinos neste (centro, braco)
        qtd_masc = df_registros[
            (df_registros['Centro'] == centro) &
            (df_registros['Gênero'] == 'Masculino') &
            (df_registros['Alocação'] == braco)
        ].shape[0]

        # Contar quantos participantes femininos neste (centro, braco)
        qtd_fem = df_registros[
            (df_registros['Centro'] == centro) &
            (df_registros['Gênero'] == 'Feminino') &
            (df_registros['Alocação'] == braco)
        ].shape[0]

        # Calcular a quantidade de ampolas necessárias
        if braco == '2506091':
            qtd_ampolas = (qtd_masc * 2) + qtd_fem
        else:  # 2506092
            qtd_ampolas = (qtd_masc * 2) + qtd_fem
        
        # calcular o total de ampolas
        total_ampolas[(centro, braco)] = qtd_ampolas

# ====================================================================================#
# Gerar o código das etiqueta das ampolas de forma aleatória (embaralhar)
# ====================================================================================#
# Os textos das etiquetas das ampolas serão geradas de forma aleatória, de acordo com o número de ampolas necessárias por Centro, gênero e braço.
# Cada centro terá na etiqueta das ampolas o nome do centro (ou código do centro ) e o número da amostra (exemplo: centro_1_P001, centro_1_P002, etc.)
def gerar_etiquetas_ampola(centro:int, braco: str, numero: int) -> list:
    """
    Gera uma lista de etiquetas de ampolas para um determinado centro e braco.
    As etiquetas são formatadas como "centro_{centro}_{braco}{numero}", onde:
    - centro: é o número do centro (exemplo: 18,19,20,21,22,23,24,25,26,27). Cada centro receberá uma quantidade exata de ampolas (18 ampolas de 2506091 e 18 ampolas de 2506092)
    -- O centro 18 receberá as ampolas 3 ampolas de 2506091 e 3 de 2506092, sendo 2 ampolas de 2506091 para homens e 1 ampola para mulheres. O mesmo para as ampolas de 2506092.
    - braco: é o braço do estudo (exemplo: "2506092" para 2506092, "2506091" para Oxandrolona)
    - numero: é o número da amostra (001 a 108 para o 2506091 e 109 a 216 para o 2506092)
    Os códigos serão embaralhados antes de retornar para garantir aleatoriedade na distribuição
    """
    etiquetas = []
    for i in range(1, numero + 1):
        etiqueta = f"centro_{centro}_{braco}{str(i).zfill(3)}"
        etiquetas.append(etiqueta)
    
    random.shuffle(etiquetas)  # Embaralhar as etiquetas para garantir aleatoriedade
    return etiquetas
# ====================================================================================#
# Gerar dicionario de pool de etiquetas
pool_etiquetas = {}

for (centro, braco), quantidade in total_ampolas.items():
    pool_etiquetas[(centro, braco)] = gerar_etiquetas_ampola(centro, braco, quantidade)
    
# ====================================================================================#
# Atribuir as etiquetas a cada participante
# ====================================================================================#
lista_ampola1=[]
lista_ampola2=[]

for idx, row in df_registros.iterrows():
    centro = row['Centro']
    braco = row['Alocação']
    genero = row['Gênero']
    pool_key = (centro, braco)
    
    if genero == 'Masculino':
        etiqueta1 = pool_etiquetas[pool_key].pop(0)  # Retira a primeira etiqueta do pool
        etiqueta2 = pool_etiquetas[pool_key].pop(0)  # Retira a segunda etiqueta do pool
        lista_ampola1.append(etiqueta1)
        lista_ampola2.append(etiqueta2)
    else:  # Feminino
        etiqueta1 = pool_etiquetas[pool_key].pop(0)
        lista_ampola1.append(etiqueta1)
        lista_ampola2.append('')

#Adicionar as colunas das etiquetas no dataframe
df_registros['Etiqueta_Ampola1'] = lista_ampola1
df_registros['Etiqueta_Ampola2'] = lista_ampola2

# ====================================================================================#
# Inserir o randomization_id e ordenar as colunas
# ====================================================================================#
df_registros.insert(
    loc=0,
    column='randomization_id',
    value=[f"R{str(i+1).zfill(3)}" for i in range(len(df_registros))]
)

# Reordena colunas para exibir: randomization_id, Centro, Gênero, Alocação, Ampola1,Ampola2
colunas_reordenadas = [
    'randomization_id', 
    'Centro', 
    'Gênero', 
    'Alocação', 
    'Etiqueta_Ampola1', 
    'Etiqueta_Ampola2'
]

df_registros = df_registros[colunas_reordenadas]

# ====================================================================================#
# Exportar o DF para .csv e .xlsx
# ====================================================================================#

# Exportar para CSV na pasta csv
df_registros.to_csv(r'.\csv\randomizacao_imox.csv', index=False, encoding='utf-8-sig')
# Exportar para Excel na pasta excel
df_registros.to_excel(r'.\xlsx\randomizacao_imox.xlsx', index=False, engine='openpyxl')
# ====================================================================================#