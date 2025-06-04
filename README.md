# Projeto de Randomização REDCap

## 1. Visão Geral

Este projeto implementa uma rotina de **randomização estratificada em blocos** para um ensaio clínico multicêntrico, alocando participantes em dois braços (“Tratamento” e “Placebo”) de forma balanceada por:

- **Centro (Site)**: quatro centros participantes (1, 2, 3 e 4);
- **Gênero**: 50% masculino e 50% feminino em cada centro.

Além disso, o script calcula a quantidade de ampolas (vials) necessárias por braço e gênero (com 50% de desvio), gera etiquetas aleatórias para essas ampolas e faz a atribuição dos rótulos a cada participante. Por fim, produz um arquivo CSV e um arquivo Excel para importação no REDCap ou para distribuição às equipes de logística.

---

## 2. Estrutura de Pastas

```
📦seu_projeto_randomizacao_redcap
 ┣ 📂csv/
 ┃ ┗ randomizacao_redcap.csv         ← Arquivo CSV gerado
 ┣ 📂xlsx/
 ┃ ┗ randomizacao_redcap.xlsx       ← Arquivo Excel gerado
 ┣ 📜randomizacao.py                ← Script principal em Python
 ┗ 📜README.md                      ← Documentação (este arquivo)
```

> **Observação**: Antes de executar o script, certifique‐se de que as pastas `csv/` e `xlsx/` existem na raiz do projeto (ou crie‐as manualmente). Caso contrário, o Python levantará erro ao tentar salvar os arquivos.

---

## 3. Requisitos

- **Python 3.7+** (testado em 3.8 e 3.9)
- Bibliotecas Python:
  - `pandas`
  - `openpyxl`

Para instalar as dependências, você pode criar um ambiente virtual e executar:

```bash
python -m venv .venv
source .venv/bin/activate       # Linux/Mac
.venv\Scripts\activate          # Windows
pip install pandas openpyxl
```

Se preferir, crie um arquivo `requirements.txt` e adicione:

```
pandas>=1.0.0
openpyxl>=3.0.0
```

Em seguida, instale com:

```bash
pip install -r requirements.txt
```

---

## 4. Como Executar

1. Clone ou baixe este repositório na sua máquina local.
2. Navegue até a pasta raiz do projeto.
3. Assegure‐se de ter criado as pastas `csv/` e `xlsx/` na raiz.
4. Ative o ambiente virtual (se estiver usando).
5. Execute o script:

```bash
python randomizacao.py
```

Após a execução, serão gerados dois arquivos:

- `csv/randomizacao_redcap.csv`
- `xlsx/randomizacao_redcap.xlsx`

Esses arquivos contêm a lista completa de participantes com:
- `randomization_id` (ID sequencial R001, R002, …)
- `Centro` (1, 2, 3 ou 4)
- `Gênero` (Masculino ou Feminino)
- `Alocação` (Tratamento ou Placebo)
- `Etiqueta_Ampola1`
- `Etiqueta_Ampola2` (vazia para participantes do sexo feminino)

---

## 5. Descrição Detalhada do Código

A seguir, explicamos passo a passo as seções principais do script `randomizacao.py`.

### 5.1. Configurações Iniciais

```python
import pandas as pd
import random
import openpyxl

# Semente para reprodutibilidade
random.seed(42)

# Tamanho total da amostra
total_participantes = 96

# Estratos
estrato_centros = [1, 2, 3, 4]           # Quatro centros
estrato_genero = ['Masculino', 'Feminino']

# Meta de participantes por centro
meta_participantes_por_centro = {
    1: 24,
    2: 24,
    3: 24,
    4: 24
}

# Verifica se a soma das metas = total_participantes
assert sum(meta_participantes_por_centro.values()) == total_participantes, (
    f"A soma das metas de participantes por centro ({sum(meta_participantes_por_centro.values())}) "
    f"deve ser igual ao total de participantes ({total_participantes})."
)

# Quantos participantes (homens + mulheres) em cada centro
numero_centros = len(estrato_centros)
participantes_por_centro = total_participantes // numero_centros

# Metade para cada gênero em cada centro (50% homens, 50% mulheres)
participantes_por_genero_por_centro = participantes_por_centro // 2
```

- **Propósito**: definir variáveis fixas do protocolo:
  - São 96 participantes no total.
  - Cada um dos 4 centros receberá 24 participantes.
  - Em cada centro, haverá 12 homens e 12 mulheres (metade/metade).

- **Cheque de consistência**: usa-se `assert` para garantir que `sum(meta_participantes_por_centro.values())` é exatamente 96.

