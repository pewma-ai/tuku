"""tuku scope create / tuku doctor scope: el árbol de ámbitos.

Fase 3 de `devel/epics.md`, versión mínima. Lo que distingue a cada
nodo de `ambitos/` es qué carga, no dónde está (`spec/ambitos.md`):

| Rol | Cómo se reconoce |
| --- | --- |
| Ámbito | Directorio **con** página propia |
| Categoría | Directorio **sin** página propia |
| Actividad | Archivo `.md` en minúscula |

De ahí la única regla verificable sin un árbol profundo, y la que `doctor scope`
comprueba: **los registros apuntan a una actividad o a un ámbito, nunca a una
categoría.** Una categoría agrupa y no tiene de qué hablar.

Un ámbito nuevo lleva solo su página. `AGENTS.md`, `CADENCIAS.md` y
`CAPACIDAD.md` de una carpeta existen cuando el autor les pone su primera regla,
cadencia o costo: ausente significa vacío.

Los ámbitos se anidan: `crear` acepta un padre y `mover_en_vault` cambia un
ámbito de lugar. Un registro nombra el ámbito por su nombre, sin ruta, así que
los nombres son únicos en todo el árbol.

**Qué lee y escribe:** crea y mueve directorios bajo `ambitos/`, y al moverlos
reescribe los links del vault que los nombran. `lint` solo lee, y además
`AHORA.md`.
**A mano:** crear la carpeta con su página (dentro de la del padre, si lo hay), y
poner la línea `keywords: []` en su frontmatter.
"""

from __future__ import annotations

import os
import re
import unicodedata
from collections.abc import Mapping, Sequence
from datetime import date, datetime
from pathlib import Path

from tuku import archivo, link
from tuku.resultado import Resultado
from tuku.scope_tree import (
    KEYWORDS_LINE,
)
from tuku.scope_tree import (
    Ambito as Ambito,
)
from tuku.scope_tree import (
    Tree as Tree,
)
from tuku.scope_tree import (
    canonico as canonico,
)
from tuku.scope_tree import (
    carpeta as carpeta,
)
from tuku.scope_tree import (
    case_clash as case_clash,
)
from tuku.scope_tree import (
    directorio_de as directorio_de,
)
from tuku.scope_tree import (
    igual_nombre as igual_nombre,
)
from tuku.scope_tree import (
    keyword_key as keyword_key,
)
from tuku.scope_tree import (
    keywords as keywords,
)
from tuku.scope_tree import (
    leer as leer,
)
from tuku.scope_tree import (
    merge_keywords as merge_keywords,
)
from tuku.scope_tree import (
    nombres as nombres,
)
from tuku.scope_tree import (
    normalizar as normalizar,
)
from tuku.scope_tree import (
    page_of as page_of,
)
from tuku.scope_tree import (
    palabras_de as palabras_de,
)
from tuku.scope_tree import (
    read_tree as read_tree,
)
from tuku.scope_tree import (
    rechazo_si_no_existe as rechazo_si_no_existe,
)
from tuku.scope_tree import (
    reject_bad_keywords as reject_bad_keywords,
)
from tuku.scope_tree import (
    resolve_scope as resolve_scope,
)
from tuku.scope_tree import (
    rutas as rutas,
)

_PARENT = re.compile(r"^parent:[ \t]*(?P<ruta>.*?)[ \t]*$", re.M)


def _rechazo_de_nombre(nombre: str) -> Resultado | None:
    if not nombre or "/" in nombre or nombre in (".", ".."):
        return Resultado.rechazo(
            f"{nombre!r} no sirve de nombre de ámbito. "
            f"Usa un nombre sin barras, como el de una carpeta."
        )
    return None


def _sin_padre(padre: str) -> str:
    return (
        f"no existe el ámbito {padre!r} para ponerlo de padre. "
        f"Créalo con `tuku scope create {padre}` si el autor lo pide."
    )


def resolver_padre(vault: Path, parent: str) -> Path | Resultado:
    """La carpeta que nombra `--parent`: un nombre o una ruta de nombres desde `ambitos/`.

    `clientes` basta si hay una sola carpeta con ese nombre; si hay varias se
    rechaza y se nombran sus rutas. `negocio/clientes` baja segmento a segmento. En
    una ruta, el último segmento puede no existir: es una categoría nueva (carpeta
    sin página) y la crea el comando que la usa, bajo un padre que sí existe.
    """
    raiz = vault / "ambitos"
    segmentos = [normalizar(x) for x in parent.split("/") if x.strip()]
    if not segmentos:
        return Resultado.rechazo(_sin_padre(parent))
    if len(segmentos) == 1:
        nombre = canonico(vault, segmentos[0])
        carpetas = [p for p in sorted(raiz.rglob("*")) if p.is_dir() and p.name == nombre]
        if not carpetas:
            return Resultado.rechazo(_sin_padre(nombre))
        if len(carpetas) > 1:
            rutas_ = ", ".join(f"`{c.relative_to(raiz).as_posix()}`" for c in carpetas)
            return Resultado.rechazo(
                f"{nombre!r} es ambiguo: hay {len(carpetas)} carpetas con ese nombre. "
                f"Di la ruta completa: {rutas_}."
            )
        return carpetas[0]
    actual = raiz
    for i, segmento in enumerate(segmentos):
        hijo = (
            next(
                (
                    c
                    for c in sorted(actual.iterdir())
                    if c.is_dir() and igual_nombre(c.name, segmento)
                ),
                None,
            )
            if actual.is_dir()
            else None
        )
        if hijo is None:
            if i == len(segmentos) - 1:
                return actual / segmento
            ruta = "/".join(segmentos[: i + 1])
            return Resultado.rechazo(
                f"no existe {ruta!r} en ambitos/. Créalo con `tuku scope create {segmento}` "
                f"si el autor lo pide."
            )
        actual = hijo
    return actual


