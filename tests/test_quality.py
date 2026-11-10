import pandas as pd

from src.quality import quality_issues


def test_quality_flags_incomplete_season():
    matches = pd.DataFrame(
        [
            {"partida_id": "a", "temporada": 2024, "rodada": 1, "mandante": "A", "visitante": "B", "data": "2024-01-01"},
        ]
    )
    issues = quality_issues(matches)
    assert any("partidas" in issue for issue in issues)
    assert any("clubes" in issue for issue in issues)

