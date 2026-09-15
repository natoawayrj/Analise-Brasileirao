# Análise do Campeonato Brasileiro (2007–2025)

Projeto de engenharia e análise de dados sobre o Campeonato Brasileiro na era dos pontos corridos. O pipeline transforma resultados de partidas em tabelas analíticas consumidas pelo Power BI e avalia a relação entre **valor de mercado do elenco**, desempenho e liderança após a 8ª rodada.

> **Nomenclatura.** O arquivo histórico se chama `Investimento.csv`, mas a variável que ele
> carrega é o **valor de mercado do elenco titular**, não investimento realizado (compras,
> salários, estrutura). Os dois não são intercambiáveis: um clube pode ter elenco valioso
> formado na base e gastar pouco. Onde o texto diz "valor de mercado", é isso que está
> sendo medido.

## Dados

- **Fonte:** *a preencher* — os CSVs em `dados/raw/` foram herdados da primeira versão do
  projeto sem registro da origem. Antes de citar o projeto em qualquer processo seletivo,
  confirme o dataset de origem e coloque o link aqui e em `docs/fontes.md`.
  `dados/raw/Investimento_2025.csv` foi montado manualmente e também precisa de fonte e
  data de coleta.
- **Período:** temporadas 2007–2025 do Brasileirão (pontos corridos, 20 clubes, 38 rodadas).
- **Granularidade:**
  - `dados/raw/Campeonato.csv` e `campeonato-brasileiro-full.csv` — 1 linha por partida
  - `campeonato-brasileiro-gols.csv` — 1 linha por gol
  - `dados/processed/fato_desempenho.csv` — 1 linha por clube por partida
  - `dados/processed/investimento_vs_desempenho.csv` — 1 linha por clube por temporada
  - `dados/processed/tese_r8_guardiola.csv` — 1 linha por temporada
- **Volume:** 8.453 / 9.165 / 10.820 linhas nas fontes brutas; 14.246 linhas na tabela fato;
  378 pares clube-temporada; 19 temporadas.
- **Limitações conhecidas:**
  - **Origem não documentada** (acima) — sem isso, nenhum número aqui é auditável por
    terceiros.
  - `valor_mercado` é um retrato do elenco, não um fluxo de gastos. A análise mede
    **associação**, não causalidade: valor de elenco e título compartilham causas comuns
    (receita, histórico, gestão, sócio-torcedor).
  - 19 temporadas é uma amostra pequena para conclusões sobre tendência temporal. Recortes
    como "antes e depois de 2018" ficam com 11 e 8 temporadas.
  - 2024 está incompleta na fonte (283 partidas) e fica fora das inferências da tese da
    8ª rodada.
  - Não há dados de folha salarial, receita de TV, lesões ou mercado de transferências —
    o projeto não consegue responder *por que* um clube performa acima do valor do elenco.

## Resultados principais

Números reproduzíveis por `python -m src.pipeline` sobre `investimento_vs_desempenho.csv`:

| Recorte | Pearson *r* (valor de mercado × pontos) | IC95% | n (clube-temporada) |
|---|---|---|---|
| 2007–2025 | 0,388 | 0,30 – 0,47 | 378 |
| Até 2017 | 0,567 | 0,47 – 0,65 | 218 |
| 2018 em diante | 0,423 | 0,29 – 0,54 | 160 |

A associação cai depois de 2018, mas os intervalos de confiança se sobrepõem — a queda
**não é conclusiva** com esta amostra.

**Campeões e dinheiro:** 14 dos 19 campeões (74%) estavam no G4 de valor de mercado no ano
do título (coluna `no_g4_financeiro`). Critério explícito: os 4 maiores valores de elenco da
temporada.

**Tese da 8ª rodada (refutada):** apenas 21% dos líderes após a 8ª rodada terminaram
campeões. Resultado negativo, reportado como tal.

> Os cartões do `.pbix` exibem `Correlação Geral 0,6404` e `Correlação Pós-2018 0,3771`.
> Esses valores dependem do estado dos slicers do relatório e não correspondem aos recortes
> da tabela acima — os números desta seção são os que o pipeline reproduz.

## Estrutura

```text
Analise-Brasileirao/
├── dados/
│   ├── raw/                 fontes brutas e valores de mercado de 2025
│   └── processed/           tabelas geradas pelo pipeline
├── src/                     ETL, qualidade e estatística
├── tests/                   testes automatizados
├── notebooks/               instruções para exploração visual
├── img/                     imagens dos dashboards
├── documentacao.md          dicionário de dados
└── docs/                    desenho e decisões do pipeline
```

## Executar

Instale as dependências:

```bash
pip install -r requirements-dev.txt
```

Para uma execução estrita:

```bash
python -m src.pipeline
```

Essa execução interrompe o processo se houver temporada incompleta. Para gerar as saídas disponíveis e marcar as limitações:

```bash
python -m src.pipeline --allow-incomplete
```

Os testes podem ser executados com:

```bash
pytest -q
```

## Saídas

- `dados/processed/fato_desempenho.csv`: uma linha por clube e partida, com pontos, saldo, acumulados, posição na rodada e indicação de partida realizada.
- `dados/processed/investimento_vs_desempenho.csv`: desempenho final cruzado com valor médio de mercado.
- `dados/processed/tese_r8_guardiola.csv`: líder após a 8ª rodada, posição final e validade da inferência.

Os nomes dos três arquivos foram preservados para reduzir o trabalho de atualização no Power BI.

## Limitações conhecidas

- A fonte disponível não possui todos os jogos de 2024; essa temporada é marcada como incompleta e não entra nas inferências da tese da 8ª rodada.
- A partida Chapecoense × Atlético-MG de 2016 aparece sem placar na fonte. Ela permanece como partida não realizada, sem receber pontos artificialmente.
- Os valores de mercado de 2025 foram separados em `dados/raw/Investimento_2025.csv` porque foram obtidos manualmente e precisam de uma fonte/data de referência no acompanhamento do projeto.
- O arquivo `.pbix` não é versionado neste repositório. As medidas e cartões devem ser revisados no Power BI após a atualização dos CSVs.

## Dashboards

![Números do campeão](img/pag1.png)

![Investimento vs performance](img/pag2.png)

![Tese da 8ª rodada](img/pag3.png)

## Documentação

- [Dicionário de dados](documentacao.md)
- [Fontes e limitações](docs/fontes.md)
- [Desenho do pipeline](docs/superpowers/specs/2026-07-20-pipeline-brasileirao-design.md)
