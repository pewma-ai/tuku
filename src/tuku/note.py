"""tuku note create / tuku note lint: el zettelkasten, en su versión mínima.

Fase 5 de `devel/epics.md`, mínima: crear una nota a petición y
enlazarla. Las notas tipadas con plantilla y el destilado del histórico no
entran acá (`spec/notas.md`).

Crear una nota **es un hecho de la vida del autor**, que la pidió, así que deja
constancia en la bitácora. Mover un pendiente de escalón es un hecho del
sistema y no la deja. Esa es la línea, y no es arbitraria: lo que el autor hizo
se registra, lo que el sistema hizo por su cuenta no.

`lint` comprueba lo que se puede comprobar sin juicio: que exista `## Ver
además` y que cada enlace de esa sección lleve texto de motivo detrás. Si el
motivo es pertinente o es relleno lo evalúa quien lee.

**Qué lee y escribe:** crea archivos en `notas/`. `lint` solo lee.
**A mano:** escribir el archivo en `notas/` con su frontmatter, cerrarlo con
`## Ver además`, y anotar en la bitácora que se creó.
"""

from __future__ import annotations

import re
import unicodedata
from datetime import date
from pathlib import Path

from tuku.resultado import Resultado

VER_ADEMAS = "## Ver además"

#: Un enlace de la sección "Ver además": markdown o wikilink, y lo que sigue.
_ENLACE = re.compile(r"^\s*[*-]\s+(?:\[[^\]]+\]\([^)]+\)|\[\[[^\]]+\]\])(?P<motivo>.*)$")


def slug(titulo: str) -> str:
    """El nombre de archivo de una nota, a partir de su título."""
    plano = unicodedata.normalize("NFKD", titulo).encode("ascii", "ignore").decode()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", plano.lower())).strip("-")


def crear(
    vault: Path,
    *,
    title: str = "",
    titulo: str = "",
    body: str = "",
    cuerpo: str = "",
    scope: str | None = None,
    ambito: str | None = None,
    today: date | None = None,
    hoy: date | None = None,
) -> Path:
    """Escribe la nota en `notas/` y devuelve su ruta. Idempotente.

    Si el archivo ya existe no lo toca: repetir la operación no duplica ni
    reescribe lo que el autor pueda haber editado a mano.

    El frontmatter lleva `type: Note`, que `reglas/types.md` asigna a todo lo de
    `notas/` y `spec/README.md` exige en cualquier archivo que guarde
    conocimiento. Es distinto de `subtype`, la lista abierta que subdivide ese
    `Note` en las notas tipadas (`spec/notas.md`): solo lo declaran algunas, y
    TUKU todavía no lo escribe.
    """
    valor_titulo = title or titulo
    valor_cuerpo = body or cuerpo
    valor_scope = scope if scope is not None else ambito
    valor_fecha = today or hoy or date.today()

    ruta = vault / "notas" / f"{slug(valor_titulo)}.md"
    if ruta.exists():
        return ruta

    ver_ademas = ""
    if valor_scope is not None:
        ver_ademas = (
            f"\n{VER_ADEMAS}\n\n"
            f"* [[{valor_scope}]] — el ámbito al que pertenece lo que esta nota explica.\n"
        )

    ruta.parent.mkdir(parents=True, exist_ok=True)
    contenido = (
        f"---\ntype: Note\ncreated: {valor_fecha.isoformat()}\n---\n\n"
        f"# {valor_titulo}\n\n{valor_cuerpo.strip()}\n{ver_ademas}"
    )
    ruta.write_text(contenido, encoding="utf-8")
    return ruta


create = crear


def registro_de_constancia(
    nota: Path,
    *,
    time: str = "",
    hora: str = "",
    scope: str | None = None,
    ambito: str | None = None,
) -> str:
    """La línea de bitácora que deja constancia de la nota creada."""
    valor_hora = time or hora
    valor_scope = scope if scope is not None else ambito
    prefijo = f"[[{valor_scope}]] " if valor_scope else ""
    return f"- {valor_hora} - {prefijo}**nota**: escribí la nota [[{nota.stem}]]"


