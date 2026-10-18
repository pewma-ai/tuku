"""Los links de TUKU: el único módulo que los compone, los reconoce y los convierte.

Un link de TUKU es Markdown estándar con **ruta relativa al archivo que lo
contiene**: `[texto](ruta/relativa.md)`. Ningún otro módulo arma ni parsea
links por su cuenta; todos pasan por acá. Es núcleo puro: recibe texto y rutas
relativas al vault, nunca toca disco. Quien recorre el vault es el caso de uso
(`doctor.revisar_links`, `fix_link`).

El único wikilink que TUKU admite es la transclusión de Obsidian
(`![[archivo.md#^ancla]]`), y se reconoce por el `!` inicial. Cualquier otro
`[[x]]` es un wikilink escrito a mano: los lectores lo entienden, los
escritores no lo producen, y `tuku fix link` lo convierte.

Lo que no se toca nunca: el código inline y los bloques de código, donde un
`[[x]]` es texto y no un link.

Parte de la conversión viene de `jntr.obsidian-links-to-markdown.py` de
mac-jpgil, con dos cambios: respeta las transclusiones (su regex las convertía
en imágenes) y no depende de disco.

**A mano:** escribir `[texto](ruta)` con la ruta calculada desde el archivo
donde va el link, por ejemplo `[personal](../personal/personal.md)` desde una
página de ámbito hermana.
"""

from __future__ import annotations

import posixpath
import re
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from urllib.parse import unquote

# ---------------------------------------------------------------------------
# Reconocer
# ---------------------------------------------------------------------------

#: Un link Markdown. El destino no lleva espacios (se escriben como `%20`).
_MD = re.compile(r"(?<!!)\[(?P<texto>[^\]\n]*)\]\((?P<destino>[^)\s]+)\)")

#: Un wikilink, sin la transclusión: el `!` delante lo excluye.
_WIKI = re.compile(r"(?<!!)\[\[(?P<crudo>[^\[\]\n]+)\]\]")

#: Un bloque de código con cercas, o hasta el final del texto si no se cierra.
_BLOQUE = re.compile(
    r"^[ \t]*(?P<cerca>```|~~~)[^\n]*\n.*?(?:^[ \t]*(?P=cerca)[^\n]*$|\Z)",
    re.S | re.M,
)
_INLINE = re.compile(r"`[^`\n]+`")

#: Un enlace en cualquiera de los dos formatos, para los lectores que solo
#: necesitan saber a qué apunta. Sin transclusiones.
ENLACE = r"(?:(?<!!)\[\[[^\[\]\n]+\]\]|(?<!!)\[[^\]\n]*\]\([^)\s]+\))"

_LECTOR = re.compile(
    r"\[\[(?P<wiki>[^\]|#\n]+)(?:[#|][^\]\n]*)?\]\]|\[[^\]\n]*\]\((?P<ruta>[^)\s]+)\)"
)

_EXTERNO = re.compile(r"^(?:[a-zA-Z][a-zA-Z0-9+.-]*:|#|/|//)")

#: Una transclusión de Obsidian: `![[ruta.md#^ancla]]`.
_TRANSCLUSION = re.compile(r"!\[\[(?P<ruta>[^\]#|\n]+)(?P<resto>[#|][^\]\n]*)?\]\]")


def _sin_codigo(texto: str) -> str:
    """El texto con el código reemplazado por espacios, para que los offsets coincidan."""

    def blanco(m: re.Match[str]) -> str:
        return re.sub(r"[^\n]", " ", m.group())

    return _INLINE.sub(blanco, _BLOQUE.sub(blanco, texto))


def nombre_de(enlace: str) -> str | None:
    """El nombre al que apunta un enlace: el del archivo destino, sin `.md`.

    `[x](ambitos/x/x.md#ancla)` y `[[x#ancla]]` dan `x`. Es lo que leen
    `todo`, `scope` y `rename` para saber a qué ámbito pertenece un registro,
    sin importar el formato en que quedó escrito.
    """
    m = _LECTOR.fullmatch(enlace.strip())
    if m is None:
        return None
    if m.group("wiki") is not None:
        return str(m.group("wiki")).strip()
    ruta = unquote(str(m.group("ruta"))).split("#", 1)[0].rstrip("/")
    base = posixpath.basename(ruta)
    return base[:-3] if base.endswith(".md") else base


