"""Test del escenario 001-004-init-author.

Escenario: 001-004-init-author.md

Cierra la capa de identidad mínima, y es la única cobertura del parámetro
`autor` de `init()`: el nombre que se pasa queda en la sección "El autor" de
`LIBRO-DE-ESTILO.md`, y omitirlo (o pasarlo vacío) deja el vault operable sin
nombre, sin romper nada (principio 2).

Ya no hay prompt ni `install.sh`: la decisión 4 del epic 002 reemplazó el
instalador shell por la función importable, así que el texto ya no atraviesa
capas de citado de shell. El nombre elegido, `ARTURO PEREZ-REVERTE (Arturo)`,
con espacios, paréntesis y guion, se mantiene igual: verifica que el reemplazo
por prefijo de línea de `_sembrar_autor` no lo parte ni toca la prosa que sigue
al marcador.

Fecha fija 2026-08-11, la misma de `001-002`, para que el vault resultante sea
comparable con `diff -r` contra el de ese escenario (salvo `LIBRO-DE-ESTILO.md`,
que acá lleva el nombre).

El caso con nombre deja el vault en `playground/001-004-init-author/`.

Ejecutable directo: `python3 tests/escenarios/test_001_004_init_author.py`
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

from vault import placeholders_sin_sustituir, preparar_playground  # noqa: E402

from tuku.init import init  # noqa: E402

SLUG = "001-004-init-author"
FECHA_FIJA = date(2026, 8, 11)
AUTOR = "ARTURO PEREZ-REVERTE (Arturo)"
MARCADOR = "**Nombre del autor:**"


def test_001_004_init_author_escribe_el_nombre_en_el_libro_de_estilo() -> None:
    destino = preparar_playground(SLUG)
    init(destino, variante="vanilla", desde=FECHA_FIJA, home=RAIZ, autor=AUTOR)

    libro = (destino / "LIBRO-DE-ESTILO.md").read_text(encoding="utf-8")
    assert f"{MARCADOR} {AUTOR}" in libro, f"el nombre no llegó al libro: {libro[:400]!r}"
    assert "por declarar" not in libro, "quedó el placeholder del nombre sin sustituir"

    for archivo in ("AHORA.md", "PENDIENTES.md", "AGENTS.md"):
        assert (destino / archivo).is_file(), f"falta {archivo} en el vault sembrado"
    assert not placeholders_sin_sustituir(destino), "quedaron placeholders vivos"


def test_001_004_sin_autor_el_vault_queda_operable_sin_nombre() -> None:
    destino = preparar_playground(SLUG + "-sin-nombre")
    init(destino, variante="vanilla", desde=FECHA_FIJA, home=RAIZ)

    libro = (destino / "LIBRO-DE-ESTILO.md").read_text(encoding="utf-8")
    linea = next(ln for ln in libro.splitlines() if ln.lstrip().startswith(MARCADOR))
    assert linea.startswith(f"{MARCADOR} por declarar"), (
        f"la línea del autor se tocó sin pasar autor: {linea!r}"
    )
    assert (destino / "AHORA.md").is_file(), "sin autor, el vault igual debe quedar operable"


def test_001_004_autor_vacio_equivale_a_no_pasarlo() -> None:
    destino = preparar_playground(SLUG + "-vacio")
    init(destino, variante="vanilla", desde=FECHA_FIJA, home=RAIZ, autor="   ")

    libro = (destino / "LIBRO-DE-ESTILO.md").read_text(encoding="utf-8")
    assert "por declarar" in libro, "un autor en blanco no debería tocar el marcador"
    assert (destino / "AHORA.md").is_file()


if __name__ == "__main__":
    test_001_004_init_author_escribe_el_nombre_en_el_libro_de_estilo()
    test_001_004_sin_autor_el_vault_queda_operable_sin_nombre()
    test_001_004_autor_vacio_equivale_a_no_pasarlo()
    print(f"ok: --author escribe el nombre; omitirlo deja el vault operable ({SLUG})")
