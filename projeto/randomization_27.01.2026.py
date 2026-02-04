import pandas as pd
import random
from datetime import datetime
from pathlib import Path

# ====================================================================================#
# Configurações iniciais
# ====================================================================================#
semente = 42 
random.seed(semente)

Path("csv").mkdir(exist_ok=True)
Path("xlsx").mkdir(exist_ok=True)

# ====================================================================================#
# Estratificação e Metas
# ====================================================================================#
estrato_centros = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
meta_participantes_por_centro = {
    1: 20, 
    2: 20, 
    3: 20, 
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

centros_fixos = {
    1: {
        "1": list(range(1, 10)),
        "2": list(range(109, 118))
    },
    2: {
        "1": list(range(10, 25)),
        "2": list(range(118, 133))
    }
}

inicio_automatico = {
    "1": 25,
    "2": 133
}

inicio_contingencia = {
    "1": 217,
    "2": 325
}

limite_etiquetas_padrao = {
    "1": 108,
    "2": 216
}

# ====================================================================================#
# 🆕 PARTICIPANTES JÁ RANDOMIZADOS (DADOS REAIS DO ESTUDO)
# ====================================================================================#
participantes_ja_randomizados = {
    1: [
        ("2", "2", [110, 116]),  # Homem
        ("2", "1", [1, 2]),      # Homem
        ("2", "1", [4, 6]),      # Homem
        ("2", "2", [113, 114])   # Homem
    ],
    2: [
        ("2", "2", [123, 131]),  # Homem
        ("1", "1", [23]),        # Mulher
    ]
}

# ====================================================================================#
# Validação de Participantes Prévios
# ====================================================================================#

def validar_participantes_ja_randomizados():
    for centro, participantes in participantes_ja_randomizados.items():
        if centro not in meta_participantes_por_centro:
            raise ValueError(f"❌ Centro {centro} em participantes_ja_randomizados não existe em meta_participantes_por_centro")
        
        if len(participantes) > meta_participantes_por_centro[centro]:
            raise ValueError(
                f"❌ Centro {centro}: {len(participantes)} participantes prévios excedem meta de {meta_participantes_por_centro[centro]}"
            )
        
        for sexo, braco, etiquetas in participantes:
            esperado = 2 if sexo == "2" else 1
            if len(etiquetas) != esperado:
                raise ValueError(
                    f"❌ Centro {centro}: Sexo '{sexo}' deveria ter {esperado} etiqueta(s), mas tem {len(etiquetas)}: {etiquetas}"
                )
            
            if centro in centros_fixos and braco in centros_fixos[centro]:
                faixa_valida = centros_fixos[centro][braco]
                for et in etiquetas:
                    if et not in faixa_valida:
                        raise ValueError(
                            f"❌ Centro {centro}, Braço {braco}: Etiqueta {et} não está na faixa fixa {faixa_valida}"
                        )
    
    print("✅ Validação de participantes prévios: OK")

validar_participantes_ja_randomizados()

# ====================================================================================#
# 🔧 Lógica de Randomização AJUSTADA (Blocos Contínuos)
# ====================================================================================#

def permutacao_blocos_braco_continua(meta_total: int, previos_bracos: list):
    """
    Gera randomização considerando participantes prévios para manter blocos de 4.
    """
    n_previos = len(previos_bracos)
    n_novos = meta_total - n_previos
    
    previos_b1 = previos_bracos.count("1")
    previos_b2 = previos_bracos.count("2")
    
    meta_b1 = meta_total // 2
    meta_b2 = meta_total // 2
    
    faltam_b1 = meta_b1 - previos_b1
    faltam_b2 = meta_b2 - previos_b2
    
    print(f"   → Prévios: {previos_b1} no Braço 1, {previos_b2} no Braço 2")
    print(f"   → Faltam: {faltam_b1} no Braço 1, {faltam_b2} no Braço 2")
    
    if faltam_b1 < 0 or faltam_b2 < 0:
        raise ValueError(f"❌ Impossível balancear: participantes prévios já desequilibraram os braços")
    
    if faltam_b1 + faltam_b2 != n_novos:
        raise ValueError(f"❌ Erro de cálculo: {faltam_b1} + {faltam_b2} != {n_novos}")
    
    novos_bracos = ["1"] * faltam_b1 + ["2"] * faltam_b2
    sequencia_final = []
    pool = novos_bracos.copy()
    
    posicao_no_bloco = n_previos % 4
    if posicao_no_bloco != 0:
        faltam_no_bloco = 4 - posicao_no_bloco
        print(f"   → Completando bloco iniciado: faltam {faltam_no_bloco} participantes")
        
        complemento = pool[:faltam_no_bloco]
        random.shuffle(complemento)
        sequencia_final.extend(complemento)
        pool = pool[faltam_no_bloco:]
    
    while len(pool) >= 4:
        bloco = pool[:4]
        
        if bloco.count("1") != 2:
            b1_no_pool = pool.count("1")
            b2_no_pool = pool.count("2")
            
            if b1_no_pool >= 2 and b2_no_pool >= 2:
                bloco = ["1", "1", "2", "2"]
                pool.remove("1")
                pool.remove("1")
                pool.remove("2")
                pool.remove("2")
            else:
                bloco = pool[:4]
                pool = pool[4:]
        else:
            pool = pool[4:]
        
        random.shuffle(bloco)
        sequencia_final.extend(bloco)
    
    if pool:
        random.shuffle(pool)
        sequencia_final.extend(pool)
    
    return sequencia_final

def gerar_sexo_proporcional_com_previos(seq_braco_novos, centro, participantes_previos):
    """
    Gera distribuição de sexo considerando participantes prévios.
    Calcula proporção 4:1 sobre o TOTAL, depois subtrai os prévios.
    
    Args:
        seq_braco_novos: Lista de braços para novos participantes
        centro: ID do centro
        participantes_previos: Lista de (sexo, braco, etiquetas) já alocados
    """
    meta_total = meta_participantes_por_centro[centro]
    n_novos = len(seq_braco_novos)
    
    # Calcula meta total de mulheres no centro (4:1)
    meta_total_mulheres = meta_total // 5
    meta_total_homens = meta_total - meta_total_mulheres
    
    # Conta quantos homens/mulheres já foram alocados nos prévios
    previos_homens = sum(1 for sexo, _, _ in participantes_previos if sexo == "2")
    previos_mulheres = sum(1 for sexo, _, _ in participantes_previos if sexo == "1")
    
    # Calcula quanto FALTA de cada sexo
    faltam_mulheres = meta_total_mulheres - previos_mulheres
    faltam_homens = meta_total_homens - previos_homens
    
    print(f"   → Meta total: {meta_total_homens} H + {meta_total_mulheres} M")
    print(f"   → Já alocados: {previos_homens} H + {previos_mulheres} M")
    print(f"   → Faltam: {faltam_homens} H + {faltam_mulheres} M")
    
    # Valida
    if faltam_homens < 0 or faltam_mulheres < 0:
        raise ValueError(f"❌ Centro {centro}: participantes prévios excedem a proporção 4:1")
    
    if faltam_homens + faltam_mulheres != n_novos:
        raise ValueError(f"❌ Centro {centro}: {faltam_homens} + {faltam_mulheres} != {n_novos}")
    
    # Conta quantos de cada braço há nos novos participantes
    n_por_braco = {"1": seq_braco_novos.count("1"), "2": seq_braco_novos.count("2")}
    
    # Distribui mulheres proporcionalmente entre os braços
    mulheres_braco = {}
    for braco in ["1", "2"]:
        if n_novos == 0:
            mulheres_braco[braco] = 0
        else:
            proporcao = n_por_braco[braco] / n_novos
            mulheres_braco[braco] = round(faltam_mulheres * proporcao)
    
    # Ajuste fino
    diferenca = faltam_mulheres - sum(mulheres_braco.values())
    if diferenca != 0:
        braco_ajuste = "1" if n_por_braco["1"] >= n_por_braco["2"] else "2"
        mulheres_braco[braco_ajuste] += diferenca
    
    # Calcula homens (o restante)
    homens_braco = {}
    for braco in ["1", "2"]:
        homens_braco[braco] = n_por_braco[braco] - mulheres_braco[braco]
    
    # Monta listas por braço
    sexo_por_braco = {}
    for braco in ["1", "2"]:
        lista = ["2"] * homens_braco[braco] + ["1"] * mulheres_braco[braco]
        random.shuffle(lista)
        sexo_por_braco[braco] = lista
    
    # Retorna na ordem da sequência de braços
    sexo_final = []
    for braco in seq_braco_novos:
        sexo_final.append(sexo_por_braco[braco].pop())
    
    return sexo_final

# ====================================================================================#
# 🆕 Geração de Sequências (COM PARTICIPANTES PRÉVIOS - BLOCOS CONTÍNUOS)
# ====================================================================================#

sequencias_por_centro = {}

for centro in estrato_centros:
    meta_total = meta_participantes_por_centro[centro]
    
    if centro in participantes_ja_randomizados:
        previos = participantes_ja_randomizados[centro]
        n_previos = len(previos)
        n_novos = meta_total - n_previos
        
        print(f"\n🔄 Centro {centro}: {n_previos} prévios + {n_novos} novos = {meta_total} total")
        
        previos_bracos = [braco for _, braco, _ in previos]
        
        if n_novos > 0:
            seq_braco_novos = permutacao_blocos_braco_continua(meta_total, previos_bracos)
            seq_sexo_novos = gerar_sexo_proporcional_com_previos(seq_braco_novos, centro, previos)
            novos = list(zip(seq_sexo_novos, seq_braco_novos))
        else:
            novos = []
        
        sequencias_por_centro[centro] = [(s, b) for s, b, _ in previos] + novos
        
    else:
        print(f"\n🆕 Centro {centro}: {meta_total} participantes novos")
        seq_braco = permutacao_blocos_braco_continua(meta_total, [])
        seq_sexo = gerar_sexo_proporcional_com_previos(seq_braco, centro, [])
        sequencias_por_centro[centro] = list(zip(seq_sexo, seq_braco))

# Validação total de mulheres
total_mulheres = sum(1 for centro in estrato_centros for sexo, _ in sequencias_por_centro[centro] if sexo == "1")
print(f"\n📊 Total de mulheres geradas: {total_mulheres}")

# ====================================================================================#
# Cálculo de necessidade de etiquetas (AJUSTADO)
# ====================================================================================#

necessidade_etiquetas = {centro: {"1": 0, "2": 0} for centro in estrato_centros}
etiquetas_usadas_previas = {centro: {"1": set(), "2": set()} for centro in estrato_centros}

for centro, participantes in participantes_ja_randomizados.items():
    for sexo, braco, etiquetas in participantes:
        etiquetas_usadas_previas[centro][braco].update(etiquetas)

for centro, seq in sequencias_por_centro.items():
    n_previos = len(participantes_ja_randomizados.get(centro, []))
    novos = seq[n_previos:]
    
    for sexo, braco in novos:
        necessidade_etiquetas[centro][braco] += 2 if sexo == "2" else 1

print("\n📦 Necessidade de etiquetas NOVAS por centro:")
for centro in estrato_centros:
    print(f"  Centro {centro}: Braço 1 = {necessidade_etiquetas[centro]['1']}, Braço 2 = {necessidade_etiquetas[centro]['2']}")

# ====================================================================================#
# Geração de Pool de Etiquetas (AJUSTADO)
# ====================================================================================#

def gerar_pool_etiquetas(necessidade_etiquetas: dict, etiquetas_usadas: dict) -> dict:
    pool = {"1": {}, "2": {}}
    ponteiro_auto = inicio_automatico.copy()
    ponteiro_contingencia = inicio_contingencia.copy()
    usando_contingencia = {"1": False, "2": False}

    for centro in estrato_centros:
        for braco in ["1", "2"]:
            qtd_necessaria = necessidade_etiquetas[centro][braco]
            lista_etiquetas = []
            usadas = etiquetas_usadas_previas[centro][braco]

            if centro in centros_fixos and braco in centros_fixos[centro]:
                etiquetas_disponiveis = [e for e in centros_fixos[centro][braco] if e not in usadas]
                
                if len(etiquetas_disponiveis) >= qtd_necessaria:
                    lista_etiquetas = etiquetas_disponiveis[:qtd_necessaria]
                else:
                    lista_etiquetas.extend(etiquetas_disponiveis)
                    qtd_faltante = qtd_necessaria - len(etiquetas_disponiveis)
                    
                    print(f"⚠️ Centro {centro} (Braço {braco}): complementando com {qtd_faltante} etiquetas")
                    
                    if ponteiro_auto[braco] <= limite_etiquetas_padrao[braco]:
                        disponiveis_padrao = limite_etiquetas_padrao[braco] - ponteiro_auto[braco] + 1
                        usar_padrao = min(qtd_faltante, disponiveis_padrao)
                        lista_etiquetas.extend(range(ponteiro_auto[braco], ponteiro_auto[braco] + usar_padrao))
                        ponteiro_auto[braco] += usar_padrao
                        qtd_faltante -= usar_padrao
                    
                    if qtd_faltante > 0:
                        if not usando_contingencia[braco]:
                            print(f"🚨 Braço {braco}: Usando CONTINGÊNCIA a partir de {inicio_contingencia[braco]}")
                            usando_contingencia[braco] = True
                        lista_etiquetas.extend(range(ponteiro_contingencia[braco], ponteiro_contingencia[braco] + qtd_faltante))
                        ponteiro_contingencia[braco] += qtd_faltante
            
            else:
                if ponteiro_auto[braco] <= limite_etiquetas_padrao[braco]:
                    disponiveis_padrao = limite_etiquetas_padrao[braco] - ponteiro_auto[braco] + 1
                    usar_padrao = min(qtd_necessaria, disponiveis_padrao)
                    lista_etiquetas.extend(range(ponteiro_auto[braco], ponteiro_auto[braco] + usar_padrao))
                    ponteiro_auto[braco] += usar_padrao
                    qtd_necessaria -= usar_padrao
                
                if qtd_necessaria > 0:
                    if not usando_contingencia[braco]:
                        print(f"🚨 Braço {braco}: Usando CONTINGÊNCIA a partir de {inicio_contingencia[braco]}")
                        usando_contingencia[braco] = True
                    lista_etiquetas.extend(range(ponteiro_contingencia[braco], ponteiro_contingencia[braco] + qtd_necessaria))
                    ponteiro_contingencia[braco] += qtd_necessaria
            
            random.shuffle(lista_etiquetas)
            pool[braco][centro] = lista_etiquetas
    
    return pool

# ====================================================================================#
# 🆕 Execução da Distribuição (COM PARTICIPANTES PRÉVIOS)
# ====================================================================================#

etiquetas_por_centro = gerar_pool_etiquetas(necessidade_etiquetas, etiquetas_usadas_previas)
resultado = []

for centro in estrato_centros:
    n_previos = len(participantes_ja_randomizados.get(centro, []))
    
    if centro in participantes_ja_randomizados:
        for sexo, braco, etiquetas_originais in participantes_ja_randomizados[centro]:
            etiquetas_str = " / ".join(f"{x:03d}" for x in sorted(etiquetas_originais))
            resultado.append({
                "demografia_centro": centro,
                "demogarfia_sexo": sexo,
                "redcap_randomization_group": braco,
                "Etiquetas": etiquetas_str,
                "Tipo": "PRÉVIO"
            })
    
    for idx, (genero, braco) in enumerate(sequencias_por_centro[centro][n_previos:], start=1):
        pool_atual = etiquetas_por_centro[braco][centro]
        
        if genero == '2':
            labels_escolhidas = [pool_atual.pop(0), pool_atual.pop(0)]
            etiquetas_str = " / ".join(f"{x:03d}" for x in sorted(labels_escolhidas))
        else:
            labels_escolhidas = [pool_atual.pop(0)]
            etiquetas_str = f"{labels_escolhidas[0]:03d}"
            
        resultado.append({
            "demografia_centro": centro,
            "demogarfia_sexo": genero,
            "redcap_randomization_group": braco,
            "Etiquetas": etiquetas_str,
            "Tipo": "NOVO"
        })

# ====================================================================================#
# Processamento de Dados
# ====================================================================================#
df_final = pd.DataFrame(resultado)
df_final["redcap_randomization_number"] = pd.NA

ordem_colunas = [
    "redcap_randomization_number", 
    "redcap_randomization_group", 
    "demogarfia_sexo", 
    "demografia_centro", 
    "Etiquetas",
    "Tipo"
]
df_final = df_final[ordem_colunas]

df_randomizacao = df_final.drop(columns=["Etiquetas"])

df_etiquetas = df_final.copy()
df_etiquetas = df_etiquetas[["Etiquetas", "redcap_randomization_group", "demogarfia_sexo", "demografia_centro", "Tipo"]]
df_etiquetas.columns = ["Etiquetas", "Braço", "Sexo", "Centro", "Tipo"]

# ====================================================================================#
# Estatísticas
# ====================================================================================#
print("\n" + "="*80)
print("📊 RESUMO ESTATÍSTICO DA RANDOMIZAÇÃO")
print("="*80)

total_previos = df_final[df_final['Tipo'] == 'PRÉVIO'].shape[0]
total_novos = df_final[df_final['Tipo'] == 'NOVO'].shape[0]
print(f"\n🔢 Participantes:")
print(f"   Prévios (já randomizados): {total_previos}")
print(f"   Novos (gerados agora): {total_novos}")
print(f"   TOTAL: {len(df_final)}")

total_homens = df_final[df_final['demogarfia_sexo'] == '2'].shape[0]
total_mulheres = df_final[df_final['demogarfia_sexo'] == '1'].shape[0]
print(f"\n👥 Distribuição por Sexo:")
print(f"   Homens (código 2): {total_homens} ({total_homens/len(df_final)*100:.1f}%)")
print(f"   Mulheres (código 1): {total_mulheres} ({total_mulheres/len(df_final)*100:.1f}%)")
if total_mulheres > 0:
    print(f"   Proporção H:M = {total_homens/total_mulheres:.2f}:1")

total_braco1 = df_final[df_final['redcap_randomization_group'] == '1'].shape[0]
total_braco2 = df_final[df_final['redcap_randomization_group'] == '2'].shape[0]
print(f"\n💊 Distribuição por Braço:")
print(f"   Braço 1: {total_braco1} ({total_braco1/len(df_final)*100:.1f}%)")
print(f"   Braço 2: {total_braco2} ({total_braco2/len(df_final)*100:.1f}%)")

print(f"\n🏥 Distribuição por Centro:")
for centro in estrato_centros:
    df_centro = df_final[df_final['demografia_centro'] == centro]
    previos = df_centro[df_centro['Tipo'] == 'PRÉVIO'].shape[0]
    novos = df_centro[df_centro['Tipo'] == 'NOVO'].shape[0]
    h = df_centro[df_centro['demogarfia_sexo'] == '2'].shape[0]
    m = df_centro[df_centro['demogarfia_sexo'] == '1'].shape[0]
    b1 = df_centro[df_centro['redcap_randomization_group'] == '1'].shape[0]
    b2 = df_centro[df_centro['redcap_randomization_group'] == '2'].shape[0]
    print(f"   Centro {centro:2d}: Total={len(df_centro):2d} (Prévios={previos}, Novos={novos}) | H={h:2d} M={m:2d} | Braço1={b1:2d} Braço2={b2:2d}")

print("\n" + "="*80)

# ====================================================================================#
# Exportação
# ====================================================================================#
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

def exportar_excel(df, nome_base):
    path_excel = Path("xlsx") / f"{nome_base}.xlsx"
    with pd.ExcelWriter(path_excel, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Dados')
        worksheet = writer.sheets['Dados']
        for col in worksheet.columns:
            max_length = max(len(str(cell.value)) for cell in col)
            worksheet.column_dimensions[col[0].column_letter].width = max_length + 2

df_randomizacao.to_csv(Path("csv") / f"randomizacao_imox_semente{semente}_{timestamp}.csv", index=False, encoding='utf-8-sig')
exportar_excel(df_randomizacao, f"randomizacao_imox_semente{semente}_{timestamp}")

df_etiquetas.to_csv(Path("csv") / f"etiquetas_imox_semente{semente}_{timestamp}.csv", index=False, encoding='utf-8-sig')
exportar_excel(df_etiquetas, f"etiquetas_imox_semente{semente}_{timestamp}")

print(f"\n✅ Sucesso! Arquivos gerados para a semente {semente}")
print(f"📁 Diretórios: ./csv/ e ./xlsx/")