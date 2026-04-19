# Dicionário de Dados — Campeonato Brasileiro de Futebol (2007-2025)

## Visão Geral

Fonte: Campeonato.csv (2007-2024) + ETL via outraFonte.ipynb com 2025 (campeonato-brasileiro-full.csv + campeonato-brasileiro-gols.csv), normalizados em tabela fato. Período: 2007 a 2025, pontos corridos, 20 clubes por edição.

---

## 1. fato_desempenho.csv

**Tabela fato** — unidade de registro: desempenho do time em uma partida por temporada. Formato longo (uma linha por time por jogo). Codificação: `latin1`.

| Coluna | Tipo | Descrição | Exemplo |
|---|---|---|---|
| `data` | object (YYYY-MM-DD) | Data em que a partida ocorreu | `2007-05-03` |
| `rodada` | int64 | Número da rodada do campeonato (1 a 38) | `1` |
| `temporada` | int64 | Ano da edição do campeonato | `2007` |
| `time` | object | Nome do clube | `Internacional` |
| `adversario` | object | Nome do clube adversário | `Botafogo` |
| `gols_pro` | int64 | Gols marcados pelo time na partida | `2` |
| `gols_contra` | int64 | Gols sofridos pelo time na partida | `3` |
| `pontos` | int64 | Pontos conquistados na partida (3 = vitória, 1 = empate, 0 = derrota) | `0` |
| `casa_fora` | object | Mando de campo: `casa` (mandante) ou `fora` (visitante) | `casa` |
| `saldo` | int64 | Saldo de gols da partida (`gols_pro - gols_contra`) | `-1` |
| `vitoria` | int64 (flag) | 1 se vitória, 0 caso contrário | `0` |
| `empate` | int64 (flag) | 1 se empate, 0 caso contrário | `0` |
| `derrota` | int64 (flag) | 1 se derrota, 0 caso contrário | `1` |
| `pontos_acum` | int64 | Soma acumulada de pontos do time ao longo da temporada até aquela rodada | `0` |
| `vitorias_acum` | int64 | Soma acumulada de vitórias do time ao longo da temporada | `0` |
| `saldo_acum` | float64 | Saldo de gols acumulado ao longo da temporada | `-1.0` |
| `posicao_rodada` | int64 | Posição do time na tabela na rodada (1 = 1º lugar) | `12` |

---

## 2. desempenho_campeao.csv

**Dashboard 1 — Desempenho do Campeão.** Derivada do `fato_desempenho.csv`, usada diretamente no Power BI. Mesmas colunas, porém com `casa_fora` capitalizado (`Casa`/`Fora`). Permite rastrear a trajetória de qualquer time ao longo da temporada: evolução de pontos, posição a cada rodada, desempenho casa/fora.

Colunas idênticas à `fato_desempenho.csv`, exceto:

| Coluna | Formato | Observação |
|---|---|---|
| `casa_fora` | `Casa` / `Fora` (capitalizado) | Diferente do `fato_desempenho.csv` que usa letras minúsculas |
| `saldo_acum` | int64 | Diferente do `fato_desempenho.csv` que pode ser float |

---

## 3. investimento_vs_desempenho.csv

**Dashboard 2 — Investimento vs Títulos.** Agregação por `temporada × time`. Cada linha representa o desempenho final de um clube em uma edição, cruzado com valor médio de mercado. Separador: `;`. Codificação: `utf-8`.

| Coluna | Tipo | Descrição | Obs. |
|---|---|---|---|
| `temporada` | int64 | Ano da edição | |
| `time` | object | Nome do clube | |
| `pontos` | int64 | Total de pontos no campeonato | |
| `saldo` | int64 | Saldo de gols total no campeonato | |
| `vitoria` | int64 | Total de vitórias no campeonato | |
| `valor_mercado` | float64 | Valor médio de mercado do elenco (em R$, fonte: Transfermarkt/outra fonte) | Média por temporada |
| `rank_performance` | float64 | Classificação por pontos (1 = campeão) | Rank por temporada |
| `rank_financeiro` | float64 | Classificação por valor de mercado (1 = mais caro) | Rank por temporada |
| `no_g4_real` | int64 (flag) | 1 se terminou no G4 (Libertadores), 0 caso contrário | |
| `no_g4_financeiro` | int64 (flag) | 1 se é time do top 4 financeiro, 0 caso contrário | |
| `destaque_gestao` | object | Categoria: `Duo Dominante (Fla/Pal)` para Flamengo/Palmeiras pós-2018, `Outros` o restante | |

---

## 4. tese_r8_guardiola.csv

**Dashboard 3 — Tese da 8ª Rodada.** Uma linha por temporada. Valida a hipótese de que o líder ao final da 8ª rodada termina o campeonato como campeão (ou no top 4). Separador: `;`. Codificação: `utf-8`.

| Coluna | Tipo | Descrição | Obs. |
|---|---|---|---|
| `temporada` | int64 | Ano da edição | |
| `lider_r8` | object | Nome do clube que liderou ao final da 8ª rodada | |
| `pts_r8` | float64 | Pontos acumulados pelo líder após 8 rodadas | Máx. possível: 24 |
| `aproveitamento_r8` | float64 | % de aproveitamento do líder (pts_r8 / 24 × 100) | |
| `campeao` | object | Nome do clube campeão da temporada | |
| `pos_final_lider_r8` | int64 | Posição final do líder da R8 ao final do campeonato | 1 = campeão |
| `tese_confirmada` | int64 (flag) | 1 se o líder da R8 foi campeão, 0 caso contrário | |
| `periodo` | object | `Pre-ruptura (2007-2017)` ou `Pos-ruptura (2018-2025)` | |
| `ic_prop_lower` | float64 | Limite inferior do IC 95% da taxa de confirmação (Wilson score) | Mesmo valor em todas as linhas |
| `ic_prop_upper` | float64 | Limite superior do IC 95% da taxa de confirmação (Wilson score) | Mesmo valor em todas as linhas |
| `ic_r_lower` | float64 | Limite inferior do IC 95% da correlação de Pearson (Fisher z-transform) | Mesmo valor em todas as linhas |
| `ic_r_upper` | float64 | Limite superior do IC 95% da correlação de Pearson (Fisher z-transform) | Mesmo valor em todas as linhas |
| `ic_pos_lower` | float64 | Limite inferior do IC 95% da posição final média do líder R8 (t de Student) | Mesmo valor em todas as linhas |
| `ic_pos_upper` | float64 | Limite superior do IC 95% da posição final média do líder R8 (t de Student) | Mesmo valor em todas as linhas |

---

## Notas Técnicas

- **Fonte original:** Campeonato.csv (dados de 2007-2024)
- **Fonte complementar 2025:** campeonato-brasileiro-full.csv + campeonato-brasileiro-gols.csv (dados.kaggle.com)
- **ETL:** outraFonte.ipynb → normaliza em formato fato → concatena com `fato_desempenho.csv` existente
- **Valores de mercado 2025:** ListaDeTimes.docx (extraídos manualmente, em reais)
- **Ruptura 2018:** marco adotado para comparar pré e pós, alinhado com a hegemonia financeira de Flamengo e Palmeiras
- **Testes estatísticos:** Pearson (correlação), Fisher z (comparação entre correlações), t-test (diferença vs. aleatório), teste binomial (frequência de campeões no top 4 financeiro)