def sin_links(texto: str) -> str:
    """El texto con cada link reemplazado por lo que se lee de él.

    `[Carmen](notas/carmen.md)` y `[[carmen|Carmen]]` quedan como `Carmen`. Sirve
    para comparar dos textos que difieren solo en sus links: un pendiente que en
    la bitácora lleva un link y en `PENDIENTES.md` no es el mismo pendiente. Las
    transclusiones (`![[...]]`) no se tocan.
    """

    def visible(m: re.Match[str]) -> str:
        return str(m.group("texto"))

    def wiki(m: re.Match[str]) -> str:
        resto, _, alias = str(m.group("crudo")).partition("|")
        return alias or resto.partition("#")[0] or resto

    return _WIKI.sub(wiki, _MD.sub(visible, texto))


def nombres_enlazados(linea: str) -> list[str]:
    """Los nombres a los que apunta una línea, en orden, en cualquier formato."""
    return [n for m in _LECTOR.finditer(linea) if (n := nombre_de(m.group())) is not None]


# ---------------------------------------------------------------------------
# Componer
# ---------------------------------------------------------------------------


def relativa(desde: str, hacia: str) -> str:
    """La ruta de `hacia` vista desde el archivo `desde`. Ambas relativas al vault."""
    return posixpath.relpath(hacia, posixpath.dirname(desde) or ".")


def md(texto: str, href: str) -> str:
    """`[texto](href)`, con los espacios del destino como `%20`."""
    return f"[{texto}]({href.replace(' ', '%20')})"


def enlace(texto: str, desde: str, hacia: str, ancla: str | None = None) -> str:
    """Un link a `hacia` escrito en el archivo `desde`."""
    href = relativa(desde, hacia)
    return md(texto, f"{href}#{ancla}" if ancla else href)


def ruta_ambito(nombre: str, rutas: Mapping[str, str] | None = None) -> str:
    """La ruta de un ámbito dentro del vault.

    Un ámbito anidado lleva su ruta completa y la conoce quien lee el árbol
    (`scope.rutas`); sin ella se asume la forma plana `ambitos/<n>/<n>.md`.
    """
    if rutas and nombre in rutas:
        return rutas[nombre]
    return f"ambitos/{nombre}/{nombre}.md"


def enlace_ambito(
    nombre: str, desde: str = "AHORA.md", rutas: Mapping[str, str] | None = None
) -> str:
    """El link a un ámbito, escrito en el archivo `desde`."""
    return enlace(nombre, desde, ruta_ambito(nombre, rutas))


# ---------------------------------------------------------------------------
# Convertir wikilinks
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Wikilink:
    """Un `[[destino#ancla|alias]]` escrito a mano, con dónde está."""

    inicio: int
    fin: int
    linea: int
    destino: str
    ancla: str | None
    alias: str | None

    @property
    def original(self) -> str:
        ancla = f"#{self.ancla}" if self.ancla is not None else ""
        alias = f"|{self.alias}" if self.alias is not None else ""
        return f"[[{self.destino}{ancla}{alias}]]"


@dataclass(frozen=True)
class Decision:
    """Un wikilink que `fix` no puede resolver solo: le toca al autor."""

    archivo: str
    linea: int
    original: str
    motivo: str


@dataclass(frozen=True)
class Conversion:
    """El resultado de convertir un archivo: texto nuevo, cuántos y qué quedó."""

    texto: str
    convertidos: int
    decisiones: list[Decision]


