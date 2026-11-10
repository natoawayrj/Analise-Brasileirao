import re
import unicodedata
from pathlib import Path

import pandas as pd


def repair_mojibake(value: object) -> str:
    """Corrige o padrão mais comum de UTF-8 interpretado como latin-1."""
    text = "" if pd.isna(value) else str(value).strip()
    if any(marker in text for marker in ("Ã", "Â", "â€")):
        try:
            repaired = text.encode("latin1").decode("utf-8")
            if repaired.count("�") <= text.count("�"):
                return repaired
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
    return text


def normalized_key(value: object) -> str:
    text = repair_mojibake(value)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.lower().replace("&", " e ")
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


_ALIASES = {
    "america mg": "América-MG",
    "america rn": "América-RN",
    "athletico pr": "Athletico-PR",
    "atletico pr": "Athletico-PR",
    "atletico go": "Atlético-GO",
    "atletico mg": "Atlético-MG",
    "avai": "Avaí",
    "avai fc": "Avaí",
    "bahia": "Bahia",
    "ec bahia": "Bahia",
    "barueri": "Barueri",
    "botafogo": "Botafogo",
    "botafogo rj": "Botafogo",
    "bragantino": "Bragantino",
    "rb bragantino": "Bragantino",
    "ceara": "Ceará",
    "ceara sc": "Ceará",
    "coritiba": "Coritiba",
    "coritiba fc": "Coritiba",
    "criciuma": "Criciúma",
    "criciuma ec": "Criciúma",
    "cuiaba": "Cuiabá",
    "cuiaba mt": "Cuiabá",
    "ipatinga": "Ipatinga",
    "ipatinga fc": "Ipatinga",
    "joinville": "Joinville",
    "joinville sc": "Joinville",
    "figueirense": "Figueirense",
    "figueirense fc": "Figueirense",
    "gremio": "Grêmio",
    "gremio prudente": "Grêmio Prudente",
    "goias": "Goiás",
    "goias ec": "Goiás",
    "nautico": "Náutico",
    "parana": "Paraná",
    "santos": "Santos",
    "santos fc": "Santos",
    "sao paulo": "São Paulo",
    "sao paulo fc": "São Paulo",
    "sport": "Sport",
    "sport recife": "Sport",
    "vasco": "Vasco",
    "vasco da gama": "Vasco",
    "vitoria": "Vitória",
    "ec vitoria": "Vitória",
}


def canonicalize_team(value: object) -> str:
    cleaned = repair_mojibake(value)
    return _ALIASES.get(normalized_key(cleaned), cleaned)


def canonicalize_team_series(series: pd.Series) -> pd.Series:
    return series.map(canonicalize_team).astype("string")


def read_csv_robust(path: Path, **kwargs) -> pd.DataFrame:
    """Lê CSVs tentando as codificações esperadas pelas fontes do projeto."""
    last_error: Exception | None = None
    for encoding in ("utf-8-sig", "utf-8", "latin1"):
        try:
            return pd.read_csv(path, encoding=encoding, **kwargs)
        except UnicodeDecodeError as error:
            last_error = error
    raise UnicodeError(f"Não foi possível decodificar {path}: {last_error}")

