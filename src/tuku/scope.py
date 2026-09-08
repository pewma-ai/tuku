"""tuku scope create / tuku scope lint: el árbol de ámbitos.

Fase 3 de `devel/epics.md`, versión mínima. Lo que distingue a cada
nodo de `ambitos/` es qué carga, no dónde está (`spec/ambitos.md`):

| Rol | Cómo se reconoce |
| --- | --- |
| Ámbito | Directorio **con** página propia |
| Categoría | Directorio **sin** página propia |
| Actividad | Archivo `.md` en minúscula |

De ahí la única regla verificable sin un árbol profundo, y la que `scope lint`
comprueba: **los registros apuntan a una actividad o a un ámbito, nunca a una
categoría.** Una categoría agrupa y no tiene de qué hablar.

`AGENTS.md` y `CADENCIAS.md` son obligatorios en cada directorio aunque queden
vacíos: el costo son dos archivos por carpeta y la ganancia es que ningún
comando tiene que manejar el caso "no existe". `CAPACIDAD.md` no se crea, porque
es opcional en todas partes.

**Qué lee y escribe:** crea directorios y archivos bajo `ambitos/`. `lint` solo
lee, y además `AHORA.md`.
**A mano:** crear la carpeta con sus tres archivos, y poner el nombre en
`keywords:` de la página propia.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_KEYWORDS = re.compile(r"^keywords:\s*\[(?P<lista>[^\]]*)\]\s*$", re.M)
_ENLACE = re.compile(r"\[\[(?P<destino>[^\]|#]+)")

OBLIGATORIOS = ("AGENTS.md", "CADENCIAS.md")


@dataclass(frozen=True)
class Ambito:
    nombre: str
    directorio: Path
    keywords: list[str]


def _pagina(directorio: Path) -> Path:
    return directorio / f"{directorio.name}.md"


def keywords(pagina: str) -> list[str]:
    """Las `keywords` del frontmatter de una página de ámbito."""
    m = _KEYWORDS.search(pagina)
    if m is None:
        return []
    return [k.strip() for k in m.group("lista").split(",") if k.strip()]


def crear(vault: Path, nombre: str) -> Path:
    """Crea el ámbito `nombre` bajo `ambitos/`. Idempotente.

    Si ya existe no toca nada: `spec/ambitos.md` no admite dos ámbitos con el
    mismo nombre, y volver a crearlo no es un error del autor.
    """
    directorio = vault / "ambitos" / nombre
    directorio.mkdir(parents=True, exist_ok=True)

    for archivo in OBLIGATORIOS:
        ruta = directorio / archivo
        if not ruta.exists():
            ruta.write_text(_plantilla_obligatorio(archivo, nombre), encoding="utf-8")

    pagina = _pagina(directorio)
    if not pagina.exists():
        # Lo mínimo que `vocab show` y `link backfill` necesitan. Sin secciones
        # sugeridas: la organización emerge del uso, no de una plantilla.
        pagina.write_text(
            f"---\nkeywords: [{nombre}]\n---\n\n# {nombre}\n", encoding="utf-8"
        )
    return directorio


def _plantilla_obligatorio(archivo: str, nombre: str) -> str:
    if archivo == "AGENTS.md":
        return (
            f"# Reglas de {nombre}\n\n"
            "Reglas que valen solo para este ámbito y lo que cuelgue de él.\n\n"
            "Puede quedar vacío.\n"
        )
    return (
        f"# Cadencias de {nombre}\n\n"
        "Lo que se repite en este ámbito con un ritmo propio.\n\n"
        "Puede quedar vacío.\n"
    )


def leer(vault: Path) -> list[Ambito]:
    """Los ámbitos del árbol: los directorios que tienen página propia."""
    raiz = vault / "ambitos"
    if not raiz.is_dir():
        return []
    salida = []
    for directorio in sorted(p for p in raiz.rglob("*") if p.is_dir()):
        pagina = _pagina(directorio)
        if pagina.is_file():
            salida.append(
                Ambito(
                    directorio.name,
                    directorio,
                    keywords(pagina.read_text(encoding="utf-8")),
                )
            )
    return salida


def categorias(vault: Path) -> list[str]:
    """Los directorios de `ambitos/` sin página propia: agrupan y nada más."""
    raiz = vault / "ambitos"
    if not raiz.is_dir():
        return []
    return sorted(
        d.name for d in raiz.rglob("*") if d.is_dir() and not _pagina(d).is_file()
    )


def lint(ahora: str, *, categorias: list[str]) -> list[str]:
    """Registros que apuntan a una categoría. No escribe nada."""
    hallazgos = []
    for n, linea in enumerate(ahora.splitlines(), start=1):
        for m in _ENLACE.finditer(linea):
            destino = m.group("destino").strip()
            if destino in categorias:
                hallazgos.append(
                    f"AHORA.md:{n}: error: [[{destino}]] es una categoría, y un registro "
                    f"no puede apuntar a una. Apúntalo al ámbito o a la actividad que "
                    f"corresponda, o dale a {destino} su página propia para volverlo ámbito."
                )
    return hallazgos
