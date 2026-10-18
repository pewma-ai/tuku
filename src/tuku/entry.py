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

from tuku import archivo, link
from tuku.resultado import Resultado

if TYPE_CHECKING:
    from tuku.todo import Marca

_HORA = re.compile(r"^- (\d{2}):(\d{2}) - ")

#: Un registro sin hora va al final de su día (`spec/bitacora.md`).
_AL_FINAL = (24, 0)


def _claves(lineas: list[str], *, nuevas: bool = False) -> list[tuple[int, int]]:
    """La clave de orden de cada línea: su hora, o la del registro anterior si no tiene.

    Así un registro sin hora queda donde está, y el siguiente que llega con hora
    se ubica a continuación si su hora es igual o mayor. Uno nuevo sin hora va al
    final del día.
    """
    claves: list[tuple[int, int]] = []
    previa = (0, 0)
    for linea in lineas:
        m = _HORA.match(linea)
        if m is not None:
            previa = (int(m.group(1)), int(m.group(2)))
        elif nuevas:
            previa = _AL_FINAL
        claves.append(previa)
    return claves


def _sin_links(linea: str) -> str:
    """La línea como se lee, con guion y espacio equivalentes."""
    return link.sin_links(linea).replace("-", " ").casefold()


def add(ahora: str, lineas: list[str], *, day: str = "", dia: str = "") -> str:
    """Devuelve `AHORA.md` con `lineas` insertadas bajo el encabezado `day` o `dia`.

    Idempotente: una línea que ya está bajo ese día no se vuelve a escribir.

    `day`/`dia` es el encabezado del día, con o sin el `## ` inicial. Las líneas
    nuevas se copian tal cual llegan; el orden final es por hora, y en empate
    las que ya estaban van antes que las nuevas (sort estable). Ninguna otra
    sección del archivo se toca.
    """
    valor_dia = day or dia
    encabezado = valor_dia if valor_dia.startswith("## ") else f"## {valor_dia}"
    src = ahora.splitlines()

    try:
        ini = next(i for i, linea in enumerate(src) if linea.strip() == encabezado)
    except StopIteration:
        from tuku.ahora import como_cerrar, fecha_del_dia, rango

        limites = rango(ahora)
        if limites is not None:
            desde, hasta = limites
            f_nueva = fecha_del_dia(encabezado, desde, hasta)
            if f_nueva is not None and desde <= f_nueva <= hasta:
                insert_idx = len(src)
                for i, linea in enumerate(src):
                    if linea.startswith("## "):
                        f_existente = fecha_del_dia(linea, desde, hasta)
                        if f_existente is not None and f_existente > f_nueva:
                            insert_idx = i
                            break
                src = [*src[:insert_idx], encabezado, "", *src[insert_idx:]]
                ini = insert_idx
            else:
                msg = (
                    f"el día {encabezado!r} cae fuera del ciclo abierto "
                    f"({desde.isoformat()} a {hasta.isoformat()}). Si el registro es "
                    f"de este ciclo, corrige la fecha; si empezó uno nuevo, cierra "
                    f"este antes: {como_cerrar(desde, hasta)}, y corre "
                    "`tuku process cycle`."
                )
                raise ValueError(msg) from None
        else:
            raise ValueError(f"no existe el encabezado {encabezado!r} en AHORA.md") from None

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
    previas = [linea for linea in src[ini + 1 : fin] if linea.startswith("- ")]
    # Idempotencia (principio 9, y `DEVEL.md`): una línea idéntica bajo el mismo
    # día es el mismo registro escrito dos veces, no dos hechos. Dos hechos de
    # verdad difieren en algo, aunque sea la hora. Se compara sin links: una
    # mención que `tuku scope create` enlazó después sigue siendo el mismo hecho.
    for linea in lineas:
        if not linea.startswith("- "):
            raise ValueError(f"un registro empieza con '- ': {linea!r}")
    vistas = {_sin_links(p) for p in previas}
    nuevas = [x for linea in lineas if _sin_links(x := linea.rstrip("\n")) not in vistas]

    con_clave = [
        *zip(_claves(previas), previas, strict=True),
        *zip(_claves(nuevas, nuevas=True), nuevas, strict=True),
    ]
    ordenadas = [linea for _, linea in sorted(con_clave, key=lambda par: par[0])]
    seccion = [encabezado, *ordenadas, ""]

    texto = "\n".join([*src[:ini], *seccion, *src[fin:]])
    if ahora.endswith("\n") and not texto.endswith("\n"):
        texto += "\n"
    return texto


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
    from tuku import todo

    ambito = ""
    if scope:
        nombre = scope.strip().strip("[]")
        ambito = f"{link.enlace_ambito(nombre, 'AHORA.md', rutas)} "
    inicio = f"{hora} - " if hora else ""
    return f"- {inicio}{ambito}{todo.canonizar(body)}"


