# Fontes e limitações

> **Pendência aberta: origem upstream não documentada.** Os arquivos de `dados/raw/` foram
> herdados da primeira versão do projeto sem registro de qual dataset os originou. Enquanto
> essa linha não for preenchida com nome do dataset, link e data de coleta, os números do
> projeto não são auditáveis por terceiros — e "de onde vieram os dados?" é a primeira
> pergunta de qualquer entrevista técnica.
>
> - Dataset de origem: _a preencher_
> - Link: _a preencher_
> - Data de coleta: _a preencher_
> - Licença / termos de uso: _a preencher_

## Resultados

- `dados/raw/Campeonato.csv`: resultados históricos de 2003 a 2024; o pipeline usa 2007–2024.
- `dados/raw/campeonato-brasileiro-full.csv`: base histórica que contém partidas até 2025; o pipeline usa apenas as partidas cuja data pertence a 2025.
- `dados/raw/campeonato-brasileiro-gols.csv`: eventos de gols disponíveis na fonte original; mantido para rastreabilidade, enquanto os placares da temporada 2025 são lidos da base completa de partidas.

## Mercado

- `dados/raw/Investimento.csv`: valores de mercado associados às partidas de 2007–2024.
- `dados/raw/Investimento_2025.csv`: valores de 2025 extraídos manualmente da fonte usada na primeira versão do projeto. A fonte primária e a data de coleta devem ser preenchidas quando essa informação estiver disponível.

## Regras de qualidade

O pipeline não considera uma temporada completa apenas porque possui 20 clubes. Ela precisa ter 38 rodadas, 380 partidas agendadas e 380 partidas com placar. Temporadas incompletas permanecem na tabela fato para transparência, mas ficam fora das inferências estatísticas da tese da 8ª rodada.

## Power BI

Depois de executar o pipeline, atualize as três fontes CSV no Power BI. Revise manualmente os cartões que dependem de medidas antigas, principalmente os indicadores de aproveitamento e de conversão do líder da 8ª rodada.
