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
from collections.abc import Mapping
from datetime import date
from pathlib import Path

from tuku import archivo, link
from tuku.resultado import Resultado

VER_ADEMAS = "## Ver además"

#: El frontmatter de una nota: lo que va entre los dos primeros `---`.
_FRONTMATTER = re.compile(r"\A---\n(?P<cuerpo>.*?)\n---\n", re.S)


def aliases(nota: str) -> list[str]:
    """Los otros nombres de la nota: `aliases: [a, b]`, o la lista YAML en bloque.

    Es el campo que Obsidian usa para lo mismo; `tuku` lo lee sin Obsidian
    (`spec/notas.md`, "Enlazar al registrar").
    """
    m = _FRONTMATTER.match(nota)
    if m is None:
        return []
    lineas = m.group("cuerpo").splitlines()
    for i, linea in enumerate(lineas):
        if not linea.startswith("aliases:"):
            continue
        resto = linea.removeprefix("aliases:").strip()
        if resto.startswith("["):
            valores = resto.strip("[]").split(",")
        else:
            valores = []
            for siguiente in lineas[i + 1 :]:
                if not siguiente.lstrip().startswith("- "):
                    break
                valores.append(siguiente.lstrip().removeprefix("- "))
        return [v.strip().strip("\"'") for v in valores if v.strip().strip("\"'")]
    return []


def subtype(nota: str) -> str | None:
    """El `subtype` del frontmatter: el tipo de la nota en `### Tipos de nota`."""
    m = _FRONTMATTER.match(nota)
    if m is None:
        return None
    for linea in m.group("cuerpo").splitlines():
        if linea.startswith("subtype:"):
            return linea.removeprefix("subtype:").strip() or None
    return None


def titulo(nota: str, ruta: Path) -> str:
    """El `# Título` de la nota, o el nombre del archivo si no lo tiene."""
    for linea in nota.splitlines():
        if linea.startswith("# "):
            return linea.removeprefix("# ").strip()
    return ruta.stem


def nombres_enlazables(vault: Path) -> dict[str, list[str]]:
    """Cada nota de un tipo enlazable, con su título y sus `aliases`.

    La clave es la ruta relativa al vault, como la pide `link.enlazar_menciones`.
    Qué tipos se enlazan lo dice la columna "Enlazable" del libro de estilo.
    """
    from tuku.config import leer_config

    dir_notas = vault / "notas"
    if not dir_notas.is_dir() or not (vault / "LIBRO-DE-ESTILO.md").is_file():
        return {}
    tipos = set(leer_config(vault).tipos_enlazables)
    if not tipos:
        return {}
    nombres: dict[str, list[str]] = {}
    for ruta in sorted(dir_notas.glob("*.md")):
        texto = archivo.leer(ruta)
        if subtype(texto) in tipos:
            nombres[f"notas/{ruta.name}"] = [titulo(texto, ruta), *aliases(texto)]
    return nombres


def enlazar(
    vault: Path, cuerpo: str, desde: str, *, salvo: str | None = None
) -> tuple[str, tuple[str, ...]]:
    """`cuerpo` con la primera mención de cada nota enlazable enlazada, y los avisos.

    `salvo` es la ruta de una nota que no se enlaza: la que se está escribiendo.
    Un nombre que comparten dos notas queda sin link y vuelve como aviso.
    """
    nombres = {r: n for r, n in nombres_enlazables(vault).items() if r != salvo}
    enlazado, ambiguos = link.enlazar_menciones(cuerpo, nombres, desde)
    avisos = tuple(
        f"{a!r} nombra a más de una nota; quedó sin link. "
        "Enlázala a mano, o deja ese nombre en los aliases de una sola."
        for a in ambiguos
    )
    return enlazado, avisos


#: Un enlace de la sección "Ver además": markdown o wikilink, y lo que sigue.
_ENLACE = re.compile(rf"^\s*[*-]\s+{link.ENLACE}(?P<motivo>.*)$")


def slug(titulo: str) -> str:
    """El nombre de archivo de una nota, a partir de su título."""
    plano = unicodedata.normalize("NFKD", titulo).encode("ascii", "ignore").decode()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", plano.lower())).strip("-")


def crear(
    vault: Path,
    *,
    title: str,
    body: str,
    scope: str | None = None,
    today: date | None = None,
    rutas: Mapping[str, str] | None = None,
) -> Path:
    """Escribe la nota en `notas/` y devuelve su ruta. Idempotente.

    Si el archivo ya existe no lo toca: repetir la operación no duplica ni
    reescribe lo que el autor pueda haber editado a mano.

    El frontmatter lleva `type: Note`, que `reglas/types.md` asigna a todo lo de
    `notas/` y `spec/vault.md` exige en cualquier archivo que guarde
    conocimiento. Es distinto de `subtype`, la lista abierta que subdivide ese
    `Note` en las notas tipadas (`spec/notas.md`): solo lo declaran algunas, y
    TUKU todavía no lo escribe.
    """
    ruta = vault / "notas" / f"{slug(title)}.md"
    if ruta.exists():
        return ruta

    ver_ademas = ""
    if scope is not None:
        enlace = link.enlace_ambito(scope, f"notas/{ruta.name}", rutas)
        ver_ademas = (
            f"\n{VER_ADEMAS}\n\n"
            f"* {enlace} — el ámbito al que pertenece lo que esta nota explica.\n"
        )

    ruta.parent.mkdir(parents=True, exist_ok=True)
    contenido = (
        f"---\ntype: Note\ncreated: {(today or date.today()).isoformat()}\n---\n\n"
        f"# {title}\n\n{body.strip()}\n{ver_ademas}"
    )
    archivo.escribir(ruta, contenido)
    return ruta


