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
poner el nombre en `keywords:` de la página propia.
"""

from __future__ import annotations

import os
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from tuku import link
from tuku.resultado import Resultado

_KEYWORDS = re.compile(r"^keywords:\s*\[(?P<lista>[^\]]*)\]\s*$", re.M)


@dataclass(frozen=True)
class Ambito:
    nombre: str
    directorio: Path
    keywords: list[str]


def _pagina(directorio: Path) -> Path:
    return directorio / f"{directorio.name}.md"


def normalizar(nombre: str) -> str:
    """El nombre de un ámbito tal como va en disco y en los enlaces.

    Los espacios pasan a guion: el autor dicta "depto centro" y el ámbito es
    `depto-centro`. Sin esto, cada agente elige su forma y el mismo frente
    termina con dos nombres.
    """
    return re.sub(r"\s+", "-", nombre.strip().strip("[]").strip())


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
    limpio = normalizar(nombre)
    return next((n for n in sorted(nombres(vault)) if igual_nombre(n, limpio)), limpio)


def _choque(vault: Path, nombre: str, *, salvo: str = "") -> str | None:
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
    un error que reporta `scope lint`, no uno que impida escribirlo.
    """
    raiz = vault / "ambitos"
    if not raiz.is_dir():
        return set()
    salida = set()
    for p in raiz.rglob("*"):
        if p.is_dir():
            salida.add(p.name)
        elif p.suffix == ".md" and not p.stem.isupper():
            salida.add(p.stem)
    return salida


def rutas(vault: Path) -> dict[str, str]:
    """Nombre → ruta relativa al vault de todo lo que un registro puede nombrar.

    Es lo que `link` necesita para componer el enlace a un ámbito anidado con
    su ruta completa: la página del ámbito, el archivo de una actividad, o la
    carpeta de una categoría. Si dos nombres chocan manda el primero en orden,
    y `spec/ambitos.md` no admite que choquen.
    """
    raiz = vault / "ambitos"
    if not raiz.is_dir():
        return {}
    salida: dict[str, str] = {}
    for p in sorted(raiz.rglob("*")):
        if p.is_dir():
            destino = _pagina(p) if _pagina(p).is_file() else p
            salida.setdefault(p.name, destino.relative_to(vault).as_posix())
        elif p.suffix == ".md" and not p.stem.isupper() and p.stem != p.parent.name:
            salida.setdefault(p.stem, p.relative_to(vault).as_posix())
    return salida


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
    existentes = ", ".join(sorted(a.nombre for a in leer(vault))) or "ninguno"
    return Resultado.rechazo(
        f"no existe el ámbito {nombre!r}. Créalo con `tuku scope create {nombre}` "
        f"si el autor lo pide, o usa uno que exista: {existentes}."
    )


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


def keywords(pagina: str) -> list[str]:
    """Las `keywords` del frontmatter de una página de ámbito."""
    m = _KEYWORDS.search(pagina)
    if m is None:
        return []
    return [k.strip() for k in m.group("lista").split(",") if k.strip()]


def crear(vault: Path, name: str, padre: Path | None = None) -> Path:
    """Crea el ámbito `name` en la carpeta `padre`, o bajo `ambitos/`. Idempotente.

    Si ya existe no toca nada: `spec/ambitos.md` no admite dos ámbitos con el
    mismo nombre, y volver a crearlo no es un error del autor.
    """
    valor = normalizar(name)
    directorio = (padre or vault / "ambitos") / valor
    directorio.mkdir(parents=True, exist_ok=True)

    pagina = _pagina(directorio)
    if not pagina.exists():
        rel = os.path.relpath(vault / "ambitos" / "PENDIENTES-AMBITOS.md", directorio)
        rel = rel.replace(os.sep, "/")
        base = f"---\ntype: Scope\nkeywords: [{valor}]\n---\n# {valor}\n\n![[{rel}#^{valor}]]\n"
        ahora_file = vault / "AHORA.md"
        ahora_texto = ahora_file.read_text(encoding="utf-8") if ahora_file.is_file() else ""
        texto = actualizar_contenido_pagina(
            base, ahora_texto, valor, pagina=pagina.relative_to(vault).as_posix()
        )
        pagina.write_text(texto, encoding="utf-8")

    if (vault / "PENDIENTES.md").is_file():
        from tuku import propagate

        propagate.propagar(vault)

    return directorio