---

### 5.2. Randomização em Blocos

```python
# Tamanho do bloco (block randomization)
tamanho_bloco = 4

# Garante que 12 (participantes_por_genero_por_centro) seja divisível por 4
assert participantes_por_genero_por_centro % tamanho_bloco == 0, (
    f"O número de participantes por gênero em cada centro ({participantes_por_genero_por_centro}) "
    f"deve ser divisível pelo tamanho do bloco ({tamanho_bloco})."
)

def criar_blocos_randomizacao(tamanho_amostral: int, tamanho_bloco: int) -> list:
    """
    Divide 'tamanho_amostral' em blocos de tamanho 'tamanho_bloco'.
    Cada bloco terá 50% 'Tratamento' e 50% 'Placebo' (bloco 4 ⇒ 2T + 2P),
    embaralhando a ordem interna para garantir aleatoriedade.
    Retorna uma lista com tamanho_amostral strings "Tratamento"/"Placebo".
    """
    assert tamanho_amostral % tamanho_bloco == 0, (
        f"{tamanho_amostral} não é divisível por {tamanho_bloco}"
    )

    alocacao = []
    total_blocos = tamanho_amostral // tamanho_bloco

    for _ in range(total_blocos):
        bloco = ['Tratamento'] * (tamanho_bloco // 2) + ['Placebo'] * (tamanho_bloco // 2)
        random.shuffle(bloco)
        alocacao.extend(bloco)

    return alocacao
```

- **Explicação**:
  1. O bloco é 4, então cada bloco contém 2 “Tratamento” e 2 “Placebo”.
  2. Para cada gênero em cada centro (12 homens e 12 mulheres), o script gera 12 alocações em blocos de 4 (portanto, 3 blocos por gênero).
  3. A função `criar_blocos_randomizacao(12, 4)` retorna uma lista de 12 itens embaralhados, contendo exatamente 6 “Tratamento” e 6 “Placebo”.

---

### 5.3. Montagem da Tabela de Registros

```python
registros = []

# Estratificação por Centro → Gênero
for centro in estrato_centros:
    # Gera 12 alocações para homens (estrato_2_a)
    estrato_2_a = criar_blocos_randomizacao(participantes_por_genero_por_centro, tamanho_bloco)
    # Gera 12 alocações para mulheres (estrato_2_b)
    estrato_2_b = criar_blocos_randomizacao(participantes_por_genero_por_centro, tamanho_bloco)

    # Preenche os registros de homens
    for aloc in estrato_2_a:
        registros.append({
            'Centro': centro,
            'Gênero': 'Masculino',
            'Alocação': aloc
        })

    # Preenche os registros de mulheres
    for aloc in estrato_2_b:
        registros.append({
            'Centro': centro,
            'Gênero': 'Feminino',
            'Alocação': aloc
        })

# Converte para DataFrame
df_registros = pd.DataFrame(registros)
print(df_registros)
```

- Cada iteração de `centro` (de 1 a 4) gera:
  - 12 linhas (participantes masculinos) com campo `Alocação` sorteado em blocos.
  - 12 linhas (participantes femininos) também com `Alocação` sorteado em blocos.
- Ao final, o DataFrame tem `4 centros × (12 homens + 12 mulheres) = 96 linhas`.

---

### 5.4. Cálculo de Ampolas (Vials) Necessárias

```python
# Homens no braço “Tratamento” recebem 2 ampolas cada; Mulheres recebem 1
tratamento_estrato_2_a = sum(
    1 for r in registros
    if r['Gênero'] == 'Masculino' and r['Alocação'] == 'Tratamento'
) * 2

tratamento_estrato_2_b = sum(
    1 for r in registros
    if r['Gênero'] == 'Feminino' and r['Alocação'] == 'Tratamento'
)

total_ampolas_tratamento = (tratamento_estrato_2_a + tratamento_estrato_2_b)

# Mesma lógica para Placebo
placebo_estrato_2_a = sum(
    1 for r in registros
    if r['Gênero'] == 'Masculino' and r['Alocação'] == 'Placebo'
) * 2

placebo_estrato_2_b = sum(
    1 for r in registros
    if r['Gênero'] == 'Feminino' and r['Alocação'] == 'Placebo'
)

total_ampolas_placebo = (placebo_estrato_2_a + placebo_estrato_2_b)
```

