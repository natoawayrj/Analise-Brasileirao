import pandas as pd

from src.normalize import canonicalize_team, canonicalize_team_series


def test_canonicalize_team_repairs_encoding_and_aliases():
    assert canonicalize_team("AmÃ©rica-RN") == "América-RN"
    assert canonicalize_team("Atlético-MG") == "Atlético-MG"
    assert canonicalize_team("Botafogo-RJ") == "Botafogo"
    assert canonicalize_team("Vasco da Gama") == "Vasco"


def test_canonicalize_unifies_club_name_variants():
    variants = {
        "Avaí": ["Avaí FC", "Avai", "Avaí"],
        "Ceará": ["Ceará SC", "Ceara", "Ceará"],
        "Bahia": ["EC Bahia", "Bahia"],
        "Vitória": ["EC Vitória", "Vitoria", "Vitória"],
        "Coritiba": ["Coritiba FC", "Coritiba"],
        "Criciúma": ["Criciúma EC", "Criciuma"],
        "Cuiabá": ["Cuiabá-MT", "Cuiaba", "Cuiabá"],
        "Ipatinga": ["Ipatinga FC"],
        "Joinville": ["Joinville-SC"],
    }
    for expected, names in variants.items():
        assert {canonicalize_team(name) for name in names} == {expected}


def test_canonicalize_keeps_distinct_clubs_separate():
    assert canonicalize_team("América-MG") != canonicalize_team("América-RN")
    assert canonicalize_team("Atlético-GO") != canonicalize_team("Atlético-MG")


def test_canonicalize_series_preserves_string_dtype():
    result = canonicalize_team_series(pd.Series(["Sao Paulo", "Gremio"]))
    assert result.tolist() == ["São Paulo", "Grêmio"]
    assert str(result.dtype) == "string"

