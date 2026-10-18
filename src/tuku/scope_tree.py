"""El árbol de `ambitos/` leído: nombres, rutas, keywords y ámbitos.

Lo que `scope` y los demás módulos necesitan saber de `ambitos/` sin depender de
las operaciones que lo cambian. No lee el reloj ni escribe: `scope` lo reexporta
para que `scope.rutas` y compañía sigan siendo los nombres de siempre.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from tuku import archivo
from tuku.resultado import Resultado

KEYWORDS_LINE = re.compile(r"^keywords:\s*\[(?P<lista>[^\]]*)\]\s*$", re.M)


@dataclass(frozen=True)
class Ambito:
    nombre: str
    directorio: Path
    keywords: list[str]


def page_of(directorio: Path) -> Path:
    return directorio / f"{directorio.name}.md"


def normalizar(nombre: str) -> str:
    """El nombre de un ámbito tal como va en disco y en los enlaces: kebab-case.

    En minúsculas y con los espacios en guion: el autor dicta "Depto Centro" y el
    ámbito es `depto-centro`. Sin esto, cada agente elige su forma y el mismo frente
    termina con dos nombres.
    """
    return re.sub(r"\s+", "-", nombre.strip().strip("[]").strip()).lower()


def igual_nombre(a: str, b: str) -> bool:
    """Dos nombres de ámbito son el mismo si solo difieren en mayúsculas.

    En macOS y Windows el disco no las distingue, y un vault viaja entre
    sistemas: dos carpetas que solo difieren en mayúsculas no pueden coexistir.
    """
    return a.casefold() == b.casefold()


def canonico(vault: Path, nombre: str) -> str:
    """El nombre normalizado, tal como está escrito el ámbito existente que calza.

    `ñandú rojo` encuentra `Ñandú-Rojo`. Si no hay ninguno, el normalizado.
    """
    return _canonical(nombres(vault), nombre)


def _canonical(names: Iterable[str], name: str) -> str:
    """`name` normalized and written as the existing name that matches, if any."""
    clean = normalizar(name)
    return next((n for n in sorted(names) if igual_nombre(n, clean)), clean)


def case_clash(vault: Path, nombre: str, *, salvo: str = "") -> str | None:
    """Otro nombre de `ambitos/` que solo difiere de `nombre` en mayúsculas."""
    return next(
        (
            n
            for n in sorted(nombres(vault))
            if igual_nombre(n, nombre) and n != nombre and n != salvo
        ),
        None,
    )


def nombres(vault: Path) -> set[str]:
    """Todo lo que un registro puede nombrar en `ambitos/`.

    Ámbitos, categorías y actividades. Que un registro apunte a una categoría es
    un error que reporta `doctor scope`, no uno que impida escribirlo.
    """
    return set(read_tree(vault).names)


@dataclass(frozen=True)
class Tree:
    """What `ambitos/` holds, read once so a command does not walk it again.

    `names` is everything a record can name (`nombres`), `paths` maps each name
    to its path relative to the vault (`rutas`) and `scopes` are the names that
    have a page of their own.
    """

    vault: Path
    names: frozenset[str]
    paths: Mapping[str, str]
    scopes: frozenset[str] = frozenset()


def read_tree(vault: Path) -> Tree:
    """Walk `ambitos/` once for the names and the paths of everything in it."""
    root = vault / "ambitos"
    names: set[str] = set()
    paths: dict[str, str] = {}
    scopes: set[str] = set()
    if root.is_dir():
        for p in sorted(root.rglob("*")):
            if p.is_dir():
                names.add(p.name)
                if page_of(p).is_file():
                    scopes.add(p.name)
                target = page_of(p) if page_of(p).is_file() else p
                paths.setdefault(p.name, target.relative_to(vault).as_posix())
            elif p.suffix == ".md" and not p.stem.isupper():
                names.add(p.stem)
                if p.stem != p.parent.name:
                    paths.setdefault(p.stem, p.relative_to(vault).as_posix())
    return Tree(vault, frozenset(names), paths, frozenset(scopes))


def resolve_scope(tree: Tree, name: str) -> str | Resultado:
    """`name` as the existing scope is written, or the rejection if none matches."""
    resolved = _canonical(tree.names, name)
    if resolved in tree.names:
        return resolved
    return _missing_scope(tree.scopes, resolved)


def rutas(vault: Path) -> dict[str, str]:
    """Nombre → ruta relativa al vault de todo lo que un registro puede nombrar.

    Es lo que `link` necesita para componer el enlace a un ámbito anidado con
    su ruta completa: la página del ámbito, el archivo de una actividad, o la
    carpeta de una categoría. Si dos nombres chocan manda el primero en orden,
    y `spec/ambitos.md` no admite que choquen.
    """
    return dict(read_tree(vault).paths)


def carpeta(vault: Path, nombre: str) -> Path:
    """La carpeta del ámbito `nombre`, anidado o no. Plana si no se encuentra."""
    for a in leer(vault):
        if a.nombre == nombre:
            return a.directorio
    return vault / "ambitos" / nombre


def directorio_de(vault: Path, nombre: str) -> Path | None:
    """La carpeta de un ámbito o de una categoría, donde esté bajo `ambitos/`."""
    raiz = vault / "ambitos"
    if not raiz.is_dir():
        return None
    return next((p for p in sorted(raiz.rglob("*")) if p.is_dir() and p.name == nombre), None)


def rechazo_si_no_existe(vault: Path, nombre: str) -> Resultado | None:
    """Rechaza un ámbito que no existe. Crearlo es decisión del autor, no del comando."""
    if nombre in nombres(vault):
        return None
    return _missing_scope({a.nombre for a in leer(vault)}, nombre)


def _missing_scope(scopes: Iterable[str], nombre: str) -> Resultado:
    existentes = ", ".join(sorted(scopes)) or "ninguno"
    return Resultado.rechazo(
        f"no existe el ámbito {nombre!r}. Créalo con `tuku scope create {nombre}` "
        f"si el autor lo pide, o usa uno que exista: {existentes}."
    )


def keywords(pagina: str) -> list[str]:
    """Las `keywords` del frontmatter de una página de ámbito."""
    m = KEYWORDS_LINE.search(pagina)
    if m is None:
        return []
    return [k.strip() for k in m.group("lista").split(",") if k.strip()]


def keyword_key(keyword: str) -> str:
    """La keyword como se compara: guiones y espacios valen lo mismo."""
    return re.sub(r"[-\s]+", " ", keyword).strip().casefold()


def palabras_de(valores: Sequence[str]) -> list[str]:
    """Las keywords que dicen `valores`: separadas por coma, en kebab-case.

    `--keyword "Los Robles, Rodolfo"` son dos keywords, `los-robles` y `rodolfo`: la
    misma regla de los nombres de ámbito (`normalizar`), así una keyword se escribe
    igual dentro de la lista `[a, b]` del frontmatter, que separa con comas y espacios.
    """
    palabras = (re.sub(r"\s+", "-", p.strip()).lower() for v in valores for p in v.split(","))
    return [p for p in palabras if p]


def merge_keywords(previas: list[str], nuevas: Sequence[str], nombre: str = "") -> list[str]:
    """`previas` y, detrás, las `nuevas` que ninguna anterior ni el `nombre` repiten.

    El nombre del ámbito ya es el de su carpeta: una keyword que lo repite no aporta.
    """
    salida = list(previas)
    vistas = {keyword_key(k) for k in salida} | ({keyword_key(nombre)} if nombre else set())
    for k in palabras_de(nuevas):
        if k and keyword_key(k) not in vistas:
            salida.append(k)
            vistas.add(keyword_key(k))
    return salida


def reject_bad_keywords(nuevas: Sequence[str]) -> Resultado | None:
    """Una keyword vive en una lista `[a, b]` de una línea: sin corchetes."""
    malas = [k for k in nuevas if re.search(r"[\[\]]", k)]
    if malas:
        return Resultado.rechazo(
            f"la keyword {malas[0]!r} lleva corchetes y no cabe en la lista del frontmatter."
        )
    return None


def leer(vault: Path) -> list[Ambito]:
    """Los ámbitos del árbol: los directorios que tienen página propia."""
    raiz = vault / "ambitos"
    if not raiz.is_dir():
        return []
    salida = []
    for directorio in sorted(p for p in raiz.rglob("*") if p.is_dir()):
        pagina = page_of(directorio)
        if pagina.is_file():
            salida.append(
                Ambito(
                    directorio.name,
                    directorio,
                    keywords(archivo.leer(pagina)),
                )
            )
    return salida
