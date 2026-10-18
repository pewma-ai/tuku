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
from collections.abc import Mapping
from datetime import date, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from tuku import link
from tuku.resultado import Resultado

if TYPE_CHECKING:
    from tuku.todo import Marca

_HORA = re.compile(r"^- (\d{2}):(\d{2}) - ")


def _clave_hora(linea: str) -> tuple[int, int]:
    m = _HORA.match(linea)
    if m is None:
        raise ValueError(f"la línea no empieza con '- HH:MM - ': {linea!r}")
    return int(m.group(1)), int(m.group(2))


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
        from tuku.ahora import fecha_del_dia, rango

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
                    f"este antes: mueve AHORA.md a bitacoras/bitacora-"
                    f"{desde.isoformat()}-{hasta.isoformat()}.md y corre "
                    f"`tuku cycle open`."
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
    previas = [linea for linea in src[ini + 1 : fin] if _HORA.match(linea)]
    # Idempotencia (principio 9, y `DEVEL.md`): una línea idéntica bajo el mismo
    # día es el mismo registro escrito dos veces, no dos hechos. Dos hechos de
    # verdad difieren en algo, aunque sea la hora. Se compara sin links: una
    # mención que `tuku scope create` enlazó después sigue siendo el mismo hecho.
    vistas = {_sin_links(p) for p in previas}
    nuevas = [x for linea in lineas if _sin_links(x := linea.rstrip("\n")) not in vistas]

    ordenadas = sorted([*previas, *nuevas], key=_clave_hora)
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
    return f"- {hora} - {ambito}{todo.canonizar(body)}"


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

    Sin `day` es hoy; sin `hour`, ahora.
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
        hora=hour or datetime.now().strftime("%H:%M"),
        scope=scope,
        body=body,
        rutas=ambitos.rutas(vault),
    )
    marca = todo.parsear(linea)
    if marca is not None:
        return Resultado.rechazo(rechazo_de_marca(marca, scope=scope, day=day, hour=hour))
    try:
        texto = add(ruta.read_text(encoding="utf-8"), [linea], day=dia)
    except ValueError as e:
        return Resultado.rechazo(str(e))

    ruta.write_text(texto, encoding="utf-8")

    for ambito in ambitos.leer(vault):
        ambitos.actualizar_pagina(vault, ambito.nombre)
    from tuku.propagate import propagar

    propagar(vault)
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

    ahora = archivo_vault(vault, "AHORA.md").read_text(encoding="utf-8")
    hallazgos = lint_registros(ahora, abiertos=leer_config(vault).vocabularios_abiertos())
    mensaje = formatear(hallazgos)
    if any(h.grado == ERROR for h in hallazgos):
        return Resultado.rechazo(mensaje, error=False)
    return Resultado.hecho(mensaje)


def corregir_en_vault(
    vault: Path, *, body: str, day: date | None = None, hour: str = ""
) -> Resultado:
    """Corrige el cuerpo de un registro ya escrito, y lo que ese cuerpo sostiene.

    El caso de uso de `tuku entry rename`. Existe porque un registro no es solo
    su línea: si llevaba `**pendiente**`, su cuerpo es también la fila de
    `PENDIENTES.md`, y las dos tienen que decir lo mismo carácter por carácter o
    el pendiente deja de poder cerrarse repitiendo su texto.

    Corregir a mano es exactamente donde eso se rompe, porque la línea está a la
    vista y la fila no.

    La hora y el ámbito no se tocan: los fija `tuku entry create`, y cambiarlos acá
    sería reescribir un hecho en vez de corregir cómo quedó dicho.
    """
    from tuku import ahora as ahora_mod
    from tuku import propagate, rename, todo

    ahora_path = vault / "AHORA.md"
    if not ahora_path.is_file():
        return Resultado.rechazo(f"no encuentro AHORA.md en {vault}. ¿Es un vault de TUKU?")
    cuerpo = todo.canonizar(body)
    if not cuerpo:
        return Resultado.rechazo("falta el cuerpo corregido. Pasa --body con el texto nuevo.")

    texto = ahora_path.read_text(encoding="utf-8")
    encabezado = ahora_mod.encabezado_de(day or date.today())
    previo = rename.cuerpo_del_registro(texto, encabezado, hour)
    if previo is None:
        return Resultado.rechazo(
            f"no hay ningún registro a las {hour} en "
            f"'{encabezado}'. Mira AHORA.md y confirma el día y la hora."
        )
    if previo == cuerpo:
        return Resultado.hecho("el registro ya decía eso: nada que corregir.")

    salida, _ = rename.corregir_registro(texto, encabezado, hour, cuerpo)
    ahora_path.write_text(salida, encoding="utf-8")

    # La fila del pendiente lleva el mismo texto que el registro, sin la marca.
    # Si el cuerpo viejo estaba en la tabla, la corrección va también ahí.
    filas = 0
    pendientes_path = vault / "PENDIENTES.md"
    if pendientes_path.is_file():
        tabla = pendientes_path.read_text(encoding="utf-8")
        # La tabla guarda el cuerpo sin la marca, y quien sabe separarlos es
        # `todo.parsear`, que trabaja sobre la línea entera: se la compone.
        marca_previa = todo.parsear(f"- {hour} - {previo}")
        marca_nueva = todo.parsear(f"- {hour} - {cuerpo}")
        if marca_previa is not None and marca_nueva is not None:
            # La fila se busca sin links: la bitácora puede llevar uno que la
            # tabla no tiene, y es el mismo pendiente.
            tabla, hubo = todo.reemplazar_cuerpo(
                tabla, marca_previa.cuerpo.strip(), marca_nueva.cuerpo.strip()
            )
            if hubo:
                pendientes_path.write_text(tabla, encoding="utf-8")
                filas = 1
        propagate.propagar(vault)

    detalle = " y su fila en PENDIENTES.md" if filas else ""
    return Resultado.hecho(f"registro de las {hour} corregido{detalle}.")
