"""jntr.entrada-insertar: coloca líneas de bitácora ya formadas en su día.

Fase 1 de `devel/que_implementar.md`. No interpreta ni reformatea: recibe
líneas que ya cumplen `spec/bitacora.md` y las inserta bajo el encabezado del
día indicado, ordenadas por hora, sin reescribir ninguna que ya estuviera.

**Qué lee y escribe:** solo `AHORA.md`. Si toca `PENDIENTES.md`, el corte de
la fase está mal hecho.
**A mano:** escribir la línea bajo el `## <día>` que corresponde, en el lugar
que le toca por hora.
"""

from __future__ import annotations

import re

_HORA = re.compile(r"^- (\d{2}):(\d{2}) - ")


def _clave_hora(linea: str) -> tuple[int, int]:
    m = _HORA.match(linea)
    if m is None:
        raise ValueError(f"la línea no empieza con '- HH:MM - ': {linea!r}")
    return int(m.group(1)), int(m.group(2))


def insertar(ahora: str, lineas: list[str], *, dia: str) -> str:
    """Devuelve `AHORA.md` con `lineas` insertadas bajo el encabezado `dia`.

    `dia` es el encabezado del día, con o sin el `## ` inicial. Las líneas
    nuevas se copian tal cual llegan; el orden final es por hora, y en empate
    las que ya estaban van antes que las nuevas (sort estable). Ninguna otra
    sección del archivo se toca.
    """
    encabezado = dia if dia.startswith("## ") else f"## {dia}"
    src = ahora.splitlines()

    try:
        ini = next(i for i, linea in enumerate(src) if linea.strip() == encabezado)
    except StopIteration:
        raise ValueError(f"no existe el encabezado {encabezado!r} en AHORA.md") from None

    fin = next(
        (i for i in range(ini + 1, len(src)) if src[i].startswith("## ")),
        len(src),
    )
    previas = [linea for linea in src[ini + 1 : fin] if _HORA.match(linea)]
    nuevas = [linea.rstrip("\n") for linea in lineas]

    ordenadas = sorted([*previas, *nuevas], key=_clave_hora)
    seccion = [encabezado, *ordenadas, ""]

    texto = "\n".join([*src[:ini], *seccion, *src[fin:]])
    if ahora.endswith("\n") and not texto.endswith("\n"):
        texto += "\n"
    return texto
