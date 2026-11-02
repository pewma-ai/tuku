"""Lectura de `AHORA.md`: el rango del ciclo y los encabezados de día.

Lo comparten `tuku doctor entry` y `tuku doctor cycle`, que necesitan lo
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
_CICLO = re.compile(r"^cycle:\s*(\S.*?)\s*$")

#: El nombre del ciclo cuando el frontmatter no lo declara.
SEMANA = "semana"


def es_dia(linea: str) -> bool:
    """Si la línea es el encabezado de un día: `## Martes 25 de agosto`."""
    m = _DIA.match(linea)
    return m is not None and m.group(2) in MESES


def como_cerrar(desde: date, hasta: date) -> str:
    """Cómo se archiva a mano el ciclo `desde`–`hasta`, mientras no exista `cycle close`.

    La bitácora vive un nivel más adentro que `AHORA.md`: sin reescribir sus links
    relativos quedan rotos, y `tuku fix link` no los repara.
    """
    return (
        f"copia AHORA.md a bitacoras/bitacora-{desde.isoformat()}-{hasta.isoformat()}.md, "
        "pon `status: stable` y baja un nivel sus links relativos "
        "(`](ambitos/` pasa a `](../ambitos/`, y lo mismo con `notas/` y `bitacoras/`)"
    )


def rango(ahora: str) -> tuple[date, date] | None:
    """`from` y `to` del frontmatter OKF, o `None` si siguen siendo placeholders."""
    campos: dict[str, date] = {}
    for linea in ahora.splitlines()[:10]:
        if m := _CAMPO.match(linea.strip()):
            campos[m.group(1)] = date.fromisoformat(m.group(2))
    if "from" not in campos or "to" not in campos:
        return None
    return campos["from"], campos["to"]


def nombre_del_ciclo(texto: str) -> str:
    """The `cycle` of the frontmatter, or `semana` when a file does not declare one."""
    for linea in texto.splitlines()[:10]:
        if m := _CICLO.match(linea.strip()):
            return m.group(1)
    return SEMANA


def fecha_del_dia(encabezado: str, desde: date, hasta: date) -> date | None:
    """La fecha de un `## Martes 11 de agosto`, o `None` si no es un día.

    El encabezado no lleva año: se elige el que deja la fecha más cerca del rango
    `desde`-`hasta`, que es 0 días si cae dentro. Así un día de la ventana de
    pendientes, posterior al fin del rango, y el rango que cruza el año se leen bien.
    """
    m = _DIA.match(encabezado)
    if m is None or m.group(2) not in MESES:
        return None
    dia, mes = int(m.group(1)), MESES.index(m.group(2)) + 1
    mejor: tuple[int, date] | None = None
    for anio in range(desde.year - 1, hasta.year + 2):
        try:
            candidata = date(anio, mes, dia)
        except ValueError:
            continue
        distancia = max((desde - candidata).days, (candidata - hasta).days, 0)
        if mejor is None or distancia < mejor[0]:
            mejor = (distancia, candidata)
    return mejor[1] if mejor else None


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
    sin día en `--at`. Es la forma canónica de un día del ciclo, no una decisión de la
    interfaz.
    """
    return f"## {DIAS[fecha.weekday()]} {fecha.day} de {MESES[fecha.month - 1]}"


def insertar_dia(
    lineas: list[str], fecha: date, limites: tuple[date, date]
) -> tuple[list[str], int]:
    """`lineas` con el encabezado de `fecha` en su lugar, y el índice de ese encabezado.

    Los días van del más nuevo al más viejo: el nuevo queda antes del primer día
    más antiguo que él, o al final si todos los que hay son más nuevos. Un día ya
    presente no se duplica.
    """
    encabezado = encabezado_de(fecha)
    for i, linea in enumerate(lineas):
        if linea.strip() == encabezado:
            return lineas, i
    destino = len(lineas)
    for i, linea in enumerate(lineas):
        if linea.startswith("## "):
            existente = fecha_del_dia(linea, *limites)
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
