"""tuku todo open / tuku todo close: las dos consecuencias deterministas.

Fase 2 de `devel/epics.md`. `**pendiente**` abre, `~~(Hecho)~~` cierra
(`spec/bitacora.md`). El cuerpo es el mismo texto en los tres lugares: el
registro que abre, la fila de `PENDIENTES.md` y el registro que cierra. **Abrir
es copiar, cerrar es encontrar y borrar.** Ninguna de las dos interpreta nada, y
por eso este paso no necesita LLM.

Operan **por registro**, no reconciliando el archivo. `PENDIENTES.md` es fuente
de verdad y no se regenera desde las bitácoras (`spec/pendientes.md`, regla 7):
un reconciliador borraría los pendientes abiertos en ciclos anteriores que el
`AHORA.md` en curso ya no menciona. La idempotencia se paga a mano: abrir
comprueba que la fila no esté, cerrar que la pareja exista.

El archivo es **una sola tabla**, `| Horizonte | Cuándo | Ámbito | Detalle |`.
El horizonte y la fecha son columnas y no estructura: bajar de escalón o agendar
mueve o edita una fila, y nunca crea ni destruye secciones.

**Qué lee y escribe:** las funciones de este módulo solo tocan `PENDIENTES.md`,
que es la fuente de verdad. La línea del registro llega como argumento; quien la
escribió en `AHORA.md` fue `tuku entry add`. El comando `tuku todo open` escribe
además las dos vistas derivadas, `AHORA.md` y `ambitos/PENDIENTES-AMBITOS.md`,
llamando a `tuku.propagate`; con `--no-propagate` no lo hace y el lote propaga
una sola vez al final.
**A mano:** agregar la fila con su horizonte, o borrarla al cerrarlo, y copiar
el pendiente bajo su día y en el callout de su ámbito.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

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

#: Una fila de la tabla: cuatro celdas. La cabecera y el separador tienen la
#: misma forma y se descartan aparte.
_FILA = re.compile(
    r"^\|(?P<horizonte>[^|\n]*)\|(?P<cuando>[^|\n]*)\|"
    r"(?P<ambito>[^|\n]*)\|(?P<cuerpo>[^|\n]*)\|\s*$"
)

_ENLACE = re.compile(r"^\[\[(?P<ambito>[^\]\n]+)\]\]$")

CABECERA = "| Horizonte | Cuándo | Ámbito | Detalle |"

#: La escalera, en orden: tres del autor más 'con fecha' del sistema (spec/pendientes.md).
ESCALERA = (
    "esta semana",
    "próxima semana",
    "fin de mes",
    "con fecha",
)

ESTA_SEMANA = "esta semana"
CON_FECHA = "con fecha"


@dataclass(frozen=True)
class Marca:
    """Lo que una línea de bitácora le pide a `PENDIENTES.md`."""

    marca: str
    ambito: str | None
    cuerpo: str


@dataclass(frozen=True)
class Fila:
    """Una fila de la tabla de pendientes."""

    horizonte: str
    cuando: str
    ambito: str | None
    cuerpo: str

    def linea(self) -> str:
        ambito = f"[[{self.ambito}]]" if self.ambito else ""
        return f"| {self.horizonte} | {self.cuando} | {ambito} | {self.cuerpo} |"


class SinTabla(Exception):
    """`PENDIENTES.md` no tiene la tabla que la operación necesita."""


def slug(nombre: str) -> str:
    """El nombre sin acentos ni espacios: `próxima semana` → `proxima-semana`."""
    plano = unicodedata.normalize("NFKD", nombre.strip().lower())
    plano = "".join(c for c in plano if not unicodedata.combining(c))
    return re.sub(r"\s+", "-", plano)


def canonico(horizonte: str) -> str:
    """El horizonte tal como se escribe en la tabla, aceptando `proxima-semana`."""
    buscado = slug(horizonte)
    for nombre in ESCALERA:
        if slug(nombre) == buscado:
            return nombre
    return horizonte.strip()


def parsear(linea: str) -> Marca | None:
    """La marca de la ontología cerrada de una línea, o `None` si no lleva.

    Estricta a propósito: `**Pendiente**` no es `**pendiente**` y acá no se
    reconoce, que es lo que `tuku entry lint` reporta por separado.
    """
    m = _REGISTRO.match(linea)
    if m is None:
        return None
    return Marca(m.group("marca"), m.group("ambito"), m.group("cuerpo"))


def _es_separador(linea: str) -> bool:
    return bool(linea.strip()) and set(linea.strip()) <= set("| -:")


def _parsear_fila(linea: str) -> Fila | None:
    """La fila de datos de una línea, o `None` si es cabecera, separador u otra cosa."""
    if _es_separador(linea):
        return None
    m = _FILA.match(linea)
    if m is None:
        return None
    horizonte = m.group("horizonte").strip()
    if horizonte == "Horizonte" and m.group("cuerpo").strip() == "Detalle":
        return None
    ambito = m.group("ambito").strip()
    enlace = _ENLACE.match(ambito)
    return Fila(
        horizonte,
        m.group("cuando").strip(),
        enlace.group("ambito") if enlace else None,
        m.group("cuerpo").strip(),
    )


def _rango_tabla(lineas: list[str]) -> tuple[int, int]:
    """Índices [inicio, fin) de las filas de datos, tras el separador de la tabla."""
    for i, linea in enumerate(lineas):
        if _es_separador(linea) and linea.strip().startswith("|"):
            fin = i + 1
            while fin < len(lineas) and _parsear_fila(lineas[fin]) is not None:
                fin += 1
            return i + 1, fin
    raise SinTabla(
        f"PENDIENTES.md no tiene la tabla de pendientes. "
        f"Agrégale la cabecera `{CABECERA}` y su separador."
    )


def filas(pendientes: str, horizonte: str | None = None) -> list[Fila]:
    """Las filas de la tabla, en el orden del archivo. Filtra por horizonte si se pide."""
    lineas = pendientes.splitlines()
    ini, fin = _rango_tabla(lineas)
    todas = [f for linea in lineas[ini:fin] if (f := _parsear_fila(linea))]
    if horizonte is None:
        return todas
    buscado = slug(horizonte)
    return [f for f in todas if slug(f.horizonte) == buscado]


def cuerpos(pendientes: str, horizonte: str | None = None) -> list[str]:
    """Los detalles de las filas, en orden."""
    return [f.cuerpo for f in filas(pendientes, horizonte)]


def _clave(fila: Fila) -> tuple[int, str]:
    """Por dónde va la fila: escalón de la escalera, y dentro por fecha.

    Un horizonte que no está en la escalera va al final, y las filas sin fecha
    después de las fechadas del mismo escalón.
    """
    escalones = [slug(n) for n in ESCALERA]
    propio = slug(fila.horizonte)
    orden = escalones.index(propio) if propio in escalones else len(escalones)
    return orden, fila.cuando or "9999-99-99"


def abrir(
    pendientes: str,
    marca: Marca,
    *,
    horizon: str = ESTA_SEMANA,
    horizonte: str | None = None,
    when: str = "",
    cuando: str | None = None,
) -> str:
    """Copia el cuerpo del registro como fila. Idempotente.

    `spec/pendientes.md`: todo pendiente nuevo va a la tabla única de
    `PENDIENTES.md`, ordenado por escalón y por fecha.

    Si el detalle ya existe no duplica la fila: un registro repetido en la
    bitácora no abre dos veces el mismo pendiente.
    """
    dest_horizon = horizonte if horizonte is not None else horizon
    dest_when = cuando if cuando is not None else when
    fila = Fila(
        horizonte=canonico(dest_horizon),
        cuando=dest_when.strip(),
        ambito=marca.ambito,
        cuerpo=marca.cuerpo,
    )
    lineas = pendientes.splitlines()
    ini, fin = _rango_tabla(lineas)
    existentes = [f for linea in lineas[ini:fin] if (f := _parsear_fila(linea))]

    if fila in existentes:
        return pendientes

    clave = _clave(fila)
    desplazamiento = next(
        (i for i, f in enumerate(existentes) if _clave(f) > clave), len(existentes)
    )
    corte = ini + desplazamiento
    nuevas = [*lineas[:corte], fila.linea(), *lineas[corte:]]
    texto = "\n".join(nuevas)
    return texto + "\n" if pendientes.endswith("\n") else texto


def horizontes(pendientes: str) -> list[str]:
    """Los horizontes que aparecen en la tabla, sin repetir, en el orden del archivo."""
    vistos: list[str] = []
    for fila in filas(pendientes):
        if fila.horizonte not in vistos:
            vistos.append(fila.horizonte)
    return vistos


def duplicados(pendientes: str) -> list[str]:
    """Detalles que aparecen en más de una fila. Regla 1 de `spec/pendientes.md`.

    Es lo que reporta `tuku todo lint`: un pendiente está en exactamente una
    fila, siempre. La misma tarea en dos horizontes es el error que el vault
    real tuvo que prohibir por escrito.
    """
    vistos: dict[str, int] = {}
    for fila in filas(pendientes):
        vistos[fila.cuerpo] = vistos.get(fila.cuerpo, 0) + 1
    return [cuerpo for cuerpo, veces in vistos.items() if veces > 1]


def cerrar(pendientes: str, marca: Marca) -> tuple[str, bool]:
    """Borra la fila cuyo detalle coincide. Devuelve el texto y si hubo pareja.

    El emparejamiento es **literal**: el cierre repite el texto del pendiente en
    vez de reescribirlo, y por eso encontrarlo no necesita juicio. Sin pareja no
    se inventa nada: se devuelve el texto intacto y `False`, y quien invoca lo
    reporta. Con `PENDIENTES.md` como fuente de verdad, un cierre inventado deja
    el archivo mintiendo.
    """
    lineas = pendientes.splitlines()
    for i, linea in enumerate(lineas):
        f = _parsear_fila(linea)
        if f is not None and f.cuerpo == marca.cuerpo:
            restantes = [*lineas[:i], *lineas[i + 1 :]]
            texto = "\n".join(restantes)
            return (texto + "\n" if pendientes.endswith("\n") else texto), True
    return pendientes, False
