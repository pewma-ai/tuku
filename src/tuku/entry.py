"""tuku entry create: coloca líneas de bitácora ya formadas en su día.

Fase 1 de `devel/epics.md`. No interpreta ni reformatea: recibe
líneas que ya cumplen `spec/bitacora.md` y las inserta bajo el encabezado del
día indicado, ordenadas por hora, sin reescribir ninguna que ya estuviera.

**Qué lee y escribe:** solo `AHORA.md`. Si toca `PENDIENTES.md`, el corte de
la fase está mal hecho.
**A mano:** escribir la línea bajo el `## <día>` que corresponde, en el lugar
que le toca por hora.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from tuku import archive, archivo, link
from tuku.plan import Change, State, apply
from tuku.resultado import Resultado

if TYPE_CHECKING:
    from tuku.todo_core import Marca

_HORA = re.compile(r"^- (\d{2}):(\d{2}) - ")


def _claves(lineas: list[str]) -> list[tuple[int, int]]:
    """La clave de orden de cada línea: su hora, o la del registro más antiguo que le sigue.

    Los registros van del más reciente al más antiguo, así que el siguiente es el
    inmediatamente más antiguo. Un registro sin hora queda donde está, y el
    registro nuevo con hora se ubica sobre el primero de hora igual o menor. Sin
    registro más antiguo, la clave es 00:00.
    """
    claves: list[tuple[int, int]] = []
    siguiente = (0, 0)
    for linea in reversed(lineas):
        m = _HORA.match(linea)
        if m is not None:
            siguiente = (int(m.group(1)), int(m.group(2)))
        claves.append(siguiente)
    return claves[::-1]


def _sin_links(linea: str) -> str:
    """La línea como se lee, con guion y espacio equivalentes."""
    return link.sin_links(linea).replace("-", " ").casefold()


def add(
    ahora: str, lineas: list[str], *, day: str = "", dia: str = "", fecha: date | None = None
) -> str:
    """Devuelve `AHORA.md` con `lineas` insertadas bajo el encabezado `day` o `dia`.

    Idempotente: una línea que ya está bajo ese día no se vuelve a escribir.

    `day`/`dia` es el encabezado del día, con o sin el `## ` inicial; si no existe
    se crea en su lugar, entre los días del más nuevo al más viejo, con el año de
    `fecha` o, sin ella, el que deja el encabezado más cerca del rango del
    frontmatter. Ningún día se rechaza por caer fuera de ese rango. Dentro del día
    el orden es por hora descendente: lo más reciente arriba. Un registro nuevo
    sin hora toma la hora del que quede inmediatamente debajo de él (el primero
    del día, es decir el más reciente) y entre claves iguales el nuevo queda
    arriba. Ninguna otra sección del archivo se toca.
    """
    valor_dia = day or dia
    encabezado = valor_dia if valor_dia.startswith("## ") else f"## {valor_dia}"
    src = ahora.splitlines()

    try:
        ini = next(i for i, linea in enumerate(src) if linea.strip() == encabezado)
    except StopIteration:
        from tuku.ahora import fecha_del_dia, insertar_dia, rango

        limites = rango(ahora)
        if limites is None:
            raise ValueError(f"no existe el encabezado {encabezado!r} en AHORA.md") from None
        f_nueva = fecha or fecha_del_dia(encabezado, *limites)
        if f_nueva is None:
            raise ValueError(f"el encabezado {encabezado!r} no es un día") from None
        src, ini = insertar_dia(src, f_nueva, limites)

    # La sección del día termina en el siguiente día o en el `---` que cierra el
    # ciclo. Sin ese segundo corte, escribir en el último día se lleva por delante
    # la marca de fin de ciclo, que no es una línea de registro y se descartaría.
    fin = next(
        (
            i
            for i in range(ini + 1, len(src))
            if src[i].startswith("## ") or src[i].strip() == "---"
        ),
        len(src),
    )
    seccion_previa = src[ini + 1 : fin]
    # Lo que va antes del primer registro (el callout de pendientes del día) se conserva.
    primero = next((i for i, x in enumerate(seccion_previa) if x.startswith("- ")), None)
    cabecera = seccion_previa[: primero if primero is not None else len(seccion_previa)]
    while cabecera and not cabecera[-1].strip():
        cabecera.pop()
    previas = [linea for linea in seccion_previa if linea.startswith("- ")]
    # Idempotencia (principio 9, y `DEVEL.md`): una línea idéntica bajo el mismo
    # día es el mismo registro escrito dos veces, no dos hechos. Dos hechos de
    # verdad difieren en algo, aunque sea la hora. Se compara sin links: una
    # mención que `tuku scope create` enlazó después sigue siendo el mismo hecho.
    for linea in lineas:
        if not linea.startswith("- "):
            raise ValueError(f"un registro empieza con '- ': {linea!r}")
    vistas = {_sin_links(p) for p in previas}
    nuevas = [x for linea in lineas if _sin_links(x := linea.rstrip("\n")) not in vistas]

    claves_previas = _claves(previas)
    tope = max(claves_previas, default=(0, 0))
    clave_nueva = [
        (int(m.group(1)), int(m.group(2))) if (m := _HORA.match(x)) else tope for x in nuevas
    ]
    # Descendente por hora; entre claves iguales, los nuevos antes que los que ya
    # estaban, y cada grupo en su orden.
    con_clave = [
        *((k, 1, i, x) for i, (k, x) in enumerate(zip(claves_previas, previas, strict=True))),
        *((k, 0, i, x) for i, (k, x) in enumerate(zip(clave_nueva, nuevas, strict=True))),
    ]
    ordenadas = [
        x for *_, x in sorted(con_clave, key=lambda t: ((-t[0][0], -t[0][1]), t[1], t[2]))
    ]
    seccion = [encabezado, *cabecera, *([""] if cabecera and ordenadas else []), *ordenadas, ""]

    texto = "\n".join([*src[:ini], *seccion, *src[fin:]])
    if ahora.endswith("\n") and not texto.endswith("\n"):
        texto += "\n"
    return texto


def stamp(logbook: str, lines: list[str], *, day: date) -> str | Resultado:
    """`AHORA.md` text with `lines` under `day`, or the rejection if they do not fit.

    `add` for the use cases: when `logbook` has no range to place the day, or a line
    is not a record, it returns the `Resultado` the command hands back as is.
    It does no I/O; the caller decides when to write.
    """
    from tuku.ahora import encabezado_de

    try:
        return add(logbook, lines, day=encabezado_de(day), fecha=day)
    except ValueError as e:
        return Resultado.rechazo(str(e))


def componer(
    *, hora: str, scope: str | None, body: str, rutas: Mapping[str, str] | None = None
) -> str:
    """La línea de bitácora a partir de sus campos.

    `- HH:MM - [ambito](ruta) **marca**: cuerpo`. Componerla es mecánico: la hora,
    el guion, el orden de los campos y el link del ámbito son formato, y no hay
    razón para pedírselos a quien dicta. Lo único que es juicio es la marca, y
    esa viaja dentro de `body`.

    La ruta del link es relativa a `AHORA.md`, donde vive la línea. `rutas`
    (`scope.rutas`) trae la de un ámbito anidado; sin ella se asume la plana.

    Un cierre se escribe siempre igual, `(Hecho): ~~cuerpo~~`, venga como venga
    en `body`: a quien dicta no le toca saber dónde va la tachadura.
    """
    from tuku import todo_core

    ambito = ""
    if scope:
        nombre = scope.strip().strip("[]")
        ambito = f"{link.enlace_ambito(nombre, 'AHORA.md', rutas)} "
    inicio = f"{hora} - " if hora else ""
    return f"- {inicio}{ambito}{todo_core.canonizar(body)}"


def plan_add(
    state: State,
    *,
    body: str,
    scope: str | None,
    day: date | None,
    hour: str | None,
    now: datetime,
) -> Change | Resultado:
    """The change of `tuku entry create`: one record in `AHORA.md`, or the rejection.

    Without `day` it is today; without `hour`, now if the day is today. A past day
    without `hour` stays without an hour, at the end of the day: the hour of now
    would be made up.
    """
    from tuku import scope_tree as ambitos
    from tuku import todo_core
    from tuku.ahora import encabezado_de

    today = now.date()
    if day is not None and day > today:
        return Resultado.rechazo(
            f"el {day.isoformat()} todavía no llega: un registro cuenta lo que ya pasó. "
            f"Si es un compromiso, ábrelo con `tuku todo open --due {day.isoformat()}`."
        )
    if scope:
        resolved = ambitos.resolve_scope(state.tree, scope)
        if isinstance(resolved, Resultado):
            return resolved
        scope = resolved

    when = day or today
    dia = encabezado_de(when)
    linea = componer(
        hora=hour or ("" if day is not None and day < today else now.strftime("%H:%M")),
        scope=scope,
        body=body,
        rutas=state.tree.paths,
    )
    marca = todo_core.parsear(linea)
    if marca is not None:
        return Resultado.rechazo(rechazo_de_marca(marca, scope=scope, day=day, hour=hour))
    placed = archive.stamp(
        state.logbook, state.history, [linea], day=when, today=today, weeks=state.weeks
    )
    if isinstance(placed, Resultado):
        return placed
    return Change(
        {"AHORA.md": placed.logbook, **placed.extra},
        f"{linea}\nen {dia.removeprefix('## ')}.",
        regenerate=("AHORA.md", *(("bitacoras/",) if placed.extra else ())),
    )


def add_al_vault(
    vault: Path,
    *,
    body: str,
    scope: str | None = None,
    day: date | None = None,
    hour: str | None = None,
    now: datetime,
) -> Resultado:
    """Escribe un registro en `AHORA.md` y propaga lo que se deriva de él.

    El caso de uso de `tuku entry create`. Un registro con marca de la ontología
    cerrada se rechaza antes de escribir: abrir y cerrar pendientes es de
    `tuku todo open` y `tuku todo close`, que escriben el registro y la fila
    juntos, y el rechazo nombra el comando exacto.

    Recibe los campos, no la línea: el encabezado `## Martes 11 de agosto` se
    calcula desde `2026-08-11`, y la línea se compone. Un registro por llamada.
    La decisión es de `plan_add`; acá solo se lee el vault y se aplica.
    """
    from tuku import scope_tree as ambitos
    from tuku.config import archivo_vault, semanas_de_archivo

    archive.archivar_en_vault(vault, now.date())
    state = State(
        ambitos.read_tree(vault),
        logbook=archivo.leer(archivo_vault(vault, "AHORA.md")),
        history=archive.read_history(vault),
        weeks=semanas_de_archivo(vault),
    )
    return apply(
        vault,
        plan_add(state, body=body, scope=scope, day=day, hour=hour, now=now),
        today=now.date(),
    )


def rechazo_de_marca(
    marca: Marca,
    *,
    scope: str | None = None,
    day: date | None = None,
    hour: str | None = None,
) -> str:
    """El mensaje que manda un `**pendiente**` o un `(Hecho)` a `tuku todo`.

    Nombra el comando entero, con los mismos campos, para que quien invoca
    solo tenga que correrlo.
    """
    from tuku import todo_core

    abre = marca.marca == todo_core.ABRE
    comando = todo_core.comando_de(marca.marca, marca.cuerpo, ambito=scope, day=day, hour=hour)
    que = "abre un pendiente" if abre else "cierra un pendiente"
    return (
        f"`{marca.marca}` {que}, y eso no lo escribe `tuku entry create`: "
        f"usa `{comando}`, que escribe el registro y la fila de "
        "`PENDIENTES.md` juntos."
    )


@dataclass(frozen=True)
class Registro:
    """Un registro de la bitácora y dónde está: su línea, su día y su hora."""

    linea: int
    dia: str
    hora: str
    ambito: str | None
    cuerpo: str


#: Un registro: `- HH:MM - [ámbito](ruta) cuerpo`. La hora falta en un registro de
#: un día pasado dicho sin hora (`spec/bitacora.md`), y el ámbito es opcional.
_REGISTRO = re.compile(
    rf"^- (?:(?P<hora>\d{{2}}:\d{{2}}) - )?(?:(?P<ambito>{link.ENLACE}) )?(?P<cuerpo>.*)$"
)


def registros(texto: str) -> list[Registro]:
    """Los registros de `AHORA.md` o de una bitácora, en el orden del archivo.

    En `AHORA.md` el más reciente va primero.

    Solo cuentan las líneas bajo un encabezado de día (`## Martes 25 de agosto`):
    el plan puede tener listas y no son registros.
    """
    from tuku.ahora import es_dia

    dia = ""
    salida: list[Registro] = []
    for n, linea in enumerate(texto.splitlines()):
        if linea.startswith("#"):
            dia = linea.removeprefix("## ").strip() if es_dia(linea) else ""
            continue
        if dia and (m := _REGISTRO.match(linea)):
            enlace = m.group("ambito")
            salida.append(
                Registro(
                    n,
                    dia,
                    m.group("hora") or "",
                    link.nombre_de(enlace) if enlace else None,
                    m.group("cuerpo"),
                )
            )
    return salida


def _comparable(texto: str) -> str:
    """Sin links, sin tildes, sin mayúsculas y con los espacios justos."""
    plano = unicodedata.normalize("NFKD", link.sin_links(texto).casefold())
    return " ".join("".join(c for c in plano if not unicodedata.combining(c)).split())


def ubicar(
    texto: str, fragmento: str, *, dia: str | None = None, hora: str | None = None
) -> Registro | None:
    """El registro más reciente cuyo cuerpo contiene `fragmento`, o `None`.

    El más reciente porque es el caso común: el autor dijo tres cosas a las 07:00 y
    "no era eso" habla de la última. `AHORA.md` va del más nuevo al más viejo, así
    que es el primero del archivo. Si el que se corrige es otro, un fragmento más
    largo lo distingue. `dia` (sin `## `) y `hora` acotan la búsqueda.
    """
    buscado = _comparable(fragmento)
    candidatos = [
        r
        for r in registros(texto)
        if buscado in _comparable(r.cuerpo)
        and (dia is None or r.dia == dia)
        and (hora is None or r.hora == hora)
    ]
    return candidatos[0] if candidatos else None


def _con_linea(texto: str, n: int, nueva: str) -> str:
    lineas = texto.splitlines(keepends=True)
    final = "\n" if lineas[n].endswith("\n") else ""
    lineas[n] = nueva + final
    return "".join(lineas)


def _linea(r: Registro, enlace: str | None) -> str:
    hora = f"{r.hora} - " if r.hora else ""
    ambito = f"{enlace} " if enlace else ""
    return f"- {hora}{ambito}{r.cuerpo}"


def _donde(r: Registro) -> str:
    return f"de las {r.hora} del {r.dia}" if r.hora else f"sin hora del {r.dia}"


def _no_calza(
    fragmento: str, archivo_nombre: str, dia: str | None, hora: str | None
) -> Resultado:
    acotado = f" del {dia}" if dia else ""
    acotado += f" a las {hora}" if hora else ""
    return Resultado.rechazo(
        f"ningún registro de {archivo_nombre}{acotado} contiene «{fragmento}». "
        "Pasa en --match un fragmento del cuerpo tal como está escrito."
    )


def actualizar_en_vault(
    vault: Path,
    *,
    match: str,
    body: str,
    day: date | None = None,
    hour: str | None = None,
    now: datetime | None = None,
) -> Resultado:
    """Corrige el cuerpo de un registro de `AHORA.md`, y lo que ese cuerpo sostiene.

    El caso de uso de `tuku entry update`. Un registro no es solo su línea: si
    lleva `**pendiente**`, su cuerpo es también la fila de `PENDIENTES.md`, y las
    dos tienen que decir lo mismo o el pendiente deja de poder cerrarse
    repitiendo su texto. La hora y el ámbito no se tocan; el ámbito lo cambia
    `tuku entry move`.
    """
    from tuku import regenerate, todo_core
    from tuku.ahora import encabezado_de
    from tuku.config import archivo_vault

    ahora_path = archivo_vault(vault, "AHORA.md")
    if not todo_core.canonizar(body):
        return Resultado.rechazo("falta el cuerpo corregido. Pasa --body con el texto nuevo.")
    if now is not None:
        archive.archivar_en_vault(vault, now.date())
    ruta = _fuente(vault, ahora_path, day)
    relativa = ruta.relative_to(vault).as_posix()
    body = link.rebasar(body, "AHORA.md", relativa)
    texto = archivo.leer(ruta)
    dia = encabezado_de(day).removeprefix("## ") if day else None
    r = ubicar(texto, match, dia=dia, hora=hour)
    if r is None:
        return _no_calza(match, relativa, dia, hour)
    # La marca (`**pendiente**:`) es de la ontología cerrada y la corrección no la
    # cambia: `--body` dice el texto, y el registro conserva lo que es.
    marca = "" if todo_core.prefijo_de_marca(body) else todo_core.prefijo_de_marca(r.cuerpo)
    cuerpo = todo_core.canonizar(marca + body)
    if r.cuerpo == cuerpo:
        return Resultado.hecho(f"el registro {_donde(r)} ya decía eso: nada que corregir.")

    original = texto.splitlines()[r.linea]
    prefijo = original[: len(original) - len(r.cuerpo)]
    archivo.escribir(ruta, _con_linea(texto, r.linea, prefijo + cuerpo))

    # La fila del pendiente lleva el mismo texto que el registro, sin la marca, y
    # se busca sin links: la bitácora puede llevar uno que la tabla no tiene.
    filas = 0
    pendientes_path = vault / "PENDIENTES.md"
    if pendientes_path.is_file():
        previa = todo_core.parsear(f"- 00:00 - {r.cuerpo}")
        nueva = todo_core.parsear(f"- 00:00 - {cuerpo}")
        if previa is not None and nueva is not None:
            tabla, hubo = todo_core.reemplazar_cuerpo(
                archivo.leer(pendientes_path), previa.cuerpo.strip(), nueva.cuerpo.strip()
            )
            if hubo:
                archivo.escribir(pendientes_path, tabla)
                filas = 1
    regenerate.rehacer(vault, [relativa, "PENDIENTES.md"], hoy=now.date() if now else None)

    detalle = " y su fila en PENDIENTES.md" if filas else ""
    return Resultado.hecho(f"corregí el registro {_donde(r)}{detalle}:\n{prefijo}{cuerpo}")


def _fuente(vault: Path, ahora: Path, dia: date | None) -> Path:
    """The file where the record of `dia` lives: `AHORA.md`, or the logbook that covers it.

    A day `AHORA.md` has stays there; one it does not goes to the logbook (either name
    style) whose `from`-`to` contains it, if any.
    """
    from tuku.ahora import encabezado_de

    if dia is None:
        return ahora
    encabezado = encabezado_de(dia)
    if any(x.strip() == encabezado for x in archivo.leer(ahora).splitlines()):
        return ahora
    return _bitacora_de(vault, dia) or ahora


def _bitacora_de(vault: Path, dia: date) -> Path | None:
    """La bitácora cerrada cuyo `from`–`to` contiene `dia`."""
    from tuku.ahora import rango

    for ruta in sorted((vault / "bitacoras").glob("*.md")):
        limites = rango(archivo.leer(ruta))
        if limites is not None and limites[0] <= dia <= limites[1]:
            return ruta
    return None


def mover_en_vault(
    vault: Path,
    *,
    match: str,
    scope: str,
    day: date | None = None,
    hour: str | None = None,
    now: datetime | None = None,
) -> Resultado:
    """Cambia el ámbito de un registro, en `AHORA.md` o en un ciclo cerrado.

    El caso de uso de `tuku entry move`. Sirve para lo escrito antes de abrir un
    ámbito (`spec/ambitos.md`): el registro pasa al ámbito nuevo con su cuerpo
    intacto. Un ciclo cerrado admite la corrección. Si el registro es un
    pendiente abierto, su fila en `PENDIENTES.md` cambia de ámbito con él.
    """
    from tuku import regenerate, todo_core
    from tuku import scope_tree as ambitos
    from tuku.ahora import encabezado_de, rango
    from tuku.config import archivo_vault

    tree = ambitos.read_tree(vault)
    resolved = ambitos.resolve_scope(tree, scope)
    if isinstance(resolved, Resultado):
        return resolved
    nombre = resolved

    if now is not None:
        archive.archivar_en_vault(vault, now.date())
    ruta = archivo_vault(vault, "AHORA.md")
    if day is not None:
        ruta = _fuente(vault, ruta, day)
        limites = rango(archivo.leer(ruta))
        if ruta.name == "AHORA.md" and (limites is None or not limites[0] <= day <= limites[1]):
            return Resultado.rechazo(
                f"ni AHORA.md ni ninguna bitácora de bitacoras/ cubre el "
                f"{day.isoformat()}. Revisa la fecha de CUÁNDO."
            )
    relativa = ruta.relative_to(vault).as_posix()
    texto = archivo.leer(ruta)
    dia = encabezado_de(day).removeprefix("## ") if day else None
    r = ubicar(texto, match, dia=dia, hora=hour)
    if r is None:
        return _no_calza(match, relativa, dia, hour)
    if r.ambito == nombre:
        return Resultado.hecho(f"el registro {_donde(r)} ya era de {nombre}: nada que mover.")

    nueva = _linea(r, link.enlace_ambito(nombre, relativa, tree.paths))
    archivo.escribir(ruta, _con_linea(texto, r.linea, nueva))

    filas = 0
    pendientes_path = vault / "PENDIENTES.md"
    marca = todo_core.parsear(nueva)
    if pendientes_path.is_file() and marca is not None and marca.marca == todo_core.ABRE:
        tabla, hubo = todo_core.cambiar_ambito(
            archivo.leer(pendientes_path), marca.cuerpo, nombre, tree.paths
        )
        if hubo:
            archivo.escribir(pendientes_path, tabla)
            filas = 1
    regenerate.rehacer(vault, [relativa, "PENDIENTES.md"], hoy=now.date() if now else None)

    detalle = " y su fila en PENDIENTES.md" if filas else ""
    return Resultado.hecho(f"moví el registro {_donde(r)} a {nombre}{detalle}:\n{nueva}")