def add_al_vault(
    vault: Path,
    *,
    body: str,
    scope: str | None = None,
    day: date | None = None,
    hour: str | None = None,
) -> Resultado:
    """Escribe un registro en `AHORA.md` y propaga lo que se deriva de él.

    El caso de uso de `tuku entry create`. Un registro con marca de la ontología
    cerrada se rechaza antes de escribir: abrir y cerrar pendientes es de
    `tuku todo open` y `tuku todo close`, que escriben el registro y la fila
    juntos, y el rechazo nombra el comando exacto.

    Recibe los campos, no la línea: el encabezado `## Martes 11 de agosto` se
    calcula desde `2026-08-11`, y la línea se compone. Un registro por llamada.

    Sin `day` es hoy; sin `hour`, ahora si el día es hoy. Un día pasado sin `hour`
    queda sin hora, al final del día: la de ahora sería inventada.
    """
    from tuku import scope as ambitos
    from tuku import todo
    from tuku.ahora import encabezado_de
    from tuku.config import archivo_vault

    if day is not None and day > date.today():
        return Resultado.rechazo(
            f"el {day.isoformat()} todavía no llega: un registro cuenta lo que ya pasó. "
            f"Si es un compromiso, ábrelo con `tuku todo open --due {day.isoformat()}`."
        )
    if scope:
        scope = ambitos.canonico(vault, scope)
        if (rechazo := ambitos.rechazo_si_no_existe(vault, scope)) is not None:
            return rechazo

    ruta = archivo_vault(vault, "AHORA.md")
    dia = encabezado_de(day or date.today())
    linea = componer(
        hora=hour
        or ("" if day is not None and day < date.today() else datetime.now().strftime("%H:%M")),
        scope=scope,
        body=body,
        rutas=ambitos.rutas(vault),
    )
    marca = todo.parsear(linea)
    if marca is not None:
        return Resultado.rechazo(rechazo_de_marca(marca, scope=scope, day=day, hour=hour))
    try:
        texto = add(archivo.leer(ruta), [linea], day=dia)
    except ValueError as e:
        return Resultado.rechazo(str(e))

    archivo.escribir(ruta, texto)

    from tuku import regenerate

    regenerate.rehacer(vault, ["AHORA.md"])
    return Resultado.hecho(f"{linea}\nen {dia.removeprefix('## ')}.")


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
    from tuku import todo

    abre = marca.marca == todo.ABRE
    comando = todo.comando_de(marca.marca, marca.cuerpo, ambito=scope, day=day, hour=hour)
    que = "abre un pendiente" if abre else "cierra un pendiente"
    return (
        f"`{marca.marca}` {que}, y eso no lo escribe `tuku entry create`: "
        f"usa `{comando}`, que escribe el registro y la fila de "
        "`PENDIENTES.md` juntos."
    )


