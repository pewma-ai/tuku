"""Lectura de `AHORA.md` y las bitácoras: los encabezados de día y su fecha.

El encabezado no lleva año a propósito (`## Martes 11 de agosto` se lee mejor),
así que el año se infiere. `AHORA.md` no declara rango: el año es el que deja la
fecha, con ese día de la semana, más cerca de `hoy`. Una bitácora semanal declara
`from` y `to`, y el año sale de ese rango.

**Qué lee y escribe:** lee `AHORA.md` y las bitácoras. No escribe.
"""

from __future__ import annotations

import re
from datetime import date

from tuku.init import DIAS, MESES

_DIA = re.compile(r"^## \w+ (\d{1,2}) de (\w+)")
_CAMPO = re.compile(r"^(from|to):\s*(\d{4}-\d{2}-\d{2})\s*$")


def es_dia(linea: str) -> bool:
    """Si la línea es el encabezado de un día: `## Martes 25 de agosto`."""
    m = _DIA.match(linea)
    return m is not None and m.group(2) in MESES


def rango(ahora: str) -> tuple[date, date] | None:
    """`from` y `to` del frontmatter OKF, o `None` si siguen siendo placeholders."""
    campos: dict[str, date] = {}
    for linea in ahora.splitlines()[:10]:
        if m := _CAMPO.match(linea.strip()):
            campos[m.group(1)] = date.fromisoformat(m.group(2))
    if "from" not in campos or "to" not in campos:
        return None
    return campos["from"], campos["to"]


def limites_de(texto: str, hoy: date | None = None) -> tuple[date, date] | None:
    """The range that dates the headings of `texto`: its `from`-`to`, or else `hoy` alone.

    A weekly logbook declares its range; `AHORA.md` does not, and its days are the
    ones nearest to `hoy`. `None` when there is neither.
    """
    return rango(texto) or ((hoy, hoy) if hoy is not None else None)


def fecha_del_dia(encabezado: str, desde: date, hasta: date) -> date | None:
    """La fecha de un `## Martes 11 de agosto`, o `None` si no es un día.

    El encabezado no lleva año: se elige el que deja la fecha más cerca del rango
    `desde`-`hasta` (0 días si cae dentro) entre los que respetan el día de la
    semana, y sin ninguno, el más cercano. Así un día de la ventana de pendientes,
    posterior al fin del rango, y el rango que cruza el año se leen bien.
    """
    m = _DIA.match(encabezado)
    if m is None or m.group(2) not in MESES:
        return None
    dia, mes = int(m.group(1)), MESES.index(m.group(2)) + 1
    nombre = encabezado.removeprefix("## ").split(maxsplit=1)[0]
    candidatas: list[tuple[int, date]] = []
    for anio in range(desde.year - 1, hasta.year + 2):
        try:
            candidata = date(anio, mes, dia)
        except ValueError:
            continue
        distancia = max((desde - candidata).days, (candidata - hasta).days, 0)
        concuerda = DIAS[candidata.weekday()] == nombre
        candidatas.append((distancia + (0 if concuerda else 10_000), candidata))
    return min(candidatas)[1] if candidatas else None


def dias(texto: str, hoy: date | None = None) -> list[tuple[int, str, date | None]]:
    """Los encabezados de día: índice de línea, texto y fecha si se pudo resolver."""
    limites = limites_de(texto, hoy)
    salida: list[tuple[int, str, date | None]] = []
    for i, linea in enumerate(texto.splitlines()):
        if not linea.startswith("## "):
            continue
        fecha = fecha_del_dia(linea, *limites) if limites is not None else None
        salida.append((i, linea, fecha))
    return salida


def encabezado_de(fecha: date) -> str:
    """El encabezado con que un día se escribe en `AHORA.md` y en las bitácoras."""
    return f"## {DIAS[fecha.weekday()]} {fecha.day} de {MESES[fecha.month - 1]}"


def insertar_dia(
    lineas: list[str], fecha: date, limites: tuple[date, date] | None = None
) -> tuple[list[str], int]:
    """`lineas` con el encabezado de `fecha` en su lugar, y el índice de ese encabezado.

    Los días van del más nuevo al más viejo: el nuevo queda antes del primer día
    más antiguo que él, o al final si todos los que hay son más nuevos. Un día ya
    presente no se duplica. Los demás días se fechan con el año más cercano a `limites`
    (el rango de una bitácora) o, sin él, a `fecha`.
    """
    encabezado = encabezado_de(fecha)
    for i, linea in enumerate(lineas):
        if linea.strip() == encabezado:
            return lineas, i
    destino = len(lineas)
    for i, linea in enumerate(lineas):
        if linea.startswith("## "):
            existente = fecha_del_dia(linea, *(limites or (fecha, fecha)))
            if existente is not None and existente < fecha:
                destino = i
                break
    if destino == len(lineas):
        # Al final de los días, pero antes del `---` que cierra el archivo.
        ultimo = max((i for i, x in enumerate(lineas) if x.startswith("## ")), default=None)
        if ultimo is not None:
            destino = next(
                (i for i in range(ultimo + 1, len(lineas)) if lineas[i].strip() == "---"),
                len(lineas),
            )
    antes = lineas[:destino]
    if antes and antes[-1].strip():
        antes = [*antes, ""]
    return [*antes, encabezado, "", *lineas[destino:]], len(antes)
