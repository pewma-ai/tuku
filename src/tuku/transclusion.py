"""tuku transclusion sync: mantiene `AHORA.md` y `PENDIENTES.md` de acuerdo.

Regla 6 de `spec/pendientes.md`: ninguna transclusión apunta a un ancla que no
existe. Cada vez que un pendiente se crea, se mueve de escalón o se borra hay
que revisar las dos direcciones de falla:

| Falla | Síntoma | Corrección |
| --- | --- | --- |
| Transclusión sin callout | Caja de error en el día | Quitar la línea |
| Callout sin transclusión | El pendiente no aparece en su día | Agregar la línea |

**La segunda es la peligrosa.** La primera se ve: hay una caja rota y alguien la
arregla. La segunda es silenciosa, el pendiente simplemente no aparece en la
agenda, y el autor se entera cuando ya venció. Ese es el motivo de que este
comando exista en vez de confiar en que quien escribe se acuerde.

Solo mira las anclas de fecha. Las de horizonte son permanentes, así que sus
transclusiones nunca quedan huérfanas y no necesitan vigilancia.

**Qué lee y escribe:** lee `PENDIENTES.md`, lee y escribe `AHORA.md`.
**A mano:** comparar los `^AAAA-MM-DD` de `PENDIENTES.md` con las líneas
`![[PENDIENTES.md#^...]]` de cada día, y cuadrarlas.
"""

from __future__ import annotations

import re

from tuku import ahora as _ahora
from tuku import todo

_TRANSCLUSION = re.compile(r"^!\[\[PENDIENTES\.md#\^(?P<ancla>[\w-]+)\]\]\s*$")


def linea_de(ancla: str) -> str:
    return f"![[PENDIENTES.md#^{ancla}]]"


def _anclas_de_fecha(pendientes: str) -> set[str]:
    """Los callouts de fecha que existen hoy en `PENDIENTES.md`."""
    return {ancla for ancla in todo.anclas(pendientes) if todo.es_fecha(ancla)}


def sync(ahora: str, pendientes: str) -> tuple[str, list[str]]:
    """Cuadra las transclusiones de `AHORA.md`. Devuelve el texto y qué reparó.

    Idempotente: sobre un vault ya sincronizado devuelve el mismo texto y una
    lista vacía de reparaciones.
    """
    vivas = _anclas_de_fecha(pendientes)
    lineas = ahora.splitlines()
    dias = _ahora.dias(ahora)
    reparaciones: list[str] = []

    # Dirección 1, la visible: la transclusión apunta a un ancla que ya no está.
    # Solo se miran las de fecha: las de horizonte son permanentes, así que nunca
    # quedan huérfanas y este comando no las toca (`spec/pendientes.md`).
    sobran: set[int] = set()
    for i, linea in enumerate(lineas):
        m = _TRANSCLUSION.match(linea)
        if m is not None and todo.es_fecha(m.group("ancla")) and m.group("ancla") not in vivas:
            sobran.add(i)
            reparaciones.append(
                f"quitada la transclusión de ^{m.group('ancla')}: ese callout ya no existe"
            )

    # Dirección 2, la silenciosa: el callout existe y el día no lo muestra.
    faltan: dict[int, str] = {}
    for k, (i, encabezado, fecha) in enumerate(dias):
        if fecha is None or fecha.isoformat() not in vivas:
            continue
        fin = dias[k + 1][0] if k + 1 < len(dias) else len(lineas)
        ya_esta = False
        for j in range(i + 1, fin):
            if j in sobran:
                continue
            m = _TRANSCLUSION.match(lineas[j])
            if m is not None and m.group("ancla") == fecha.isoformat():
                ya_esta = True
                break
        if not ya_esta:
            faltan[i] = fecha.isoformat()
            reparaciones.append(
                f"agregada la transclusión de ^{fecha.isoformat()} bajo "
                f"{encabezado.removeprefix('## ')}"
            )

    salida: list[str] = []
    for i, linea in enumerate(lineas):
        if i in sobran:
            continue
        salida.append(linea)
        if i in faltan:
            salida.append(linea_de(faltan[i]))

    texto = "\n".join(salida)
    if ahora.endswith("\n") and not texto.endswith("\n"):
        texto += "\n"
    return texto, reparaciones


def formatear(reparaciones: list[str]) -> str:
    if not reparaciones:
        return "transclusion sync: ya estaba todo cuadrado."
    return "\n".join([*reparaciones, f"transclusion sync: {len(reparaciones)} reparación(es)."])
