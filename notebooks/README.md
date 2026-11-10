# Notebooks

O ETL principal não fica mais em um notebook. Para regenerar as tabelas consumidas pelo Power BI, execute na raiz do projeto:

```bash
python -m src.pipeline --allow-incomplete
```

O argumento `--allow-incomplete` é necessário enquanto a fonte disponível não tiver todos os jogos de 2024. A temporada será marcada como incompleta nas saídas e não será usada nas inferências da tese da 8ª rodada.

Use notebooks separados apenas para exploração, gráficos e validação visual dos CSVs gerados.
