"""tuku entry add: coloca líneas de bitácora ya formadas en su día.

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
from datetime import date, datetime
from pathlib import Path

from tuku.resultado import Resultado

_HORA = re.compile(r"^- (\d{2}):(\d{2}) - ")


def _clave_hora(linea: str) -> tuple[int, int]:
    m = _HORA.match(linea)
    if m is None:
        raise ValueError(f"la línea no empieza con '- HH:MM - ': {linea!r}")
    return int(m.group(1)), int(m.group(2))


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
    # verdad difieren en algo, aunque sea la hora.
    nuevas = [x for linea in lineas if (x := linea.rstrip("\n")) not in previas]

    ordenadas = sorted([*previas, *nuevas], key=_clave_hora)
    seccion = [encabezado, *ordenadas, ""]

    texto = "\n".join([*src[:ini], *seccion, *src[fin:]])
    if ahora.endswith("\n") and not texto.endswith("\n"):
        texto += "\n"
    return texto


def componer(*, hora: str, scope: str | None, body: str) -> str:
    """La línea de bitácora a partir de sus campos.

    `- HH:MM - [[ambito]] **marca**: cuerpo`. Componerla es mecánico: la hora, el
    guion, el orden de los campos y los corchetes del ámbito son formato, y no
    hay razón para pedírselos a quien dicta. Lo único que es juicio es la marca,
    y esa viaja dentro de `body`.
    """
    ambito = ""
    if scope:
        ambito = f"[[{scope.strip().strip('[]')}]] "
    return f"- {hora} - {ambito}{body.strip()}"


def add_al_vault(
    vault: Path,
    *,
    body: str,
    scope: str | None = None,
    day: date | None = None,
    hour: str | None = None,
    horizon: str | None = None,
    when: str = "",
) -> Resultado:
    """Escribe un registro y aplica todo lo que ese registro implica.

    El caso de uso completo de `tuku entry add`. Escribir un registro tiene
    consecuencias y todas son parte de escribirlo: queda en `AHORA.md`, las
    páginas de ámbito lo reflejan, y si lleva una marca de la ontología cerrada
    se aplica lo que esa marca declara: `**pendiente**` abre el pendiente y
    `~~(Hecho)~~` lo cierra.

    Que las consecuencias sean parte de escribir, y no un segundo comando, es lo
    que evita que el vault quede a medias. Durante un tiempo esto valió solo para
    la propagación y no para los pendientes, y esa asimetría era el modo de falla
    más caro del sistema: un archivo bien formado al que le faltaba la mitad, sin
    nada que lo delatara. `tuku todo open` y `close` siguen existiendo para
    corregir a mano, no para completar lo que este comando dejó a medias.

    Recibe los campos, no la línea: el encabezado `## Martes 11 de agosto` se
    calcula desde `2026-08-11`, y la línea se compone. Un registro por llamada.

    Sin `day` es hoy; sin `hour`, ahora.
    """
    from tuku import scope as ambitos
    from tuku.ahora import encabezado_de
    from tuku.config import archivo_vault

    ruta = archivo_vault(vault, "AHORA.md")
    dia = encabezado_de(day or date.today())
    linea = componer(hora=hour or datetime.now().strftime("%H:%M"), scope=scope, body=body)
    try:
        texto = add(ruta.read_text(encoding="utf-8"), [linea], day=dia)
    except ValueError as e:
        return Resultado.rechazo(str(e))

    ruta.write_text(texto, encoding="utf-8")

    from tuku import todo

    hecho = [f"{linea}", f"en {dia.removeprefix('## ')}."]
    marca = todo.parsear(linea)
    if marca is not None and marca.marca == todo.ABRE:
        consecuencia = todo.abrir_en_vault(
            vault,
            body=marca.cuerpo,
            scope=scope,
            horizon=horizon or todo.ESTA_SEMANA,
            when=when,
            propagate=False,
        )
        hecho.append(consecuencia.mensaje)
    elif marca is not None and marca.marca == todo.CIERRA:
        hecho.append(todo.cerrar_en_vault(vault, body=marca.cuerpo, propagate=False).mensaje)

    for ambito in ambitos.leer(vault):
        ambitos.actualizar_pagina(vault, ambito.nombre)
    from tuku.propagate import propagar

    propagar(vault)
    return Resultado.hecho("\n".join(hecho))


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