def extraer_actividad_ambito(
    ahora: str, nombre_ambito: str, *, pagina: str | None = None
) -> dict[str, list[str]]:
    """Extrae las líneas de bitácora vinculadas al ámbito, agrupadas por día.

    Omite la hora `- HH:MM - ` dejando `- cuerpo`.
    Remueve auto-enlaces al propio ámbito:
    - Si inicia con el enlace al ámbito, elimina el prefijo.
    - Si aparece dentro del texto, lo reemplaza por el nombre a secas.

    El enlace se reconoce en cualquiera de los dos formatos. Los demás links de
    la línea se copian a la página del ámbito, que vive en otra carpeta, así que
    sus rutas se recalculan desde `AHORA.md` hacia `pagina` (por defecto, la
    forma plana `ambitos/<n>/<n>.md`).

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
            m = re.match(r"^- \d{2}:\d{2} - (.*)$", lineas[i])
            if m is None or not any(es_el_ambito(e) for e in propio.finditer(m.group(1))):
                continue
            cuerpo = m.group(1)
            primero = propio.match(cuerpo)
            if primero is not None and es_el_ambito(primero):
                cuerpo = cuerpo[primero.end() :].lstrip()
            cuerpo = propio.sub(
                lambda e: nombre_ambito if es_el_ambito(e) else e.group(), cuerpo
            )
            lineas_dia.append(f"- {link.rebasar(cuerpo, 'AHORA.md', destino)}")

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


def actualizar_contenido_pagina(
    contenido_actual: str, ahora_texto: str, nombre_ambito: str, *, pagina: str | None = None
) -> str:
    """Actualiza o incorpora `## Esta semana` y `## Actividad reciente` en el ámbito."""
    from datetime import date

    from tuku.ahora import rango
    from tuku.init import MESES

    actividad = extraer_actividad_ambito(ahora_texto, nombre_ambito, pagina=pagina)
    seccion_semana = formatear_esta_semana(actividad).strip()

    limites = rango(ahora_texto) if ahora_texto else None
    fecha_ref = limites[0] if limites else date.today()
    mes_str = MESES[fecha_ref.month - 1].capitalize()
    mes_anio = f"{mes_str} {fecha_ref.year}"

    partes_semana = contenido_actual.split("## Esta semana", 1)
    base = partes_semana[0].rstrip()

    if "## Actividad reciente" in contenido_actual:
        parte_reciente = contenido_actual.split("## Actividad reciente", 1)[1].rstrip()
        if not parte_reciente.strip():
            seccion_reciente = f"## Actividad reciente\n### {mes_anio}"
        else:
            seccion_reciente = f"## Actividad reciente{parte_reciente}"
    else:
        seccion_reciente = f"## Actividad reciente\n### {mes_anio}"

    return f"{base}\n\n{seccion_semana}\n\n{seccion_reciente}\n"


def actualizar_pagina(vault: Path, nombre: str) -> Path | None:
    """Regenera la actividad en la página del ámbito. Devuelve la ruta si cambió."""
    pagina = _pagina(carpeta(vault, nombre))
    if not pagina.is_file():
        return None
    ahora_path = vault / "AHORA.md"
    if not ahora_path.is_file():
        return None
    ahora_texto = ahora_path.read_text(encoding="utf-8")
    actual = pagina.read_text(encoding="utf-8")
    nuevo = actualizar_contenido_pagina(
        actual, ahora_texto, nombre, pagina=pagina.relative_to(vault).as_posix()
    )
    if nuevo != actual:
        pagina.write_text(nuevo, encoding="utf-8")
        return pagina
    return None


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
    return sorted(d.name for d in raiz.rglob("*") if d.is_dir() and not _pagina(d).is_file())


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
        contenido = pagina.read_text(encoding="utf-8")
        patron = rf"!\[\[[^\]]*PENDIENTES-AMBITOS(?:\.md)?#\^{re.escape(a.nombre)}\]\]"
        if not re.search(patron, contenido):
            rel = os.path.relpath(vault / "ambitos" / "PENDIENTES-AMBITOS.md", a.directorio)
            ruta_rel = pagina.relative_to(vault)
            hallazgos.append(
                f"{ruta_rel}: error: falta la transclusión a PENDIENTES-AMBITOS.md "
                f"(esperada: '![[{rel}#^{a.nombre}]]')."
            )
    return hallazgos


def lint_callouts(vault: Path) -> list[str]:
    """Comprueba que en PENDIENTES-AMBITOS.md exista un callout por cada ámbito."""
    archivo = vault / "ambitos" / "PENDIENTES-AMBITOS.md"
    if not archivo.is_file():
        return [
            "ambitos/PENDIENTES-AMBITOS.md: error: falta el archivo. "
            "Corre `tuku regenerate todo` para generarlo."
        ]
    contenido = archivo.read_text(encoding="utf-8")
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
        hallazgos.extend(
            lint_categorias(ahora_path.read_text(encoding="utf-8"), categorias=cats)
        )
    hallazgos.extend(lint_transclusiones(vault))
    hallazgos.extend(lint_callouts(vault))
    return hallazgos


#: El cuerpo de la constancia que deja `scope create` en la bitácora.
CONSTANCIA = "**nota**: abrí el ámbito"


def registro_de_constancia(
    nombre: str, *, hour: str, rutas: Mapping[str, str] | None = None
) -> str:
    """La línea de bitácora que deja constancia del ámbito creado, para `AHORA.md`."""
    return f"- {hour} - {link.enlace_ambito(nombre, 'AHORA.md', rutas)} {CONSTANCIA}"


def crear_con_enlazado(
    vault: Path,
    nombre: str,
    *,
    parent: str | None = None,
    day: date | None = None,
    hour: str | None = None,
) -> Resultado:
    """Crea el ámbito, enlaza las menciones sueltas que ya había y deja constancia.

    El enlazado retroactivo es parte de crear, no un segundo paso: un ámbito que
    nace sin recoger lo que el autor ya había escrito sobre él deja la mitad del
    trabajo hecha y nadie se entera.

    Crear un ámbito es una decisión del autor sobre su estructura, así que deja
    huella en `AHORA.md`, en el día `day` (HOY si falta) y a la hora `hour` (AHORA
    si falta). Solo la deja quien crea la carpeta: correrlo sobre un ámbito que ya
    existe no escribe nada, ni en este ciclo ni en uno posterior.

    **Se rechaza antes de tocar nada:** lo que haría fallar la propagación, o un
    día fuera del ciclo abierto, se revisa antes de crear la carpeta, para que un
    rechazo no deje un ámbito a medias.

    Con `parent`, el ámbito va dentro de la carpeta de otro, que debe existir. Si
    el ámbito ya existe en otro lugar se rechaza y se nombra `scope move`.
    """
    from datetime import datetime

    from tuku import entry, todo
    from tuku.ahora import encabezado_de

    nombre = normalizar(nombre)
    if (rechazo := _rechazo_de_nombre(nombre)) is not None:
        return rechazo
    if (otro := _choque(vault, nombre)) is not None:
        return Resultado.rechazo(
            f"ya existe el ámbito {otro!r}, y los nombres no distinguen mayúsculas. "
            f"Usa {otro!r}, o elige otro nombre."
        )
    padre: Path | None = None
    if parent:
        parent = canonico(vault, parent)
        padre = directorio_de(vault, parent)
        if padre is None:
            return Resultado.rechazo(_sin_padre(parent))
    existente = next((a.directorio for a in leer(vault) if a.nombre == nombre), None)
    if existente is not None and padre is not None and existente.parent != padre:
        return Resultado.rechazo(
            f"el ámbito {nombre!r} ya existe en {existente.relative_to(vault).as_posix()}. "
            f"Para ponerlo bajo {parent!r}: `tuku scope move {nombre} --parent {parent}`."
        )
    pendientes = vault / "PENDIENTES.md"
    if pendientes.is_file():
        try:
            todo.filas(pendientes.read_text(encoding="utf-8"))
        except todo.SinTabla as e:
            return Resultado.rechazo(str(e))

    ahora_path = vault / "AHORA.md"
    nuevo = existente is None
    dia = encabezado_de(day or date.today())
    hora = hour or datetime.now().strftime("%H:%M")
    if nuevo and ahora_path.is_file():
        try:
            entry.add(ahora_path.read_text(encoding="utf-8"), [], day=dia)
        except ValueError as e:
            return Resultado.rechazo(str(e))

    directorio = crear(vault, nombre, existente.parent if existente is not None else padre)
    menciones = 0
    pagina_path = directorio / f"{nombre}.md"
    if ahora_path.is_file() and pagina_path.is_file():
        original = ahora_path.read_text(encoding="utf-8")
        texto, menciones = link.backfill(
            original,
            scope=nombre,
            keywords=keywords(pagina_path.read_text(encoding="utf-8")),
            rutas=rutas(vault),
        )
        if nuevo:
            constancia = registro_de_constancia(nombre, hour=hora, rutas=rutas(vault))
            texto = entry.add(texto, [constancia], day=dia)
        if texto != original:
            ahora_path.write_text(texto, encoding="utf-8")
        actualizar_pagina(vault, nombre)

    if menciones > 0:
        return Resultado.hecho(
            f"ámbito creado en {directorio} ({menciones} mención(es) enlazada(s))."
        )
    return Resultado.hecho(f"ámbito creado en {directorio}.")


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
    from tuku import propagate, rename

    viejo, nuevo = canonico(vault, viejo), normalizar(nuevo)
    if (rechazo := _rechazo_de_nombre(nuevo)) is not None:
        return rechazo
    origen = directorio_de(vault, viejo)
    if origen is None:
        return Resultado.rechazo(f"no existe el ámbito {viejo!r}. Míralos en ambitos/.")
    destino = origen.parent / nuevo
    if viejo == nuevo:
        return Resultado.hecho(f"el ámbito ya se llama {nuevo!r}: nada que hacer.")
    if (otro := _choque(vault, nuevo, salvo=viejo)) is not None or (
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

    # El nombre viejo vive en las cabeceras de los archivos del ámbito, en su
    # `keywords`, en el ancla que transcluye sus pendientes y en los enlaces de
    # todo el vault. Se recorre el vault entero una vez y se escribe solo lo que
    # cambió, que es lo que hace la operación idempotente.
    enlaces = 0
    for ruta in sorted(vault.rglob("*.md")):
        texto = ruta.read_text(encoding="utf-8")
        salida, n = rename.renombrar_enlaces(texto, viejo, nuevo)
        enlaces += n
        salida, _ = rename.renombrar_ancla(salida, viejo, nuevo)
        salida = salida.replace(f"keywords: [{viejo}]", f"keywords: [{nuevo}]")
        if ruta.parent == destino:
            salida = salida.replace(f"de {viejo}", f"de {nuevo}")
            if ruta.name == f"{nuevo}.md":
                salida = rename.renombrar_titulo(salida, nuevo)
        if salida != texto:
            ruta.write_text(salida, encoding="utf-8")

    # El callout de `PENDIENTES-AMBITOS.md` lleva el nombre legible del ámbito,
    # y quien sabe componerlo es la propagación: se regenera en vez de parchear.
    if (vault / "PENDIENTES.md").is_file():
        propagate.propagar(vault)
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
    from tuku import link, propagate

    nombre = canonico(vault, nombre)
    origen = directorio_de(vault, nombre)
    if origen is None:
        return Resultado.rechazo(f"no existe el ámbito {nombre!r}. Míralos en ambitos/.")
    if parent:
        parent = canonico(vault, parent)
        padre = directorio_de(vault, parent)
        if padre is None:
            return Resultado.rechazo(_sin_padre(parent))
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
        from tuku import todo

        try:
            todo.filas(pendientes.read_text(encoding="utf-8"))
        except todo.SinTabla as e:
            return Resultado.rechazo(str(e))

    def rel(ruta: Path) -> str:
        return ruta.relative_to(vault).as_posix()

    viejo_dir, nuevo_dir = rel(origen), rel(destino)
    textos = {
        p: p.read_text(encoding="utf-8")
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
            (vault / despues).write_text(salida, encoding="utf-8")
            cambiados += 1

    if pendientes.is_file():
        propagate.propagar(vault)
    detalle = f" ({cambiados} archivo(s) con links actualizados)" if cambiados else ""
    return Resultado.hecho(f"ámbito {nombre!r} movido a {nuevo_dir}{detalle}.")


def lint_del_vault(vault: Path) -> Resultado:
    """Revisa el árbol de ámbitos y reporta; no escribe."""
    hallazgos = lint(vault)
    if not hallazgos:
        return Resultado.hecho("sin hallazgos.")
    return Resultado.rechazo("\n".join(hallazgos), error=False)