def lint_del_vault(vault: Path) -> Resultado:
    """Revisa los registros de `AHORA.md` y reporta; no escribe.

    Solo la ontología cerrada mueve el resultado a rechazo: un tipo abierto que
    nadie declaró es una pregunta sobre el vocabulario del autor, no un error
    (`spec/bitacora.md`).
    """
    from tuku.config import archivo_vault, leer_config
    from tuku.lint import ERROR, formatear
    from tuku.lint import lint as lint_registros

    ahora = archivo.leer(archivo_vault(vault, "AHORA.md"))
    hallazgos = lint_registros(ahora, abiertos=leer_config(vault).vocabularios_abiertos())
    mensaje = formatear(hallazgos)
    if any(h.grado == ERROR for h in hallazgos):
        return Resultado.rechazo(mensaje, error=False)
    return Resultado.hecho(mensaje)


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
    """El último registro cuyo cuerpo contiene `fragmento`, o `None`.

    El último porque es el caso común: el autor dijo tres cosas a las 07:00 y
    "no era eso" habla de la última. Si el que se corrige es otro, un fragmento
    más largo lo distingue. `dia` (sin `## `) y `hora` acotan la búsqueda.
    """
    buscado = _comparable(fragmento)
    candidatos = [
        r
        for r in registros(texto)
        if buscado in _comparable(r.cuerpo)
        and (dia is None or r.dia == dia)
        and (hora is None or r.hora == hora)
    ]
    return candidatos[-1] if candidatos else None


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
    vault: Path, *, match: str, body: str, day: date | None = None, hour: str | None = None
) -> Resultado:
    """Corrige el cuerpo de un registro de `AHORA.md`, y lo que ese cuerpo sostiene.

    El caso de uso de `tuku entry update`. Un registro no es solo su línea: si
    lleva `**pendiente**`, su cuerpo es también la fila de `PENDIENTES.md`, y las
    dos tienen que decir lo mismo o el pendiente deja de poder cerrarse
    repitiendo su texto. La hora y el ámbito no se tocan; el ámbito lo cambia
    `tuku entry move`.
    """
    from tuku import regenerate, todo
    from tuku.ahora import encabezado_de, rango
    from tuku.config import archivo_vault

    ahora_path = archivo_vault(vault, "AHORA.md")
    if not todo.canonizar(body):
        return Resultado.rechazo("falta el cuerpo corregido. Pasa --body con el texto nuevo.")
    texto = archivo.leer(ahora_path)
    limites = rango(texto)
    if day is not None and limites is not None and not limites[0] <= day <= limites[1]:
        return Resultado.rechazo(
            f"el {day.isoformat()} no está en el ciclo en curso, y `entry update` corrige "
            "solo AHORA.md. Un registro de un ciclo cerrado se corrige a mano en bitacoras/."
        )
    dia = encabezado_de(day).removeprefix("## ") if day else None
    r = ubicar(texto, match, dia=dia, hora=hour)
    if r is None:
        return _no_calza(match, "AHORA.md", dia, hour)
    # La marca (`**pendiente**:`) es de la ontología cerrada y la corrección no la
    # cambia: `--body` dice el texto, y el registro conserva lo que es.
    marca = "" if todo.prefijo_de_marca(body) else todo.prefijo_de_marca(r.cuerpo)
    cuerpo = todo.canonizar(marca + body)
    if r.cuerpo == cuerpo:
        return Resultado.hecho(f"el registro {_donde(r)} ya decía eso: nada que corregir.")

    original = texto.splitlines()[r.linea]
    prefijo = original[: len(original) - len(r.cuerpo)]
    archivo.escribir(ahora_path, _con_linea(texto, r.linea, prefijo + cuerpo))

    # La fila del pendiente lleva el mismo texto que el registro, sin la marca, y
    # se busca sin links: la bitácora puede llevar uno que la tabla no tiene.
    filas = 0
    pendientes_path = vault / "PENDIENTES.md"
    if pendientes_path.is_file():
        previa = todo.parsear(f"- 00:00 - {r.cuerpo}")
        nueva = todo.parsear(f"- 00:00 - {cuerpo}")
        if previa is not None and nueva is not None:
            tabla, hubo = todo.reemplazar_cuerpo(
                archivo.leer(pendientes_path), previa.cuerpo.strip(), nueva.cuerpo.strip()
            )
            if hubo:
                archivo.escribir(pendientes_path, tabla)
                filas = 1
    regenerate.rehacer(vault, ["AHORA.md", "PENDIENTES.md"])

    detalle = " y su fila en PENDIENTES.md" if filas else ""
    return Resultado.hecho(f"corregí el registro {_donde(r)}{detalle}:\n{prefijo}{cuerpo}")


