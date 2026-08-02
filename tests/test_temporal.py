import pytest

from tuku.io.temporal import DateGrammarError, TemporalExpr


def test_parse_fecha_precisa() -> None:
    t1 = TemporalExpr.parse("2026-08-11")
    assert t1.kind == "precise"
    assert t1.start_date == "2026-08-11"
    assert t1.time_str is None

    t2 = TemporalExpr.parse("(2026-08-11 12:45)")
    assert t2.kind == "precise"
    assert t2.start_date == "2026-08-11"
    assert t2.time_str == "12:45"


def test_parse_rango_y_difusa() -> None:
    t_rango = TemporalExpr.parse("2026-08-11/2026-08-14")
    assert t_rango.kind == "range"
    assert t_rango.start_date == "2026-08-11"
    assert t_rango.end_date == "2026-08-14"

    t_dif = TemporalExpr.parse("(~2026-08)")
    assert t_dif.kind == "fuzzy"
    assert t_dif.fuzzy_str == "2026-08"


def test_parse_next_ciclo() -> None:
    t_next = TemporalExpr.parse("(next:turno)")
    assert t_next.kind == "next"
    assert t_next.cycle_type == "turno"


def test_fecha_invalida_se_rechaza() -> None:
    with pytest.raises(DateGrammarError, match="inválida"):
        TemporalExpr.parse("2026-99-99")