def crear(
    vault: Path,
    name: str,
    padre: Path | None = None,
    palabras: Sequence[str] = (),
    today: date | None = None,
) -> Path:
    """Crea el ámbito `name` en la carpeta `padre`, o bajo `ambitos/`. Idempotente.

    Si ya existe no toca nada: `spec/ambitos.md` no admite dos ámbitos con el
    mismo nombre, y volver a crearlo no es un error del autor. Las `palabras`
    son las `keywords` de la página nueva; el nombre no va en la lista, porque ya es
    el de la carpeta. `today` fecha la sección de actividad cuando `AHORA.md` no trae
    ciclo del que tomarla.
    """
    valor = normalizar(name)
    directorio = (padre or vault / "ambitos") / valor
    directorio.mkdir(parents=True, exist_ok=True)

    pagina = page_of(directorio)
    if not pagina.exists():
        rel = os.path.relpath(vault / "ambitos" / "PENDIENTES-AMBITOS.md", directorio)
        rel = rel.replace(os.sep, "/")
        lista = ", ".join(merge_keywords([], palabras, valor))
        base = f"---\ntype: Scope\nkeywords: [{lista}]\n---\n# {valor}\n\n![[{rel}#^{valor}]]\n"
        ahora_file = vault / "AHORA.md"
        ahora_texto = archivo.leer(ahora_file) if ahora_file.is_file() else ""
        texto = actualizar_contenido_pagina(
            base, ahora_texto, valor, pagina=pagina.relative_to(vault).as_posix(), hoy=today
        )
        archivo.escribir(pagina, texto)

    if (vault / "PENDIENTES.md").is_file():
        from tuku import regenerate

        regenerate.rehacer(vault, ["ambitos/", "AHORA.md", "bitacoras/"])

    return directorio


#: El título del callout con los hijos, que lleva la página del padre. El `+` lo deja
#: desplegado y plegable en Obsidian.
_HIJOS = "> [!abstract]+ En "
_TITULO_DE_HIJOS = re.compile(r"^> \[!abstract\][+-]? En ")


def _bloque_de_hijos(lineas: list[str]) -> tuple[int, int] | None:
    """Dónde está el callout de hijos en las líneas de una página: `[inicio, fin)`."""
    inicio = next((i for i, x in enumerate(lineas) if _TITULO_DE_HIJOS.match(x)), None)
    if inicio is None:
        return None
    fin = inicio + 1
    while fin < len(lineas) and lineas[fin].startswith(">"):
        fin += 1
    return inicio, fin


def _titulo_de_hijos(padre: Path, texto: str) -> str:
    from tuku import regenerate

    return f"{_HIJOS}**{regenerate.display_name(padre.name, texto)}**:"


def _lineas_de_hijos(base: Path, carpeta: Path, nivel: int = 0) -> list[str]:
    """El cuerpo del callout de hijos de `base`, desde `carpeta`.

    Primero los ámbitos (los que tienen página) en orden alfabético; después cada
    categoría (carpeta sin página) como un callout interior plegable con sus ámbitos,
    también por orden alfabético y separado por `---`. Una categoría sin ámbitos no sale.
    El orden es siempre el mismo: lo escriba `create`, `move` o `regenerate`.
    """
    from tuku import regenerate

    marca = "> " * (nivel + 1)
    hijos = sorted(h for h in carpeta.iterdir() if h.is_dir() and not h.name.startswith("."))
    lineas = [
        f"{marca}- {link.md(h.name, os.path.relpath(page_of(h), base).replace(os.sep, '/'))}"
        for h in hijos
        if page_of(h).is_file()
    ]
    for categoria in (h for h in hijos if not page_of(h).is_file()):
        interior = _lineas_de_hijos(base, categoria, nivel + 1)
        if not interior:
            continue
        titulo = regenerate.display_name(categoria.name)
        if lineas:
            lineas.append(f"{marca}---")
        lineas += [f"{marca}> [!abstract]+ {titulo}", *interior]
    return lineas


def _sin_bloque(lineas: list[str], inicio: int, fin: int) -> None:
    """Quita el bloque `[inicio, fin)` y la línea en blanco que lo separaba."""
    antes = inicio - 1 if inicio > 0 and not lineas[inicio - 1].strip() else inicio
    del lineas[antes:fin]


def _con_hijos(padre: Path, texto: str) -> str:
    """El texto de la página con el callout de hijos hecho desde las carpetas, o sin callout."""
    lineas = texto.splitlines()
    bloque = _bloque_de_hijos(lineas)
    cuerpo = _lineas_de_hijos(padre, padre)
    if not cuerpo:
        if bloque is not None:
            _sin_bloque(lineas, *bloque)
    else:
        callout = [_titulo_de_hijos(padre, texto), *cuerpo]
        if bloque is not None:
            lineas[bloque[0] : bloque[1]] = callout
        else:
            ancla = next((i for i, x in enumerate(lineas) if x.startswith("![[")), None)
            if ancla is None:
                ancla = next(
                    (i for i, x in enumerate(lineas) if x.startswith("# ")), len(lineas) - 1
                )
            nuevo = ["", *callout]
            if ancla + 1 < len(lineas) and lineas[ancla + 1].strip():
                nuevo.append("")
            lineas[ancla + 1 : ancla + 1] = nuevo
    return "\n".join(lineas) + "\n"


def refrescar_hijos(carpeta: Path) -> None:
    """Rehace el callout de hijos del ámbito al que `carpeta` pertenece.

    Es el ámbito más cercano que la contiene (ella misma si tiene página): una
    categoría no tiene página, así que lo que cuelga de `clientes/` se lista en
    `negocio.md`. Siempre lo deriva de las carpetas, así que `scope create`,
    `scope move` y `scope rename` dejan lo mismo que `tuku regenerate scope`.
    """
    for d in (carpeta, *carpeta.parents):
        if d.name == "ambitos":
            return
        if page_of(d).is_file():
            pagina = page_of(d)
            texto = archivo.leer(pagina)
            salida = _con_hijos(d, texto)
            if salida != texto:
                archivo.escribir(pagina, salida)
            return


def _frontmatter(texto: str) -> tuple[int, int] | None:
    """El frontmatter de una página como `[inicio, fin)`, sin los `---`."""
    if not texto.startswith("---\n"):
        return None
    fin = texto.find("\n---", 3)
    return (4, fin) if fin != -1 else None


def parent_de(pagina: str) -> str | None:
    """El `parent:` del frontmatter de una página de ámbito, o `None` si no lo declara."""
    rango = _frontmatter(pagina)
    if rango is None:
        return None
    m = _PARENT.search(pagina[rango[0] : rango[1]])
    return m.group("ruta") if m and m.group("ruta") else None