def _bitacora_de(vault: Path, dia: date) -> Path | None:
    """La bitácora cerrada cuyo `from`–`to` contiene `dia`."""
    from tuku.ahora import rango

    for ruta in sorted((vault / "bitacoras").glob("*.md")):
        limites = rango(archivo.leer(ruta))
        if limites is not None and limites[0] <= dia <= limites[1]:
            return ruta
    return None


def mover_en_vault(
    vault: Path, *, match: str, scope: str, day: date | None = None, hour: str | None = None
) -> Resultado:
    """Cambia el ámbito de un registro, en `AHORA.md` o en un ciclo cerrado.

    El caso de uso de `tuku entry move`. Sirve para lo escrito antes de abrir un
    ámbito (`spec/ambitos.md`): el registro pasa al ámbito nuevo con su cuerpo
    intacto. Un ciclo cerrado admite la corrección. Si el registro es un
    pendiente abierto, su fila en `PENDIENTES.md` cambia de ámbito con él.
    """
    from tuku import regenerate, todo
    from tuku import scope as ambitos
    from tuku.ahora import encabezado_de, rango
    from tuku.config import archivo_vault

    nombre = ambitos.canonico(vault, scope)
    if (rechazo := ambitos.rechazo_si_no_existe(vault, nombre)) is not None:
        return rechazo

    ruta = archivo_vault(vault, "AHORA.md")
    if day is not None:
        limites = rango(archivo.leer(ruta))
        if limites is None or not limites[0] <= day <= limites[1]:
            cerrada = _bitacora_de(vault, day)
            if cerrada is None:
                return Resultado.rechazo(
                    f"ni AHORA.md ni ninguna bitácora de bitacoras/ cubre el "
                    f"{day.isoformat()}. Revisa la fecha de CUÁNDO."
                )
            ruta = cerrada
    relativa = ruta.relative_to(vault).as_posix()
    texto = archivo.leer(ruta)
    dia = encabezado_de(day).removeprefix("## ") if day else None
    r = ubicar(texto, match, dia=dia, hora=hour)
    if r is None:
        return _no_calza(match, relativa, dia, hour)
    if r.ambito == nombre:
        return Resultado.hecho(f"el registro {_donde(r)} ya era de {nombre}: nada que mover.")

    rutas = ambitos.rutas(vault)
    nueva = _linea(r, link.enlace_ambito(nombre, relativa, rutas))
    archivo.escribir(ruta, _con_linea(texto, r.linea, nueva))

    filas = 0
    pendientes_path = vault / "PENDIENTES.md"
    marca = todo.parsear(nueva)
    if pendientes_path.is_file() and marca is not None and marca.marca == todo.ABRE:
        tabla, hubo = todo.cambiar_ambito(
            archivo.leer(pendientes_path), marca.cuerpo, nombre, rutas
        )
        if hubo:
            archivo.escribir(pendientes_path, tabla)
            filas = 1
    regenerate.rehacer(vault, [relativa, "PENDIENTES.md"])

    detalle = " y su fila en PENDIENTES.md" if filas else ""
    return Resultado.hecho(f"moví el registro {_donde(r)} a {nombre}{detalle}:\n{nueva}")