def registro_de_constancia(
    nota: Path,
    *,
    hour: str,
    scope: str | None = None,
    rutas: Mapping[str, str] | None = None,
) -> str:
    """La línea de bitácora que deja constancia de la nota creada.

    Va en `AHORA.md`, así que los dos links son relativos a ese archivo.
    """
    prefijo = f"{link.enlace_ambito(scope, 'AHORA.md', rutas)} " if scope else ""
    nota_link = link.enlace(nota.stem, "AHORA.md", f"notas/{nota.name}")
    return f"- {hour} - {prefijo}**nota**: escribí la nota {nota_link}"


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

    if not slug(title):
        return Resultado.rechazo(
            f"{title!r} no sirve de título: sin letras ni números no hay nombre de archivo."
        )
    if scope:
        scope = scope_mod.canonico(vault, scope)
        if (rechazo := scope_mod.rechazo_si_no_existe(vault, scope)) is not None:
            return rechazo

    hoy = day or date.today()
    hora = hour or datetime.now().strftime("%H:%M")
    ruta = vault / "notas" / f"{slug(title)}.md"
    desde = f"notas/{ruta.name}"
    body, avisos = enlazar(vault, body, desde, salvo=desde)

    ahora_path = vault / "AHORA.md"
    pendiente: str | None = None
    if record and ahora_path.is_file():
        texto = archivo.leer(ahora_path)
        constancia = registro_de_constancia(
            ruta, hour=hora, scope=scope, rutas=scope_mod.rutas(vault)
        )
        if constancia not in texto:
            try:
                pendiente = add(texto, [constancia], day=encabezado_de(hoy))
            except ValueError as e:
                return Resultado.rechazo(str(e))

    crear(vault, title=title, body=body, scope=scope, today=hoy, rutas=scope_mod.rutas(vault))
    if pendiente is not None:
        archivo.escribir(ahora_path, pendiente)
        if scope:
            scope_mod.actualizar_pagina(vault, scope)

    return Resultado.hecho(f"nota creada en {ruta}.", avisos=avisos)


def lint_del_vault(vault: Path, nota: Path | None = None) -> Resultado:
    """Revisa una nota, o todas las de `notas/` si no se nombra ninguna."""
    rutas = [nota] if nota is not None else []
    if nota is None:
        dir_notas = vault / "notas"
        if dir_notas.is_dir():
            rutas = sorted(dir_notas.glob("*.md"))
    if not rutas:
        return Resultado.hecho("sin notas que revisar.")

    hallazgos = [
        f"{ruta.name}: {error}" for ruta in rutas for error in lint(archivo.leer(ruta))
    ]
    if not hallazgos:
        return Resultado.hecho("sin hallazgos.")
    return Resultado.rechazo("\n".join(hallazgos), error=False)


def renombrar_en_vault(vault: Path, viejo: str, nuevo: str) -> Resultado:
    """Renombra una nota y arregla lo que la enlazaba.

    El caso de uso de `tuku note rename`. Una nota se nombra en tres lugares a
    la vez: el archivo, su `# título` y cada enlace que la menciona, entre
    ellos la constancia que dejó el día que se creó. Renombrar solo el archivo
    rompe los enlaces sin decirlo.

    `viejo` y `nuevo` son títulos: el archivo sale del `slug` de cada uno, igual
    que al crearla, así que el autor nombra la nota como la nombra siempre.
    """
    from tuku import rename

    if not nuevo.strip():
        return Resultado.rechazo("falta el título nuevo. Pasa el nombre que quieres darle.")
    origen = vault / "notas" / f"{slug(viejo)}.md"
    destino = vault / "notas" / f"{slug(nuevo)}.md"
    if not origen.is_file():
        return Resultado.rechazo(
            f"no existe la nota {viejo!r} en notas/. Mira notas/ y confirma el título."
        )
    if origen == destino:
        return Resultado.hecho(f"la nota ya se llama {nuevo!r}: nada que hacer.")
    if destino.exists():
        return Resultado.rechazo(
            f"ya existe una nota {nuevo!r}. "
            f"Elige otro título, o funde las dos a mano y borra la que sobre."
        )

    origen.rename(destino)
    archivo.escribir(destino, rename.renombrar_titulo(archivo.leer(destino), nuevo.strip()))

    # Los enlaces apuntan al nombre del archivo, no al título: `notas/<slug>.md`.
    enlaces = 0
    for ruta in sorted(vault.rglob("*.md")):
        texto = archivo.leer(ruta)
        salida, n = rename.renombrar_enlaces(texto, origen.stem, destino.stem)
        if n:
            enlaces += n
            archivo.escribir(ruta, salida)

    detalle = f" ({enlaces} enlace(s) actualizado(s))" if enlaces else ""
    return Resultado.hecho(f"nota {viejo!r} renombrada a {nuevo!r}{detalle}.")