def _parent_esperado(vault: Path, directorio: Path) -> str | None:
    """La carpeta que contiene al ámbito, desde `ambitos/`, como se dice en `--parent`.

    `None` si el ámbito cuelga de `ambitos/`.
    """
    raiz = vault / "ambitos"
    padre = directorio.parent
    return None if padre == raiz else padre.relative_to(raiz).as_posix()


def _con_parent(texto: str, parent: str | None) -> str:
    """La página con `parent:` en su frontmatter, al final; sin la línea si no hay padre."""
    rango = _frontmatter(texto)
    if rango is None:
        return texto
    inicio, fin = rango
    lineas = [x for x in texto[inicio:fin].splitlines() if not x.startswith("parent:")]
    if parent:
        lineas.append(f"parent: {parent}")
    return texto[:inicio] + "\n".join(lineas) + texto[fin:]


def regenerar_parent(vault: Path) -> list[Path]:
    """Pone en cada página de ámbito el `parent:` que dice su carpeta. Devuelve lo que cambió.

    La carpeta manda: `parent` es su reflejo en el frontmatter, para que Obsidian y
    cualquier lector de propiedades vean dónde cuelga el ámbito sin recorrer rutas.
    """
    cambiados: list[Path] = []
    for a in leer(vault):
        pagina = page_of(a.directorio)
        texto = archivo.leer(pagina)
        salida = _con_parent(texto, _parent_esperado(vault, a.directorio))
        if salida != texto:
            archivo.escribir(pagina, salida)
            cambiados.append(pagina)
    return cambiados


def regenerar_hijos(vault: Path) -> list[Path]:
    """Recrea el callout de hijos de cada ámbito desde las carpetas. Devuelve lo que cambió.

    Es la forma de repararlo: se rehace entero, sin conservar lo que el autor
    hubiera puesto a mano en él. Un ámbito sin hijos queda sin callout.
    """
    cambiados: list[Path] = []
    for a in leer(vault):
        pagina = page_of(a.directorio)
        if not pagina.is_file():
            continue
        texto = archivo.leer(pagina)
        salida = _con_hijos(a.directorio, texto)
        if salida != texto:
            archivo.escribir(pagina, salida)
            cambiados.append(pagina)
    return cambiados


def retitular_hijos(directorio: Path) -> None:
    """Pone al callout de hijos el nombre que tiene ahora el ámbito."""
    pagina = page_of(directorio)
    if not pagina.is_file():
        return
    texto = archivo.leer(pagina)
    lineas = texto.splitlines()
    bloque = _bloque_de_hijos(lineas)
    if bloque is None:
        return
    lineas[bloque[0]] = _titulo_de_hijos(directorio, texto)
    archivo.escribir(pagina, "\n".join(lineas) + "\n")


def extraer_actividad_ambito(
    ahora: str, nombre_ambito: str, *, pagina: str | None = None, origen: str = "AHORA.md"
) -> dict[str, list[str]]:
    """Extrae las líneas de bitácora vinculadas al ámbito, agrupadas por día.

    Omite la hora `- HH:MM - ` dejando `- cuerpo`.
    Remueve auto-enlaces al propio ámbito:
    - Si inicia con el enlace al ámbito, elimina el prefijo.
    - Si aparece dentro del texto, lo reemplaza por el nombre a secas.

    El enlace se reconoce en cualquiera de los dos formatos. Los demás links de
    la línea se copian a la página del ámbito, que vive en otra carpeta, así que
    sus rutas se recalculan desde `origen` (`AHORA.md`, o una bitácora cerrada) hacia
    `pagina` (por defecto, la forma plana `ambitos/<n>/<n>.md`).

    El orden de días y de líneas dentro de cada día es el mismo de `AHORA.md`.
    """
    from tuku.ahora import dias

    destino = pagina or f"ambitos/{nombre_ambito}/{nombre_ambito}.md"
    propio = re.compile(link.ENLACE)

    def es_el_ambito(m: re.Match[str]) -> bool:
        return link.nombre_de(m.group()) == nombre_ambito

    salida: dict[str, list[str]] = {}
    lineas = ahora.splitlines()

    lista_dias = dias(ahora)
    for idx, (ini, encabezado, _) in enumerate(lista_dias):
        fin = lista_dias[idx + 1][0] if idx + 1 < len(lista_dias) else len(lineas)
        for i in range(ini + 1, fin):
            if lineas[i].strip() == "---":
                fin = i
                break

        lineas_dia: list[str] = []
        for i in range(ini + 1, fin):
            m = re.match(r"^- (?:\d{2}:\d{2} - )?(.*)$", lineas[i])
            if m is None or not any(es_el_ambito(e) for e in propio.finditer(m.group(1))):
                continue
            cuerpo = m.group(1)
            primero = propio.match(cuerpo)
            if primero is not None and es_el_ambito(primero):
                cuerpo = cuerpo[primero.end() :].lstrip()
            cuerpo = propio.sub(
                lambda e: nombre_ambito if es_el_ambito(e) else e.group(), cuerpo
            )
            lineas_dia.append(f"- {link.rebasar(cuerpo, origen, destino)}")

        if lineas_dia:
            salida[encabezado] = lineas_dia

    return salida


def formatear_esta_semana(actividad: dict[str, list[str]]) -> str:
    """Formatea la sección `## Esta semana` con los días y líneas sin hora."""
    if not actividad:
        return "## Esta semana"

    bloques = ["## Esta semana"]
    for encabezado, lineas in actividad.items():
        sub = "### " + encabezado.removeprefix("## ").strip()
        bloques.append(sub)
        bloques.extend(lineas)

    return "\n".join(bloques)


#: Meses hacia atrás que cubre `## Actividad reciente` (`spec/ambitos.md`).
MESES_DE_ACTIVIDAD = 12


def _hace_doce_meses(hoy: date) -> date:
    anio, mes = divmod(hoy.year * 12 + hoy.month - 1 - MESES_DE_ACTIVIDAD, 12)
    dia = hoy.day
    while True:
        try:
            return date(anio, mes + 1, dia)
        except ValueError:
            dia -= 1


