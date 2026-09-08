"""tuku todo propagate: las dos vistas derivadas de `PENDIENTES.md`.

`PENDIENTES.md` es fuente de verdad y nada más lo es (`spec/pendientes.md`).
Todo lo que muestre un pendiente fuera de él es derivado, y se **regenera** en
vez de repararse: propagar es una función pura de la tabla contra su salida, y
por eso correrlo dos veces da el mismo texto y sobre un vault cuadrado no
cambia ningún archivo.

Las dos vistas:

| Vista | Dónde | Qué contiene |
| --- | --- | --- |
| El día | La región del día en `AHORA.md` | Las filas cuyo `Cuándo` cae en ese día |
| El ámbito | `ambitos/PENDIENTES-AMBITOS.md` | Un callout por ámbito del árbol |

**La región del día** es lo que va entre el encabezado `## <día>` y el primer
registro. No lleva marca que la delimite: los registros empiezan siempre por
`- HH:MM - `, así que la frontera es estructura visible. El comando es su dueño
y al regenerar la reemplaza entera, prosa suelta incluida.

**El archivo por ámbito** es generado, no un reporte: los reportes llevan fecha
en el nombre y este no, porque siempre dice el estado de ahora. Tiene un callout
por cada ámbito que exista en `ambitos/`, tenga pendientes o no, y el que no
tiene lleva `SIN PENDIENTES`. Que el callout exista siempre es el punto: la
transclusión `![[PENDIENTES-AMBITOS.md#^personal.md]]` de cada página de ámbito
nunca queda apuntando a un ancla que no existe, que es la falla silenciosa que
este rediseño persigue.

**Un pendiente sin ámbito no aparece en ninguna vista de ámbito.** No se le
inventa un callout «sin ámbito»: ese ancla no correspondería a ninguna página
que lo transcluya, y el archivo dejaría de ser el espejo del árbol. Sigue
entero en `PENDIENTES.md`, y aparece en su día si tiene fecha; aterrizarlo en
un ámbito es lo que lo hace aparecer acá.

**Qué lee y escribe:** lee `PENDIENTES.md` y el árbol `ambitos/`; escribe
`AHORA.md` y `ambitos/PENDIENTES-AMBITOS.md`.
**A mano:** copiar bajo cada día los pendientes con esa fecha, y mantener el
archivo de ámbitos con un callout por carpeta de `ambitos/`.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from tuku import scope, todo
from tuku.ahora import dias

#: Un registro de bitácora. Es la frontera inferior de la región del día.
_REGISTRO = re.compile(r"^- \d{2}:\d{2} - ")

ARCHIVO_AMBITOS = Path("ambitos") / "PENDIENTES-AMBITOS.md"

SIN_PENDIENTES = "SIN PENDIENTES"

_ENCABEZADO_AMBITOS = "---\ntype: Pending\n---\n\n# Pendientes por ámbito\n"


def linea_del_dia(fila: todo.Fila) -> str:
    """La fila, como línea de la región del día: `- [[ambito]] - detalle`."""
    if fila.ambito:
        return f"- [[{fila.ambito}]] - {fila.cuerpo}"
    return f"- {fila.cuerpo}"


def region_del_dia(filas: list[todo.Fila], dia: date) -> list[str]:
    """Las líneas propagadas de un día: las filas cuyo `Cuándo` es esa fecha.

    Una fila sin fecha no cae en ningún día: no tener fecha es el estado normal
    de un pendiente del ciclo en curso, no una fecha implícita de hoy.
    """
    marca = dia.isoformat()
    return [linea_del_dia(f) for f in filas if f.cuando.strip() == marca]


def _fin_de_seccion(lineas: list[str], ini: int) -> int:
    """Índice donde termina la sección del día que empieza en `ini`."""
    return next(
        (
            i
            for i in range(ini + 1, len(lineas))
            if lineas[i].startswith("## ") or lineas[i].strip() == "---"
        ),
        len(lineas),
    )


def propagar_ahora(ahora: str, pendientes: str) -> str:
    """`AHORA.md` con la región de cada día regenerada desde la tabla.

    Reemplaza la región entera, así que propagar dos veces no duplica ninguna
    línea. Un día cuyo encabezado no se puede fechar (el ciclo sin `from`/`to`
    resueltos) se deja intacto: sin fecha no hay nada que derivar.
    """
    todas = todo.filas(pendientes)
    lineas = ahora.splitlines()

    # De atrás hacia adelante: reemplazar una sección corre los índices de las
    # que vienen después, y los de `dias()` son sobre el texto original.
    for ini, _, fecha in reversed(dias(ahora)):
        if fecha is None:
            continue
        fin = _fin_de_seccion(lineas, ini)
        corte = next(
            (i for i in range(ini + 1, fin) if _REGISTRO.match(lineas[i])),
            fin,
        )
        resto = lineas[corte:fin] or [""]
        lineas[ini + 1 : fin] = [*region_del_dia(todas, fecha), *resto]

    texto = "\n".join(lineas)
    return texto + "\n" if ahora.endswith("\n") and not texto.endswith("\n") else texto


def display_name(nombre: str, pagina_texto: str | None = None) -> str:
    """Nombre legible de un ámbito para el callout."""
    if pagina_texto:
        for linea in pagina_texto.splitlines():
            if linea.startswith("# "):
                tit = linea.removeprefix("# ").strip()
                tit = re.sub(r"^(?:Ambito|Ámbito):\s*", "", tit, flags=re.IGNORECASE).strip()
                if tit:
                    return tit
    return nombre.replace("-", " ").title()


def callout(
    ambito: str,
    cuerpos: list[str],
    *,
    display_name: str | None = None,
) -> str:
    """El callout de un ámbito, con su ancla de bloque `^<ambito>`.

    El ancla existe siempre, con o sin pendientes: una transclusión que apunta a
    un ancla ausente falla en silencio, y ese es justo el modo de falla que este
    archivo elimina.
    """
    disp = display_name or ambito.replace("-", " ").title()
    lineas = [f"> [!todo] Pendientes en **{disp}** ^{ambito}"]
    lineas += [f"> - {c}" for c in cuerpos] or [f"> {SIN_PENDIENTES}"]
    return "\n".join(lineas)


def documento_ambitos(
    pendientes: str,
    ambitos: list[str],
    display_names: dict[str, str] | None = None,
) -> str:
    """`ambitos/PENDIENTES-AMBITOS.md` entero: un callout por ámbito, en orden."""
    nombres_display = display_names or {}
    por_ambito: dict[str, list[str]] = {nombre: [] for nombre in ambitos}
    for fila in todo.filas(pendientes):
        if fila.ambito in por_ambito:
            por_ambito[fila.ambito].append(fila.cuerpo)
    bloques = [
        callout(nombre, cuerpos, display_name=nombres_display.get(nombre))
        for nombre, cuerpos in por_ambito.items()
    ]
    if not bloques:
        return _ENCABEZADO_AMBITOS
    return _ENCABEZADO_AMBITOS + "\n" + "\n\n".join(bloques) + "\n"


def propagar(vault: Path) -> list[Path]:
    """Regenera las dos vistas del vault. Devuelve los archivos que cambiaron.

    Escribe solo lo que difiere: sobre un vault ya cuadrado no toca ningún
    archivo, y la lista vuelve vacía.
    """
    from tuku.config import archivo_vault

    pendientes = archivo_vault(vault, "PENDIENTES.md").read_text(encoding="utf-8")
    cambiados = []

    ruta_ahora = archivo_vault(vault, "AHORA.md")
    texto = propagar_ahora(ruta_ahora.read_text(encoding="utf-8"), pendientes)
    if texto != ruta_ahora.read_text(encoding="utf-8"):
        ruta_ahora.write_text(texto, encoding="utf-8")
        cambiados.append(ruta_ahora)

    ambitos_objs = scope.leer(vault)
    disp_map: dict[str, str] = {}
    for a in ambitos_objs:
        pag = a.directorio / f"{a.nombre}.md"
        texto_pag = pag.read_text(encoding="utf-8") if pag.is_file() else None
        disp_map[a.nombre] = display_name(a.nombre, texto_pag)

    ruta_ambitos = vault / ARCHIVO_AMBITOS
    documento = documento_ambitos(
        pendientes, [a.nombre for a in ambitos_objs], display_names=disp_map
    )
    previo = ruta_ambitos.read_text(encoding="utf-8") if ruta_ambitos.is_file() else None
    if documento != previo:
        ruta_ambitos.parent.mkdir(parents=True, exist_ok=True)
        ruta_ambitos.write_text(documento, encoding="utf-8")
        cambiados.append(ruta_ambitos)

    return cambiados
