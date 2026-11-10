from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

from .config import (
    MARKET_2025_FILE,
    NEW_MATCHES_FILE,
    OLD_MARKET_FILE,
    OLD_MATCHES_FILE,
    SEASON_END,
    SEASON_START,
)
from .normalize import canonicalize_team_series, read_csv_robust
from .statistics import r8_confidence_metrics


def _stable_match_id(row: pd.Series) -> str:
    raw = "|".join(str(row[column]) for column in ("temporada", "rodada", "data", "mandante", "visitante"))
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def load_old_matches(path: Path = OLD_MATCHES_FILE) -> pd.DataFrame:
    df = read_csv_robust(path)
    df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")].copy()
    required = {
        "ano_campeonato", "data", "rodada", "time_mandante", "time_visitante",
        "gols_mandante", "gols_visitante",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Colunas ausentes em {path.name}: {sorted(missing)}")

    df = df.rename(columns={"ano_campeonato": "temporada", "time_mandante": "mandante", "time_visitante": "visitante"})
    df["temporada"] = pd.to_numeric(df["temporada"], errors="raise").astype(int)
    df = df[df["temporada"].between(SEASON_START, SEASON_END - 1)].copy()
    df["data"] = pd.to_datetime(df["data"], errors="coerce", format="mixed", dayfirst=True)
    df["rodada"] = pd.to_numeric(df["rodada"], errors="coerce")
    for column in ("gols_mandante", "gols_visitante"):
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df["mandante"] = canonicalize_team_series(df["mandante"])
    df["visitante"] = canonicalize_team_series(df["visitante"])
    df["fonte"] = path.name
    df["partida_id"] = df.apply(_stable_match_id, axis=1)
    return df[["partida_id", "temporada", "data", "rodada", "mandante", "visitante", "gols_mandante", "gols_visitante", "fonte"]]


def load_2025_matches(path: Path = NEW_MATCHES_FILE) -> pd.DataFrame:
    df = read_csv_robust(path)
    df.columns = df.columns.astype(str).str.strip().str.lower()
    df = df.rename(columns={"rodata": "rodada", "id": "partida_id"})
    required = {"partida_id", "data", "rodada", "mandante", "visitante", "mandante_placar", "visitante_placar"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Colunas ausentes em {path.name}: {sorted(missing)}")
    df["data"] = pd.to_datetime(df["data"], errors="coerce", format="mixed", dayfirst=True)
    df = df[df["data"].dt.year == 2025].copy()
    df["temporada"] = 2025
    df["rodada"] = pd.to_numeric(df["rodada"], errors="coerce")
    df["gols_mandante"] = pd.to_numeric(df["mandante_placar"], errors="coerce")
    df["gols_visitante"] = pd.to_numeric(df["visitante_placar"], errors="coerce")
    df["mandante"] = canonicalize_team_series(df["mandante"])
    df["visitante"] = canonicalize_team_series(df["visitante"])
    df["partida_id"] = "2025-" + df["partida_id"].astype(str)
    df["fonte"] = path.name
    return df[["partida_id", "temporada", "data", "rodada", "mandante", "visitante", "gols_mandante", "gols_visitante", "fonte"]]


def load_matches() -> pd.DataFrame:
    matches = pd.concat([load_old_matches(), load_2025_matches()], ignore_index=True)
    numeric_columns = ["temporada", "rodada", "gols_mandante", "gols_visitante"]
    invalid_schedule = matches[["temporada", "rodada"]].isna().any(axis=1)
    if invalid_schedule.any():
        bad = matches[invalid_schedule]
        raise ValueError(f"Partidas com temporada/rodada inválidas: {bad[['partida_id', *numeric_columns]].to_dict('records')[:3]}")
    matches["rodada"] = matches["rodada"].astype(int)
    matches[["gols_mandante", "gols_visitante"]] = matches[["gols_mandante", "gols_visitante"]].astype(float)
    return matches.sort_values(["temporada", "rodada", "data", "partida_id"]).reset_index(drop=True)


def build_fact(matches: pd.DataFrame) -> pd.DataFrame:
    home = matches.rename(columns={"mandante": "time", "visitante": "adversario", "gols_mandante": "gols_pro", "gols_visitante": "gols_contra"}).copy()
    home["casa_fora"] = "casa"
    away = matches.rename(columns={"visitante": "time", "mandante": "adversario", "gols_visitante": "gols_pro", "gols_mandante": "gols_contra"}).copy()
    away["casa_fora"] = "fora"
    fact = pd.concat([home, away], ignore_index=True)
    played = fact["gols_pro"].notna() & fact["gols_contra"].notna()
    fact["partida_realizada"] = played.astype(int)
    fact["pontos"] = np.select(
        [~played, fact["gols_pro"] > fact["gols_contra"], fact["gols_pro"] == fact["gols_contra"]],
        [np.nan, 3, 1],
        default=0,
    )
    fact["saldo"] = fact["gols_pro"] - fact["gols_contra"]
    fact["vitoria"] = (fact["pontos"] == 3).astype(int)
    fact["empate"] = (fact["pontos"] == 1).astype(int)
    fact["derrota"] = (fact["pontos"] == 0).astype(int)
    fact = fact.sort_values(["temporada", "time", "rodada", "data", "partida_id"]).reset_index(drop=True)
    group = fact.groupby(["temporada", "time"], sort=False)
    fact["pontos_acum"] = fact.assign(_pontos=fact["pontos"].fillna(0)).groupby(["temporada", "time"], sort=False)["_pontos"].cumsum()
    fact["vitorias_acum"] = group["vitoria"].cumsum()
    fact["saldo_acum"] = fact.assign(_saldo=fact["saldo"].fillna(0)).groupby(["temporada", "time"], sort=False)["_saldo"].cumsum()
    fact["gols_pro_acum"] = fact.assign(_gols=fact["gols_pro"].fillna(0)).groupby(["temporada", "time"], sort=False)["_gols"].cumsum()

    round_table = fact.groupby(["temporada", "rodada", "time"], as_index=False).agg(
        pontos_acum=("pontos_acum", "max"),
        vitorias_acum=("vitorias_acum", "max"),
        saldo_acum=("saldo_acum", "max"),
        gols_pro_acum=("gols_pro_acum", "max"),
    )
    round_table = round_table.sort_values(
        ["temporada", "rodada", "pontos_acum", "vitorias_acum", "saldo_acum", "gols_pro_acum", "time"],
        ascending=[True, True, False, False, False, False, True],
    )
    round_table["posicao_rodada"] = round_table.groupby(["temporada", "rodada"]).cumcount() + 1
    fact = fact.merge(round_table[["temporada", "rodada", "time", "posicao_rodada"]], on=["temporada", "rodada", "time"], how="left", validate="many_to_one")
    columns = [
        "partida_id", "data", "rodada", "temporada", "time", "adversario", "gols_pro", "gols_contra",
        "pontos", "casa_fora", "saldo", "vitoria", "empate", "derrota", "pontos_acum", "vitorias_acum",
        "saldo_acum", "posicao_rodada", "partida_realizada", "fonte",
    ]
    return fact.sort_values(["temporada", "rodada", "partida_id", "casa_fora"])[columns].reset_index(drop=True)


def season_summary(fact: pd.DataFrame) -> pd.DataFrame:
    summary = fact.groupby("temporada").agg(
        linhas=("partida_id", "size"),
        partidas_agendadas=("partida_id", "nunique"),
        clubes=("time", "nunique"),
        rodadas=("rodada", "nunique"),
    ).reset_index()
    played = fact[fact["partida_realizada"].eq(1)].groupby("temporada")["partida_id"].nunique()
    summary["partidas_jogadas"] = summary["temporada"].map(played).fillna(0).astype(int)
    summary["temporada_completa"] = (
        (summary["partidas_agendadas"] == 380) & (summary["partidas_jogadas"] == 380) & (summary["clubes"] == 20) & (summary["rodadas"] == 38)
    ).astype(int)
    return summary


def final_standings(fact: pd.DataFrame) -> pd.DataFrame:
    standings = fact.groupby(["temporada", "time"], as_index=False).agg(
        pontos=("pontos", "sum"), saldo=("saldo", "sum"), vitoria=("vitoria", "sum"), gols_pro=("gols_pro", "sum")
    )
    standings = standings.sort_values(
        ["temporada", "pontos", "vitoria", "saldo", "gols_pro", "time"],
        ascending=[True, False, False, False, False, True],
    ).reset_index(drop=True)
    standings["rank_performance"] = standings.groupby("temporada").cumcount() + 1
    return standings


def _market_long(df: pd.DataFrame) -> pd.DataFrame:
    home = df[["ano_campeonato", "time_mandante", "valor_equipe_titular_mandante"]].rename(
        columns={"ano_campeonato": "temporada", "time_mandante": "time", "valor_equipe_titular_mandante": "valor_mercado"}
    )
    away = df[["ano_campeonato", "time_visitante", "valor_equipe_titular_visitante"]].rename(
        columns={"ano_campeonato": "temporada", "time_visitante": "time", "valor_equipe_titular_visitante": "valor_mercado"}
    )
    values = pd.concat([home, away], ignore_index=True)
    values["time"] = canonicalize_team_series(values["time"])
    values["valor_mercado"] = pd.to_numeric(values["valor_mercado"], errors="coerce")
    return values


def load_market_values() -> pd.DataFrame:
    old = read_csv_robust(OLD_MARKET_FILE)
    old = old.loc[:, ~old.columns.astype(str).str.startswith("Unnamed")]
    old_values = _market_long(old)
    manual = read_csv_robust(MARKET_2025_FILE)
    manual["time"] = canonicalize_team_series(manual["time"])
    manual["valor_mercado"] = pd.to_numeric(manual["valor_mercado"], errors="coerce")
    return pd.concat([old_values, manual[["temporada", "time", "valor_mercado"]]], ignore_index=True)


def build_investment(fact: pd.DataFrame) -> pd.DataFrame:
    standings = final_standings(fact)
    values = load_market_values().groupby(["temporada", "time"], as_index=False)["valor_mercado"].mean()
    result = standings.merge(values, on=["temporada", "time"], how="left", validate="one_to_one")
    result = result.merge(season_summary(fact)[["temporada", "temporada_completa"]], on="temporada", how="left")
    result = result.dropna(subset=["valor_mercado"]).copy()
    result["rank_financeiro"] = result.sort_values(
        ["temporada", "valor_mercado", "time"], ascending=[True, False, True]
    ).groupby("temporada").cumcount() + 1
    result["no_g4_real"] = (result["rank_performance"] <= 4).astype(int)
    result["no_g4_financeiro"] = (result["rank_financeiro"] <= 4).astype(int)
    result["destaque_gestao"] = np.where(
        result["temporada"].ge(2018) & result["time"].isin(["Flamengo", "Palmeiras"]),
        "Duo Dominante (Fla/Pal)",
        "Outros",
    )
    return result[[
        "temporada", "time", "pontos", "saldo", "vitoria", "valor_mercado", "rank_performance", "rank_financeiro",
        "no_g4_real", "no_g4_financeiro", "destaque_gestao", "temporada_completa",
    ]].sort_values(["temporada", "rank_performance"]).reset_index(drop=True)


def build_r8(fact: pd.DataFrame) -> pd.DataFrame:
    summary = season_summary(fact).set_index("temporada")
    final = final_standings(fact)
    rows: list[dict] = []
    for season in sorted(fact["temporada"].unique()):
        complete = bool(summary.loc[season, "temporada_completa"])
        r8 = fact[(fact["temporada"] == season) & (fact["rodada"] <= 8)]
        r8_standings = r8.groupby("time", as_index=False).agg(
            pts_r8=("pontos", "sum"), saldo_r8=("saldo", "sum"), gols_r8=("gols_pro", "sum")
        ).sort_values(["pts_r8", "saldo_r8", "gols_r8", "time"], ascending=[False, False, False, True])
        if r8_standings.empty:
            continue
        leader = r8_standings.iloc[0]
        final_season = final[final["temporada"] == season].set_index("time")
        valid_result = complete and leader["time"] in final_season.index
        final_position = int(final_season.loc[leader["time"], "rank_performance"]) if valid_result else pd.NA
        champion = final_season.index[0] if valid_result and not final_season.empty else pd.NA
        rows.append({
            "temporada": season,
            "lider_r8": leader["time"],
            "pts_r8": int(leader["pts_r8"]),
            "aproveitamento_r8": float(leader["pts_r8"] / 24 * 100),
            "campeao": champion,
            "pos_final_lider_r8": final_position,
            "tese_confirmada": int(final_position == 1) if valid_result else pd.NA,
            "periodo": "Pre-ruptura (2007-2017)" if season <= 2017 else "Pos-ruptura (2018-2025)",
            "temporada_completa": int(complete),
            "incluida_inferencia": int(valid_result),
        })
    result = pd.DataFrame(rows)
    metrics = r8_confidence_metrics(result)
    for column, value in metrics.items():
        result[column] = value
    return result