def actividad_reciente(
    cerradas: Sequence[tuple[str, str]],
    nombre_ambito: str,
    *,
    pagina: str,
    hoy: date,
) -> str:
    """La sección `## Actividad reciente`: los registros del ámbito en los ciclos cerrados.

    `cerradas` son las bitácoras, como (ruta desde el vault, texto). Entran los días
    de los últimos doce meses, agrupados bajo `### Octubre 2026`, del mes más reciente
    al más antiguo, y cada línea lleva su día: `- 12 - entregué 40 cuadernos`.
    """
    from tuku.ahora import fecha_del_dia, rango
    from tuku.init import MESES

    desde = _hace_doce_meses(hoy)
    por_mes: dict[tuple[int, int], list[tuple[date, str]]] = {}
    for ruta, texto in cerradas:
        limites = rango(texto)
        if limites is None or limites[1] < desde:
            continue
        for encabezado, lineas in extraer_actividad_ambito(
            texto, nombre_ambito, pagina=pagina, origen=ruta
        ).items():
            fecha = fecha_del_dia(encabezado, *limites)
            if fecha is None or fecha < desde:
                continue
            for linea in lineas:
                cuerpo = linea.removeprefix("- ")
                por_mes.setdefault((fecha.year, fecha.month), []).append(
                    (fecha, f"- {fecha.day} - {cuerpo}")
                )
    bloques = ["## Actividad reciente"]
    for anio, mes in sorted(por_mes, reverse=True):
        bloques.append(f"### {MESES[mes - 1].capitalize()} {anio}")
        bloques.extend(linea for _, linea in sorted(por_mes[(anio, mes)], key=lambda x: x[0]))
    return "\n".join(bloques)


def actualizar_contenido_pagina(
    contenido_actual: str,
    ahora_texto: str,
    nombre_ambito: str,
    *,
    pagina: str | None = None,
    cerradas: Sequence[tuple[str, str]] | None = None,
    hoy: date | None = None,
) -> str:
    """Actualiza o incorpora `## Esta semana` y `## Actividad reciente` en el ámbito.

    Con `cerradas` (las bitácoras de `bitacoras/`), `## Actividad reciente` se rehace
    desde ellas, contando los doce meses desde el inicio del ciclo abierto: lo derivado
    depende de lo canónico y no del reloj. Sin `cerradas` se conserva lo que la página
    ya trae.
    """
    from tuku.ahora import rango
    from tuku.init import MESES

    actividad = extraer_actividad_ambito(ahora_texto, nombre_ambito, pagina=pagina)
    seccion_semana = formatear_esta_semana(actividad).strip()

    limites = rango(ahora_texto) if ahora_texto else None
    fecha_ref = limites[0] if limites else hoy
    vacia = "## Actividad reciente"
    if fecha_ref is not None:
        vacia += f"\n### {MESES[fecha_ref.month - 1].capitalize()} {fecha_ref.year}"

    partes_semana = contenido_actual.split("## Esta semana", 1)
    base = partes_semana[0].rstrip()

    if cerradas is not None and fecha_ref is not None:
        destino = pagina or f"ambitos/{nombre_ambito}/{nombre_ambito}.md"
        seccion_reciente = actividad_reciente(
            cerradas, nombre_ambito, pagina=destino, hoy=hoy or fecha_ref
        )
    elif "## Actividad reciente" in contenido_actual:
        parte_reciente = contenido_actual.split("## Actividad reciente", 1)[1].rstrip()
        if not parte_reciente.strip():
            seccion_reciente = vacia
        else:
            seccion_reciente = f"## Actividad reciente{parte_reciente}"
    else:
        seccion_reciente = vacia

    return f"{base}\n\n{seccion_semana}\n\n{seccion_reciente}\n"


def actualizar_pagina(vault: Path, nombre: str) -> Path | None:
    """Regenera la actividad en la página del ámbito. Devuelve la ruta si cambió."""
    pagina = page_of(carpeta(vault, nombre))
    if not pagina.is_file():
        return None
    ahora_path = vault / "AHORA.md"
    if not ahora_path.is_file():
        return None
    ahora_texto = archivo.leer(ahora_path)
    actual = archivo.leer(pagina)
    cerradas = [
        (b.relative_to(vault).as_posix(), archivo.leer(b))
        for b in sorted((vault / "bitacoras").glob("*.md"))
    ]
    nuevo = actualizar_contenido_pagina(
        actual,
        ahora_texto,
        nombre,
        pagina=pagina.relative_to(vault).as_posix(),
        cerradas=cerradas,
    )
    if nuevo != actual:
        archivo.escribir(pagina, nuevo)
        return pagina
    return None


def categorias(vault: Path) -> list[str]:
    """Los directorios de `ambitos/` sin página propia: agrupan y nada más."""
    raiz = vault / "ambitos"
    if not raiz.is_dir():
        return []
    return sorted(d.name for d in raiz.rglob("*") if d.is_dir() and not page_of(d).is_file())


def lint_categorias(ahora: str, *, categorias: list[str]) -> list[str]:
    """Registros que apuntan a una categoría. No escribe nada."""
    hallazgos = []
    for n, linea in enumerate(ahora.splitlines(), start=1):
        for destino in link.nombres_enlazados(linea):
            if destino in categorias:
                hallazgos.append(
                    f"AHORA.md:{n}: error: {destino} es una categoría, y un registro "
                    f"no puede apuntar a una. Apúntalo al ámbito o a la actividad que "
                    f"corresponda, o dale a {destino} su página propia para volverlo ámbito."
                )
    return hallazgos


def lint_transclusiones(vault: Path) -> list[str]:
    """Comprueba que todas las páginas de ámbito transcluyan sus pendientes."""
    hallazgos = []
    for a in leer(vault):
        pagina = a.directorio / f"{a.nombre}.md"
        contenido = archivo.leer(pagina)
        patron = rf"!\[\[[^\]]*PENDIENTES-AMBITOS(?:\.md)?#\^{re.escape(a.nombre)}\]\]"
        if not re.search(patron, contenido):
            rel = os.path.relpath(vault / "ambitos" / "PENDIENTES-AMBITOS.md", a.directorio)
            ruta_rel = pagina.relative_to(vault)
            hallazgos.append(
                f"{ruta_rel}: error: falta la transclusión a PENDIENTES-AMBITOS.md "
                f"(esperada: '![[{rel}#^{a.nombre}]]')."
            )
    return hallazgos


