"""`--at` y `--due`: qué formas aceptan, cómo completan lo que falta y el error sin año."""

from __future__ import annotations

import argparse
from datetime import date, datetime

import pytest

from tuku.cli import USO, main, opciones
from tuku.cli.opciones import Momento, momento_con_hora, momento_futuro, momento_pasado

#: Martes 11 de agosto de 2026, 21:30.
HOY = date(2026, 8, 11)


@pytest.fixture(autouse=True)
def _ahora(monkeypatch: pytest.MonkeyPatch) -> None:
    class Hoy(date):
        @classmethod
        def today(cls) -> Hoy:
            return cls(2026, 8, 11)

    class Ahora(datetime):
        @classmethod
        def now(cls, tz: object = None) -> Ahora:
            return cls(2026, 8, 11, 21, 30)

    monkeypatch.setattr(opciones, "date", Hoy)
    monkeypatch.setattr(opciones, "datetime", Ahora)


@pytest.mark.parametrize(
    ("valor", "dia", "hora"),
    [
        ("2026-08-10 09:12", date(2026, 8, 10), "09:12"),
        ("2026-08-10 9:12", date(2026, 8, 10), "09:12"),
        ("2026-08-10", date(2026, 8, 10), None),
        ("9:12", None, "09:12"),
    ],
)
def test_at_acepta_fecha_con_hora_solo_fecha_o_solo_hora(
    valor: str, dia: date | None, hora: str | None
) -> None:
    m = momento_pasado(valor)
    assert (m.dia, m.hora, m.propuesto) == (dia, hora, None)


@pytest.mark.parametrize(
    "valor",
    ["", "mañana", "11-08-2026", "2026-08-10 09:12 x", "09:12 2026-08-10", "2026-02-30"],
)
def test_lo_que_no_es_ninguna_de_las_tres_formas_se_rechaza(valor: str) -> None:
    with pytest.raises(argparse.ArgumentTypeError):
        momento_pasado(valor)


def test_due_con_solo_hora_es_la_proxima_vez_que_llega() -> None:
    assert momento_futuro("22:00").celda() == "2026-08-11 22:00"
    assert momento_futuro("09:00").celda() == "2026-08-12 09:00"
    assert momento_futuro("21:30").celda() == "2026-08-12 21:30"


def test_la_celda_de_vence() -> None:
    assert momento_futuro("2026-08-12").celda() == "2026-08-12"
    assert momento_futuro("2026-08-12 9:00").celda() == "2026-08-12 09:00"
    assert Momento().celda() == ""


@pytest.mark.parametrize(
    ("valor", "at", "due"),
    [
        ("08-11", date(2026, 8, 11), date(2026, 8, 11)),
        ("08-10", date(2026, 8, 10), date(2027, 8, 10)),
        ("08-12", date(2025, 8, 12), date(2026, 8, 12)),
        ("02-29", date(2024, 2, 29), date(2028, 2, 29)),
    ],
)
def test_sin_anio_se_propone_el_mas_cercano_hacia_atras_o_hacia_adelante(
    valor: str, at: date, due: date
) -> None:
    assert momento_pasado(valor).propuesto == at
    assert momento_futuro(valor).propuesto == due


def test_sin_anio_falla_y_ofrece_el_comando_con_anio(
    capsys: pytest.CaptureFixture[str],
) -> None:
    argv = ["todo", "open", "--at", "08-10 9:12", "--due", "08-12", "--body", "pagar la luz"]
    assert main(argv) == USO
    err = capsys.readouterr().err
    assert "¿el lunes 10 de agosto de 2026?" in err
    assert "¿el miércoles 12 de agosto de 2026?" in err
    assert (
        "tuku todo open --at '2026-08-10 09:12' --due 2026-08-12 --body 'pagar la luz'" in err
    )


def test_un_registro_que_ya_existe_se_ubica_con_hora() -> None:
    assert momento_con_hora("2026-08-10 09:12").hora == "09:12"
    with pytest.raises(argparse.ArgumentTypeError):
        momento_con_hora("2026-08-10")


@pytest.mark.parametrize("valor", ["-08-10", "mañana", "2026/08/10"])
def test_lo_que_no_parece_hora_dice_las_tres_formas_y_no_pide_una_hora(valor: str) -> None:
    with pytest.raises(argparse.ArgumentTypeError, match="AAAA-MM-DD"):
        momento_pasado(valor)
