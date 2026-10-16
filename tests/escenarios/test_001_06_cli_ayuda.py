"""Test del escenario 001-06-cli-ayuda.

`tuku init -h` nombra sus opciones, y una instalación rota sale con el código de
entorno (3).

Ejecutable directo: `python3 tests/escenarios/test_001_06_cli_ayuda.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import gherkin  # noqa: E402

from tuku.cli import ENTORNO, EXITO  # noqa: E402

SLUG = "001-06-cli-ayuda"


def test_tuku_init_menos_h_lista_lo_que_anade_el_epic_001() -> None:
    corrida = gherkin.correr(SLUG, "lista las opciones que añade el epic 001")
    assert corrida.codigo == EXITO, "`tuku init -h` no salió con código 0"
    for pieza in ("dir", "--variante", "--author", "--force"):
        assert pieza in corrida.stdout, f"`tuku init -h` no nombra {pieza}"


def test_entorno_roto_no_se_confunde_con_error_de_uso() -> None:
    """Una instalación rota sale con 3, no con el 2 de un comando mal escrito."""
    corrida = gherkin.correr(SLUG, "un entorno roto no se confunde con un error de uso")

    assert corrida.codigo == ENTORNO, (
        "una instalación rota debería salir con el código de entorno"
    )
    assert "template" in corrida.stderr, "el error no dice qué le falta al árbol"


if __name__ == "__main__":
    test_tuku_init_menos_h_lista_lo_que_anade_el_epic_001()
    test_entorno_roto_no_se_confunde_con_error_de_uso()
    print("ok: init -h nombra sus opciones y un entorno roto sale con el código 3")