def lint_parent(vault: Path) -> list[str]:
    """Comprueba que el `parent:` de cada página diga en qué carpeta está el ámbito."""
    hallazgos = []
    for a in leer(vault):
        pagina = page_of(a.directorio)
        esperado = _parent_esperado(vault, a.directorio)
        actual = parent_de(archivo.leer(pagina))
        if actual != esperado:
            dice = f"`parent: {actual}`" if actual else "no declara `parent:`"
            debe = f"`parent: {esperado}`" if esperado else "ningún `parent:`"
            hallazgos.append(
                f"{pagina.relative_to(vault)}: error: la página {dice} y su carpeta pide "
                f"{debe}. Corre `tuku regenerate scope`."
            )
    return hallazgos


def lint_callouts(vault: Path) -> list[str]:
    """Comprueba que en PENDIENTES-AMBITOS.md exista un callout por cada ámbito."""
    ruta = vault / "ambitos" / "PENDIENTES-AMBITOS.md"
    if not ruta.is_file():
        return [
            "ambitos/PENDIENTES-AMBITOS.md: error: falta el archivo. "
            "Corre `tuku regenerate todo` para generarlo."
        ]
    contenido = archivo.leer(ruta)
    hallazgos = []
    for a in leer(vault):
        patron = rf">\s*\[!todo\].*\^{re.escape(a.nombre)}(?:\s|$)"
        if not re.search(patron, contenido):
            hallazgos.append(
                f"ambitos/PENDIENTES-AMBITOS.md: error: falta el callout para el ámbito "
                f"'{a.nombre}' (esperado: '^{a.nombre}'). Corre `tuku regenerate todo`."
            )
    return hallazgos


def lint(
    vault_o_ahora: Path | str,
    *,
    categorias: list[str] | None = None,
) -> list[str]:
    """Linter del árbol de ámbitos.

    Si recibe un Path (vault), revisa registros contra categorías, transclusiones
    en páginas de ámbito y callouts en PENDIENTES-AMBITOS.md. Si recibe str, revisa
    registros contra categorías.
    """
    if isinstance(vault_o_ahora, str):
        return lint_categorias(vault_o_ahora, categorias=categorias or [])

    vault = vault_o_ahora
    hallazgos: list[str] = []
    ahora_path = vault / "AHORA.md"
    if ahora_path.is_file():
        cats = categorias if categorias is not None else globals()["categorias"](vault)
        hallazgos.extend(lint_categorias(archivo.leer(ahora_path), categorias=cats))
    hallazgos.extend(lint_transclusiones(vault))
    hallazgos.extend(lint_parent(vault))
    hallazgos.extend(lint_callouts(vault))
    return hallazgos


#: El cuerpo de la constancia que deja `scope create` en la bitácora.
CONSTANCIA = "**nota**: abrí el ámbito"


def registro_de_constancia(
    nombre: str,
    *,
    hour: str,
    rutas: Mapping[str, str] | None = None,
    bajo: str | None = None,
) -> str:
    """La línea de bitácora que deja constancia del ámbito creado, para `AHORA.md`.

    Con `bajo` (el ámbito padre como enlace, y las categorías que haya en medio por su
    nombre) la constancia dice dónde quedó: `abrí el ámbito bajo [negocio](…), en clientes`.
    """
    donde = f" bajo {bajo}" if bajo else ""
    return f"- {hour} - {link.enlace_ambito(nombre, 'AHORA.md', rutas)} {CONSTANCIA}{donde}"


def _donde_cuelga(vault: Path, carpeta: Path) -> tuple[Path | None, list[str]]:
    """El ámbito más cercano que contiene a `carpeta` y las categorías que hay entre ambos.

    Las categorías van de la más externa a la más interna. Una carpeta de `ambitos/`
    sin ningún ámbito arriba devuelve `None` y sus categorías.
    """
    categorias: list[str] = []
    raiz = vault / "ambitos"
    while carpeta != raiz and not page_of(carpeta).is_file():
        categorias.insert(0, carpeta.name)
        carpeta = carpeta.parent
    return (None if carpeta == raiz else carpeta), categorias


