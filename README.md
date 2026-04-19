# Análise do Campeonato Brasileiro (2007–2025)

> **v1.0 — Primeira versão.** A estrutura atual é funcional e cobre todos os dashboards, mas está previsto um refatoramento em que o ETL do Jupyter será modularizado com uso de *models*, eliminando a redundância entre notebooks.

Projeto de análise histórica do Campeonato Brasileiro de Futebol na era dos pontos corridos. Abrange 19 edições (2007–2025), com ETL em Python/Jupyter e visualizações em Power BI.

---

## Estrutura do Projeto

```
Campeonato/
├── dados/
│   ├── raw/          # Fontes brutas (Campeonato.csv, gols, mercado)
│   └── processed/    # Tabelas geradas pelo ETL, consumidas pelo BI
├── notebooks/        # ETL, análises e scripts auxiliares
├── bi/               # Dashboard Power BI (verdadeiro.pbix)
├── img/              # Prints dos dashboards
└── documentacao.md   # Dicionário de dados completo
```

---

## Dashboards

### Página 1 — Números do Campeão

Perfil histórico de cada campeão: pontuação, vitórias, saldo de gols e aproveitamento. Inclui a evolução da posição ao longo das rodadas e os clubes que mais vezes lideraram o campeonato.

![Números do Campeão](img/pag1.png)

---

### Página 2 — Investimento vs Performance

Analisa a relação entre valor de mercado do elenco e desempenho em campo. Traz correlação de Pearson (geral e por período), percentual de campeões entre os maiores investidores e dispersão entre custo e posição final.

![Investimento vs Performance](img/pag2.png)

---

### Página 3 — Tese do Guardiola

Valida empiricamente a afirmação de Pep Guardiola: *"um campeonato se ganha nas últimas 8 rodadas e se perde nas 8 primeiras"*. Testa se o líder após a 8ª rodada converte a vantagem em título, com análise de ruptura pré/pós-2018 e inferência estatística (correlação de Pearson, teste de hipótese).

![Tese do Guardiola](img/pag3.png)

---

## Pipeline de Dados

```
Fontes brutas (raw/)
    └── ETL (notebooks/UltimateVersion_backup.ipynb)
            ├── fato_desempenho.csv
            ├── investimento_vs_desempenho.csv
            └── tese_r8_guardiola.csv
                    └── Power BI (bi/verdadeiro.pbix)
```

### Fontes brutas

| Arquivo | Descrição |
|---|---|
| `Campeonato.csv` | Resultados partida a partida (2007–2024) |
| `campeonato-brasileiro-full.csv` | Dados complementares 2025 |
| `campeonato-brasileiro-gols.csv` | Gols detalhados 2025 |
| `Investimento.csv` | Valor de mercado dos elencos por temporada |

### Tabelas processadas

| Arquivo | Dashboard |
|---|---|
| `fato_desempenho.csv` | Base geral — desempenho partida a partida |
| `investimento_vs_desempenho.csv` | Dashboard 2 — Investimento vs Performance |
| `tese_r8_guardiola.csv` | Dashboard 3 — Tese do Guardiola |

---

## Reproduzindo o ETL

1. Clone o repositório
2. Instale as dependências: `pip install pandas numpy scipy jupyter`
3. Abra `notebooks/UltimateVersion_backup.ipynb` e execute todas as células
4. Os CSVs gerados serão salvos em `dados/processed/`
5. Atualize as fontes de dados no Power BI apontando para `dados/processed/`

---

## Tecnologias

- **Python** — pandas, numpy, scipy (ETL e inferência estatística)
- **Jupyter Notebook** — pipeline de análise
- **Power BI Desktop** — dashboards e visualizações
