"""Tests del escenario 005-02-lo-derivado-se-reconstruye.

El principio 9 sobre un vault de dos semanas: borrar lo derivado y regenerar
devuelve el mismo vault, y un vault armado comando a comando ya está regenerado.

Ejecutable directo: `python3 tests/escenarios/test_005_02_lo_derivado_se_reconstruye.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import gherkin  # noqa: E402

from tuku.cli import EXITO  # noqa: E402

SLUG = "005-02-lo-derivado-se-reconstruye"
BASE = "005-01-las-dos-semanas-de-andrea"
CADENA_BASE = (
    "el árbol de Andrea nace con su negocio",
    "la primera semana se registra día por día",
    "la semana se cierra a mano y abre la siguiente",
    "la segunda semana cae sobre lo ya escrito",
)
BORRAR_Y_REGENERAR = "borrar lo derivado y regenerar devuelve lo mismo"
YA_REGENERADO = "un vault armado comando a comando ya está regenerado"


def _correr(titulo: str) -> gherkin.Corrida:
    for previo in CADENA_BASE:
        gherkin.correr(BASE, previo)
    return gherkin.correr(SLUG, titulo)


def test_005_02_borrar_lo_derivado_y_regenerar_deja_el_vault_idéntico() -> None:
    corrida = _correr(BORRAR_Y_REGENERAR)
    assert corrida.delta_de("mi-vault") == {}


def test_005_02_regenerar_dos_veces_no_escribe_nada() -> None:
    corrida = _correr(BORRAR_Y_REGENERAR)
    regeneraciones = [r for r in corrida.resultados if r.comando == "tuku regenerate"]
    assert len(regeneraciones) == 2
    segunda = regeneraciones[1]
    assert segunda.codigo == EXITO
    assert "al día" in segunda.stdout + segunda.stderr


def test_005_02_un_vault_armado_comando_a_comando_ya_esta_regenerado() -> None:
    corrida = _correr(YA_REGENERADO)
    assert corrida.codigo == EXITO
    assert corrida.delta_de("mi-vault") == {}
    assert "al día" in corrida.stdout + corrida.stderr
