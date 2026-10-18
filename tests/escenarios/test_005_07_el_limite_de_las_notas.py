"""Tests del escenario 005-07-el-limite-de-las-notas.

Con treinta personas, `context note` trae las veinticinco de `updated` más reciente,
y el agente enlaza solo a las que `context` ofrece.

Ejecutable directo: `python3 tests/escenarios/test_005_07_el_limite_de_las_notas.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import agente  # noqa: E402
import gherkin  # noqa: E402

from tuku.cli import EXITO  # noqa: E402

SLUG = "005-07-el-limite-de-las-notas"
BASE = "005-01-las-dos-semanas-de-andrea"
CADENA_BASE = (
    "el árbol de Andrea nace con su negocio",
    "la primera semana se registra día por día",
    "la semana se cierra a mano y abre la siguiente",
    "la segunda semana cae sobre lo ya escrito",
)
LIMITE = "context note trae las veinticinco más recientes"
ENLAZA = "el agente enlaza a quien context ofrece y a nadie más"
FUERA = ("rodrigo-salinas", "elena-vidal", "hugo-ortega", "ines-cabrera", "samuel-toro")

sin_arnes = pytest.mark.skipif(
    not agente.disponible(), reason=agente.motivo_no_disponible() or ""
)


def _correr(titulo: str) -> gherkin.Corrida:
    for previo in CADENA_BASE:
        gherkin.correr(BASE, previo)
    return gherkin.correr(SLUG, titulo)


def test_005_07_context_note_trae_las_veinticinco_mas_recientes() -> None:
    corrida = _correr(LIMITE)
    assert corrida.codigo == EXITO
    rutas = [
        x.split(":")[0].removeprefix("- ")
        for x in corrida.stdout.splitlines()
        if x.startswith("- ")
    ]
    assert len(rutas) == 25
    assert rutas[0] == "notas/daniela-paredes.md" and rutas[-1] == "notas/teresa-montt.md"


def test_005_07_las_cinco_mas_antiguas_no_salen() -> None:
    salida = _correr(LIMITE).stdout
    for nombre in FUERA:
        assert f"notas/{nombre}.md" not in salida, nombre


def _cuerpos(corrida: gherkin.Corrida) -> str:
    argvs = corrida.turno.invocaciones_de("entry", "create")
    return "\n".join(a[a.index("--body") + 1] for a in argvs if "--body" in a)


@pytest.mark.agentic
@sin_arnes
def test_005_07_el_registro_de_daniela_enlaza_a_su_nota() -> None:
    cuerpos = _cuerpos(_correr(ENLAZA))
    assert "(notas/daniela-paredes.md)" in cuerpos, cuerpos


@pytest.mark.agentic
@sin_arnes
def test_005_07_las_dos_mas_antiguas_quedan_sin_link_y_sin_nota_nueva() -> None:
    corrida = _correr(ENLAZA)
    cuerpos = _cuerpos(corrida)
    assert "Rodrigo Salinas" in cuerpos and "Elena Vidal" in cuerpos, cuerpos
    assert "rodrigo-salinas" not in cuerpos and "elena-vidal" not in cuerpos, cuerpos
    assert not corrida.turno.invocaciones_de("note", "create")
