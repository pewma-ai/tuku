"""Test del escenario 001-04-init-author.

`--author` deja el nombre en `reglas/autor.md`, y un
nombre en blanco deja la línea intacta y el vault operable.

Ejecutable directo: `python3 tests/escenarios/test_001_04_init_author.py`
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import gherkin  # noqa: E402

from tuku.cli import EXITO  # noqa: E402

SLUG = "001-04-init-author"
FECHA_FIJA = date(2026, 8, 11)
AUTOR = "ARTURO PEREZ-REVERTE (Arturo)"
MARCADOR = "**Nombre del autor:**"


def _linea_del_autor(vault: Path) -> str:
    autor = (vault / "reglas" / "autor.md").read_text(encoding="utf-8")
    return next(ln for ln in autor.splitlines() if ln.lstrip().startswith(MARCADOR))


def test_001_04_init_author_escribe_el_nombre_en_reglas_autor() -> None:
    corrida = gherkin.correr(SLUG, "el nombre del autor queda en reglas/autor.md")
    assert corrida.codigo == EXITO, corrida.stderr
    destino = corrida.ruta("mi-vault")

    autor = (destino / "reglas" / "autor.md").read_text(encoding="utf-8")
    assert f"{MARCADOR} {AUTOR}" in autor, f"el nombre no llegó a autor.md: {autor[:400]!r}"
    assert "Nombre del autor:** por declarar" not in autor, "quedó el placeholder sin sustituir"


def test_001_04_un_nombre_en_blanco_deja_el_vault_operable_sin_nombre() -> None:
    corrida = gherkin.correr(SLUG, "un nombre en blanco deja el vault operable")
    assert corrida.codigo == EXITO, corrida.stderr

    vault = corrida.ruta("en-blanco")
    linea = _linea_del_autor(vault)
    assert linea.startswith(f"{MARCADOR} por declarar"), f"se tocó la línea: {linea!r}"
    assert (vault / "AHORA.md").is_file(), "el vault no quedó operable"


if __name__ == "__main__":
    test_001_04_init_author_escribe_el_nombre_en_reglas_autor()
    test_001_04_un_nombre_en_blanco_deja_el_vault_operable_sin_nombre()
    print(f"ok: --author escribe el nombre; en blanco deja el vault operable ({SLUG})")
