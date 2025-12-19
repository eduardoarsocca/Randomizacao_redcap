import pandas as pd
import random
from datetime import datetime
from pathlib import Path

# ====================================================================================#
# Configurações Iniciais
# ====================================================================================#
semente = 81
random.seed(semente)

Path("csv").mkdir(exist_ok=True)
Path("xlsx").mkdir(exist_ok=True)

estrato_centros = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
meta_participantes_por_centro = {
    1: 12, 2: 20, 3: 16, 4: 8, 5: 12, 6: 12, 
    7: 4, 8: 8, 9: 8, 10: 12, 11: 4
}

# ====================================================================================#
# GESTÃO DE LOGÍSTICA (Onde a mágica acontece)
# ====================================================================================#

# 1. INVENTÁRIO MANUAL: Use isto para definir o que cada centro recebeu FISICAMENTE.
# Se precisar redistribuir a etiqueta 11 do Centro 1 para o 11, tire da lista do 1 e ponha na do 11.
inventario_manual = {
    1: {
        "1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12], # A 11 foi removida daqui
        "2": list(range(109, 121))
    },
    11: {
        "1": [11, 201, 202, 203], # A 11 entrou aqui como sobra vinda do Centro 1
        "2": [301, 302, 303]
    }
}

# 2. CONFIGURAÇÃO DE GERAÇÃO AUTOMÁTICA
# Define o ponto de partida para centros que não têm estoque manual definido.
inicio_automatico = {"1": 13, "2": 121}

def preparar_estoque_estudo() -> dict:
    """
    Organiza o pool de etiquetas garantindo que números manuais/redistribuídos 
    sejam protegidos e não duplicados.
    """
    pool_final = {"1": {}, "2": {}}
    
    # Criamos uma "Blacklist" de todos os números já alocados manualmente no estudo
    blacklist = {"1": set(), "2": set()}
    for c in inventario_manual:
        for b in ["1", "2"]:
            blacklist[b].update(inventario_manual[c].get(b, []))

    proximo_id = inicio_automatico.copy()

    for centro in estrato_centros:
        meta = meta_participantes_por_centro[centro]
        qtd_necessaria = (3 * meta) // 4 

        for braco in ["1", "2"]:
            # Puxa o que já foi definido manualmente (incluindo redistribuições)
            estoque_atual = inventario_manual.get(centro, {}).get(braco, []).copy()
            
            # Se o manual não for suficiente para a meta, gera o restante automaticamente
            while len(estoque_atual) < qtd_necessaria:
                candidato = proximo_id[braco]
                if candidato not in blacklist[braco]:
                    estoque_atual.append(candidato)
                    blacklist[braco].add(candidato)
                proximo_id[braco] += 1
            
            # Randomiza a ordem de saída das ampolas para este centro
            random.shuffle(estoque_atual)
            pool_final[braco][centro] = estoque_atual
            
    return pool_final

# ====================================================================================#
# Lógica de Blocos e Atribuição
# ====================================================================================#

def permutacao_blocos(meta: int):
    base = [("2", "1"), ("2", "2"), ("1", "1"), ("1", "2")]
    sequencia = []
    for _ in range(meta // 4):
        bloco = base[:]
        random.shuffle(bloco)
        sequencia.extend(bloco)
    return sequencia

estoque_total = preparar_estoque_estudo()
resultado = []

for centro in estrato_centros:
    meta = meta_participantes_por_centro[centro]
    sequencia_centro = permutacao_blocos(meta)
    
    for genero, braco in sequencia_centro:
        pool = estoque_total[braco][centro]
        
        if genero == '2': # Homem consome 2
            labels = [pool.pop(0), pool.pop(0)]
            etiqueta_str = " / ".join(f"{x:03}" for x in sorted(labels))
        else:             # Mulher consome 1
            etiqueta_str = f"{pool.pop(0):03}"
            
        resultado.append({
            "demografia_centro": centro,
            "demogarfia_sexo": genero,
            "redcap_randomization_group": braco,
            "Etiquetas": etiqueta_str
        })

# ====================================================================================#
# Exportação
# ====================================================================================#
df_final = pd.DataFrame(resultado)
df_final["redcap_randomization_number"] = pd.NA
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Salva arquivo completo para conferência logística
df_final.to_csv(Path("csv") / f"randomizacao_completa_semente{semente}_{timestamp}.csv", 
                index=False, encoding='utf-8-sig')

print(f"Lista gerada com sucesso. Semente: {semente}")