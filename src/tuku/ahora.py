"""Lectura de `AHORA.md`: el rango del ciclo y los encabezados de día.

Lo comparten `tuku entry lint` y `tuku cycle lint`, que necesitan lo
mismo: saber qué día es cada `## <día>` y si cae dentro del ciclo abierto.

El encabezado no lleva año a propósito (`## Martes 11 de agosto` se lee mejor),
así que el año sale del rango del frontmatter. Por eso todo aquí depende de que
`from` y `to` estén resueltos: en un vault recién sembrado lo están.

**Qué lee y escribe:** lee `AHORA.md`. No escribe.
"""

from __future__ import annotations

import re
from datetime import date

from tuku.init import DIAS, MESES

_DIA = re.compile(r"^## \w+ (\d{1,2}) de (\w+)")
_CAMPO = re.compile(r"^(from|to):\s*(\d{4}-\d{2}-\d{2})\s*$")


def rango(ahora: str) -> tuple[date, date] | None:
    """`from` y `to` del frontmatter OKF, o `None` si siguen siendo placeholders."""
    campos: dict[str, date] = {}
    for linea in ahora.splitlines()[:10]:
        if m := _CAMPO.match(linea.strip()):
            campos[m.group(1)] = date.fromisoformat(m.group(2))
    if "from" not in campos or "to" not in campos:
        return None
    return campos["from"], campos["to"]


def fecha_del_dia(encabezado: str, desde: date, hasta: date) -> date | None:
    """La fecha de un `## Martes 11 de agosto`, o `None` si no es un día.

    El año se prueba contra el rango porque el encabezado no lo lleva; así el
    ciclo que cruza el año no rompe la lectura.
    """
    m = _DIA.match(encabezado)
    if m is None or m.group(2) not in MESES:
        return None
    dia, mes = int(m.group(1)), MESES.index(m.group(2)) + 1
    for anio in (desde.year, hasta.year):
        try:
            candidata = date(anio, mes, dia)
        except ValueError:
            continue
        if desde <= candidata <= hasta:
            return candidata
    try:
        return date(desde.year, mes, dia)
    except ValueError:
        return None


def dias(ahora: str) -> list[tuple[int, str, date | None]]:
    """Los encabezados de día: índice de línea, texto y fecha si se pudo resolver."""
    limites = rango(ahora)
    salida: list[tuple[int, str, date | None]] = []
    for i, linea in enumerate(ahora.splitlines()):
        if not linea.startswith("## "):
            continue
        fecha = fecha_del_dia(linea, *limites) if limites is not None else None
        salida.append((i, linea, fecha))
    return salida


def encabezado_de(fecha: date) -> str:
    """El encabezado con que un día se escribe en `AHORA.md`.

    Vivía en `cli.py`, que lo necesitaba para saber bajo qué día cae un registro
    sin `--day`. Es la forma canónica de un día del ciclo, no una decisión de la
    interfaz.
    """
    return f"## {DIAS[fecha.weekday()]} {fecha.day} de {MESES[fecha.month - 1]}"
