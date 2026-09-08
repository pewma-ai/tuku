"""tuku todo open / tuku todo close: las dos consecuencias deterministas.

Fase 2 de `devel/epics.md`. `**pendiente**` abre, `~~(Hecho)~~` cierra
(`spec/bitacora.md`). El cuerpo es el mismo texto en los tres lugares: el
registro que abre, el ítem de `PENDIENTES.md` y el registro que cierra. **Abrir
es copiar, cerrar es encontrar y borrar.** Ninguna de las dos interpreta nada, y
por eso este paso no necesita LLM.

Operan **por registro**, no reconciliando el archivo. `PENDIENTES.md` es fuente
de verdad y no se regenera desde las bitácoras (`spec/pendientes.md`, regla 7):
un reconciliador borraría los pendientes abiertos en ciclos anteriores que el
`AHORA.md` en curso ya no menciona. La idempotencia se paga a mano: abrir
comprueba que el ítem no esté, cerrar que la pareja exista.

**Qué lee y escribe:** `PENDIENTES.md`. La línea del registro llega como
argumento; quien la escribió en `AHORA.md` fue `tuku entry add`.
**A mano:** copiar el cuerpo del registro como ítem bajo el callout que toca, o
borrar esa línea al cerrarlo.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

ABRE = "**pendiente**"
CIERRA = "~~(Hecho)~~"

#: Un registro con marca de la ontología cerrada. La clasificación abierta que
#: puede venir después de la marca no participa: no cambia la consecuencia.
_REGISTRO = re.compile(
    r"^- \d{2}:\d{2} - "
    r"(?:\[\[(?P<ambito>[^\]\n]+)\]\] )?"
    r"(?P<marca>\*\*pendiente\*\*|~~\(Hecho\)~~)"
    r"(?: \*\*[^*\n]+\*\*)?"
    r": (?P<cuerpo>.+)$"
)

#: Un ítem dentro de un callout: `> - [[ambito]] - cuerpo`, o sin ámbito.
_ITEM = re.compile(r"^> - (?:\[\[(?P<ambito>[^\]\n]+)\]\] - )?(?P<cuerpo>.+)$")

_CALLOUT = re.compile(r"^> \[!TODO\].*\^(?P<ancla>[\w-]+)\s*$")

SIN_FECHA = "sin-fecha"


@dataclass(frozen=True)
class Marca:
    """Lo que una línea de bitácora le pide a `PENDIENTES.md`."""

    marca: str
    ambito: str | None
    cuerpo: str


class SinCallout(Exception):
    """`PENDIENTES.md` no tiene el callout que la operación necesita."""


def parsear(linea: str) -> Marca | None:
    """La marca de la ontología cerrada de una línea, o `None` si no lleva.

    Estricta a propósito: `**Pendiente**` no es `**pendiente**` y acá no se
    reconoce, que es lo que `tuku entry lint` reporta por separado.
    """
    m = _REGISTRO.match(linea)
    if m is None:
        return None
    return Marca(m.group("marca"), m.group("ambito"), m.group("cuerpo"))


def _item(ambito: str | None, cuerpo: str) -> str:
    return f"> - [[{ambito}]] - {cuerpo}" if ambito else f"> - {cuerpo}"


def _rango_callout(lineas: list[str], ancla: str) -> tuple[int, int]:
    """Índices [inicio, fin) del callout `ancla`: su título y sus ítems."""
    for i, linea in enumerate(lineas):
        m = _CALLOUT.match(linea)
        if m is not None and m.group("ancla") == ancla:
            fin = i + 1
            while fin < len(lineas) and _ITEM.match(lineas[fin]):
                fin += 1
            return i, fin
    raise SinCallout(
        f"no existe el callout ^{ancla} en PENDIENTES.md. "
        f"Agrégalo con su título, o revisa el ancla."
    )


def cuerpos(pendientes: str, ancla: str) -> list[str]:
    """Los cuerpos de los ítems de un callout, en orden."""
    lineas = pendientes.splitlines()
    ini, fin = _rango_callout(lineas, ancla)
    return [m.group("cuerpo") for linea in lineas[ini + 1 : fin] if (m := _ITEM.match(linea))]


def _crear_callout(lineas: list[str], ancla: str) -> list[str]:
    """Agrega el callout de fecha al final, sin desplazar los horizontes.

    Los cinco de horizonte son permanentes y se leen como escalera; los de fecha
    son efímeros y nacen por debajo (`spec/pendientes.md`).
    """
    titulo = f"> [!TODO] pendientes del {ancla} ^{ancla}"
    cola = [""] if lineas and lineas[-1].strip() else []
    return [*lineas, *cola, titulo]


def abrir(pendientes: str, marca: Marca, *, ancla: str = SIN_FECHA) -> str:
    """Copia el cuerpo del registro como ítem bajo `ancla`. Idempotente.

    Si el ítem ya está, devuelve el texto sin tocar: correr el comando dos veces
    sobre el mismo registro no duplica. Si el callout es de fecha y no existe,
    nace acá; los de horizonte nunca se crean, porque el estado cero los siembra.
    """
    item = _item(marca.ambito, marca.cuerpo)
    lineas = pendientes.splitlines()

    try:
        ini, fin = _rango_callout(lineas, ancla)
    except SinCallout:
        if not es_fecha(ancla):
            raise
        lineas = _crear_callout(lineas, ancla)
        ini, fin = _rango_callout(lineas, ancla)

    if item in lineas[ini + 1 : fin]:
        return pendientes

    nuevas = [*lineas[:fin], item, *lineas[fin:]]
    texto = "\n".join(nuevas)
    return texto + "\n" if pendientes.endswith("\n") else texto


def es_fecha(ancla: str) -> bool:
    """Si el ancla es un bucket de fecha (`^2026-08-12`) y no un horizonte."""
    try:
        date.fromisoformat(ancla)
    except ValueError:
        return False
    return True


def duplicados(pendientes: str) -> list[str]:
    """Cuerpos que aparecen en más de un callout. Regla 1 de `spec/pendientes.md`.

    Es lo que reporta `tuku todo lint`: un pendiente está en exactamente un
    callout, siempre. La misma tarea en el callout del día y en la caja de la
    semana es el error que el vault real tuvo que prohibir por escrito.
    """
    vistos: dict[str, int] = {}
    for linea in pendientes.splitlines():
        if m := _ITEM.match(linea):
            cuerpo = m.group("cuerpo")
            vistos[cuerpo] = vistos.get(cuerpo, 0) + 1
    return [cuerpo for cuerpo, veces in vistos.items() if veces > 1]


def cerrar(pendientes: str, marca: Marca) -> tuple[str, bool]:
    """Borra el ítem cuyo cuerpo coincide. Devuelve el texto y si hubo pareja.

    El emparejamiento es **literal**: el cierre repite el texto del pendiente en
    vez de reescribirlo, y por eso encontrarlo no necesita juicio. Sin pareja no
    se inventa nada: se devuelve el texto intacto y `False`, y quien invoca lo
    reporta. Con `PENDIENTES.md` como fuente de verdad, un cierre inventado deja
    el archivo mintiendo.
    """
    lineas = pendientes.splitlines()
    for i, linea in enumerate(lineas):
        m = _ITEM.match(linea)
        if m is not None and m.group("cuerpo") == marca.cuerpo:
            restantes = [*lineas[:i], *lineas[i + 1 :]]
            texto = "\n".join(restantes)
            return (texto + "\n" if pendientes.endswith("\n") else texto), True
    return pendientes, False


def anclas(pendientes: str) -> list[str]:
    """Los anclas de todos los callouts, en el orden del archivo."""
    return [
        m.group("ancla")
        for linea in pendientes.splitlines()
        if (m := _CALLOUT.match(linea))
    ]
