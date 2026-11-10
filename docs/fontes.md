# Fontes e limitações

Última revisão: 27/10/2026. Esta página registra de onde vem cada dado e o que ele mede.
Onde a origem não pôde ser confirmada, está escrito.

## Partidas (placares, rodadas, datas)

| Arquivo | Período usado | Origem |
|---|---|---|
| `dados/raw/Campeonato.csv` | 2007–2024 | Dataset de terceiros herdado da primeira versão do projeto. **Origem não registrada.** 2024 tem 283 de 380 jogos |
| `dados/raw/campeonato-brasileiro-full.csv` | só jogos de 2025 | Mesma situação: **origem não registrada** |
| `dados/raw/campeonato-brasileiro-gols.csv` | não usado nas métricas | Eventos de gol, mantido por rastreabilidade |

Referências consultadas para os dados de partidas (informadas pelo autor; não verificadas como
origem exata dos CSVs):

- Base dos Dados, dataset "Campeonatos de Futebol" (organização listada: Transfermarkt; cobertura 2000 a 05/03/2025).
- RPubs, "Brasileirão 2003–2024" (a página não informa a origem dos seus dados).

## Valor de mercado

A coluna `valor_mercado` **não é uma série única e comparável**. Ela junta três medidas:

| Período | Origem | O que mede | Escala observada |
|---|---|---|---|
| 2007–2022 | colunas `valor_equipe_titular_mandante/visitante` do `Campeonato.csv`; média por clube-temporada | Valor do time titular por jogo | mediana por temporada de 3,7 a 22,6 milhões |
| 2023–2024 | mesmas colunas do `Campeonato.csv` | mesma medida, porém em **escala diferente** | mediana de 2.888 (2023) e 3.120 (2024) |
| 2025 | `dados/raw/Investimento_2025.csv`, digitado à mão a partir de uma lista (`ListaDeTimes.docx`) | Valor do **elenco inteiro**, em euros (confere com o Transfermarkt no início de 2025) | mediana de cerca de 88 milhões |

Consequências:

- Os valores de 2023 e 2024 não são comparáveis aos de 2007–2022 nem aos de 2025.
- Por isso a correlação de Pearson sobre `valor_mercado` bruto **não é usada como resultado**. O
  pipeline a mantém apenas em `resumo_pearson_bruto_nao_confiavel`.
- A análise usa o **ranking dentro de cada temporada** (Spearman, clubes da mesma temporada),
  que não depende de unidade nem de moeda.

### Conferência cruzada (matérias, acessadas em 27/10/2026)

Usadas só como checagem. **Não** são a origem dos CSVs.

| Ano | Matéria | Fonte citada | Medida | Referência |
|---|---|---|---|---|
| 2023 | Lance!, ranking de elencos mais valiosos | Pluri Consultoria | elenco inteiro, € | abril/2023; a matéria traz só os 5 primeiros e o último |
| 2024 | Lance!, "Palmeiras supera Flamengo…" | Transfermarkt | elenco inteiro, R$ | 11/04/2024; 20 clubes |
| 2025 | Times Brasil/CNBC; O Antagonista; Lance! | Transfermarkt | elenco inteiro, € | 29/03/2025 |

O ranking de 2024 das matérias **não coincide** com o do CSV (por exemplo, o Botafogo é o 10º
na matéria e o 5º no CSV), o que confirma que o CSV mede outra coisa.

### Pendências de verificação

- Dois valores de 2025 divergem das matérias: Botafogo (135,95 mi no arquivo; 133,95 mi nas matérias) e Mirassol (18,23 mi no arquivo; 15,4 mi na matéria). Pode ser digitação ou outra data de consulta.
- Origem do `Campeonato.csv` e do `campeonato-brasileiro-full.csv`.

## Limitações

- **Associação, não causalidade.** Valor de elenco e desempenho compartilham causas (receita, histórico, gestão).
- **Amostra pequena:** 17 temporadas completas (10 até 2017 e 7 de 2018 em diante). Diferenças entre períodos exigem cautela.
- **Temporadas incompletas ficam fora das inferências:** 2016 (uma partida sem placar na fonte, Chapecoense × Atlético-MG) e 2024 (283 jogos).
- **2007 e 2011 têm 19 clubes** na análise de valor, porque um clube ficou sem valor de mercado na fonte.
- **Sem dados de folha salarial, receita, lesões ou transferências.** O projeto mede associação, não explica o porquê.
- **Os arquivos brutos não são redistribuídos com licença conhecida.** Verifique os termos de uso das fontes antes de republicar os dados.

## Regras de qualidade

Uma temporada só é completa com 20 clubes, 38 rodadas, 380 partidas agendadas e 380 partidas
com placar. Temporadas incompletas continuam na tabela fato, mas saem das inferências.

## Power BI

O `.pbix` não é versionado. As três fontes do modelo devem apontar para `dados/processed/`
e ser atualizadas após cada execução do pipeline.
