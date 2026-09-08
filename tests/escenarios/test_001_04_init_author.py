"""Test del escenario 001-04-init-author.

Escenario: 001-04-init-author.md

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

Fecha fija 2026-08-11, la misma de `001-02`, para que el vault resultante sea
comparable con `diff -r` contra el de ese escenario (salvo `LIBRO-DE-ESTILO.md`,
que acá lleva el nombre).

El caso con nombre deja el vault en
`playground/001-04-init-author/<escenario>/mi-vault/`; el segundo escenario deja
los dos suyos al lado, `sin-nombre/` y `en-blanco/`.

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
from vault import placeholders_sin_sustituir  # noqa: E402

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

    for archivo in ("AHORA.md", "PENDIENTES.md", "AGENTS.md"):
        assert (destino / archivo).is_file(), f"falta {archivo} en el vault sembrado"
    assert not placeholders_sin_sustituir(destino), "quedaron placeholders vivos"


def test_001_04_sin_autor_o_en_blanco_el_vault_queda_operable_sin_nombre() -> None:
    corrida = gherkin.correr(SLUG, "omitir el nombre deja el vault operable")
    assert corrida.codigo == EXITO, corrida.stderr

    for nombre in ("sin-nombre", "en-blanco"):
        vault = corrida.ruta(nombre)
        linea = _linea_del_autor(vault)
        assert linea.startswith(f"{MARCADOR} por declarar"), (
            f"la línea del autor se tocó en {nombre}: {linea!r}"
        )
        assert (vault / "AHORA.md").is_file(), f"{nombre} no quedó operable"


if __name__ == "__main__":
    test_001_04_init_author_escribe_el_nombre_en_el_libro_de_estilo()
    test_001_04_sin_autor_o_en_blanco_el_vault_queda_operable_sin_nombre()
    print(f"ok: --author escribe el nombre; omitirlo deja el vault operable ({SLUG})")
