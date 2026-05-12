<div align="center">

# 🎮 LoL Match Analytics

### Pipeline ETL com Riot API · Arquitetura Medallion · Machine Learning · Python + SQLite

![Status](https://img.shields.io/badge/status-concluído-brightgreen?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)

</div>

---

> **Primeiro projeto desenvolvido do zero** — construído para aprender na prática conceitos de engenharia de dados, consumo de APIs, modelagem relacional e machine learning aplicado. O pipeline completo vai da coleta bruta via Riot API até um dashboard interativo com modelos de ML capazes de prever vitórias e identificar estilos de jogo.

<br>

## 🧠 Skills Aplicadas

<table>
  <tr>
    <td valign="top" width="50%">

**📦 Engenharia de Dados**
- Arquitetura Medallion (Bronze / Silver / Gold)
- Design de pipelines ETL com separação clara de responsabilidades
- Controle de idempotência (evita reprocessamento duplicado)
- Isolamento de erros por registro

**🐍 Python**
- Organização em pacotes e módulos (`src/core`, `src/layers`)
- Manipulação de arquivos JSON com `pathlib` e `json`
- `logging` para rastreabilidade do pipeline
- Type hints e boas práticas de legibilidade

**🤖 Machine Learning**
- Classificação com Random Forest (`scikit-learn`)
- Clustering não-supervisionado com KMeans
- Normalização de features com `StandardScaler`
- Engenharia de features a partir de dados brutos da API

  </td>
  <td valign="top" width="50%">

**🗄️ Banco de Dados**
- Modelagem relacional (PKs, FKs, índices)
- SQL com `INSERT OR IGNORE` e `ON CONFLICT DO UPDATE`
- SQLAlchemy como engine de conexão
- SQLite para prototipagem local

**🌐 Consumo de API REST**
- Autenticação via API Key (Riot Developer Portal)
- Encadeamento de chamadas: conta → puuid → match ids → detalhes
- Tratamento de rate limit com retry automático

**✅ Boas Práticas**
- `.env` para gerenciamento de segredos
- `.gitignore` configurado corretamente
- Funções com responsabilidade única
- Serialização de modelos com `pickle`

  </td>
  </tr>
</table>

<br>

---

## 📐 Arquitetura Geral

O projeto segue o padrão **Medallion Architecture**, onde cada camada tem uma responsabilidade bem definida e os dados ficam progressivamente mais refinados.

```
┌─────────────┐
│  Riot  API  │
└──────┬──────┘
       │  JSON bruto por partida
       ▼
┌─────────────────────────────────────────────────────────┐
│  🥉 BRONZE LAYER                                        │
│  JSONs brutos em data/bronze/  +  tabela bronze_raw     │
│  Responsabilidade: coleta e rastreamento de ingestão    │
└──────┬──────────────────────────────────────────────────┘
       │  Registros pendentes (processado = 0)
       ▼
┌─────────────────────────────────────────────────────────┐
│  🥈 SILVER LAYER                                        │
│  Tabelas relacionais: jogadores, partidas, desempenho   │
│  Responsabilidade: limpeza, normalização e estrutura    │
└──────┬──────────────────────────────────────────────────┘
       │  Features numéricas limpas
       ▼
┌─────────────────────────────────────────────────────────┐
│  🥇 GOLD LAYER                                          │
│  ├── Classificador (Random Forest) → prevê vitórias     │
│  ├── Clustering (KMeans) → identifica estilos de jogo   │
│  └── Dashboard Streamlit → visualização interativa      │
└─────────────────────────────────────────────────────────┘
```

<br>

---

## 🗂️ Estrutura do Projeto

```
.
├── main.py                              # Ponto de entrada do pipeline Bronze + Silver
├── .env                                 # Chave da Riot API (não commitado)
│
├── data/
│   ├── lol.db                           # Banco SQLite gerado automaticamente
│   ├── bronze/                          # JSONs brutos das partidas
│   │   └── BR1_XXXXXXXXX.json
│   └── models/                          # Modelos ML serializados
│       ├── classificador.pkl
│       ├── scaler_classificador.pkl
│       ├── kmeans.pkl
│       ├── scaler_clustering.pkl
│       ├── perfil_clusters.csv
│       └── feature_importance.csv
│
├── app.py                               # Dashboard Streamlit (ponto de entrada da Gold)
│
└── src/
    ├── core/
    │   ├── config.py                    # Constantes centralizadas (URLs, caminhos)
    │   ├── db.py                        # Engine SQLAlchemy + inicialização do banco
    │   └── riot_cliente.py              # Wrapper da Riot API com retry
    │
    └── layers/
        ├── layer_bronze/
        │   ├── ingest_bronze.py         # Download e registro dos JSONs brutos
        │   └── schema_bronze.sql        # DDL da tabela bronze_raw
        │
        ├── layer_silver/
        │   ├── extractor.py             # Lê pendentes do banco
        │   ├── transformer.py           # Transforma JSON → dicionários limpos
        │   ├── loader.py                # Persiste dados nas tabelas relacionais
        │   ├── pipeline.py              # Orquestra o fluxo Silver
        │   └── schema_silver.sql        # DDL das tabelas relacionais
        │
        └── layer_gold/
            ├── features.py              # Seleção e preparação de features para ML
            ├── classificador.py         # Treino do Random Forest
            ├── clustering.py            # Treino do KMeans + rotulagem automática
            └── predict.py               # Script de exemplo para usar o classificador
```

<br>

---

## 🗄️ Modelo de Dados

### 🟫 `bronze_raw` — Controle de ingestão

| Coluna | Tipo | Descrição |
|:---|:---:|:---|
| `match_id` | TEXT PK | ID único da partida |
| `caminho` | TEXT | Caminho do arquivo JSON em disco |
| `processado` | INTEGER | `0` pendente · `1` sucesso · `2` erro |
| `log` | TEXT | Mensagem de status ou descrição do erro |

### 🥈 Silver — Tabelas relacionais

<table>
<tr>
<td valign="top">

**`jogadores`**

| Coluna | Descrição |
|:---|:---|
| `puuid` PK | ID permanente do jogador na Riot |
| `nick` | Nome de invocador |
| `tag` | Tag da conta (ex: `BR1`) |
| `regiao` | Região da partida |

> O `puuid` é usado como chave primária — ao contrário do nick, ele nunca muda quando o jogador troca de nome.

</td>
<td valign="top">

**`partidas`**

| Coluna | Descrição |
|:---|:---|
| `match_id` PK | ID da partida |
| `data` | Timestamp de início (`YYYY-MM-DD HH:MM:SS`) |
| `duracao` | Duração formatada (`MM:SS`) |
| `modo` | Modo de jogo (ex: `CLASSIC`) |

</td>
</tr>
</table>

**`desempenho`** — tabela principal de análise (uma linha por jogador por partida)

| Grupo | Colunas | Descrição |
|:---|:---|:---|
| Identidade | `puuid`, `match_id`, `campeao`, `posicao` | Quem jogou o quê e onde |
| Resultado | `vitoria`, `surrender` | Desfecho da partida |
| KDA | `kills`, `deaths`, `assists` | Abates, mortes e assistências |
| Economia | `ouro`, `cs`, `gpm` | Farm e geração de ouro |
| Dano | `dano_campeoes`, `dano_objetivos`, `dano_mitigado`, `dpm` | Impacto no combate |
| Visão | `placar_visao`, `visao_por_minuto`, `wards_colocadas`, `wards_controle_colocadas` | Controle de mapa |
| Early game | `cs_primeiros_10_min`, `vantagem_cs_oponente`, `vantagem_nivel_oponente`, `pratos_torre` | Dominância de fase de rota |
| Combate avançado | `solo_kills`, `killing_sprees`, `skillshots_acertados`, `skillshots_desviados` | Mecânica individual |
| Sobrevivência | `tempo_morto`, `maior_tempo_vivo`, `nivel_final` | Gestão de vida |
| Participação | `kp`, `pct_dano_time`, `pct_dano_recebido_time`, `tempo_cc_aplicado` | Contribuição para o time |
| Objetivos | `torres_destruidas`, `dragoes_abatidos`, `first_blood_kill` | Objetivos conquistados |

<br>

---

## ⚙️ Configuração

**Pré-requisitos**
- Python 3.12+
- Conta no [Riot Games Developer Portal](https://developer.riotgames.com/) para obter uma API Key

**Instalação**

```bash
git clone https://github.com/seu-usuario/lol-match-analyzer.git
cd lol-match-analyzer
pip install -r requirements.txt
```

**Variáveis de ambiente**

Crie um arquivo `.env` na raiz do projeto:

```env
RIOT_API_KEY=RGAPI-xxxx-xxxx-xxxx-xxxx
```

> ⚠️ Nunca commite sua API Key. O `.gitignore` já está configurado para ignorá-la.

<br>

---

## ▶️ Como Usar

### 1. Coletar e processar dados

```python
# main.py — roda Bronze + Silver em sequência
iniciar_ingestao_bruta("NickDoJogador", "TAG")  # coleta JSONs da API
processar_silver()                               # transforma e salva no banco
```

```bash
python main.py
```

### 2. Treinar os modelos (via dashboard ou direto)

```bash
# Via terminal
python -m src.layers.layer_gold.classificador   # treina o Random Forest
python -m src.layers.layer_gold.clustering      # treina o KMeans
```

Ou use os botões na sidebar do dashboard Streamlit.

### 3. Abrir o dashboard

```bash
streamlit run app.py
```

> Você também pode rodar cada célula individualmente no VS Code com `# %%`.

<br>

---

## 🔄 Fluxo do Pipeline

```
iniciar_ingestao_bruta(nick, tag)
       │
       ├── GET /account/by-riot-id  ──► puuid do jogador
       ├── GET /match/by-puuid      ──► lista de até 100 match_ids
       └── Para cada match_id:
             ├── JSON já existe?    ──► ⏩ pula (idempotente)
             ├── GET /match/{id}    ──► salva JSON em data/bronze/
             └── Registra em bronze_raw com processado = 0

processar_silver()
       │
       ├── SELECT bronze_raw WHERE processado = 0
       └── Para cada partida pendente:
             ├── extractor   ──► lê o JSON do disco
             ├── transformer ──► extrai partida, jogadores e desempenhos
             ├── loader      ──► upsert nas tabelas relacionais
             └── Marca como ✅ sucesso (1) ou ❌ erro (2)
```

<br>

---

## 🥇 Camada Gold — Machine Learning

A camada Gold é onde os dados estruturados viram **inteligência**. Dois modelos foram implementados com objetivos complementares: um prevê o resultado da partida, o outro identifica o estilo de jogo do jogador.

---

### 🌲 Modelo 1 — Classificador de Vitória (Random Forest)

**O que faz:** dado o desempenho de um jogador em uma partida, o modelo calcula a probabilidade de aquela partida ter sido uma vitória.

**Por que Random Forest?** É um algoritmo robusto que combina centenas de árvores de decisão. Cada árvore "vota" no resultado e a decisão final é a maioria dos votos. Isso torna o modelo resistente a ruído e overfitting, além de fornecer naturalmente a importância de cada feature.

#### Como o treino funciona (passo a passo)

```
[Silver Layer — tabela desempenho]
       │
       ▼
features.py → preparar_classificador()
       │  Filtra: só partidas CLASSIC sem surrender
       │  Remove linhas com valores nulos
       │  Retorna X (29 features) e y (vitoria = 0 ou 1)
       │
       ▼
classificador.py → treinar()
       │
       ├── 1. Divide em treino (80%) e teste (20%)
       │       Estratificado: mantém proporção de vitórias/derrotas
       │
       ├── 2. Normaliza com StandardScaler
       │       Transforma cada feature para média 0 e desvio padrão 1
       │       Necessário porque features como "ouro" (15.000) e
       │       "first_blood_kill" (0 ou 1) têm escalas muito diferentes
       │
       ├── 3. Treina RandomForestClassifier
       │       200 árvores, profundidade máxima 10, mínimo 5 amostras por folha
       │
       ├── 4. Avalia no conjunto de teste
       │       Imprime acurácia e relatório de classificação
       │
       └── 5. Salva em data/models/
               ├── classificador.pkl        (o modelo treinado)
               ├── scaler_classificador.pkl (o scaler ajustado)
               └── feature_importance.csv  (importância de cada feature)
```

#### As 29 features usadas

```python
FEATURES_CLASSIFICADOR = [
    # Economia e farm
    "dpm", "kp", "cs", "gpm", "ouro",

    # Combate
    "dano_campeoes", "dano_objetivos", "dano_mitigado",

    # Visão
    "placar_visao", "visao_por_minuto",

    # Objetivos
    "torres_destruidas", "dragoes_abatidos", "first_blood_kill",

    # Early game
    "cs_primeiros_10_min", "vantagem_cs_oponente", "vantagem_nivel_oponente",
    "pratos_torre",

    # Mecânica individual
    "solo_kills", "killing_sprees",
    "skillshots_acertados", "skillshots_desviados",

    # Sobrevivência e tempo
    "tempo_cc_aplicado", "tempo_morto", "maior_tempo_vivo", "nivel_final",

    # Wards
    "wards_colocadas", "wards_controle_colocadas",

    # Participação no time
    "pct_dano_time", "pct_dano_recebido_time",
]
```

#### Como usar o modelo para prever

```python
# predict.py — exemplo de uso direto
import pickle, pandas as pd

with open("data/models/classificador.pkl", "rb") as f:
    modelo = pickle.load(f)
with open("data/models/scaler_classificador.pkl", "rb") as f:
    scaler = pickle.load(f)

dados = pd.DataFrame([{
    "dpm": 800, "kp": 60, "cs": 150, "gpm": 400, "ouro": 12000,
    # ... demais features
}])

X_scaled  = scaler.transform(dados)        # normaliza da mesma forma que no treino
predicao  = modelo.predict(X_scaled)       # 1 = vitória, 0 = derrota
prob      = modelo.predict_proba(X_scaled) # [prob_derrota, prob_vitória]

print("Vitória 🏆" if predicao[0] == 1 else "Derrota 💀")
print(f"Confiança: {max(prob[0]) * 100:.1f}%")
```

> **Por que normalizar antes de prever?** O scaler foi ajustado (`fit`) nos dados de treino. Na hora de prever, aplicamos apenas a transformação (`transform`) usando os mesmos parâmetros. Se normalizássemos com valores diferentes, o modelo receberia dados fora do padrão que ele aprendeu.

---

### 🔵 Modelo 2 — Clustering de Estilo de Jogo (KMeans)

**O que faz:** agrupa partidas em perfis de jogo baseados em como o jogador se comportou — sem usar o resultado da partida. O objetivo é responder: *"Como você joga?"*, não *"Você ganhou?"*.

**Por que KMeans?** É um algoritmo de agrupamento que divide os dados em K grupos, onde cada ponto pertence ao grupo cujo centro (centróide) é mais próximo. É simples, rápido e produz grupos interpretáveis.

#### Como o treino funciona (passo a passo)

```
[Silver Layer — tabela desempenho]
       │
       ▼
features.py → preparar_clustering()
       │  Filtra: só partidas CLASSIC sem surrender
       │  Seleciona apenas as 12 features de estilo
       │  Remove linhas com valores nulos
       │
       ▼
clustering.py → treinar_clustering(n_clusters=4)
       │
       ├── 1. Normaliza com StandardScaler
       │       Essencial no KMeans: features em escalas diferentes
       │       distorcem o cálculo de distância entre pontos
       │
       ├── 2. Treina KMeans com 4 clusters
       │       n_init=10 → roda 10 vezes com centroides aleatórios diferentes
       │       e mantém o melhor resultado (menor inércia)
       │
       ├── 3. Atribui cada partida a um cluster
       │
       ├── 4. Calcula o perfil médio de cada cluster
       │       Usa os valores originais (não normalizados) para legibilidade
       │
       ├── 5. Rotula automaticamente os clusters
       │       Compara os centróides e identifica qual feature
       │       cada cluster lidera em relação aos demais
       │       Ex: cluster com maior visao_por_minuto → 👁️ Suporte/Visionário
       │
       └── 6. Salva em data/models/
               ├── kmeans.pkl              (o modelo treinado)
               ├── scaler_clustering.pkl   (o scaler ajustado)
               └── perfil_clusters.csv     (médias e rótulos de cada cluster)
```

#### As 12 features de estilo usadas

```python
FEATURES_CLUSTERING = [
    "dpm",                      # intensidade ofensiva
    "kp",                       # quanto participa dos abates do time
    "cs",                       # foco em farm individual
    "gpm",                      # eficiência econômica geral
    "placar_visao",             # controle de mapa absoluto
    "visao_por_minuto",         # consistência na visão
    "solo_kills",               # habilidade em duelos 1v1
    "pct_dano_time",            # fatia do dano total da equipe
    "pct_dano_recebido_time",   # quanto do dano inimigo absorve (= tanque)
    "tempo_cc_aplicado",        # quanto CC aplica (engage/controle)
    "wards_colocadas",          # geração de informação para o time
    "wards_controle_colocadas", # remoção de visão inimiga
]
```

> Note que `vitoria` não é uma feature aqui — o modelo descobre padrões sem saber quem ganhou. Isso permite identificar o estilo independentemente do resultado.

#### Os 4 perfis gerados

O algoritmo de rotulagem automática analisa qual feature cada cluster lidera e atribui um rótulo. Os perfis típicos são:

| Perfil | Características |
|:---|:---|
| 🗡️ **Carry de Dano** | Alto DPM, alta fatia do dano do time, farm elevado |
| 🔒 **Controlador de Área** | Muito CC aplicado, engage constante, suporte ao time |
| 👁️ **Suporte/Visionário** | Alta visão por minuto, muitas wards, baixo dano individual |
| 🤝 **Team Player** | Alta participação em kills, jogo orientado ao time |

> Os rótulos são determinados automaticamente com base nos dados reais — podem variar dependendo do conjunto de partidas coletado.

#### Rotulagem automática — como funciona

```python
# clustering.py — _rotular_clusters()

# Critérios em ordem de prioridade:
criterios = [
    ("visao_por_minuto",  "👁️ Suporte/Visionário", "Alta visão por minuto"),
    ("tempo_cc_aplicado", "🔒 Controlador de Área", "Muito CC aplicado"),
    ("dpm",               "🗡️ Carry de Dano",       "Alto DPM"),
    ("cs",                "🌾 Farmer",              "Farm elevado"),
    ("kp",                "🤝 Team Player",         "Alta participação em kills"),
    ("solo_kills",        "⚔️ Duelista",            "Muitas kills solo"),
]

# Para cada cluster, verifica qual feature ele lidera
# O primeiro critério que se aplica define o rótulo
# Cada rótulo só pode ser atribuído a um cluster
```

---

### 📊 Feature Importance — O que o modelo aprendeu?

Após o treino, o classificador expõe a importância de cada feature. Isso responde: *"O que mais diferencia uma vitória de uma derrota?"*

As features mais impactantes tipicamente são:

| Feature | Por quê importa |
|:---|:---|
| `torres_destruidas` | Destruir torres é pressão de mapa direta — quem controla o mapa vence |
| `pratos_torre` | Ouro e pressão no early game antes de qualquer objetivo maior |
| `tempo_morto` | Tempo morto é tempo sem contribuir — morrer menos é melhor que matar mais |
| `dano_objetivos` | Dragões e Barão viram o jogo; participar neles é fundamental |
| `gpm` | Ouro por minuto consolida tudo: farm, kills, objetivos |

Esses valores são salvos em `feature_importance.csv` e exibidos graficamente no dashboard.

---

### 🖥️ Dashboard — Streamlit

O `app.py` é o ponto de entrada da camada Gold. Ele conecta tudo num dashboard interativo com 4 abas:

| Aba | Conteúdo |
|:---|:---|
| 📊 **Visão Geral** | Métricas de resumo, pior/melhor partida, gráficos por campeão |
| 🤖 **Análise Gold (ML)** | Probabilidade de vitória por partida, acurácia do modelo, diagnóstico |
| 🔵 **Estilo de Jogo** | Cluster dominante, winrate por perfil, você vs média do perfil |
| 🔍 **Feature Importance** | Ranking das features, explicações em linguagem natural |

```
app.py
  │
  ├── Sidebar: busca jogador, treina modelos
  │
  ├── Aba 1: carregar_dados_do_banco() → visualizações pandas + st.bar_chart
  │
  ├── Aba 2: scaler.transform(X) → modelo.predict_proba(X) → st.line_chart
  │
  ├── Aba 3: prever_cluster(df) → winrate por cluster → comparação com perfil
  │
  └── Aba 4: feature_importance.csv → st.bar_chart + explicações por feature
```

<br>

---

## 🔄 Fluxo Completo — Bronze até Gold

```
[Riot API]
    │
    ▼ ingest_bronze.py
[data/bronze/*.json]  +  [bronze_raw: processado=0]
    │
    ▼ pipeline.py (extractor → transformer → loader)
[jogadores]  [partidas]  [desempenho]   ← Silver Layer
    │
    ▼ features.py
[X: 29 features numéricas]  [y: vitoria]
    │
    ├──▶ classificador.py ──▶ classificador.pkl  +  feature_importance.csv
    │
    └──▶ clustering.py   ──▶ kmeans.pkl  +  perfil_clusters.csv
                                    │
                                    ▼
                              [app.py — Streamlit]
                          Dashboard interativo completo
```

<br>

---

## 📦 Dependências Principais

```txt
requests
python-dotenv
sqlalchemy
pandas
scikit-learn
streamlit
```

<br>

---

<div align="center">

*Este projeto não é endossado pela Riot Games e não reflete os pontos de vista ou opiniões da Riot Games ou de qualquer pessoa oficialmente envolvida na produção ou gestão de League of Legends.*

</div>