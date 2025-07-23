# Randomização IMOX - Sistema de Randomização para Estudo Clínico

Este repositório contém um sistema de randomização para o estudo clínico IMOX, implementado em Python. O sistema realiza a alocação aleatória de participantes em diferentes braços de tratamento, estratificada por centro e gênero.

## 📋 Descrição Geral

O script `randomizacao_imox` implementa um sistema de randomização em blocos para um estudo clínico multicêntrico com as seguintes características:

- **10 centros de pesquisa** (códigos 18-27)
- **2 braços de tratamento** (2506091 e 2506092)
- **Estratificação por centro e gênero** (Masculino/Feminino)
- **120 participantes totais** (12 por centro)
- **Randomização em blocos** com tamanho de bloco = 4

## 🏗️ Estrutura do Projeto

```
Randomizacao_redcap/
├── README.md
├── requirements.txt
├── projeto/
│   ├── randomizacao_imox          # Script principal de randomização
│   ├── randomizacao_redcap.py
│   └── rando.ipynb
├── csv/
│   ├── randomizacao_imox_semente42.csv
│   └── randomizacao_imox_semente81.csv
└── xlsx/
    ├── randomizacao_imox_semente42.xlsx
    └── randomizacao_imox_semente81.xlsx
```

## ⚙️ Funcionalidades

### Características da Randomização

1. **Estratificação por Centro**: 
   - 10 centros participantes (18, 19, 20, 21, 22, 23, 24, 25, 26, 27)
   - 12 participantes por centro
   - Meta total: 120 participantes

2. **Estratificação por Gênero**:
   - 50% participantes masculinos
   - 50% participantes femininos
   - Por centro: 6 homens e 6 mulheres

3. **Braços de Tratamento**:
   - **2506091**: Etiquetas numeradas de 001 a 108
   - **2506092**: Etiquetas numeradas de 109 a 216
   - Distribuição equilibrada: 50% em cada braço

4. **Sistema de Etiquetas**:
   - **Participantes masculinos**: Recebem 2 etiquetas cada
   - **Participantes femininos**: Recebem 1 etiqueta cada
   - Formato: "001/ 002" (masculino) ou "003" (feminino)

### Parâmetros de Configuração

```python
# Centros participantes
estrato_centros = [18,19,20,21,22,23,24,25,26,27]

# Meta de participantes por centro
meta_participantes_por_centro = {
    18: 12, 19: 12, 20: 12, 21: 12, 22: 12,
    23: 12, 24: 12, 25: 12, 26: 12, 27: 12
}

# Parâmetros de randomização
tamanho_bloco = 4
bracos = ['2506091', '2506092']
```

## 🚀 Como Usar

### Pré-requisitos

```bash
pip install pandas openpyxl
```

### Executando o Script

1. **Configure a semente aleatória** (para reprodutibilidade):
   ```python
   random.seed(42)  # ou 81 para versão alternativa
   ```

2. **Execute o script**:
   ```bash
   python projeto/randomizacao_imox
   ```

3. **Arquivos de saída**:
   - CSV: `csv/randomizacao_imox_semente42.csv`
   - Excel: `xlsx/randomizacao_imox_semente42.xlsx`

### Estrutura dos Dados de Saída

| Centro | Genero    | Braco   | Etiquetas |
|--------|-----------|---------|-----------|
| 18     | Masculino | 2506091 | 045/ 023  |
| 18     | Feminino  | 2506091 | 067       |
| 18     | Masculino | 2506092 | 134/ 156  |
| ...    | ...       | ...     | ...       |

## 🔧 Componentes Técnicos

### Função Principal: `distribuir_por_braco()`

```python
def distribuir_por_braco(centro: int, braco: str, meta: int, etiquetas: list[int]) -> list[tuple]:
    """
    Distribui etiquetas para um centro e braço específicos
    
    Args:
        centro: Código do centro (18-27)
        braco: Braço do tratamento ('2506091' ou '2506092')
        meta: Total de participantes no centro
        etiquetas: Lista de etiquetas disponíveis
    
    Returns:
        Lista de tuplas (centro, genero, braco, etiquetas_str)
    """
```

### Algoritmo de Distribuição

1. **Por centro**: Divide participantes igualmente entre os braços
2. **Por braço**: Divide participantes igualmente entre gêneros
3. **Por gênero**: 
   - Homens: 2 etiquetas sequenciais
   - Mulheres: 1 etiqueta

### Validações Implementadas

- ✅ Verificação da soma total de participantes
- ✅ Distribuição equilibrada por centro
- ✅ Distribuição equilibrada por gênero
- ✅ Alocação correta de etiquetas por braço

## 📊 Saídas Geradas

### Formatos de Arquivo

1. **CSV** (`csv/randomizacao_imox_semente42.csv`):
   - Encoding: UTF-8 com BOM
   - Separador: vírgula
   - Sem índice

2. **Excel** (`xlsx/randomizacao_imox_semente42.xlsx`):
   - Planilha: "Randomizacao Imox Semente 42"
   - Colunas auto-ajustadas
   - Formatação otimizada

### Estatísticas da Randomização

- **Total de participantes**: 120
- **Participantes por centro**: 12
- **Participantes por braço**: 60
- **Participantes masculinos**: 60 (2 etiquetas cada = 120 etiquetas)
- **Participantes femininas**: 60 (1 etiqueta cada = 60 etiquetas)
- **Total de etiquetas**: 180

## 🔒 Reprodutibilidade

O sistema garante reprodutibilidade através de:

- **Sementes fixas**: 42 e 81 para diferentes versões
- **Algoritmo determinístico**: Mesmos resultados com mesma semente
- **Validações automáticas**: Verificação de integridade dos dados

## 📝 Notas Importantes

- ⚠️ **Não modificar a semente** após gerar os arquivos finais
- ⚠️ **Verificar consistência** entre diferentes execuções
- ⚠️ **Backup dos arquivos** de randomização gerados
- ⚠️ **Validar distribuições** antes do uso clínico

## 📧 Suporte

Para dúvidas ou problemas relacionados ao sistema de randomização, consulte a documentação do protocolo do estudo ou entre em contato com a equipe de bioestística.

---

**Versão**: 1.0  
**Última atualização**: Julho 2025  
**Compatibilidade**: Python 3.7+
