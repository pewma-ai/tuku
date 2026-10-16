"""tuku entry lint: revisa los registros de `AHORA.md` y reporta. Nunca escribe.

Fase 1 de `devel/epics.md`, criterio de salida. Las dos ontologías de
`spec/bitacora.md` se tratan distinto en la misma zona de la línea:

- **Cerrada, de TUKU** (`**pendiente**`, `(Hecho)`, `**cadencia**`): estricta.
  Una marca que solo difiere en mayúsculas o en una letra es un error, porque
  ningún comando la va a reconocer y el autor cree que sí.
- **Abierta, del autor**: permisiva. Un tipo que no está en el libro de estilo
  se reporta como pregunta para formalizarlo después, nunca como error. Un lint
  que rechaza vocabulario nuevo impide que la organización emerja.

Un registro fuera del rango del ciclo abierto también es error, y el lint no
inventa los días que faltan para acomodarlo.

**Qué lee y escribe:** lee `AHORA.md` y `LIBRO-DE-ESTILO.md`. **No escribe.**
Verificar y corregir son operaciones distintas (`spec/cli.md`).
**A mano:** leer los registros del ciclo comparando las marcas contra el libro
de estilo.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

from tuku import ahora as _ahora
from tuku import link

#: La ontología cerrada, tal como `spec/bitacora.md` la fija. Crece solo cuando
#: TUKU incorpora una consecuencia nueva, nunca por uso del autor.
CERRADA = ("**pendiente**", "(Hecho)", "**cadencia**")

#: La marca tachada en vez del cuerpo, que ya no es válida: se reporta con su corrección.
TACHADA = "~~(Hecho)~~"

_HORA = re.compile(r"^- (\d{2}):(\d{2}) - ")
_MARCA = re.compile(r"\*\*[^*\n]+\*\*|~~\([^)\n]+\)~~")

#: `(Hecho)` no lleva delimitadores, así que su mala escritura se busca en la
#: posición de la marca: tras la hora y el link del ámbito.
_CIERRE = re.compile(
    rf"^- \d{{2}}:\d{{2}} - (?:{link.ENLACE} )?\((?P<texto>hecho)\)", re.IGNORECASE
)

ERROR = "error"
PREGUNTA = "pregunta"


@dataclass(frozen=True)
class Hallazgo:
    """Un hallazgo del lint. `correccion` no es opcional: `spec/cli.md` exige
    que toda salida nombre el defecto y qué hacer con él."""

    linea: int
    grado: str
    defecto: str
    correccion: str

    def __str__(self) -> str:
        marca = "error" if self.grado == ERROR else "pregunta"
        return f"AHORA.md:{self.linea}: {marca}: {self.defecto}. {self.correccion}"


def lint(ahora: str, *, abiertos: list[str]) -> list[Hallazgo]:
    """Los hallazgos de `AHORA.md`, en orden de aparición. No modifica nada."""
    hallazgos: list[Hallazgo] = []
    rango = _ahora.rango(ahora)
    cerrada_plegada = {marca.casefold(): marca for marca in CERRADA}
    cerrada_plegada[TACHADA.casefold()] = "(Hecho)"
    abiertos_plegados = {termino.casefold() for termino in abiertos}
    dia_actual: date | None = None
    dia_fuera = False

    for n, linea in enumerate(ahora.splitlines(), start=1):
        if linea.startswith("## "):
            dia_fuera = False
            dia_actual = None
            if rango is not None:
                desde, hasta = rango
                dia_actual = _ahora.fecha_del_dia(linea, desde, hasta)
                dia_fuera = dia_actual is not None and not (desde <= dia_actual <= hasta)
            continue

        if not _HORA.match(linea):
            continue

        if dia_fuera and dia_actual is not None:
            desde, hasta = rango  # type: ignore[misc]
            hallazgos.append(
                Hallazgo(
                    n,
                    ERROR,
                    f"el registro cae en {dia_actual.isoformat()}, fuera del ciclo "
                    f"abierto ({desde.isoformat()} a {hasta.isoformat()})",
                    "Muévelo al ciclo que le corresponde, o abre ese ciclo.",
                )
            )

        cierre = _CIERRE.match(linea)
        if cierre is not None and cierre.group("texto") != "Hecho":
            hallazgos.append(
                Hallazgo(
                    n,
                    ERROR,
                    f"({cierre.group('texto')}) no es una marca de la ontología cerrada",
                    "Escríbela exactamente (Hecho), o ningún comando la reconoce.",
                )
            )

        for marca in _MARCA.findall(linea):
            if marca in CERRADA:
                continue
            canonica = cerrada_plegada.get(marca.casefold())
            if canonica is not None:
                hallazgos.append(
                    Hallazgo(
                        n,
                        ERROR,
                        f"{marca} no es una marca de la ontología cerrada",
                        f"Escríbela exactamente {canonica}, o ningún comando la reconoce.",
                    )
                )
                continue
            termino = marca.strip("*")
            if termino.casefold() not in abiertos_plegados:
                hallazgos.append(
                    Hallazgo(
                        n,
                        PREGUNTA,
                        f"{marca} no está en el libro de estilo",
                        "Se acepta igual. Agrégalo a `### Clasificaciones` "
                        "cuando sepas qué significa.",
                    )
                )

    return hallazgos


def formatear(hallazgos: list[Hallazgo]) -> str:
    """El reporte, para persona y para agente. Es el mismo texto para los dos."""
    if not hallazgos:
        return "entry lint: sin hallazgos."
    errores = sum(1 for h in hallazgos if h.grado == ERROR)
    preguntas = len(hallazgos) - errores
    resumen = f"entry lint: {errores} error(es), {preguntas} pregunta(s)."
    return "\n".join([*(str(h) for h in hallazgos), resumen])
