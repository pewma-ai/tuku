"""Tests del escenario 005-06-el-agente-con-historia.

El agente elige el ámbito por las keywords, escribe lo dicho tal como se dijo y
no adivina entre dos personas con el mismo nombre.

Ejecutable directo: `python3 tests/escenarios/test_005_06_el_agente_con_historia.py`
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import agente  # noqa: E402
import gherkin  # noqa: E402

SLUG = "005-06-el-agente-con-historia"
BASE = "005-01-las-dos-semanas-de-andrea"
CADENA_BASE = (
    "el árbol de Andrea nace con su negocio",
    "la primera semana se registra día por día",
    "la semana se cierra a mano y abre la siguiente",
    "la segunda semana cae sobre lo ya escrito",
)
PATRICIA = "una keyword única decide el ámbito"
PAULA = "dos personas con el mismo nombre esperan al autor"
DOMINGO = "## Domingo 23 de agosto"
LINK = re.compile(r"\[[^\]]*\]\([^)]*\)")

sin_arnes = pytest.mark.skipif(
    not agente.disponible(), reason=agente.motivo_no_disponible() or ""
)


def _correr(titulo: str) -> gherkin.Corrida:
    for previo in CADENA_BASE:
        gherkin.correr(BASE, previo)
    return gherkin.correr(SLUG, titulo)


def _domingo(corrida: gherkin.Corrida) -> list[str]:
    ahora = corrida.ruta("mi-vault", "AHORA.md").read_text(encoding="utf-8")
    dia = ahora.split(DOMINGO, 1)[1].split("\n## ", 1)[0]
    return [x for x in dia.splitlines() if re.match(r"- \d\d:\d\d - ", x)]


def _flag(argv: list[str], nombre: str) -> str | None:
    return argv[argv.index(nombre) + 1] if nombre in argv else None


@pytest.mark.agentic
@sin_arnes
def test_005_06_la_frase_de_la_patricia_es_un_solo_registro_del_liceo() -> None:
    turno = _correr(PATRICIA).turno
    assert turno.traduccion == ["entry create"], f"la traza dice: {turno.comandos}"
    (argv,) = turno.invocaciones_de("entry", "create")
    assert _flag(argv, "--scope") == "liceo-tecnico-andes", argv


@pytest.mark.agentic
@sin_arnes
def test_005_06_el_cuerpo_conserva_las_palabras_de_andrea_y_no_se_enlaza() -> None:
    corrida = _correr(PATRICIA)
    (argv,) = corrida.turno.invocaciones_de("entry", "create")
    cuerpo = _flag(argv, "--body") or ""
    assert "Patricia" in cuerpo and "Lillo" not in cuerpo, cuerpo
    assert not LINK.search(cuerpo.split("**", 2)[-1]), f"el cuerpo se enlazó solo: {cuerpo}"
    registro = next(x for x in _domingo(corrida) if "Patricia" in x)
    assert "(ambitos/negocio/clientes/liceo-tecnico-andes/liceo-tecnico-andes.md)" in registro


@pytest.mark.agentic
@sin_arnes
def test_005_06_el_registro_de_la_patricia_toca_solo_el_ciclo_y_la_pagina_del_liceo() -> None:
    corrida = _correr(PATRICIA)
    assert set(corrida.delta_de("mi-vault")) == {
        "AHORA.md",
        "ambitos/negocio/clientes/liceo-tecnico-andes/liceo-tecnico-andes.md",
    }


@pytest.mark.agentic
@sin_arnes
def test_005_06_la_paula_queda_sin_ambito_de_ninguna_de_las_dos() -> None:
    turno = _correr(PAULA).turno
    for argv in turno.invocaciones_de("entry", "create"):
        assert _flag(argv, "--scope") not in ("catalogo-marzo", "escuela-los-maitenes"), argv
    assert not turno.invocaciones_de("todo", "open")
    assert not turno.invocaciones_de("todo", "close")


@pytest.mark.agentic
@sin_arnes
def test_005_06_si_el_agente_pregunta_por_la_paula_nombra_a_las_dos() -> None:
    corrida = _correr(PAULA)
    if corrida.turno.invocaciones_de("entry", "create"):
        pytest.skip("el agente registró en el ámbito común en vez de preguntar")
    respuesta = corrida.turno.stdout
    assert "?" in respuesta, respuesta
    assert "Ibáñez" in respuesta and "Reyes" in respuesta, respuesta
