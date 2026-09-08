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
        f"---\ncreated: {valor_fecha.isoformat()}\n---\n\n"
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
