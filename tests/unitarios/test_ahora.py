"""Unitarios de `tuku.ahora`: leer el ciclo de `AHORA.md` sin tocar disco.

Es el módulo que traduce entre la forma en que el autor escribe un día
(`## Martes 11 de agosto`) y una fecha. El encabezado canónico vivía en
`cli.py`, y es lo que decide bajo qué día cae un registro sin `--day`.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from tuku import ahora  # noqa: E402

pytestmark = pytest.mark.unitario

CICLO = (
    "---\ntype: Logbook\nstatus: draft\nfrom: 2026-08-11\nto: 2026-08-17\n---\n\n"
    "## Martes 11 de agosto\n\n- 09:12 - algo\n\n"
    "## Miércoles 12 de agosto\n\n"
)


def test_encabezado_de_da_la_forma_canonica_de_un_dia() -> None:
    assert ahora.encabezado_de(date(2026, 8, 11)) == "## Martes 11 de agosto"


def test_encabezado_de_no_rellena_el_dia_con_cero() -> None:
    assert ahora.encabezado_de(date(2026, 8, 3)) == "## Lunes 3 de agosto"


def test_rango_lee_el_frontmatter_del_ciclo() -> None:
    assert ahora.rango(CICLO) == (date(2026, 8, 11), date(2026, 8, 17))


def test_rango_sin_frontmatter_devuelve_none() -> None:
    assert ahora.rango("# Sin frontmatter\n\n## Martes 11 de agosto\n") is None


def test_fecha_del_dia_resuelve_dentro_del_rango() -> None:
    desde, hasta = date(2026, 8, 11), date(2026, 8, 17)
    assert ahora.fecha_del_dia("## Martes 11 de agosto", desde, hasta) == date(2026, 8, 11)
    assert ahora.fecha_del_dia("## Lunes 17 de agosto", desde, hasta) == date(2026, 8, 17)


def test_fecha_del_dia_resuelve_tambien_fuera_del_rango() -> None:
    """El rango elige el año, no filtra: un día fuera del ciclo igual se fecha.

    Tiene que ser así para que `entry lint` pueda decir *qué* fecha quedó fuera
    del ciclo abierto. Filtrar acá dejaría al lint sin nada que reportar.
    """
    desde, hasta = date(2026, 8, 11), date(2026, 8, 17)
    assert ahora.fecha_del_dia("## Martes 25 de agosto", desde, hasta) == date(2026, 8, 25)


def test_lo_que_no_es_un_encabezado_de_dia_no_se_fecha() -> None:
    desde, hasta = date(2026, 8, 11), date(2026, 8, 17)
    assert ahora.fecha_del_dia("## Una sección cualquiera", desde, hasta) is None
    assert ahora.fecha_del_dia("## Martes 11 de brumario", desde, hasta) is None


def test_dias_devuelve_los_encabezados_con_su_fecha() -> None:
    encontrados = ahora.dias(CICLO)

    assert [d[1] for d in encontrados] == [
        "## Martes 11 de agosto",
        "## Miércoles 12 de agosto",
    ]
    assert [d[2] for d in encontrados] == [date(2026, 8, 11), date(2026, 8, 12)]


def test_dias_de_un_texto_sin_encabezados_es_vacio() -> None:
    assert ahora.dias("") == []
