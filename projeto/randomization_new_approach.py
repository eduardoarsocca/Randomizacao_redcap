import pandas as pd
import random
from datetime import datetime
from pathlib import Path

# ====================================================================================#
# Configurações iniciais
# ====================================================================================#
semente = 81
# semente = 42 
random.seed(semente)

# Configuração de pastas (Modern Python: pathlib)
Path("csv").mkdir(exist_ok=True)
Path("xlsx").mkdir(exist_ok=True)

# ====================================================================================#
# Estratificação e Metas
# ====================================================================================#
estrato_centros = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
meta_participantes_por_centro = {
    1: 12, 
    2: 20, 
    3: 16, 
    4: 8, 
    5: 12, 
    6: 12, 
    7: 4, 
    8: 8, 
    9: 8, 
    10: 12, 
    11: 4
}

# ====================================================================================#
# CONFIGURAÇÃO DE ETIQUETAS (Ampolas Físicas)
# ====================================================================================#

# 1. Defina aqui os centros que JÁ possuem etiquetas físicas (Não serão alterados)
centros_fixos = {
    1: {
        "1": list(range(1, 10)),    # Braço 1: Etiquetas 001 a 009
        "2": list(range(109, 118))  # Braço 2: Etiquetas 109 a 117
    },
    2: {
        "1": list(range(10, 25)),   # Braço 1: Etiquetas 010 a 024
        "2": list(range(118, 133))  # Braço 2: Etiquetas 118 a 132
    }
}

# 2. Defina onde começa a contagem AUTOMÁTICA para os demais centros
inicio_automatico = {
    "1": 25,   # Próxima etiqueta disponível para Braço 1
    "2": 133   # Próxima etiqueta disponível para Braço 2
}

def gerar_pool_etiquetas() -> dict:
    """
    Gera o dicionário mestre de etiquetas: {braço: {centro: [lista_etiquetas]}}
    """
    pool = {"1": {}, "2": {}}
    ponteiro_auto = inicio_automatico.copy()

    for centro in estrato_centros:
        meta = meta_participantes_por_centro[centro]
        # Regra 3/4: Homem(2) + Mulher(1) em blocos de 4. 
        # Para cada 4 pessoas, usamos 6 etiquetas (3 por braço)
        qtd_necessaria = (3 * meta) // 4 

        for braco in ["1", "2"]:
            if centro in centros_fixos:
                # Usa as etiquetas já enviadas para este centro
                lista_etiquetas = centros_fixos[centro][braco].copy()
                if len(lista_etiquetas) < qtd_necessaria:
                    raise ValueError(f"Centro {centro} (Braço {braco}) fixo tem apenas {len(lista_etiquetas)} "
                                     f"etiquetas, mas precisa de {qtd_necessaria}.")
            else:
                # Gera etiquetas sequenciais automaticamente
                start = ponteiro_auto[braco]
                lista_etiquetas = list(range(start, start + qtd_necessaria))
                ponteiro_auto[braco] += qtd_necessaria
            
            # Embaralha para a randomização
            random.shuffle(lista_etiquetas)
            pool[braco][centro] = lista_etiquetas
    return pool

# ====================================================================================#
# Lógica de Randomização em Blocos
# ====================================================================================#

def permutacao_blocos(meta: int):
    if meta % 4 != 0:
        raise ValueError(f"Meta {meta} não é múltiplo de 4 para bloco equilibrado.")
    
    sequencia = []
    # Bloco equilibrado: 1H/B1, 1H/B2, 1M/B1, 1M/B2
    base = [("2", "1"), ("2", "2"), ("1", "1"), ("1", "2")]
    
    for _ in range(meta // 4):
        bloco = base[:]
        random.shuffle(bloco)
        sequencia.extend(bloco)
    return sequencia

# ====================================================================================#
# Execução da Distribuição
# ====================================================================================#

etiquetas_por_centro = gerar_pool_etiquetas()
resultado = []

for centro in estrato_centros:
    meta = meta_participantes_por_centro[centro]
    sequencia_centro = permutacao_blocos(meta)
    
    for genero, braco in sequencia_centro:
        pool_atual = etiquetas_por_centro[braco][centro]
        
        if genero == '2': # Masculino consome 2 etiquetas
            labels_escolhidas = [pool_atual.pop(0), pool_atual.pop(0)]
            etiquetas_str = " / ".join(f"{x:03}" for x in sorted(labels_escolhidas))
        else:             # Feminino consome 1 etiqueta
            labels_escolhidas = [pool_atual.pop(0)]
            etiquetas_str = f"{labels_escolhidas[0]:03}"
            
        resultado.append({
            "demografia_centro": centro,
            "demogarfia_sexo": genero,
            "redcap_randomization_group": braco,
            "Etiquetas": etiquetas_str
        })

# ====================================================================================#
# Processamento de Dados (Pandas)
# ====================================================================================#
df_final = pd.DataFrame(resultado)
df_final["redcap_randomization_number"] = pd.NA

# Reordenando para o padrão REDCap
ordem_colunas = [
    "redcap_randomization_number", 
    "redcap_randomization_group", 
    "demogarfia_sexo", 
    "demografia_centro", 
    "Etiquetas"
]
df_final = df_final[ordem_colunas]

# DF para Alocação (Sem as etiquetas visíveis para evitar quebra de cegamento se necessário)
df_randomizacao = df_final.drop(columns=["Etiquetas"])

# DF de Etiquetas (Logística)
df_etiquetas = df_final.copy().rename(columns={
    "Etiquetas": "redcap_randomization_number",
    "redcap_randomization_number": "redcap_randomization_group" # Mantendo seu padrão de renome
})

# ====================================================================================#
# Exportação com Formatação
# ====================================================================================#
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

def exportar_excel(df, nome_base):
    path_excel = Path("xlsx") / f"{nome_base}_{timestamp}.xlsx"
    with pd.ExcelWriter(path_excel, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Dados')
        worksheet = writer.sheets['Dados']
        for col in worksheet.columns:
            max_length = max(len(str(cell.value)) for cell in col)
            worksheet.column_dimensions[col[0].column_letter].width = max_length + 2

# Exportando arquivos
df_randomizacao.to_csv(Path("csv") / f"randomizacao_imox_semente{semente}.csv", index=False, encoding='utf-8-sig')
exportar_excel(df_randomizacao, f"randomizacao_imox_semente{semente}")

df_etiquetas.to_csv(Path("csv") / f"etiquetas_imox_semente{semente}.csv", index=False, encoding='utf-8-sig')
exportar_excel(df_etiquetas, f"etiquetas_imox_semente{semente}")

print(f"Sucesso! Arquivos gerados para a semente {semente}.")