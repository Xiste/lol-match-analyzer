<div align="center">

# 🎮 LoL Match Analytics

### Pipeline ETL com Riot API · Arquitetura Medallion · Python + SQLite

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-em%20breve-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)

</div>

---

> 🚧 **Primeiro projeto desenvolvido do zero** — construído para aprender na prática conceitos de engenharia de dados, consumo de APIs e organização de código em camadas. O pipeline de coleta e transformação já está funcional, mas o projeto ainda está em fase de estruturação. A próxima etapa é a **camada Gold**, com análise dos dados e dashboard interativo em **Streamlit**.

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
- Armazenamento estruturado das respostas

**✅ Boas Práticas**
- `.env` para gerenciamento de segredos
- `.gitignore` configurado corretamente
- Funções com responsabilidade única

  </td>
  </tr>
</table>

<br>

---

## 📐 Arquitetura

O projeto segue o padrão **Medallion Architecture**, separando responsabilidades entre coleta bruta, transformação e apresentação dos dados.

```
┌─────────────┐
│  Riot  API  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│  🥉 BRONZE LAYER                                        │
│  JSONs brutos em data/bronze/  +  tabela bronze_raw     │
└──────┬──────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│  🥈 SILVER LAYER                                        │
│  Tabelas relacionais: jogadores, partidas, desempenho   │
└──────┬──────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│  🥇 GOLD LAYER                        🚧 em breve       │
│  Análises + Dashboard interativo com Streamlit          │
└─────────────────────────────────────────────────────────┘
```

<br>

---

## 🗂️ Estrutura do Projeto

```
.
├── main.py                         # Ponto de entrada do pipeline
├── .env                            # Chave da Riot API (não commitado)
│
├── data/
│   ├── lol.db                      # Banco SQLite gerado automaticamente
│   └── bronze/                     # JSONs brutos das partidas
│       └── BR1_XXXXXXXXX.json
│
└── src/
    ├── core/
    │   ├── db.py                   # Engine SQLAlchemy
    │   └── riot_cliente.py         # Wrapper da Riot API
    │
    ├── layers/
    │   ├── layer_bronze/
    │   │   └── ingest_bronze.py    # Download e registro dos JSONs brutos
    │   │
    │   └── layer_silver/
    │       ├── extractor.py        # Lê pendentes do banco
    │       ├── transformer.py      # Transforma JSON → dicionários limpos
    │       ├── loader.py           # Persiste dados nas tabelas relacionais
    │       └── pipeline.py         # Orquestra o fluxo Silver
    │
    └── sql/
        └── schema.sql              # DDL das tabelas
```

<br>

---

## 🗄️ Modelo de Dados

### 🟫 `bronze_raw` — Controle de ingestão

| Coluna | Tipo | Descrição |
|:---|:---:|:---|
| `match_id` | TEXT PK | ID único da partida |
| `caminho` | TEXT | Caminho do arquivo JSON |
| `processado` | INTEGER | `0` pendente · `1` sucesso · `2` erro |
| `log` | TEXT | Mensagem de status ou erro |
| `data_coleta` | DATETIME | Timestamp da coleta |

### 🥈 Silver — Tabelas relacionais

<table>
<tr>
<td valign="top">

**`jogadores`**

| Coluna | Descrição |
|:---|:---|
| `puuid` PK | ID Riot do jogador |
| `nick` | Nome de invocador |
| `tag` | Tag da conta |
| `regiao` | Região da partida |

</td>
<td valign="top">

**`partidas`**

| Coluna | Descrição |
|:---|:---|
| `match_id` PK | ID da partida |
| `data` | Timestamp de criação |
| `duracao` | Duração em segundos |
| `modo` | Modo de jogo |

</td>
</tr>
</table>

**`desempenho`** — tabela principal de análise

| Coluna | Descrição |
|:---|:---|
| `campeao` / `posicao` | Campeão e rota jogados |
| `vitoria` | `1` vitória · `0` derrota |
| `kills` / `deaths` / `assists` | KDA |
| `ouro` / `cs` | Economia e farm |
| `dano_campeoes` / `dano_objetivos` / `dano_mitigado` | Combate |
| `dpm` | Dano por minuto |
| `kp` | Kill participation `(kills + assists) / kills_do_time` |
| `placar_visao` | Vision score |

<br>

---

## ⚙️ Configuração

**Pré-requisitos**
- Python 3.12+
- Conta no [Riot Games Developer Portal](https://developer.riotgames.com/) para obter uma API Key

**Instalação**

```bash
git clone https://github.com/seu-usuario/seu-repo.git
cd seu-repo
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

O pipeline roda em dois estágios sequenciais via `main.py`:

```python
# Estágio 1 — Bronze: coleta os JSONs brutos da Riot API
iniciar_ingestao_bruta("NickDoJogador", "TAG")

# Estágio 2 — Silver: transforma e persiste no banco relacional
processar_silver()
```

```bash
python main.py
```

> Você também pode rodar cada célula individualmente no VS Code com `# %%`.

<br>

---

## 🔄 Fluxo do Pipeline

```
iniciar_ingestao_bruta(nick, tag)
       │
       ├── GET /account/by-riot-id ──► puuid
       ├── GET /match/by-puuid     ──► lista de match_ids
       └── Para cada match_id:
             ├── Já existe JSON?  ──► ⏩ pula
             ├── GET /match/{id}  ──► salva JSON em data/bronze/
             └── Registra em bronze_raw (processado = 0)

processar_silver()
       │
       ├── SELECT bronze_raw WHERE processado = 0
       └── Para cada partida pendente:
             ├── extractor   ──► lê o JSON do disco
             ├── transformer ──► extrai partida, jogadores, desempenhos
             ├── loader      ──► upsert nas tabelas relacionais
             └── Marca como ✅ sucesso (1) ou ❌ erro (2)
```

<br>

---

## 🚧 Próximos Passos — Camada Gold

A camada Gold consumirá os dados estruturados na Silver e os transformará em **insights visuais e interativos** através de um dashboard em **Streamlit**.

**Funcionalidades planejadas:**

| Feature | Descrição |
|:---|:---|
| 📈 Visão geral | Desempenho do jogador ao longo das partidas |
| 📉 Evolução | KDA, DPM e KP por sessão ao longo do tempo |
| ⚔️ Por campeão | Comparativo de métricas entre campeões jogados |
| 🔍 Filtros | Modo de jogo, período, vitória/derrota |
| 🏆 Cards | Médias, recordes e tendências consolidadas |

```
[Silver Layer]
      │
      ▼
[Gold Layer]
      ├── Queries analíticas sobre jogadores, partidas e desempenho
      └── Dashboard Streamlit ──► gráficos · tabelas · filtros interativos
```

<br>

---

<div align="center">

*Este projeto não é endossado pela Riot Games e não reflete os pontos de vista ou opiniões da Riot Games ou de qualquer pessoa oficialmente envolvida na produção ou gestão de League of Legends.*

</div>