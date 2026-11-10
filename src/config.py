from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "dados" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "dados" / "processed"

SEASON_START = 2007
SEASON_END = 2025
EXPECTED_TEAMS = 20
EXPECTED_ROUNDS = 38
EXPECTED_MATCHES = 380

OLD_MATCHES_FILE = RAW_DIR / "Campeonato.csv"
OLD_MARKET_FILE = RAW_DIR / "Investimento.csv"
NEW_MATCHES_FILE = RAW_DIR / "campeonato-brasileiro-full.csv"
NEW_GOALS_FILE = RAW_DIR / "campeonato-brasileiro-gols.csv"
MARKET_2025_FILE = RAW_DIR / "Investimento_2025.csv"

FACT_FILE = PROCESSED_DIR / "fato_desempenho.csv"
INVESTMENT_FILE = PROCESSED_DIR / "investimento_vs_desempenho.csv"
R8_FILE = PROCESSED_DIR / "tese_r8_guardiola.csv"