def wikilinks(texto: str) -> list[Wikilink]:
    """Los wikilinks del texto, sin las transclusiones y sin los que están en código."""
    limpio = _sin_codigo(texto)
    salida = []
    for m in _WIKI.finditer(limpio):
        resto, _, alias = str(m.group("crudo")).partition("|")
        destino, _, ancla = resto.partition("#")
        tiene_alias = "|" in m.group("crudo")
        tiene_ancla = "#" in resto
        salida.append(
            Wikilink(
                m.start(),
                m.end(),
                texto.count("\n", 0, m.start()) + 1,
                destino,
                ancla if tiene_ancla else None,
                alias if tiene_alias else None,
            )
        )
    return salida


def indice(archivos: Iterable[str]) -> dict[str, list[str]]:
    """Nombre sin `.md` → rutas con ese nombre. Las rutas son relativas al vault."""
    salida: dict[str, list[str]] = {}
    for ruta in archivos:
        if ruta.endswith(".md"):
            salida.setdefault(posixpath.basename(ruta)[:-3], []).append(ruta)
    return salida


def _sin_md(nombre: str) -> str:
    return nombre[:-3] if nombre.endswith(".md") else nombre


def _resolver(w: Wikilink, desde: str, idx: Mapping[str, list[str]]) -> tuple[str, str] | str:
    """`(texto, href)` si el wikilink resuelve; si no, el motivo."""
    origen = posixpath.dirname(desde)
    if not w.destino:
        if w.ancla is None:
            return "el wikilink está vacío"
        return (w.alias or w.ancla, "#" + w.ancla.replace(" ", "%20"))

    nombre = _sin_md(posixpath.basename(w.destino))
    candidatos = idx.get(nombre, [])
    local = posixpath.normpath(
        posixpath.join(origen, w.destino if w.destino.endswith(".md") else w.destino + ".md")
    )
    if local in candidatos:
        elegido = local
    else:
        if "/" in w.destino:
            cola = posixpath.normpath(w.destino).lstrip("./")
            cola = cola if cola.endswith(".md") else cola + ".md"
            candidatos = [c for c in candidatos if c.endswith(cola)]
        if not candidatos:
            return f"no existe ningún archivo {nombre}.md en el vault"
        if len(candidatos) > 1:
            return f"es ambiguo, coincide con {', '.join(candidatos)}"
        elegido = candidatos[0]

    href = relativa(desde, elegido)
    if w.ancla is not None:
        href += "#" + w.ancla
    return (w.alias or _sin_md(posixpath.basename(elegido)), href.replace(" ", "%20"))


def convertir(texto: str, desde: str, idx: Mapping[str, list[str]]) -> Conversion:
    """Convierte los wikilinks resolubles de `texto` (el archivo `desde`) a Markdown.

    Lo que no resuelve, o resuelve a más de un archivo, se deja como está y
    sale como `Decision`: elegir el archivo, o crearlo, es del autor. Idempotente:
    sobre el resultado no queda nada que convertir.
    """
    piezas: list[str] = []
    cursor = 0
    convertidos = 0
    decisiones: list[Decision] = []
    for w in wikilinks(texto):
        r = _resolver(w, desde, idx)
        if isinstance(r, str):
            decisiones.append(Decision(desde, w.linea, w.original, r))
            continue
        piezas.append(texto[cursor : w.inicio])
        piezas.append(f"[{r[0]}]({r[1]})")
        cursor = w.fin
        convertidos += 1
    piezas.append(texto[cursor:])
    return Conversion("".join(piezas), convertidos, decisiones)


# ---------------------------------------------------------------------------
# Revisar
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Roto:
    """Un link Markdown cuya ruta no existe."""

    linea: int
    texto: str
    destino: str


def _ruta_local(destino: str, desde: str) -> str | None:
    """La ruta del destino relativa al vault, o `None` si no es un archivo local."""
    if _EXTERNO.match(destino):
        return None
    ruta = unquote(destino).split("#", 1)[0]
    if not ruta:
        return None
    return posixpath.normpath(posixpath.join(posixpath.dirname(desde), ruta))


