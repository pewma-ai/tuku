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
from datetime import date
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
    nuevas = [linea.rstrip("\n") for linea in lineas]

    ordenadas = sorted([*previas, *nuevas], key=_clave_hora)
    seccion = [encabezado, *ordenadas, ""]

    texto = "\n".join([*src[:ini], *seccion, *src[fin:]])
    if ahora.endswith("\n") and not texto.endswith("\n"):
        texto += "\n"
    return texto


def add_al_vault(
    vault: Path, lineas: list[str], *, day: str | None = None, hoy: date | None = None
) -> Resultado:
    """Escribe los registros en su día y actualiza las páginas de ámbito.

    El caso de uso completo de `tuku entry add`, con las dos consecuencias que
    tiene escribir un registro: queda en `AHORA.md` y las páginas de ámbito
    reflejan lo que se escribió. Que la propagación sea parte de escribir, y no
    un segundo comando, es lo que evita que el vault quede a medias.

    Sin `day`, el día es el de hoy en la forma canónica de `ahora.encabezado_de`.
    """
    from tuku import scope
    from tuku.ahora import encabezado_de
    from tuku.config import archivo_vault

    ruta = archivo_vault(vault, "AHORA.md")
    dia = day if day is not None else encabezado_de(hoy or date.today())
    try:
        texto = add(ruta.read_text(encoding="utf-8"), lineas, day=dia)
    except ValueError as e:
        return Resultado.rechazo(str(e))

    ruta.write_text(texto, encoding="utf-8")
    for ambito in scope.leer(vault):
        scope.actualizar_pagina(vault, ambito.nombre)
    return Resultado.hecho(f"{len(lineas)} registro(s) en {dia.removeprefix('## ')}.")


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
