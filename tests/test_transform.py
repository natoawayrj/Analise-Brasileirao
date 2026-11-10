import pandas as pd

from src.transform import build_fact, final_standings


def sample_matches():
    return pd.DataFrame(
        [
            {"partida_id": "a", "temporada": 2025, "data": "2025-01-01", "rodada": 1, "mandante": "A", "visitante": "B", "gols_mandante": 2, "gols_visitante": 0, "fonte": "test"},
            {"partida_id": "b", "temporada": 2025, "data": "2025-01-08", "rodada": 2, "mandante": "B", "visitante": "A", "gols_mandante": 1, "gols_visitante": 1, "fonte": "test"},
        ]
    )


def test_build_fact_derives_points_and_accumulates():
    fact = build_fact(sample_matches())
    a = fact[fact["time"] == "A"].sort_values("rodada")
    assert a["pontos"].tolist() == [3, 1]
    assert a["pontos_acum"].tolist() == [3, 4]
    assert a["vitoria"].tolist() == [1, 0]


def test_final_standings_uses_points_before_other_tiebreakers():
    fact = build_fact(sample_matches())
    standings = final_standings(fact)
    assert standings.iloc[0]["time"] == "A"
    assert standings.iloc[0]["rank_performance"] == 1

