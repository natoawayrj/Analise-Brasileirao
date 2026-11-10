# Dicionário de dados — Campeonato Brasileiro (2007–2025)

## Convenções

- Encoding dos CSVs processados: UTF-8.
- A unidade da tabela fato é um clube em uma partida.
- `partida_id` identifica a partida; a chave da fato é `partida_id + time`.
- `temporada_completa = 1` somente quando há 20 clubes, 38 rodadas, 380 partidas agendadas e 380 partidas com placar.

## `fato_desempenho.csv`

| Coluna | Descrição |
|---|---|
| `partida_id` | Identificador estável da partida |
| `data` | Data da partida |
| `rodada` | Rodada do campeonato |
| `temporada` | Edição do campeonato |
| `time` | Clube observado |
| `adversario` | Clube adversário |
| `gols_pro` | Gols marcados pelo clube |
| `gols_contra` | Gols sofridos pelo clube |
| `pontos` | 3, 1 ou 0; fica vazio quando não há placar |
| `casa_fora` | `casa` ou `fora` |
| `saldo` | `gols_pro - gols_contra` |
| `vitoria`, `empate`, `derrota` | Indicadores binários do resultado |
| `pontos_acum` | Pontos acumulados na temporada |
| `vitorias_acum` | Vitórias acumuladas na temporada |
| `saldo_acum` | Saldo acumulado na temporada |
| `posicao_rodada` | Posição após a rodada, usando pontos, vitórias, saldo, gols marcados e nome como desempate determinístico |
| `partida_realizada` | 1 quando há placar; 0 quando a partida não foi realizada na fonte |
| `fonte` | Arquivo de origem |

## `investimento_vs_desempenho.csv`

Uma linha por `temporada × time`, após a agregação do valor médio de mercado.

| Coluna | Descrição |
|---|---|
| `temporada`, `time` | Chave analítica |
| `pontos`, `saldo`, `vitoria` | Desempenho final |
| `valor_mercado` | Valor médio de mercado disponível |
| `rank_performance` | Ranking final por pontos e critérios de desempate |
| `rank_financeiro` | Ranking por valor de mercado |
| `no_g4_real` | 1 quando terminou entre os quatro primeiros |
| `no_g4_financeiro` | 1 quando ficou entre os quatro maiores valores |
| `destaque_gestao` | Classificação usada no dashboard |
| `temporada_completa` | Indicador de cobertura da temporada |

## `tese_r8_guardiola.csv`

Uma linha por temporada. A inferência só usa temporadas completas.

| Coluna | Descrição |
|---|---|
| `temporada` | Edição analisada |
| `lider_r8` | Líder após a 8ª rodada |
| `pts_r8` | Pontos do líder após oito rodadas |
| `aproveitamento_r8` | `pts_r8 / 24 × 100` |
| `campeao` | Campeão final, quando a temporada é válida para inferência |
| `pos_final_lider_r8` | Posição final do líder da 8ª rodada |
| `tese_confirmada` | 1 quando o líder da 8ª rodada foi campeão; vazio para temporada inválida |
| `periodo` | Pré ou pós-ruptura de 2018 |
| `temporada_completa` | Indicador de cobertura |
| `incluida_inferencia` | 1 quando o resultado foi usado nos testes |
| `ic_prop_lower`, `ic_prop_upper` | Limites do IC de 95% para a proporção de confirmações |
| `ic_r_lower`, `ic_r_upper` | Limites do IC de 95% da correlação entre aproveitamento na R8 e posição final |
| `ic_pos_lower`, `ic_pos_upper` | Limites do IC de 95% da posição final média |
