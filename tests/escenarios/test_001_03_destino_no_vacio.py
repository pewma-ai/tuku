"""Tests del escenario 001-03-destino-no-vacio.

Sobre un destino con contenido, `tuku init` sale con 1, nombra `--force` y no
toca nada. Con `--force` lo reemplaza y deja un vault operable.

Ejecutable directo: `python3 tests/escenarios/test_001_03_destino_no_vacio.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import gherkin  # noqa: E402

from tuku.cli import EXITO, RECHAZO  # noqa: E402

SLUG = "001-03-destino-no-vacio"
CENTINELA = "algo-que-ya-estaba.txt"


def test_001_03_destino_no_vacio_se_niega_y_no_toca_nada() -> None:
    corrida = gherkin.correr(SLUG, "no sembrar sobre un directorio que ya tiene algo")

    assert corrida.codigo == RECHAZO, f"el comando no se negó: código {corrida.codigo}"
    assert "--force" in corrida.stderr, (
        f"el rechazo no nombra la corrección: {corrida.stderr!r}"
    )

    destino = corrida.ruta("mi-vault")
    assert [p.name for p in destino.iterdir()] == [CENTINELA], "el destino no quedó intacto"
    assert (destino / CENTINELA).read_text(encoding="utf-8") == "no tocar\n"


def test_001_03_force_reemplaza_el_destino_no_vacio() -> None:
    corrida = gherkin.correr(SLUG, "`--force` siembra igual")

    assert corrida.codigo == EXITO, corrida.stderr
    destino = corrida.ruta("mi-vault")
    assert not (destino / CENTINELA).exists(), "force no reemplazó el contenido previo"
    assert (destino / "AHORA.md").is_file(), "force no dejó un vault operable"
    assert "DD de mes" not in (destino / "AHORA.md").read_text(encoding="utf-8")


if __name__ == "__main__":
    test_001_03_destino_no_vacio_se_niega_y_no_toca_nada()
    test_001_03_force_reemplaza_el_destino_no_vacio()
    print(f"ok: se niega sin force, force reemplaza (playground/{SLUG}/)")
