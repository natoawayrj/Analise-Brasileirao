from __future__ import annotations

import pandas as pd

from .config import EXPECTED_MATCHES, EXPECTED_ROUNDS, EXPECTED_TEAMS


class DataQualityError(ValueError):
    """Erro levantado quando a fonte não atende ao contrato do pipeline."""


def quality_issues(matches: pd.DataFrame, fact: pd.DataFrame | None = None) -> list[str]:
    issues: list[str] = []
    home_clubs = matches.groupby("temporada")["mandante"].agg(lambda values: set(values))
    away_clubs = matches.groupby("temporada")["visitante"].agg(lambda values: set(values))
    club_counts = home_clubs.combine(away_clubs, lambda home, away: len(home | away))
    summary = matches.groupby("temporada").agg(
        partidas=("partida_id", "nunique"),
        rodadas=("rodada", "nunique"),
    )
    summary["clubes"] = club_counts
    for season, row in summary.iterrows():
        if int(row["clubes"]) != EXPECTED_TEAMS:
            issues.append(f"{season}: {int(row['clubes'])} clubes distintos; esperado {EXPECTED_TEAMS}")
        if int(row["rodadas"]) != EXPECTED_ROUNDS:
            issues.append(f"{season}: {int(row['rodadas'])} rodadas; esperado {EXPECTED_ROUNDS}")
        if int(row["partidas"]) != EXPECTED_MATCHES:
            issues.append(f"{season}: {int(row['partidas'])} partidas; esperado {EXPECTED_MATCHES}")
    score_columns = {"gols_mandante", "gols_visitante"}
    if not score_columns.issubset(matches.columns):
        issues.append("Colunas de placar ausentes na fonte")
    else:
        missing_scores = matches["gols_mandante"].isna() | matches["gols_visitante"].isna()
        if missing_scores.any():
            for season, count in matches.loc[missing_scores].groupby("temporada").size().items():
                issues.append(f"{season}: {int(count)} partidas sem placar; elas não entram nas inferências")
    duplicated = matches.duplicated(["temporada", "rodada", "mandante", "visitante", "data"])
    if duplicated.any():
        issues.append(f"{int(duplicated.sum())} partidas duplicadas pela chave natural")
    unknown_mojibake = matches["mandante"].astype(str).str.contains(r"Ã|Â|�", regex=True) | matches["visitante"].astype(str).str.contains(r"Ã|Â|�", regex=True)
    if unknown_mojibake.any():
        issues.append(f"{int(unknown_mojibake.sum())} partidas ainda contêm texto com encoding inválido")
    if fact is not None:
        played = fact["partida_realizada"].eq(1)
        expected_points = ((fact["gols_pro"] > fact["gols_contra"]).astype(int) * 3 + (fact["gols_pro"] == fact["gols_contra"]).astype(int))
        if not fact.loc[played, "pontos"].eq(expected_points[played]).all():
            issues.append("Pontos incompatíveis com o placar na tabela fato")
        if fact.duplicated(["partida_id", "time"]).any():
            issues.append("A tabela fato contém mais de uma linha por partida e clube")
    return issues


def validate(matches: pd.DataFrame, fact: pd.DataFrame | None = None, strict: bool = True) -> list[str]:
    issues = quality_issues(matches, fact)
    if issues and strict:
        formatted = "\n".join(f"- {issue}" for issue in issues)
        raise DataQualityError(f"Falhas de qualidade de dados:\n{formatted}")
    return issues