def crear_con_constancia(
    vault: Path,
    nombre: str,
    *,
    parent: str | None = None,
    day: date | None = None,
    hour: str | None = None,
    palabras: Sequence[str] = (),
    since: str | None = None,
    now: datetime,
) -> Resultado:
    """Crea el ámbito y deja constancia. No modifica nada de lo ya escrito.

    Lo que el autor ya había escrito sobre el frente queda como estaba: ningún
    comando enlaza ni cambia un body por su cuenta.

    Crear un ámbito es una decisión del autor sobre su estructura, así que deja
    huella en `AHORA.md`, en el día `day` (HOY si falta) y a la hora `hour` (AHORA
    si falta). Solo la deja quien crea la carpeta: correrlo sobre un ámbito que ya
    existe no escribe nada, ni en este ciclo ni en uno posterior.

    **Se rechaza antes de tocar nada:** lo que haría fallar la propagación, o un
    día fuera del ciclo abierto, se revisa antes de crear la carpeta, para que un
    rechazo no deje un ámbito a medias.

    Con `parent`, el ámbito va dentro de la carpeta de otro, que debe existir. Si
    el ámbito ya existe en otro lugar se rechaza y se nombra `scope move`.

    Las `palabras` son las `keywords` con que el autor nombra el ámbito sin decir
    su nombre. Si no vienen, la salida le pide al agente que las pregunte: el
    agente las lee de la página para saber de qué frente es algo que no lo nombra.

    La salida lista, desde `since` (7 días si falta), los registros de otros ámbitos
    que nombran al nuevo (`registros_que_nombran`), para moverlos con `tuku entry move`.
    Sobre un ámbito que ya existe vuelve a listar sin crear nada.
    """
    from tuku import context, entry, todo_core

    nombre = normalizar(nombre)
    if (rechazo := _rechazo_de_nombre(nombre)) is not None:
        return rechazo
    if (rechazo := reject_bad_keywords(palabras)) is not None:
        return rechazo
    try:
        inicio = context.desde(since, now.date(), DESDE_POR_DEFECTO)
    except ValueError as e:
        return Resultado.rechazo(str(e))
    palabras = palabras_de(palabras)
    if (otro := case_clash(vault, nombre)) is not None:
        return Resultado.rechazo(
            f"ya existe el ámbito {otro!r}, y los nombres no distinguen mayúsculas. "
            f"Usa {otro!r}, o elige otro nombre."
        )
    padre: Path | None = None
    if parent:
        resuelto = resolver_padre(vault, parent)
        if isinstance(resuelto, Resultado):
            return resuelto
        padre = resuelto
    existente = next((a.directorio for a in leer(vault) if a.nombre == nombre), None)
    if existente is not None and padre is not None and existente.parent != padre:
        return Resultado.rechazo(
            f"el ámbito {nombre!r} ya existe en {existente.relative_to(vault).as_posix()}. "
            f"Para ponerlo bajo {parent!r}: `tuku scope move {nombre} --parent {parent}`."
        )
    pendientes = vault / "PENDIENTES.md"
    if pendientes.is_file():
        try:
            todo_core.filas(archivo.leer(pendientes))
        except todo_core.SinTabla as e:
            return Resultado.rechazo(str(e))

    ahora_path = vault / "AHORA.md"
    nuevo = existente is None
    when = day or now.date()
    hora = hour or now.strftime("%H:%M")
    if nuevo and ahora_path.is_file():
        fits = entry.stamp(archivo.leer(ahora_path), [], day=when)
        if isinstance(fits, Resultado):
            return fits

    directorio = crear(
        vault,
        nombre,
        existente.parent if existente is not None else padre,
        palabras,
        today=now.date(),
    )
    if padre is not None:
        refrescar_hijos(padre)
    regenerar_parent(vault)
    pagina_path = directorio / f"{nombre}.md"
    if not nuevo and palabras:
        r = actualizar(vault, nombre, palabras)
        if not r.ok:
            return r
        return Resultado.hecho(
            "\n".join(filter(None, (r.mensaje, _registros_previos(vault, nombre, inicio)))),
            avisos=r.avisos,
        )
    if ahora_path.is_file() and pagina_path.is_file():
        original = archivo.leer(ahora_path)
        texto = original
        if nuevo:
            mapa = rutas(vault)
            bajo = None
            if padre is not None:
                ambito_padre, categorias = _donde_cuelga(vault, padre)
                bajo = " / ".join(categorias)
                if ambito_padre is not None:
                    bajo = link.enlace_ambito(ambito_padre.name, "AHORA.md", mapa) + (
                        f", en {bajo}" if bajo else ""
                    )
            constancia = registro_de_constancia(nombre, hour=hora, rutas=mapa, bajo=bajo)
            stamped = entry.stamp(texto, [constancia], day=when)
            if isinstance(stamped, Resultado):
                return stamped
            texto = stamped
        if texto != original:
            archivo.escribir(ahora_path, texto)
        actualizar_pagina(vault, nombre)
        if nuevo and padre is not None:
            ambito_padre, _ = _donde_cuelga(vault, padre)
            if ambito_padre is not None:
                # la constancia enlaza al padre, y la actividad de su página la cuenta
                actualizar_pagina(vault, ambito_padre.name)

    mensaje = f"ámbito creado en {directorio}." if nuevo else f"el ámbito {nombre} ya existe."
    if nuevo and not palabras:
        mensaje += "\n" + _pedir_keywords(nombre)
    if previos := _registros_previos(vault, nombre, inicio):
        mensaje += "\n" + previos
    avisos = avisos_de_keywords(vault, nombre, palabras) if nuevo else ()
    return Resultado.hecho(mensaje, avisos=avisos)


#: Días hacia atrás que busca `scope create` registros que nombran al ámbito nuevo.
DESDE_POR_DEFECTO = 7

_REGISTRO_LINEA = re.compile(r"^- (?:(?P<hora>\d{2}:\d{2}) - )?(?P<cuerpo>.*)$")


def _plegar(texto: str) -> str:
    """Sin mayúsculas, tildes ni guiones: `Los-Robles` y `los robles` son lo mismo."""
    plano = unicodedata.normalize("NFKD", texto)
    plano = "".join(c for c in plano if not unicodedata.combining(c)).lower()
    return " ".join(re.sub(r"[-_\s]+", " ", plano).split())


def registros_que_nombran(
    vault: Path, nombre: str, inicio: date
) -> tuple[list[tuple[date, str | None, str, str]], int]:
    """Los registros de otros ámbitos que nombran a `nombre`, y cuántas bitácoras quedan atrás.

    Nombrar es decir el nombre o una keyword del ámbito, por palabras completas y sin
    distinguir mayúsculas, tildes, guiones ni espacios. Cada registro vuelve como
    (día, hora, ámbito en que está, cuerpo). Lo segundo es el número de bitácoras
    cerradas anteriores a `inicio`, que esta búsqueda no leyó.
    """
    from tuku import context
    from tuku.ahora import rango

    pagina = page_of(carpeta(vault, nombre))
    claves = {_plegar(nombre), *(_plegar(k) for k in keywords(archivo.leer(pagina)))}
    patron = re.compile(
        "|".join(rf"(?<!\w){re.escape(c)}(?!\w)" for c in sorted(claves, key=len, reverse=True))
    )
    hallados: list[tuple[date, str | None, str, str]] = []
    for fecha, _, lineas in context.registros_desde(vault, inicio):
        for linea in lineas:
            m = _REGISTRO_LINEA.match(linea)
            if m is None:
                continue
            cuerpo = m.group("cuerpo")
            duenos = [
                n for e in re.finditer(link.ENLACE, cuerpo) if (n := link.nombre_de(e.group()))
            ]
            if nombre in duenos[:1]:
                continue
            if (inicial := re.match(link.ENLACE, cuerpo)) is not None:
                cuerpo = cuerpo[inicial.end() :].lstrip()
            sin_links = link.sin_links(cuerpo)
            if patron.search(_plegar(sin_links)):
                hallados.append(
                    (fecha, m.group("hora"), duenos[0] if duenos else "", sin_links)
                )
    anteriores = 0
    bitacoras = vault / "bitacoras"
    if bitacoras.is_dir():
        for b in bitacoras.glob("*.md"):
            limites = rango(archivo.leer(b))
            if limites is not None and limites[1] < inicio:
                anteriores += 1
    return hallados, anteriores


def _registros_previos(vault: Path, nombre: str, inicio: date) -> str:
    """El bloque de la salida de `scope create` con los registros que ya nombran al ámbito."""
    hallados, anteriores = registros_que_nombran(vault, nombre, inicio)
    lineas: list[str] = []
    if hallados:
        lineas.append(
            f"Registros de otros ámbitos que nombran a {nombre!r} "
            f"desde el {inicio.isoformat()}. "
            "Decide con el autor cuáles son del ámbito y muévelos con "
            f"`tuku entry move AAAA-MM-DD HH:MM --match TEXTO --scope {nombre}`:"
        )
        for fecha, hora, dueno, cuerpo in hallados:
            cuando = f"{fecha.isoformat()} {hora}" if hora else fecha.isoformat()
            lineas.append(f"- {cuando} ({dueno or 'sin ámbito'}): {cuerpo}")
    if anteriores:
        lineas.append(
            f"Hay {anteriores} bitácoras cerradas más antiguas que el {inicio.isoformat()}: "
            "pregunta al autor hasta cuándo buscar y repite con `--since`."
        )
    return "\n".join(lineas)


