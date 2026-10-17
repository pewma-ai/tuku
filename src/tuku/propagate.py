"""Las dos vistas derivadas de `PENDIENTES.md`, que regenera `tuku regenerate todo`.

`PENDIENTES.md` es fuente de verdad y nada más lo es (`spec/pendientes.md`).
Todo lo que muestre un pendiente fuera de él es derivado, y se **regenera** en
vez de repararse: propagar es una función pura de la tabla contra su salida, y
por eso correrlo dos veces da el mismo texto y sobre un vault cuadrado no
cambia ningún archivo.

Las dos vistas:

| Vista | Dónde | Qué contiene |
| --- | --- | --- |
| El día | La región del día en `AHORA.md` | Las filas cuyo `Vence` cae en ese día |
| El ámbito | `ambitos/PENDIENTES-AMBITOS.md` | Un callout por ámbito del árbol |

**La región del día** es lo que va entre el encabezado `## <día>` y el primer
registro. No lleva marca que la delimite: los registros empiezan siempre por
`- HH:MM - `, así que la frontera es estructura visible. El comando es su dueño
y al regenerar la reemplaza entera, prosa suelta incluida.

**El archivo por ámbito** es generado, no un reporte: los reportes llevan fecha
en el nombre y este no, porque siempre dice el estado de ahora. Tiene un callout
por cada ámbito que exista en `ambitos/`, tenga pendientes o no, y el que no
tiene queda solo con su título. Que el callout exista siempre es el punto: la
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
from collections.abc import Mapping
from datetime import date
from pathlib import Path

from tuku import link, scope, todo
from tuku.ahora import dias
from tuku.config import FORMATO_FECHA, fecha_corta, formato_fecha

#: Un registro de bitácora. Es la frontera inferior de la región del día.
_REGISTRO = re.compile(r"^- \d{2}:\d{2} - ")

ARCHIVO_AMBITOS = Path("ambitos") / "PENDIENTES-AMBITOS.md"

_ENCABEZADO_AMBITOS = (
    "---\n"
    "type: Derived\n"
    "origin: PENDIENTES.md\n"
    "command: tuku regenerate todo\n"
    "---\n\n"
    "# Pendientes por ámbito\n\n"
    "> [!warning] Vista derivada\n"
    "> No modificar este archivo directamente. Los cambios se realizan en "
    "[PENDIENTES.md](../PENDIENTES.md) y se reflejan aquí mediante propagación automática.\n"
)


def linea_del_dia(fila: todo.Fila, rutas: Mapping[str, str] | None = None) -> str:
    """La fila, como línea de la región del día: `- [ambito](ruta) - detalle`.

    La región vive en `AHORA.md`, así que la ruta es relativa a ese archivo.
    """
    hora = f"{fila.hora} - " if fila.hora else ""
    if fila.ambito:
        return f"- {hora}{link.enlace_ambito(fila.ambito, 'AHORA.md', rutas)} - {fila.cuerpo}"
    return f"- {hora}{fila.cuerpo}"


def region_del_dia(
    filas: list[todo.Fila], dia: date, rutas: Mapping[str, str] | None = None
) -> list[str]:
    """Las líneas propagadas de un día: callout `[!todo] Pendientes del día` si hay pendientes.

    Una fila sin fecha no cae en ningún día: no tener fecha es el estado normal
    de un pendiente del ciclo en curso, no una fecha implícita de hoy.
    """
    items = [linea_del_dia(f, rutas) for f in filas if f.dia == dia]
    if not items:
        return []
    return [
        "> [!todo] Pendientes del día",
        *(f"> {item}" for item in items),
    ]


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


def propagar_ahora(
    ahora: str, pendientes: str, rutas: Mapping[str, str] | None = None
) -> str:
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
        resto = lineas[corte:fin]
        callout_lineas = region_del_dia(todas, fecha, rutas)
        if callout_lineas:
            lineas[ini + 1 : fin] = [*callout_lineas, "", *resto]
        else:
            lineas[ini + 1 : fin] = resto or [""]

    texto = "\n".join(lineas)
    return texto + "\n" if ahora.endswith("\n") and not texto.endswith("\n") else texto


def display_name(nombre: str, pagina_texto: str | None = None) -> str:
    """Nombre legible de un ámbito para el callout."""
    if pagina_texto:
        for linea in pagina_texto.splitlines():
            if linea.startswith("# "):
                tit = linea.removeprefix("# ").strip()
                tit = re.sub(r"^(?:Ambito|Ámbito):\s*", "", tit, flags=re.IGNORECASE).strip()
                if tit and tit != nombre:
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
    archivo elimina. Un ámbito sin pendientes lleva solo el título.
    """
    disp = display_name or ambito.replace("-", " ").title()
    lineas = [f"> [!todo] Pendientes en **{disp}** ^{ambito}"]
    lineas += [f"> - {c}" for c in cuerpos]
    return "\n".join(lineas)