- **Lógica**:
  - Para cada participante masculino (registros onde `Gênero == 'Masculino'`) no braço “Tratamento”, conta‐se +2 ampolas.
  - Para cada participante feminino no braço “Tratamento”, conta‐se +1 ampola.
  - Mesma lógica para o braço “Placebo”.
  - No final, `total_ampolas_tratamento` e `total_ampolas_placebo` contêm a quantidade bruta de ampolas sem o excesso de segurança (o código original considera +50%, mas a multiplicação já está no cálculo de contingência — se quiser implementar +50%, basta multiplicar por 1.5 ou arredondar para cima).

```python
print(tratamento_estrato_2_a, tratamento_estrato_2_b, total_ampolas_tratamento)
print(placebo_estrato_2_a, placebo_estrato_2_b, total_ampolas_placebo)
print("Total de ampolas:", total_ampolas_tratamento + total_ampolas_placebo)
```

---

### 5.5. Ampolas por Centro e Braço

Em seguida, calcula‐se quantas ampolas serão necessárias em cada combinação (centro, braço):

```python
total_ampolas = {}

for centro in estrato_centros:
    for braco in ['Tratamento', 'Placebo']:
        qtd_masc = df_registros[
            (df_registros['Centro'] == centro) &
            (df_registros['Gênero'] == 'Masculino') &
            (df_registros['Alocação'] == braco)
        ].shape[0]

        qtd_fem = df_registros[
            (df_registros['Centro'] == centro) &
            (df_registros['Gênero'] == 'Feminino') &
            (df_registros['Alocação'] == braco)
        ].shape[0]

        # Para ampolas: Homem → 2, Mulher → 1
        qtd_ampolas = (qtd_masc * 2) + qtd_fem

        total_ampolas[(centro, braco)] = qtd_ampolas
```

- `total_ampolas[(centro, braco)]` passa a conter um inteiro, p.ex. `(1, 'Tratamento') → 12` (HTTP).
- Esse valor será usado para gerar etiquetas específicas para aquele par (centro, braço).

---

### 5.6. Geração Aleatória de Etiquetas (“labels”) para as Ampolas

```python
def gerar_etiquetas_ampola(centro: int, braco: str, quantidade: int) -> list:
    """
    Gera etiquetas no formato “centro_{centro}_{braco[0].upper()}{i:03d}”,
    embaralha e retorna lista.
    - Centro: número do centro (1,2,3,4)
    - braco: 'Tratamento' ou 'Placebo' → usamos 'T' ou 'P'
    - numero: de 001 a quantidade
    """
    prefixo = f"centro_{centro}_{braco[0].upper()}"
    etiquetas = [f"{prefixo}{i:03d}" for i in range(1, quantidade + 1)]
    random.shuffle(etiquetas)
    return etiquetas

# Cria um dicionário com chave (centro, braço) e lista de etiquetas
pool_etiquetas = {}
for (centro, braco), quantidade in total_ampolas.items():
    pool_etiquetas[(centro, braco)] = gerar_etiquetas_ampola(centro, braco, quantidade)
```

Exemplo de saída para `(centro=1, braco='Tratamento', quantidade=18)`:
```
['centro_1_T017', 'centro_1_T003', 'centro_1_T012', ..., 'centro_1_T005']  # embaralhadas
```

---

### 5.7. Atribuição de Etiquetas aos Participantes

```python
lista_ampola1 = []
lista_ampola2 = []

for idx, row in df_registros.iterrows():
    centro = row['Centro']
    braco = row['Alocação']
    genero = row['Gênero']
    pool_key = (centro, braco)

    if genero == 'Masculino':
        etiqueta1 = pool_etiquetas[pool_key].pop(0)  # 1ª ampola
        etiqueta2 = pool_etiquetas[pool_key].pop(0)  # 2ª ampola
        lista_ampola1.append(etiqueta1)
        lista_ampola2.append(etiqueta2)
    else:  # Feminino
        etiqueta1 = pool_etiquetas[pool_key].pop(0)  # 1 ampola apenas
        lista_ampola1.append(etiqueta1)
        lista_ampola2.append('')
```

- Homens recebem duas etiquetas (duas ampolas): `Etiqueta_Ampola1` e `Etiqueta_Ampola2`.
- Mulheres recebem apenas uma: `Etiqueta_Ampola1`, enquanto `Etiqueta_Ampola2` fica vazia.

Após o loop, adicionamos as duas colunas no DataFrame:

```python
df_registros['Etiqueta_Ampola1'] = lista_ampola1
df_registros['Etiqueta_Ampola2'] = lista_ampola2
```

---

### 5.8. Inserção de `randomization_id` e Reordenação de Colunas

