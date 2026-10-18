"""`--at` y `--due`: qué formas aceptan, cómo completan lo que falta y el error sin año."""

from __future__ import annotations

import argparse
from datetime import date

import pytest

from conftest import AHORA
from tuku.cli import USO, main
from tuku.cli.opciones import Momento, momento_con_hora, momento_futuro, momento_pasado


def test_at_acepta_fecha_con_hora_solo_fecha_o_solo_hora_y_rechaza_el_resto() -> None:
    for valor, dia, hora in [
        ("2026-08-10 09:12", date(2026, 8, 10), "09:12"),
        ("2026-08-10 9:12", date(2026, 8, 10), "09:12"),
        ("2026-08-10", date(2026, 8, 10), None),
        ("9:12", None, "09:12"),
    ]:
        m = momento_pasado(valor)
        assert (m.dia, m.hora, m.propuesto) == (dia, hora, None), valor

    for valor in [
        "",
        "mañana",
        "11-08-2026",
        "2026-08-10 09:12 x",
        "09:12 2026-08-10",
        "2026-02-30",
    ]:
        with pytest.raises(argparse.ArgumentTypeError):
            momento_pasado(valor)

    for valor in ["-08-10", "mañana", "2026/08/10"]:
        with pytest.raises(argparse.ArgumentTypeError, match="AAAA-MM-DD"):
            momento_pasado(valor)

    assert momento_con_hora("2026-08-10 09:12").hora == "09:12"
    with pytest.raises(argparse.ArgumentTypeError):
        momento_con_hora("2026-08-10")


def test_due_con_solo_hora_es_la_proxima_vez_que_llega_y_la_celda_de_vence() -> None:
    def celda(valor: str) -> str:
        return momento_futuro(valor).con_reloj(AHORA).celda()

    assert celda("22:00") == "2026-08-12 22:00"
    assert celda("09:00") == "2026-08-13 09:00"
    assert celda("08:30") == "2026-08-13 08:30"
    assert celda("2026-08-12") == "2026-08-12"
    assert celda("2026-08-12 9:00") == "2026-08-12 09:00"
    assert Momento().celda() == ""


def test_sin_anio_se_propone_el_mas_cercano_y_el_error_ofrece_el_comando_con_anio(
    capsys: pytest.CaptureFixture[str],
) -> None:
    for valor, at, due in [
        ("08-12", date(2026, 8, 12), date(2026, 8, 12)),
        ("08-11", date(2026, 8, 11), date(2027, 8, 11)),
        ("08-13", date(2025, 8, 13), date(2026, 8, 13)),
        ("02-29", date(2024, 2, 29), date(2028, 2, 29)),
    ]:
        assert momento_pasado(valor).con_reloj(AHORA).propuesto == at, valor
        assert momento_futuro(valor).con_reloj(AHORA).propuesto == due, valor

    argv = ["todo", "open", "--at", "08-10 9:12", "--due", "08-12", "--body", "pagar la luz"]
    assert main(argv, now=AHORA) == USO
    err = capsys.readouterr().err
    assert "¿el lunes 10 de agosto de 2026?" in err
    assert "¿el miércoles 12 de agosto de 2026?" in err
    assert (
        "tuku todo open --at '2026-08-10 09:12' --due 2026-08-12 --body 'pagar la luz'" in err
    )