def _orden_en_el_ambito(fila: todo.Fila) -> tuple[int, str]:
    return (0, fila.vence) if fila.dia else (1, "")


def linea_del_ambito(fila: todo.Fila, formato: str = FORMATO_FECHA) -> str:
    """La fila, como línea del callout de su ámbito: `<fecha> - detalle`, o solo el detalle.

    La fecha va con el `date_format` del vault y el ámbito no va, porque el
    callout ya es el del ámbito. El detalle se escribió para `PENDIENTES.md`
    y el callout vive en `ambitos/`, así que sus links se rebasan.
    """
    cuerpo = link.rebasar(fila.cuerpo, "PENDIENTES.md", str(ARCHIVO_AMBITOS.as_posix()))
    fecha = fila.dia
    vence = fecha_corta(fecha, formato) if fecha else fila.vence.strip()
    if fecha and fila.hora:
        vence = f"{vence} {fila.hora}"
    return f"{vence} - {cuerpo}" if vence else cuerpo


def documento_ambitos(
    pendientes: str,
    ambitos: list[str],
    display_names: dict[str, str] | None = None,
    formato: str = FORMATO_FECHA,
) -> str:
    """`ambitos/PENDIENTES-AMBITOS.md` entero: un callout por ámbito, en orden.

    Dentro de cada callout van primero los pendientes con fecha, de la más
    próxima a la más lejana, y después los demás en el orden de la tabla.
    """
    nombres_display = display_names or {}
    por_ambito: dict[str, list[todo.Fila]] = {nombre: [] for nombre in ambitos}
    for fila in todo.filas(pendientes):
        if fila.ambito in por_ambito:
            por_ambito[fila.ambito].append(fila)
    bloques = [
        callout(
            nombre,
            [linea_del_ambito(f, formato) for f in sorted(filas_, key=_orden_en_el_ambito)],
            display_name=nombres_display.get(nombre),
        )
        for nombre, filas_ in por_ambito.items()
    ]
    if not bloques:
        return _ENCABEZADO_AMBITOS
    return _ENCABEZADO_AMBITOS + "\n" + "\n\n".join(bloques) + "\n"


def documento_del_vault(vault: Path, pendientes: str) -> str:
    """El `ambitos/PENDIENTES-AMBITOS.md` que corresponde al árbol y a la tabla."""
    ambitos_objs = scope.leer(vault)
    raiz = vault / "ambitos"

    def titulo(directorio: Path) -> str:
        pag = directorio / f"{directorio.name}.md"
        return display_name(
            directorio.name, pag.read_text(encoding="utf-8") if pag.is_file() else None
        )

    def camino(directorio: Path) -> str:
        partes = directorio.relative_to(raiz).parts
        return " / ".join(titulo(raiz.joinpath(*partes[: i + 1])) for i in range(len(partes)))

    # Un ámbito anidado lleva en el título el camino hasta él: `Faena / Faena Ai`.
    disp_map = {a.nombre: camino(a.directorio) for a in ambitos_objs}
    return documento_ambitos(
        pendientes,
        [a.nombre for a in ambitos_objs],
        display_names=disp_map,
        formato=formato_fecha(vault),
    )


def propagar(vault: Path, *, vistas: bool = True, paginas: bool = True) -> list[Path]:
    """Regenera lo derivado del vault. Devuelve los archivos que cambiaron.

    Escribe solo lo que difiere: sobre un vault ya cuadrado no toca ningún
    archivo, y la lista vuelve vacía. Con `vistas`, las dos vistas de
    `PENDIENTES.md`. Con `paginas`, la actividad de cada página de ámbito, que
    se deriva de `AHORA.md`.
    """
    from tuku.config import archivo_vault

    cambiados: list[Path] = []

    if vistas:
        pendientes = archivo_vault(vault, "PENDIENTES.md").read_text(encoding="utf-8")
        ruta_ahora = archivo_vault(vault, "AHORA.md")
        texto = propagar_ahora(
            ruta_ahora.read_text(encoding="utf-8"), pendientes, scope.rutas(vault)
        )
        if texto != ruta_ahora.read_text(encoding="utf-8"):
            ruta_ahora.write_text(texto, encoding="utf-8")
            cambiados.append(ruta_ahora)

    for a in scope.leer(vault) if paginas else []:
        pag_mod = scope.actualizar_pagina(vault, a.nombre)
        if pag_mod and pag_mod not in cambiados:
            cambiados.append(pag_mod)

    if vistas:
        ruta_ambitos = vault / ARCHIVO_AMBITOS
        documento = documento_del_vault(vault, pendientes)
        previo = ruta_ambitos.read_text(encoding="utf-8") if ruta_ambitos.is_file() else None
        if documento != previo:
            ruta_ambitos.parent.mkdir(parents=True, exist_ok=True)
            ruta_ambitos.write_text(documento, encoding="utf-8")
            cambiados.append(ruta_ambitos)

    return cambiados
