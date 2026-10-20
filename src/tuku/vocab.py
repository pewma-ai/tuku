"""tuku context style: los vocabularios abiertos del autor, desde `reglas/`.

`spec/bitacora.md` fija dónde vive cada uno: un archivo `X.user.md` de `reglas/`
por entidad, con una sola tabla y sin encabezados. Archivo y encabezados de la
tabla son contrato: las filas crecen con el uso, el nombre no se cambia. Si falta
el archivo o su tabla el error es ruidoso y no silencioso, que es lo que separa
esto de marcar el documento con marcas invisibles.

**Qué lee y escribe:** lee `reglas/clasificaciones.user.md`,
`reglas/pendientes.user.md`, `reglas/notas.user.md` y `reglas/ciclo.user.md`. No escribe nada.
**A mano:** abrir esos archivos y leer su tabla.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import Path

from tuku import archivo, capitulos

#: Dónde vive cada vocabulario: el archivo de `reglas/`, con su única tabla. Es el
#: contrato; el libro de estilo lo transcluye en el capítulo de su entidad.
FUENTES = {
    "clasificaciones": "reglas/clasificaciones.user.md",
    "horizontes": "reglas/pendientes.user.md",
    "tipos-de-nota": "reglas/notas.user.md",
    "ciclos": "reglas/ciclo.user.md",
}

#: Los archivos de `reglas/` que declaran vocabulario.
ARCHIVOS = tuple(FUENTES.values())

#: Primera celda de una fila de tabla, que es donde va el término entre backticks.
_TERMINO = re.compile(r"^`([^`]+)`$")


class VocabularioIncompleto(Exception):
    """A un archivo de `reglas/` le falta su tabla de contrato, o el archivo entero."""


def _tabla(texto: str | None, vocabulario: str) -> capitulos.Tabla:
    ruta = FUENTES[vocabulario]
    if texto is None:
        raise VocabularioIncompleto(f"falta {ruta}. Es contrato: agrégalo con su tabla.")
    tabla = capitulos.primera_tabla(texto)
    if tabla is None:
        raise VocabularioIncompleto(
            f"falta la tabla en {ruta}. Es contrato: agrégala con sus encabezados."
        )
    return tabla


def terminos(texto: str | None, vocabulario: str) -> list[str]:
    """Los términos de un vocabulario, en el orden en que el archivo los declara."""
    return [
        m.group(1)
        for fila in _tabla(texto, vocabulario)[1:]
        if fila and (m := _TERMINO.match(fila[0]))
    ]


def leer(textos: Mapping[str, str | None]) -> dict[str, list[str]]:
    """Los vocabularios abiertos. `textos` mapea cada ruta de `reglas/` a su texto."""
    return {
        vocabulario: terminos(textos.get(ruta), vocabulario)
        for vocabulario, ruta in FUENTES.items()
    }


def leer_del_vault(vault: Path) -> dict[str, list[str]]:
    """Los vocabularios abiertos del vault."""
    return leer({ruta: leer_opcional(vault, ruta) for ruta in ARCHIVOS})


def leer_opcional(vault: Path, ruta: str) -> str | None:
    """El texto de `ruta` dentro del vault, o `None` si el archivo no está."""
    archivo_ruta = vault / ruta
    return archivo.leer(archivo_ruta) if archivo_ruta.is_file() else None


def enlazables(notas_md: str) -> list[str]:
    """Los tipos de nota con `sí` en la columna "Enlazable" de `reglas/notas.user.md`.

    La columna se busca por su encabezado; sin ella, ningún tipo se enlaza
    (`spec/notas.md`, "Enlazar notas").
    """
    tabla = capitulos.primera_tabla(notas_md)
    if not tabla:
        return []
    cabecera = [c.lower() for c in tabla[0]]
    if "enlazable" not in cabecera:
        return []
    columna = cabecera.index("enlazable")
    return [
        m.group(1)
        for fila in tabla[1:]
        if len(fila) > columna
        and (m := _TERMINO.match(fila[0]))
        and fila[columna].lower() in ("sí", "si")
    ]


def formatear(vocabularios: dict[str, list[str]]) -> str:
    """El reporte de `tuku context style`, para persona y para agente."""
    bloques = [
        f"{nombre}: {', '.join(terminos) if terminos else '(ninguno declarado)'}"
        for nombre, terminos in vocabularios.items()
    ]
    return "\n".join(bloques)
