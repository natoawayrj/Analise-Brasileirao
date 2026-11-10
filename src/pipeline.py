from __future__ import annotations

import argparse
import json

from .config import FACT_FILE, INVESTMENT_FILE, PROCESSED_DIR, R8_FILE
from .quality import validate
from .statistics import summarize_champions_g4, summarize_investment, summarize_r8, summarize_rank_correlation
from .transform import build_fact, build_investment, build_r8, load_matches, season_summary


def run(allow_incomplete: bool = False) -> dict:
    matches = load_matches()
    fact = build_fact(matches)
    issues = validate(matches, fact, strict=not allow_incomplete)
    summary = season_summary(fact)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    fact.to_csv(FACT_FILE, index=False, encoding="utf-8")
    investment = build_investment(fact)
    investment.to_csv(INVESTMENT_FILE, index=False, sep=";", encoding="utf-8")
    r8 = build_r8(fact)
    r8.to_csv(R8_FILE, index=False, sep=";", encoding="utf-8")
    stats = summarize_r8(r8)

    result = {
        "linhas_fato": len(fact),
        "linhas_investimento": len(investment),
        "linhas_tese_r8": len(r8),
        "problemas_qualidade": issues,
        "resumo_temporadas": summary.to_dict(orient="records"),
        "resumo_r8": stats,
        "resumo_correlacao_ranking": summarize_rank_correlation(investment),
        "resumo_campeoes_g4": summarize_champions_g4(investment),
        "resumo_pearson_bruto_nao_confiavel": summarize_investment(investment),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera as tabelas processadas do Brasileirão.")
    parser.add_argument("--allow-incomplete", action="store_true", help="Gera saídas mesmo com temporadas incompletas, marcando-as no resultado.")
    args = parser.parse_args()
    run(allow_incomplete=args.allow_incomplete)


if __name__ == "__main__":
    main()
