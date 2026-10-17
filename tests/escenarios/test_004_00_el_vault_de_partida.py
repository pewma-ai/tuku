"""Tests del escenario 004-00-la-conversacion: el vault de partida del epic.

Cuatro frentes con un pendiente abierto cada uno, y un `tuku doctor` sano.

Ejecutable directo: `python3 tests/escenarios/test_004_00_el_vault_de_partida.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import gherkin  # noqa: E402

from tuku.cli import EXITO  # noqa: E402

SLUG = "004-00-la-conversacion"
TITULO = "el vault de partida"
MARTES = "## Martes 11 de agosto"


def _dia(texto: str, encabezado: str) -> str:
    return texto.split(encabezado, 1)[1].split("\n## ", 1)[0]


def test_004_00_pendientes_abiertos_por_frente() -> None:
    corrida = gherkin.correr(SLUG, TITULO)
    filas = [
        [c.strip() for c in f.strip("|").split("|")]
        for f in corrida.ruta("mi-vault", "PENDIENTES.md")
        .read_text(encoding="utf-8")
        .splitlines()
        if f.startswith("| ") and not f.startswith("| Horizonte") and not f.startswith("| ---")
    ]
    assert [(f[0], f[1]) for f in filas] == [
        ("esta semana", ""),
        ("esta semana", ""),
        ("esta semana", ""),
        ("con fecha", "2026-08-12"),
    ]


def test_004_00_el_martes_lleva_cuatro_constancias_y_cuatro_pendientes() -> None:
    corrida = gherkin.correr(SLUG, TITULO)
    martes = _dia(corrida.ruta("mi-vault", "AHORA.md").read_text(encoding="utf-8"), MARTES)
    assert martes.count("**nota**: abrí el ámbito") == 4
    assert martes.count("**pendiente**") == 4


def test_004_00_el_doctor_confirma_el_vault() -> None:
    corrida = gherkin.correr(SLUG, TITULO)
    revision = corrida.de("tuku doctor")
    assert revision.codigo == EXITO, revision.stdout + revision.stderr
    assert "el vault está sano" in revision.stdout