def _claves_de(vault: Path) -> dict[str, set[str]]:
    """Por ámbito, las palabras con que se lo nombra: su nombre y sus keywords."""
    return {
        a.nombre: {keyword_key(a.nombre), *(keyword_key(k) for k in a.keywords)}
        for a in leer(vault)
    }


def _aviso_de_palabra(palabra: str, duenos: Sequence[str], de: str | None = None) -> str:
    otros = " y ".join(duenos)
    donde = f"{de} y {otros}" if de else otros
    return (
        f"la palabra {palabra!r} nombra a más de un ámbito ({donde}): con ella, el agente no "
        "puede elegir sin preguntar. Si no es a propósito, quita la de uno en el frontmatter "
        "de su página."
    )


def avisos_de_keywords(vault: Path, nombre: str, palabras: Sequence[str]) -> tuple[str, ...]:
    """Un aviso por cada una de `palabras` que ya nombra a otro ámbito distinto de `nombre`.

    Avisa y no rechaza: una palabra compartida puede ser a propósito
    (`spec/ambitos.md`), y `tuku doctor scope` la vuelve a nombrar como pregunta.
    """
    claves = _claves_de(vault)
    avisos = []
    for palabra in palabras:
        duenos = [n for n, cs in claves.items() if n != nombre and keyword_key(palabra) in cs]
        if duenos:
            avisos.append(_aviso_de_palabra(palabra, duenos, nombre))
    return tuple(avisos)


def keywords_repetidas(vault: Path) -> list[str]:
    """Las palabras que nombran a más de un ámbito, cada una como una pregunta.

    Lo que `tuku doctor scope` pregunta sin fallar: una keyword repetida hace
    ambiguo el ámbito de lo que el autor dice (la Paula de dos clientes).
    """
    ambitos = leer(vault)
    claves = _claves_de(vault)
    vistas: dict[str, str] = {}
    for a in ambitos:
        for k in a.keywords:
            vistas.setdefault(keyword_key(k), k)
    salida = []
    for clave, palabra in vistas.items():
        duenos = [n for n, cs in claves.items() if clave in cs]
        if len(duenos) > 1:
            salida.append(f"scope: pregunta: {_aviso_de_palabra(palabra, duenos)}")
    return salida


def _pedir_keywords(nombre: str) -> str:
    """Lo que la salida de `scope create` le pide al agente que haga con el autor."""
    return (
        f"Pregunta al autor qué palabras, cuando las mencione, indican que algo es de "
        f"{nombre!r}: siglas, sistemas, personas, proyectos (para `paranal`: vlti, gravity, "
        f"LCU, TCS, VLT). No son otros nombres del ámbito, son lo que lo delata. "
        f"No las inventes. Regístralas con `tuku scope update {nombre} --keyword PALABRA`, "
        f"repetible o separadas por coma: quedan en el frontmatter de la página y sirven "
        f"para elegir este ámbito cuando el autor las mencione, sin modificar lo que dice."
    )


def actualizar(vault: Path, nombre: str, nuevas: Sequence[str]) -> Resultado:
    """Suma `nuevas` a las `keywords` de la página del ámbito.

    Una keyword sirve para elegir el ámbito de lo que el autor dice, y no modifica ni
    enlaza lo que ya está escrito. Idempotente: lo que ya estaba, sin distinguir
    mayúsculas, guiones ni espacios, no se repite, y si nada es nuevo no escribe nada.
    """
    resolved = resolve_scope(read_tree(vault), nombre)
    if isinstance(resolved, Resultado):
        return resolved
    nombre = resolved
    if (rechazo := reject_bad_keywords(nuevas)) is not None:
        return rechazo
    if not palabras_de(nuevas):
        return Resultado.rechazo(
            f"nada que actualizar. Uso: `tuku scope update {nombre} --keyword PALABRA`."
        )
    pagina = page_of(carpeta(vault, nombre))
    texto = archivo.leer(pagina)
    if KEYWORDS_LINE.search(texto) is None:
        return Resultado.rechazo(
            f"la página de {nombre!r} no declara `keywords:` en su frontmatter. "
            f"Agrega la línea `keywords: []` a mano y vuelve a correrlo."
        )
    previas = keywords(texto)
    todas = merge_keywords(previas, nuevas, nombre)
    if todas == previas:
        return Resultado.hecho(f"{nombre!r} ya tenía esas keywords: {', '.join(previas)}.")
    archivo.escribir(
        pagina, KEYWORDS_LINE.sub(lambda _m: f"keywords: [{', '.join(todas)}]", texto, count=1)
    )
    nuevas_palabras = [k for k in todas if k not in previas]
    return Resultado.hecho(
        f"keywords de {nombre!r}: {', '.join(todas)}.",
        avisos=avisos_de_keywords(vault, nombre, nuevas_palabras),
    )


