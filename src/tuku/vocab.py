"""tuku vocab show: los vocabularios abiertos del autor, desde el libro de estilo.

`spec/bitacora.md` fija que los tres encabezados de `LIBRO-DE-ESTILO.md` son
contrato: se leen esos, exactos. Las filas crecen con el uso, el encabezado no
se renombra. Si falta un encabezado el error es ruidoso y no silencioso, que es
lo que separa esto de marcar el documento con marcas invisibles.

**Qué lee y escribe:** lee `LIBRO-DE-ESTILO.md`. No escribe nada.
**A mano:** abrir el libro de estilo y leer las tres tablas.
"""

from __future__ import annotations

import re
from pathlib import Path

from tuku.resultado import Resultado

#: Encabezado de contrato por vocabulario. Cambiar uno rompe la lectura, y por
#: eso el libro de estilo lo dice en su propia prosa.
ENCABEZADOS = {
    "clasificaciones": "### Clasificaciones",
    "horizontes": "### Horizontes",
    "tipos-de-nota": "### Tipos de nota",
}

#: Primera celda de una fila de tabla, que es donde va el término entre backticks.
_TERMINO = re.compile(r"^\|\s*`([^`]+)`\s*\|")


class VocabularioIncompleto(Exception):
    """Al libro de estilo le falta un encabezado de contrato."""


def leer(libro: str) -> dict[str, list[str]]:
    """Los tres vocabularios abiertos, en el orden en que el libro los declara."""
    lineas = libro.splitlines()
    vocabularios: dict[str, list[str]] = {}

    for nombre, encabezado in ENCABEZADOS.items():
        try:
            ini = next(i for i, linea in enumerate(lineas) if linea.strip() == encabezado)
        except StopIteration:
            raise VocabularioIncompleto(
                f"falta el encabezado {encabezado!r} en LIBRO-DE-ESTILO.md. "
                f"Es contrato: agrégalo con su tabla debajo."
            ) from None

        fin = next(
            (i for i in range(ini + 1, len(lineas)) if lineas[i].startswith(("## ", "### "))),
            len(lineas),
        )
        terminos = [
            m.group(1)
            for linea in lineas[ini + 1 : fin]
            if (m := _TERMINO.match(linea)) and m.group(1) != "Clasificación"
        ]
        vocabularios[nombre] = terminos

    return vocabularios


def formatear(vocabularios: dict[str, list[str]]) -> str:
    """El reporte de `tuku vocab show`, para persona y para agente."""
    bloques = [
        f"{nombre}: {', '.join(terminos) if terminos else '(ninguno declarado)'}"
        for nombre, terminos in vocabularios.items()
    ]
    return "\n".join(bloques)


def mostrar_del_vault(vault: Path) -> Resultado:
    """Los vocabularios que el autor declaró en su libro de estilo."""
    from tuku.config import leer_config

    return Resultado.hecho(formatear(leer_config(vault).vocabularios))
