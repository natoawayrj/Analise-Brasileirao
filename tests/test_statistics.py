import pandas as pd
import pytest

from src.statistics import season_spearman, summarize_champions_g4, summarize_rank_correlation


def make_investment() -> pd.DataFrame:
    rows = []
    # Duas temporadas completas com escalas de valor totalmente diferentes.
    # O ranking dentro de cada temporada e identico, entao o Spearman deve ser igual.
    for season, scale in ((2010, 1_000_000), (2023, 1)):
        for i, club in enumerate("ABCDEF"):
            rows.append(
                {
                    "temporada": season,
                    "time": club,
                    "pontos": 80 - i * 10,
                    "valor_mercado": (6 - i) * scale,
                    "rank_performance": i + 1,
                    "rank_financeiro": i + 1,
                    "no_g4_financeiro": int(i < 4),
                    "temporada_completa": 1,
                }
            )
    # Temporada incompleta: deve ser ignorada.
    rows.append(
        {"temporada": 2024, "time": "A", "pontos": 10, "valor_mercado": 1, "rank_performance": 1,
         "rank_financeiro": 5, "no_g4_financeiro": 0, "temporada_completa": 0}
    )
    return pd.DataFrame(rows)


def test_spearman_is_scale_invariant_across_seasons():
    by_season = season_spearman(make_investment())
    assert by_season["temporada"].tolist() == [2010, 2023]
    assert by_season["spearman_rho"].tolist() == pytest.approx([1.0, 1.0])


def test_rank_correlation_ignores_incomplete_seasons_and_splits_periods():
    summary = summarize_rank_correlation(make_investment())
    assert summary["completo"]["temporadas"] == 2
    assert summary["pre_ruptura"]["temporadas"] == 1
    assert summary["pos_ruptura"]["temporadas"] == 1


def test_champions_g4_reports_total_and_complete_seasons():
    result = summarize_champions_g4(make_investment())
    assert result["campeoes"] == 3
    assert result["campeoes_no_g4_financeiro"] == 2
    assert result["campeoes_temporadas_completas"] == 2
    assert result["campeoes_completas_no_g4_financeiro"] == 2