def renombrar_en_vault(vault: Path, viejo: str, nuevo: str) -> Resultado:
    """Renombra un ámbito y arregla todo lo que lo nombraba.

    Un ámbito no es una carpeta: es una carpeta, una página, un ancla de
    transclusión, las cabeceras de sus archivos y cada enlace
    del vault que apunta a él. Renombrar a mano cualquiera de esas piezas por
    separado deja el resto colgando, y el vault no avisa hasta que algo hace
    falta.

    **Se rechaza antes de tocar nada.** Un renombrado a medias es peor que uno
    que no ocurrió: deja al autor con dos ámbitos incompletos y sin saber cuál
    es el bueno.
    """
    from tuku import regenerate, rename

    viejo, nuevo = canonico(vault, viejo), normalizar(nuevo)
    if (rechazo := _rechazo_de_nombre(nuevo)) is not None:
        return rechazo
    origen = directorio_de(vault, viejo)
    if origen is None:
        return Resultado.rechazo(f"no existe el ámbito {viejo!r}. Míralos en ambitos/.")
    destino = origen.parent / nuevo
    if viejo == nuevo:
        return Resultado.hecho(f"el ámbito ya se llama {nuevo!r}: nada que hacer.")
    if (otro := case_clash(vault, nuevo, salvo=viejo)) is not None or (
        destino.exists() and not igual_nombre(viejo, nuevo)
    ):
        return Resultado.rechazo(
            f"ya existe un ámbito {otro or nuevo!r}. "
            f"Dos ámbitos no pueden llamarse igual: elige otro nombre, o mueve "
            f"a mano lo que quieras conservar de {viejo!r} y bórralo después."
        )

    origen.rename(destino)
    pagina_vieja = destino / f"{viejo}.md"
    if pagina_vieja.is_file():
        pagina_vieja.rename(destino / f"{nuevo}.md")

    # El nombre viejo vive en las cabeceras de los archivos del ámbito, en el ancla
    # que transcluye sus pendientes y en los enlaces de todo el vault. Se recorre
    # el vault entero una vez y se escribe solo lo que cambió, que es lo que hace
    # la operación idempotente.
    enlaces = 0
    viejo_dir = origen.relative_to(vault).as_posix()
    nuevo_dir = destino.relative_to(vault).as_posix()
    for ruta in sorted(vault.rglob("*.md")):
        texto = archivo.leer(ruta)
        salida, n = rename.renombrar_enlaces(texto, viejo, nuevo)
        enlaces += n
        salida, _ = rename.renombrar_ancla(salida, viejo, nuevo)
        # Los descendientes cambian de ruta con la carpeta: sus links se recalculan.
        despues = ruta.relative_to(vault).as_posix()
        antes = despues
        if despues.startswith(f"{nuevo_dir}/"):
            antes = viejo_dir + despues[len(nuevo_dir) :]
            if antes == f"{viejo_dir}/{nuevo}.md":
                antes = f"{viejo_dir}/{viejo}.md"
        salida = link.reubicar(salida, antes, despues, {viejo_dir: nuevo_dir})
        if ruta.parent == destino:
            salida = salida.replace(f"de {viejo}", f"de {nuevo}")
            if ruta.name == f"{nuevo}.md":
                salida = rename.renombrar_titulo(salida, nuevo)
        if salida != texto:
            archivo.escribir(ruta, salida)

    # El callout de `PENDIENTES-AMBITOS.md` lleva el nombre legible del ámbito,
    # y quien sabe componerlo es la propagación: se regenera en vez de parchear.
    if (vault / "PENDIENTES.md").is_file():
        regenerate.rehacer(vault, ["ambitos/", "AHORA.md", "bitacoras/"])
    retitular_hijos(destino)
    refrescar_hijos(destino.parent)
    regenerar_parent(vault)
    actualizar_pagina(vault, nuevo)

    detalle = f" ({enlaces} enlace(s) actualizado(s))" if enlaces else ""
    return Resultado.hecho(f"ámbito {viejo!r} renombrado a {nuevo!r}{detalle}.")


def mover_en_vault(vault: Path, nombre: str, *, parent: str | None = None) -> Resultado:
    """Mueve un ámbito dentro de otro (o a la raíz de `ambitos/`) y arregla sus links.

    Un ámbito movido cambia de ruta, y la ruta está en cada link que lo nombra,
    en los links de sus propios archivos hacia afuera y en la transclusión de su
    página. Se recalculan todos, también en las bitácoras cerradas: reparar un
    link que dejaría de resolver no es enriquecer el pasado (`spec/ambitos.md`).

    **Se rechaza antes de tocar nada:** un ámbito o un padre que no existen, un
    padre que cuelga del propio ámbito, un destino ocupado o una tabla de
    pendientes rota. Moverlo donde ya está no escribe nada.
    """
    from tuku import link, regenerate

    nombre = canonico(vault, nombre)
    origen = directorio_de(vault, nombre)
    if origen is None:
        return Resultado.rechazo(f"no existe el ámbito {nombre!r}. Míralos en ambitos/.")
    if parent:
        resuelto = resolver_padre(vault, parent)
        if isinstance(resuelto, Resultado):
            return resuelto
        padre = resuelto
        if padre == origen or origen in padre.parents:
            return Resultado.rechazo(
                f"{nombre!r} no puede ir dentro de sí mismo: {parent!r} cuelga de él. "
                f"Elige otro padre."
            )
    else:
        padre = vault / "ambitos"
    destino = padre / origen.name
    if destino == origen:
        return Resultado.hecho(f"el ámbito {nombre!r} ya está ahí: nada que hacer.")
    if destino.exists():
        return Resultado.rechazo(
            f"ya existe {destino.relative_to(vault).as_posix()}. Elige otro padre, o mueve "
            f"a mano lo que quieras conservar de {nombre!r}."
        )
    pendientes = vault / "PENDIENTES.md"
    if pendientes.is_file():
        from tuku import todo_core

        try:
            todo_core.filas(archivo.leer(pendientes))
        except todo_core.SinTabla as e:
            return Resultado.rechazo(str(e))

    def rel(ruta: Path) -> str:
        return ruta.relative_to(vault).as_posix()

    viejo_dir, nuevo_dir = rel(origen), rel(destino)
    textos = {
        p: archivo.leer(p)
        for p in sorted(vault.rglob("*.md"))
        if not any(parte.startswith(".") for parte in p.relative_to(vault).parts)
    }
    destino.parent.mkdir(parents=True, exist_ok=True)
    origen.rename(destino)

    cambiados = 0
    for ruta, texto in textos.items():
        antes = rel(ruta)
        despues = (
            nuevo_dir + antes[len(viejo_dir) :] if antes.startswith(f"{viejo_dir}/") else antes
        )
        salida = link.reubicar(texto, antes, despues, {viejo_dir: nuevo_dir})
        if salida != texto:
            archivo.escribir((vault / despues), salida)
            cambiados += 1

    refrescar_hijos(origen.parent)
    refrescar_hijos(padre)
    regenerar_parent(vault)
    if pendientes.is_file():
        regenerate.rehacer(vault, ["ambitos/", "AHORA.md", "bitacoras/"])
    detalle = f" ({cambiados} archivo(s) con links actualizados)" if cambiados else ""
    return Resultado.hecho(f"ámbito {nombre!r} movido a {nuevo_dir}{detalle}.")
