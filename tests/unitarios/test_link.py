"""Unitarios de `tuku.link`: convertir menciones sueltas en enlaces.

El enlazado retroactivo toca texto que el autor ya escribió, así que lo que se
verifica acá es sobre todo lo que **no** debe pasar: reescribir el resto de la
línea, o enlazar dos veces lo que ya estaba enlazado.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from tuku import link  # noqa: E402

pytestmark = pytest.mark.unitario


def test_enlaza_la_mencion_y_no_toca_el_resto_de_la_linea() -> None:
    linea = "- 18:40 - le mandé la boleta del depto centro a la administradora\n"

    texto, n = link.backfill(linea, scope="depto-centro", keywords=["depto centro"])

    assert n == 1
    assert texto == (
        "- 18:40 - le mandé la boleta del [[depto-centro]] a la administradora\n"
    )


def test_no_enlaza_dos_veces_lo_que_ya_estaba_enlazado() -> None:
    linea = "- 18:40 - la boleta del [[depto-centro]] a la administradora\n"

    texto, n = link.backfill(linea, scope="depto-centro", keywords=["depto centro"])

    assert n == 0
    assert texto == linea
    assert "[[[[" not in texto


def test_sin_keywords_no_cambia_nada() -> None:
    linea = "- 18:40 - una línea cualquiera\n"
    assert link.backfill(linea, scope="depto-centro", keywords=[]) == (linea, 0)


def test_una_mencion_que_no_aparece_no_inventa_enlaces() -> None:
    linea = "- 18:40 - nada que ver acá\n"
    assert link.backfill(linea, scope="x", keywords=["depto centro"]) == (linea, 0)


def test_cuenta_todas_las_menciones_que_enlaza() -> None:
    texto = "- 09:00 - el depto centro\n- 10:00 - otra vez el depto centro\n"

    resultado, n = link.backfill(texto, scope="depto-centro", keywords=["depto centro"])

    assert n == 2
    assert resultado.count("[[depto-centro]]") == 2


def test_un_texto_vacio_se_devuelve_igual() -> None:
    assert link.backfill("", scope="x", keywords=["y"]) == ("", 0)