def salientes(texto: str, desde: str) -> list[tuple[int, str, str, str]]:
    """Los links Markdown de `texto` a archivos locales: (línea, texto, ruta, destino).

    La ruta es relativa al vault, como en `rotos`, y el destino es como se escribió:
    dos links al mismo archivo dan la misma ruta aunque se escriban distinto. Salta
    lo externo, las anclas de la misma página y lo que va en código.
    """
    salida = []
    for m in _MD.finditer(_sin_codigo(texto)):
        if (local := _ruta_local(m.group("destino"), desde)) is not None:
            salida.append(
                (
                    texto.count("\n", 0, m.start()) + 1,
                    m.group("texto"),
                    local,
                    m.group("destino"),
                )
            )
    return salida


def rotos(texto: str, desde: str, existe: Callable[[str], bool]) -> list[Roto]:
    """Los links Markdown del archivo `desde` cuya ruta no existe.

    `existe` recibe una ruta relativa al vault y dice si hay un archivo o
    carpeta ahí: así el núcleo no toca disco. Los links externos y los que solo
    apuntan a un ancla de la misma página no se revisan.
    """
    salida = []
    for m in _MD.finditer(_sin_codigo(texto)):
        local = _ruta_local(m.group("destino"), desde)
        if local is None:
            continue
        if local.startswith("..") or not existe(local):
            salida.append(
                Roto(texto.count("\n", 0, m.start()) + 1, m.group("texto"), m.group("destino"))
            )
    return salida


def rebasar(texto: str, desde: str, hacia: str) -> str:
    """Recalcula las rutas de los links de `texto` al moverlo del archivo `desde` a `hacia`.

    Una línea copiada de `AHORA.md` a la página de un ámbito deja de resolver si
    sus rutas relativas no se recalculan. Los links externos y de ancla quedan
    como están.
    """
    if posixpath.dirname(desde) == posixpath.dirname(hacia):
        return texto

    def cambiar(m: re.Match[str]) -> str:
        local = _ruta_local(m.group("destino"), desde)
        if local is None:
            return m.group()
        ancla = m.group("destino").partition("#")[2]
        href = relativa(hacia, local)
        return md(m.group("texto"), f"{href}#{ancla}" if ancla else href)

    return _MD.sub(cambiar, texto)


def reubicar(texto: str, desde_viejo: str, desde_nuevo: str, movidos: Mapping[str, str]) -> str:
    """Recalcula las rutas de los links de `texto` cuando algo cambia de lugar.

    El archivo que contiene el texto pasa de `desde_viejo` a `desde_nuevo` (puede
    ser el mismo), y las carpetas de `movidos` (ruta vieja → ruta nueva, relativas
    al vault) cambian de lugar. Un link que apuntaba dentro de una carpeta movida
    sigue su destino, y uno que sale de un archivo movido se recalcula desde el
    lugar nuevo. Vale también para la transclusión. Los links externos, los de
    ancla y el código quedan como están.
    """

    def destino_nuevo(local: str) -> str:
        for viejo, nuevo in movidos.items():
            if local == viejo or local.startswith(f"{viejo}/"):
                return nuevo + local[len(viejo) :]
        return local

    oculto = _sin_codigo(texto)
    reemplazos: list[tuple[int, int, str]] = []
    for m in _MD.finditer(oculto):
        local = _ruta_local(m.group("destino"), desde_viejo)
        if local is None:
            continue
        ruta, _, ancla = m.group("destino").partition("#")
        href = relativa(desde_nuevo, destino_nuevo(local))
        if href != unquote(ruta):
            nuevo = md(m.group("texto"), f"{href}#{ancla}" if ancla else href)
            reemplazos.append((m.start(), m.end(), nuevo))
    for m in _TRANSCLUSION.finditer(oculto):
        local = _ruta_local(m.group("ruta"), desde_viejo)
        if local is None:
            continue
        href = relativa(desde_nuevo, destino_nuevo(local))
        if href != m.group("ruta"):
            reemplazos.append((m.start(), m.end(), f"![[{href}{m.group('resto') or ''}]]"))

    salida = texto
    for inicio, fin, nuevo in sorted(reemplazos, reverse=True):
        salida = salida[:inicio] + nuevo + salida[fin:]
    return salida
