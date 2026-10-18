"""tuku note create / tuku doctor note: el zettelkasten, en su versión mínima.

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
from collections.abc import Mapping, Sequence
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
    (`spec/notas.md`, "Enlazar notas").
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


def campo(nota: str, nombre: str) -> str | None:
    """Un campo de una línea del frontmatter, como `created` o `updated`."""
    m = _FRONTMATTER.match(nota)
    if m is None:
        return None
    for linea in m.group("cuerpo").splitlines():
        if linea.startswith(f"{nombre}:"):
            return linea.removeprefix(f"{nombre}:").strip() or None
    return None


def modificada(nota: str) -> str:
    """Cuándo se tocó por última vez: `updated`, o `created` si no lo tiene, o vacío."""
    return campo(nota, "updated") or campo(nota, "created") or ""


def con_updated(nota: str, hoy: date) -> str:
    """La nota con `updated: hoy` en su frontmatter, que se crea si falta.

    Va tras `created` si está, y si no, al final del frontmatter. Una nota sin
    frontmatter queda igual: no se inventa uno.
    """
    m = _FRONTMATTER.match(nota)
    if m is None:
        return nota
    lineas = [x for x in m.group("cuerpo").splitlines() if not x.startswith("updated:")]
    marca = f"updated: {hoy.isoformat()}"
    pos = next((i + 1 for i, x in enumerate(lineas) if x.startswith("created:")), len(lineas))
    lineas.insert(pos, marca)
    return "---\n" + "\n".join(lineas) + "\n---\n" + nota[m.end() :]


def titulo(nota: str, ruta: Path) -> str:
    """El `# Título` de la nota, o el nombre del archivo si no lo tiene."""
    for linea in nota.splitlines():
        if linea.startswith("# "):
            return linea.removeprefix("# ").strip()
    return ruta.stem


#: Un enlace de la sección "Ver además": markdown o wikilink, y lo que sigue.
_ENLACE = re.compile(rf"^\s*[*-]\s+{link.ENLACE}(?P<motivo>.*)$")


def _links_del_cuerpo(cuerpo: str, desde: str) -> list[tuple[str, str]]:
    """Los links locales del cuerpo, como (texto, destino) y una vez por nota."""
    vistos: set[str] = set()
    salida = []
    for _, texto, ruta, destino in link.salientes(cuerpo, desde):
        if ruta not in vistos:
            vistos.add(ruta)
            salida.append((texto, destino))
    return salida


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
    subtype: str | None = None,
    menciones: Sequence[tuple[str, str]] = (),
) -> Path:
    """Escribe la nota en `notas/` y devuelve su ruta. Idempotente.

    Si el archivo ya existe no lo toca: repetir la operación no duplica ni
    reescribe lo que el autor pueda haber editado a mano.

    El frontmatter lleva `type: Note`, que `reglas/types.md` asigna a todo lo de
    `notas/` y `spec/vault.md` exige en cualquier archivo que guarde
    conocimiento. Es distinto de `subtype`, la lista abierta que subdivide ese
    `Note` en las notas tipadas (`spec/notas.md`): solo lo declaran algunas, y
    se escribe si se pasa `subtype`.

    `menciones` son los links del cuerpo, como (texto, destino): cada uno entra a
    `## Ver además` con un motivo mecánico, porque esa sección lista todos los
    enlaces salientes de la nota.
    """
    ruta = vault / "notas" / f"{slug(title)}.md"
    if ruta.exists():
        return ruta

    items = []
    if scope is not None:
        enlace = link.enlace_ambito(scope, f"notas/{ruta.name}", rutas)
        items.append(f"* {enlace} — el ámbito al que pertenece lo que esta nota explica.")
    items += [
        f"* [{texto}]({destino}) — mencionada en el cuerpo." for texto, destino in menciones
    ]
    ver_ademas = f"\n{VER_ADEMAS}\n\n" + "\n".join(items) + "\n" if items else ""

    marca_subtype = f"subtype: {subtype}\n" if subtype else ""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    creada = (today or date.today()).isoformat()
    contenido = (
        f"---\ntype: Note\n{marca_subtype}created: {creada}\nupdated: {creada}\n---\n\n"
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
    hallazgos += _enlaces_sin_listar(lineas, ini)
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


def _enlaces_sin_listar(lineas: list[str], ini: int) -> list[str]:
    """Los enlaces del cuerpo que `## Ver además` (en la línea `ini`) no lista.

    La sección es la lista de todos los enlaces salientes de la nota: uno que el
    cuerpo usa y ella no nombra no tiene motivo escrito.
    """
    desde = "notas/nota.md"
    listados = {ruta for _, _, ruta, _ in link.salientes("\n".join(lineas[ini:]), desde)}
    hallazgos = []
    vistos: set[str] = set()
    for n, texto, ruta, destino in link.salientes("\n".join(lineas[:ini]), desde):
        if ruta in listados or ruta in vistos:
            continue
        vistos.add(ruta)
        hallazgos.append(
            f"línea {n}: error: el cuerpo enlaza a {ruta} y `{VER_ADEMAS}` no lo lista. "
            f"Agrega `* [{texto}]({destino}) — para qué conecta` en esa sección."
        )
    return hallazgos


def _rechazo_de_subtype(vault: Path, subtype: str) -> Resultado | None:
    """El rechazo de un `--subtype` que `### Tipos de nota` no lista, o `None` si sirve."""
    from tuku.config import leer_config

    tipos = leer_config(vault).tipos_nota
    if subtype in tipos:
        return None
    hay = ", ".join(f"`{t}`" for t in tipos) or "ninguno"
    return Resultado.rechazo(
        f"{subtype!r} no es un tipo de nota. Los de `### Tipos de nota` en "
        f"LIBRO-DE-ESTILO.md son: {hay}. Elige uno, o agrega una fila a esa tabla para "
        "crear el tipo nuevo."
    )


def crear_con_constancia(
    vault: Path,
    *,
    title: str,
    body: str,
    scope: str | None = None,
    day: date | None = None,
    hour: str | None = None,
    record: bool = True,
    subtype: str | None = None,
) -> Resultado:
    """Escribe la nota y deja constancia en la bitácora. Idempotente.

    Con `subtype` la nota es tipada: debe ser una fila de `### Tipos de nota` del
    libro de estilo, y si no lo es se rechaza nombrando los que hay. Agregar un
    tipo es agregar una fila a esa tabla.

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
    from tuku.entry import stamp

    if not slug(title):
        return Resultado.rechazo(
            f"{title!r} no sirve de título: sin letras ni números no hay nombre de archivo."
        )
    if subtype is not None:
        subtype = subtype.strip().lower()
        if (rechazo := _rechazo_de_subtype(vault, subtype)) is not None:
            return rechazo
    tree = scope_mod.read_tree(vault)
    if scope:
        resolved = scope_mod.resolve_scope(tree, scope)
        if isinstance(resolved, Resultado):
            return resolved
        scope = resolved

    hoy = day or date.today()
    hora = hour or datetime.now().strftime("%H:%M")
    ruta = vault / "notas" / f"{slug(title)}.md"
    desde = f"notas/{ruta.name}"
    menciones = _links_del_cuerpo(body, desde)

    ahora_path = vault / "AHORA.md"
    pendiente: str | None = None
    if record and ahora_path.is_file():
        texto = archivo.leer(ahora_path)
        constancia = registro_de_constancia(ruta, hour=hora, scope=scope, rutas=tree.paths)
        if constancia not in texto:
            stamped = stamp(texto, [constancia], day=hoy)
            if isinstance(stamped, Resultado):
                return stamped
            pendiente = stamped

    crear(
        vault,
        title=title,
        body=body,
        scope=scope,
        today=hoy,
        rutas=tree.paths,
        subtype=subtype,
        menciones=menciones,
    )
    if pendiente is not None:
        archivo.escribir(ahora_path, pendiente)
        if scope:
            scope_mod.actualizar_pagina(vault, scope)

    return Resultado.hecho(f"nota creada en {ruta}.")


def lint_del_vault(vault: Path, nota: Path | None = None) -> Resultado:
    """Revisa una nota, o todas las de `notas/` si no se nombra ninguna."""
    rutas = [nota] if nota is not None else []
    if nota is None:
        dir_notas = vault / "notas"
        if dir_notas.is_dir():
            # `AGENTS.md` instruye al agente que escribe en `notas/`: no es una nota.
            rutas = sorted(r for r in dir_notas.glob("*.md") if r.name != "AGENTS.md")
    if not rutas:
        return Resultado.hecho("sin notas que revisar.")

    hallazgos = [
        f"{ruta.name}: {error}" for ruta in rutas for error in lint(archivo.leer(ruta))
    ]
    if not hallazgos:
        return Resultado.hecho("sin hallazgos.")
    return Resultado.rechazo("\n".join(hallazgos), error=False)


def renombrar_en_vault(
    vault: Path, viejo: str, nuevo: str, hoy: date | None = None
) -> Resultado:
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
    renombrada = rename.renombrar_titulo(archivo.leer(destino), nuevo.strip())
    archivo.escribir(destino, con_updated(renombrada, hoy or date.today()))

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
