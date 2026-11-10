from __future__ import annotations

from math import comb

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr, t


def wilson_interval(successes: int, trials: int, confidence: float = 0.95) -> tuple[float, float]:
    if trials <= 0:
        return (float("nan"), float("nan"))
    z = 1.959963984540054
    if confidence != 0.95:
        raise ValueError("Esta implementação usa apenas intervalo de 95%.")
    p = successes / trials
    denominator = 1 + z**2 / trials
    center = (p + z**2 / (2 * trials)) / denominator
    margin = z * np.sqrt(p * (1 - p) / trials + z**2 / (4 * trials**2)) / denominator
    return (center - margin, center + margin)


def binomial_upper_tail(successes: int, trials: int, probability: float) -> float:
    if trials <= 0:
        return float("nan")
    return sum(comb(trials, k) * probability**k * (1 - probability) ** (trials - k) for k in range(successes, trials + 1))


def summarize_r8(r8: pd.DataFrame) -> dict[str, float | int]:
    valid = r8[r8["incluida_inferencia"] == 1].copy()
    trials = len(valid)
    successes = int(valid["tese_confirmada"].sum()) if trials else 0
    lower, upper = wilson_interval(successes, trials)
    return {
        "temporadas_validas": trials,
        "teses_confirmadas": successes,
        "taxa_confirmacao": successes / trials if trials else float("nan"),
        "ic95_inferior": lower,
        "ic95_superior": upper,
        "p_binomial_vs_20pct": binomial_upper_tail(successes, trials, 0.2),
    }


def r8_confidence_metrics(r8: pd.DataFrame) -> dict[str, float]:
    valid = r8[r8["incluida_inferencia"] == 1].copy()
    for col in ("aproveitamento_r8", "pos_final_lider_r8"):
        valid[col] = pd.to_numeric(valid[col], errors="coerce").astype(float)
    n = len(valid)
    successes = int(valid["tese_confirmada"].sum()) if n else 0
    prop_lower, prop_upper = wilson_interval(successes, n)
    if n >= 4 and valid["aproveitamento_r8"].nunique() > 1 and valid["pos_final_lider_r8"].nunique() > 1:
        correlation, _ = pearsonr(valid["aproveitamento_r8"], valid["pos_final_lider_r8"])
        z = np.arctanh(correlation)
        margin = 1.959963984540054 / np.sqrt(n - 3)
        corr_lower, corr_upper = np.tanh([z - margin, z + margin])
    else:
        corr_lower = corr_upper = float("nan")
    if n >= 2:
        mean = valid["pos_final_lider_r8"].mean()
        standard_error = valid["pos_final_lider_r8"].sem()
        margin = t.ppf(0.975, n - 1) * standard_error
        position_lower, position_upper = mean - margin, mean + margin
    else:
        position_lower = position_upper = float("nan")
    return {
        "ic_prop_lower": round(prop_lower * 100, 1),
        "ic_prop_upper": round(prop_upper * 100, 1),
        "ic_r_lower": round(float(corr_lower), 4),
        "ic_r_upper": round(float(corr_upper), 4),
        "ic_pos_lower": round(float(position_lower), 2),
        "ic_pos_upper": round(float(position_upper), 2),
    }


def summarize_investment(investment: pd.DataFrame) -> dict[str, dict[str, float | int]]:
    """Pearson bruto sobre valor_mercado x pontos.

    ATENCAO: nao use como resultado analitico. A coluna valor_mercado mistura escalas
    entre periodos (2023-2024 em milhares; 2025 e valor de elenco em euros), o que
    distorce a correlacao. Mantido apenas para rastreabilidade; veja
    ``summarize_rank_correlation`` para a metrica valida.
    """
    result: dict[str, dict[str, float | int]] = {}
    periods = {
        "completo": investment,
        "pre_ruptura": investment[investment["temporada"] <= 2017],
        "pos_ruptura": investment[investment["temporada"] >= 2018],
    }
    for name, frame in periods.items():
        clean = frame[["valor_mercado", "pontos"]].dropna()
        if len(clean) < 3 or clean["valor_mercado"].nunique() < 2 or clean["pontos"].nunique() < 2:
            result[name] = {"n": len(clean), "pearson_r": float("nan"), "p_value": float("nan")}
            continue
        correlation, p_value = pearsonr(clean["valor_mercado"], clean["pontos"])
        result[name] = {"n": len(clean), "pearson_r": float(correlation), "p_value": float(p_value)}
    return result


def season_spearman(investment: pd.DataFrame) -> pd.DataFrame:
    """Spearman entre valor de mercado e pontos DENTRO de cada temporada completa.

    Comparar clubes apenas dentro da mesma temporada elimina o efeito de unidade, moeda e
    inflacao do valor de mercado, que variam entre periodos na fonte.
    """
    valid = investment[investment["temporada_completa"] == 1]
    rows: list[dict[str, float | int]] = []
    for season, frame in valid.groupby("temporada"):
        clean = frame[["valor_mercado", "pontos"]].dropna()
        if len(clean) < 5 or clean["valor_mercado"].nunique() < 2 or clean["pontos"].nunique() < 2:
            continue
        rho, p_value = spearmanr(clean["valor_mercado"], clean["pontos"])
        rows.append({"temporada": int(season), "n": len(clean), "spearman_rho": float(rho), "p_value": float(p_value)})
    return pd.DataFrame(rows, columns=["temporada", "n", "spearman_rho", "p_value"])


def summarize_rank_correlation(investment: pd.DataFrame) -> dict[str, dict[str, float | int]]:
    """Resumo do Spearman por periodo (media entre temporadas completas)."""
    by_season = season_spearman(investment)
    periods = {
        "completo": by_season,
        "pre_ruptura": by_season[by_season["temporada"] <= 2017],
        "pos_ruptura": by_season[by_season["temporada"] >= 2018],
    }
    result: dict[str, dict[str, float | int]] = {}
    for name, frame in periods.items():
        if frame.empty:
            result[name] = {"temporadas": 0, "rho_medio": float("nan"), "rho_min": float("nan"), "rho_max": float("nan")}
            continue
        result[name] = {
            "temporadas": int(len(frame)),
            "rho_medio": float(frame["spearman_rho"].mean()),
            "rho_min": float(frame["spearman_rho"].min()),
            "rho_max": float(frame["spearman_rho"].max()),
        }
    return result


def summarize_champions_g4(investment: pd.DataFrame) -> dict[str, int]:
    """Campeoes entre os 4 maiores valores de mercado da temporada.

    O ranking financeiro e calculado dentro da temporada, entao nao depende da escala.
    Reporta o total e o recorte apenas com temporadas completas.
    """
    champions = investment[investment["rank_performance"] == 1]
    complete = champions[champions["temporada_completa"] == 1]
    return {
        "campeoes": int(len(champions)),
        "campeoes_no_g4_financeiro": int(champions["no_g4_financeiro"].sum()),
        "campeoes_temporadas_completas": int(len(complete)),
        "campeoes_completas_no_g4_financeiro": int(complete["no_g4_financeiro"].sum()),
    }