```python
# Cria IDs sequenciais R001, R002, ..., R096
df_registros.insert(
    loc=0,
    column='randomization_id',
    value=[f"R{str(i+1).zfill(3)}" for i in range(len(df_registros))]
)

# Reordena para: randomization_id, Centro, Gênero, Alocação, Etiqueta_Ampola1, Etiqueta_Ampola2
colunas_reordenadas = [
    'randomization_id',
    'Centro',
    'Gênero',
    'Alocação',
    'Etiqueta_Ampola1',
    'Etiqueta_Ampola2'
]
df_registros = df_registros[colunas_reordenadas]
```

- Ao final, a tabela final (`df_registros`) possui estas colunas, prontas para exportação.

---

### 5.9. Exportação para CSV e Excel

```python
# Exporta para .csv (codificação UTF-8 BOM)
df_registros.to_csv(r'.\csv\randomizacao_redcap.csv', index=False, encoding='utf-8-sig')

# Exporta para .xlsx (engine=openpyxl)
df_registros.to_excel(r'.\xlsx\randomizacao_redcap.xlsx', index=False, engine='openpyxl')
```

- **csv/randomizacao_redcap.csv**: pode ser importado em qualquer editor de planilhas ou diretamente no REDCap (caso use importação CSV).
- **xlsx/randomizacao_redcap.xlsx**: contém exatamente as mesmas colunas e registros, em formato Excel nativo.

---

## 6. Observações e Personalizações Possíveis

1. **Tamanho do Bloco**  
   - Atualmente, `tamanho_bloco = 4`. Se quiser blocos maiores (por exemplo, bloco 6 ⇒ 3T + 3P) basta alterar essa variável e garantir que `participantes_por_genero_por_centro` seja divisível pelo novo tamanho.

2. **Número de Centros ou Metas Diferentes**  
   - Caso algum centro tenha meta diferente (por ex. 30 participantes) basta atualizar o dicionário `meta_participantes_por_centro`.  
   - Atualize também a lógica de `participantes_por_centro` se a distribuição não for uniforme.

3. **Número de Ampolas de Contingência**  
   - O script calcula a necessidade exata de ampolas (2 por homem, 1 por mulher).  
   - Se quiser adicionar +50% de desvio, pode multiplicar `qtd_ampolas` por `1.5` e arredondar para cima antes de gerar etiquetas.

4. **Formato das Etiquetas**  
   - Hoje é `centro_{número}_{T ou P}{i:03d}`.  
   - Você pode modificar o prefixo para incluir siglas, datas ou qualquer outro padrão, alterando a função `gerar_etiquetas_ampola()`.

5. **Integração Direta com REDCap**  
   - Caso deseje automatizar o upload das planilhas no REDCap via API, você pode:
     1. Adicionar uma etapa ao final do script para consumir a API REST do REDCap.
     2. Enviar o arquivo `.csv` diretamente para o projeto específico, usando `requests` e parâmetros de token.

---

## 7. Exemplo de Saída (print do DataFrame)

```text
   randomization_id  Centro     Gênero  Alocação Etiqueta_Ampola1 Etiqueta_Ampola2
0              R001       1  Masculino  Placebo         P001         P014
1              R002       1  Masculino  Tratamento      T008         T023
2              R003       1  Masculino  Placebo         P007         P016
3              R004       1  Masculino  Tratamento      T003         T009
4              R005       1  Masculino  Placebo         P004         P012
..               ...     ...        ...       ...           ...           ...
91             R092       4   Feminino  Placebo         P081
92             R093       4   Feminino  Tratamento      T055
93             R094       4   Feminino  Placebo         P089
94             R095       4   Feminino  Tratamento      T061
95             R096       4   Feminino  Placebo         P097

[96 rows x 6 columns]
```

- A coluna `Etiqueta_Ampola2` para participantes femininos estará vazia porque elas recebem apenas 1 ampola.

---

## 8. Contribuições e Licença

Sinta‐se à vontade para:
- **Reportar problemas** (issues) diretamente neste repositório.
- **Enviar pull requests** para melhorias (ex.: adicionar +50% de contingência automática, criar API call para REDCap etc.).
- Dar crédito ou adaptar o código conforme sua necessidade.

---

## 9. Contato

Para dúvidas ou sugestões, abra uma issue ou entre em contato com o autor:

- **Nome:** Edaurdo Augusto Rabelo Socca
- **E‐mail:** eduardo_socca@yahoo.com.br
- **Empresa:** Science Valley Research Institute (SVRI)

Obrigado por utilizar este script!  
Boa sorte no seu ensaio clínico! 🚀