def lint(nota: str) -> list[str]:
    """Hallazgos de una nota. Solo lo verificable sin juicio."""
    hallazgos = []
    if VER_ADEMAS not in nota:
        hallazgos.append(
            f"error: falta la sección `{VER_ADEMAS}`. "
            f"Toda nota cierra con sus enlaces salientes y el motivo de cada uno."
        )
        return hallazgos

    lineas = nota.splitlines()
    ini = lineas.index(VER_ADEMAS)
    for n, linea in enumerate(lineas[ini + 1 :], start=ini + 2):
        m = _ENLACE.match(linea)
        if m is None:
            continue
        if not m.group("motivo").strip(" —-\t"):
            hallazgos.append(
                f"línea {n}: error: el enlace no dice para qué conecta. "
                f"Agrega el motivo después del enlace, en una frase."
            )
    return hallazgos


def crear_con_constancia(
    vault: Path,
    *,
    title: str,
    body: str,
    scope: str | None = None,
    day: date | None = None,
    hour: str | None = None,
    record: bool = True,
) -> Resultado:
    """Escribe la nota y deja constancia en la bitácora. Idempotente.

    Crear una nota es un hecho de la vida del autor, que la pidió, así que se
    registra; mover un pendiente de escalón es del sistema y no se registra. Esa
    es la línea, y por eso la constancia va acá y no en un comando aparte.

    Repetir la operación no duplica nada: la nota no se reescribe si ya existe, y
    la constancia solo se añade si no estaba. `record=False` la omite.

    **Nada se escribe hasta que todo cabe.** La constancia se compone y se prueba
    contra `AHORA.md` en memoria antes de tocar el disco, porque si el día cae
    fuera del ciclo abierto la operación se rechaza entera. Escribir la nota
    primero dejaba el vault a medias, con una nota que nada registra, y el
    rechazo salía como traceback.
    """
    from datetime import datetime

    from tuku import scope as scope_mod
    from tuku.ahora import encabezado_de
    from tuku.entry import add

    hoy = day or date.today()
    hora = hour or datetime.now().strftime("%H:%M")
    ruta = vault / "notas" / f"{slug(title)}.md"

    ahora_path = vault / "AHORA.md"
    pendiente: str | None = None
    if record and ahora_path.is_file():
        texto = ahora_path.read_text(encoding="utf-8")
        constancia = registro_de_constancia(ruta, time=hora, scope=scope)
        if constancia not in texto:
            try:
                pendiente = add(texto, [constancia], day=encabezado_de(hoy))
            except ValueError as e:
                return Resultado.rechazo(str(e))

    crear(vault, title=title, body=body, scope=scope, today=hoy)
    if pendiente is not None:
        ahora_path.write_text(pendiente, encoding="utf-8")
        if scope:
            scope_mod.actualizar_pagina(vault, scope)

    return Resultado.hecho(f"nota creada en {ruta}.")


def lint_del_vault(vault: Path, archivo: Path | None = None) -> Resultado:
    """Revisa una nota, o todas las de `notas/` si no se nombra ninguna."""
    rutas = [archivo] if archivo is not None else []
    if archivo is None:
        dir_notas = vault / "notas"
        if dir_notas.is_dir():
            rutas = sorted(dir_notas.glob("*.md"))
    if not rutas:
        return Resultado.hecho("sin notas que revisar.")

    hallazgos = [
        f"{ruta.name}: {error}"
        for ruta in rutas
        for error in lint(ruta.read_text(encoding="utf-8"))
    ]
    if not hallazgos:
        return Resultado.hecho("sin hallazgos.")
    return Resultado.rechazo("\n".join(hallazgos), error=False)
