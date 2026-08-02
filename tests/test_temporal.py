"""Pruebas del parser de la gramática temporal de tareas (F1.4).

Verifica el parsing de fechas precisas, rangos y relativas a ciclo según `spec/tarea.md` §4.
"""

import pytest

from tuku.io.temporal import DateGrammarError, TemporalExpr


def test_parse_fecha_precisa() -> None:
    """Verifica que fechas precisas absolutas ISO se extraigan correctamente."""
    t1 = TemporalExpr.parse("2026-08-11")
    assert t1.kind == "precise"
    assert t1.start_date == "2026-08-11"
    assert t1.time_str is None

    t2 = TemporalExpr.parse("(2026-08-11 12:45)")
    assert t2.kind == "precise"
    assert t2.start_date == "2026-08-11"
    assert t2.time_str == "12:45"


def test_parse_rango_y_difusa() -> None:
    """Verifica el parsing de rangos de fechas (inicio/fin) y expresiones difusas (~YYYY-MM)."""
    t_rango = TemporalExpr.parse("2026-08-11/2026-08-14")
    assert t_rango.kind == "range"
    assert t_rango.start_date == "2026-08-11"
    assert t_rango.end_date == "2026-08-14"

    t_dif = TemporalExpr.parse("(~2026-08)")
    assert t_dif.kind == "fuzzy"
    assert t_dif.fuzzy_str == "2026-08"


def test_parse_next_ciclo() -> None:
    """Verifica la expresión temporal relativa a ciclo (next:<tipo>)."""
    t_next = TemporalExpr.parse("(next:turno)")
    assert t_next.kind == "next"
    assert t_next.cycle_type == "turno"


def test_fecha_invalida_se_rechaza() -> None:
    """F1.4: Rechazo de fecha inválida fuera de rango con DateGrammarError."""
    with pytest.raises(DateGrammarError, match="inválida"):
        TemporalExpr.parse("2026-99-99")
