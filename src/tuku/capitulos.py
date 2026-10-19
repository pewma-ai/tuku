"""Chapters of the style book and of `reglas/`: `##` headings with at most one table.

`spec/vault.md` ("El libro de estilo") fixes the contract the commands read: a
chapter is a `##` section, and it holds at most one table, so a command asks for
a chapter by name and takes its only table. Headings and rows inside a code
fence are examples, not structure, and are skipped.

**What it reads and writes:** text in, text out. It touches no file.
**By hand:** open the file and find the `##` heading.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass

_CAPITULO = re.compile(r"^## (?P<nombre>\S.*?)\s*$")
_VALLA = re.compile(r"^\s*(```|~~~)")
_SEPARADOR = re.compile(r"^[\s|:-]+$")
_TRANSCLUSION = re.compile(r"!\[[^\]\n]*\]\((?P<ruta>[^)\s]+)\)")

Tabla = list[list[str]]


@dataclass(frozen=True)
class Capitulo:
    """A `##` section: its name, the 1-based line of its heading and its body."""

    nombre: str
    linea: int
    cuerpo: tuple[str, ...]

    def tablas(self) -> list[Tabla]:
        return tablas(self.cuerpo)


def _estructurales(lineas: Sequence[str]) -> Iterable[tuple[int, str]]:
    """The `(index, line)` pairs outside code fences."""
    en_valla = False
    for i, linea in enumerate(lineas):
        if _VALLA.match(linea):
            en_valla = not en_valla
            continue
        if not en_valla:
            yield i, linea


def separar(texto: str) -> list[Capitulo]:
    """The chapters of `texto` in order. What comes before the first `##` belongs to none."""
    lineas = texto.splitlines()
    marcas = [
        (i, m.group("nombre"))
        for i, linea in _estructurales(lineas)
        if (m := _CAPITULO.match(linea))
    ]
    if not marcas:
        return []
    fines = [i for i, _ in marcas[1:]] + [len(lineas)]
    return [
        Capitulo(nombre, i + 1, tuple(lineas[i + 1 : fin]))
        for (i, nombre), fin in zip(marcas, fines, strict=True)
    ]


def capitulo(texto: str, nombre: str) -> Capitulo | None:
    """The chapter called `nombre` (its heading without the `## `), or `None`."""
    return next((c for c in separar(texto) if c.nombre == nombre), None)


def _celdas(linea: str) -> list[str]:
    return [c.strip() for c in linea.strip().strip("|").split("|")]


def tablas(cuerpo: Sequence[str]) -> list[Tabla]:
    """The tables in `cuerpo`: each a list of rows (header first, separator dropped)."""
    resultado: list[Tabla] = []
    actual: Tabla | None = None
    previa = -2
    for i, linea in _estructurales(cuerpo):
        if linea.lstrip().startswith("|"):
            if actual is None or i != previa + 1:
                actual = []
                resultado.append(actual)
            if not _SEPARADOR.match(linea):
                actual.append(_celdas(linea))
            previa = i
        else:
            actual = None
    return resultado


def tabla_unica(texto: str, nombre: str) -> Tabla | None:
    """The first table of the chapter `nombre`, or `None` if it has no chapter or no table."""
    cap = capitulo(texto, nombre)
    if cap is None:
        return None
    todas = cap.tablas()
    return todas[0] if todas else None


def exceso_de_tablas(texto: str) -> list[Capitulo]:
    """The chapters of `texto` that hold more than one table."""
    return [c for c in separar(texto) if len(c.tablas()) > 1]


def transclusiones(texto: str) -> list[str]:
    """The paths that `![](ruta)` embeds in `texto`, in order and without repeats."""
    vistas: list[str] = []
    for _, linea in _estructurales(texto.splitlines()):
        for m in _TRANSCLUSION.finditer(linea):
            if m.group("ruta") not in vistas:
                vistas.append(m.group("ruta"))
    return vistas


_LINEA_TRANSCLUIDA = re.compile(r"^\s*!\[[^\]\n]*\]\((?P<ruta>[^)\s]+)\)\s*$")
_ENCABEZADO = re.compile(r"^(?P<marcas>#{1,6}) (?P<texto>\S.*)$")


def sin_frontmatter(texto: str) -> str:
    """`texto` without its YAML block, if it opens with one."""
    if not texto.startswith("---\n"):
        return texto
    fin = texto.find("\n---", 3)
    if fin == -1:
        return texto
    return texto[fin + 4 :].removeprefix("\n")


def solo_capitulos(texto: str) -> str:
    """The chapters of `texto`: no frontmatter, and nothing before the first `##`.

    What an author's file says before its first chapter (its title, a callout) is
    for whoever edits it. Without any `##` the text is returned whole.
    """
    cuerpo = sin_frontmatter(texto)
    lineas = cuerpo.splitlines()
    primero = next((i for i, linea in _estructurales(lineas) if _CAPITULO.match(linea)), None)
    return cuerpo if primero is None else "\n".join(lineas[primero:])


def bajar_encabezados(texto: str, nivel: int) -> str:
    """Shifts the headings of `texto` so the shallowest one lands at `nivel`.

    Headings inside code fences are examples and stay as they are.
    """
    lineas = texto.splitlines()
    estructurales = list(_estructurales(lineas))
    niveles = [
        len(m.group("marcas")) for _, linea in estructurales if (m := _ENCABEZADO.match(linea))
    ]
    if not niveles:
        return texto
    desplazamiento = nivel - min(niveles)
    for i, linea in estructurales:
        if m := _ENCABEZADO.match(linea):
            marcas = min(6, len(m.group("marcas")) + desplazamiento)
            lineas[i] = f"{'#' * marcas} {m.group('texto')}"
    return "\n".join(lineas)


def expandir(texto: str, leer: Callable[[str], str | None], *, nivel: int = 3) -> str:
    """`texto` with each whole-line `![](ruta)` replaced by the content of `ruta`.

    `leer` gives the text of a path, or `None` if it does not exist: that line
    becomes a visible mark naming the file, so the reader sees what is missing.
    The expansion is one level deep, the headings of the embedded file go down to
    `nivel`, only its chapters are taken (`solo_capitulos`), and a path that leaves
    the vault counts as missing.
    """
    salida: list[str] = []
    lineas = texto.splitlines()
    transcluidas = {
        i: m.group("ruta")
        for i, linea in _estructurales(lineas)
        if (m := _LINEA_TRANSCLUIDA.match(linea))
    }
    for i, linea in enumerate(lineas):
        ruta = transcluidas.get(i)
        if ruta is None:
            salida.append(linea)
            continue
        propio = leer(ruta) if not ruta.startswith(("/", "..")) and "/../" not in ruta else None
        if propio is None:
            salida.append(f"> [!warning] falta {ruta}")
        else:
            salida.append(bajar_encabezados(solo_capitulos(propio), nivel).strip("\n"))
    return "\n".join(salida)
