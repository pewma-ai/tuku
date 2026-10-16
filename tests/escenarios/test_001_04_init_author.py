"""Test del escenario 001-04-init-author.

`--author` deja el nombre en la sección "El autor" de `LIBRO-DE-ESTILO.md`, y un
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
    libro = (vault / "LIBRO-DE-ESTILO.md").read_text(encoding="utf-8")
    return next(ln for ln in libro.splitlines() if ln.lstrip().startswith(MARCADOR))


def test_001_04_init_author_escribe_el_nombre_en_el_libro_de_estilo() -> None:
    corrida = gherkin.correr(SLUG, "el nombre del autor queda en el libro de estilo")
    assert corrida.codigo == EXITO, corrida.stderr
    destino = corrida.ruta("mi-vault")

    libro = (destino / "LIBRO-DE-ESTILO.md").read_text(encoding="utf-8")
    assert f"{MARCADOR} {AUTOR}" in libro, f"el nombre no llegó al libro: {libro[:400]!r}"
    assert "por declarar" not in libro, "quedó el placeholder del nombre sin sustituir"


def test_001_04_un_nombre_en_blanco_deja_el_vault_operable_sin_nombre() -> None:
    corrida = gherkin.correr(SLUG, "un nombre en blanco deja el vault operable")
    assert corrida.codigo == EXITO, corrida.stderr

    vault = corrida.ruta("en-blanco")
    linea = _linea_del_autor(vault)
    assert linea.startswith(f"{MARCADOR} por declarar"), f"se tocó la línea: {linea!r}"
    assert (vault / "AHORA.md").is_file(), "el vault no quedó operable"


if __name__ == "__main__":
    test_001_04_init_author_escribe_el_nombre_en_el_libro_de_estilo()
    test_001_04_un_nombre_en_blanco_deja_el_vault_operable_sin_nombre()
    print(f"ok: --author escribe el nombre; en blanco deja el vault operable ({SLUG})")
