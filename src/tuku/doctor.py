"""tuku doctor: ¿está sano el vault? Corre todos los lint y revisa las tablas.

Los lint sueltos (`cycle`, `entry`, `todo`, `style`) siguen existiendo para uso
fino. Este los junta y agrega lo que ninguno cubre: que las tablas de contrato
existan y estén bien formadas. Es el comando de quien vuelve al vault después de
un mes y no se acuerda de qué revisar.

Las tablas de `reglas/types.md` son distintas de las del libro de estilo. Las del
libro son vocabulario del autor: una fila que no está no es error, es vocabulario
por formalizar. Las de `types.md` son contrato con OKF: una fila que falta sí es
error, porque algún archivo del vault va a quedar sin `type` que ponerle.

Cuando algo falla, el reporte termina diciendo dónde está el template original.
Un `uv tool install` deja una copia intacta en `~/.tuku/`, y contra ella se repara
un vault roto sin adivinar cómo era. El doctor nunca copia nada: verificar y
corregir son operaciones distintas (`spec/cli.md`), y el conjunto canónico no se
sobreescribe sin que el autor lo apruebe (principio 3).

**Qué lee y escribe:** lee todo lo anterior. **No escribe.**
**A mano:** correr los cuatro lint y revisar que `reglas/types.md` tenga su tabla.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from tuku.resultado import Resultado

#: Los campos de `config.tuku.md` sin los cuales los comandos no pueden operar.
CAMPOS_REQUERIDOS = ("TZ", "cycle_type", "tuku_template")

#: Los `type` sin los cuales un vault no se puede describir entero.
TIPOS_REQUERIDOS = ("Logbook", "Pending", "Scope", "Note", "Cadence", "Config", "Style Guide")

_FILA = re.compile(r"^\|\s*`([^`]+)`\s*\|")

#: Lo que en un documento del vault se lee como una invocación: algo entre
#: backticks que empieza por `tuku`. Se mira el archivo entero y no solo la
#: tabla, porque la prosa que rodea la tabla también nombra comandos.
_INVOCACION = re.compile(r"`tuku ([a-z]+(?: [a-z]+)?)`")

#: El `type` del frontmatter. Solo se mira el bloque de arriba del archivo.
_TYPE = re.compile(r"^type:\s*(.+?)\s*$", re.MULTILINE)

#: Los archivos sin los cuales el vault no opera.
ARCHIVOS_REQUERIDOS = (
    "AHORA.md",
    "PENDIENTES.md",
    "LIBRO-DE-ESTILO.md",
    "reglas/config.tuku.md",
    "reglas/types.md",
    "reglas/plantilla/AHORA.md",
)

#: Reglas de operación, no conocimiento: quedan fuera de OKF a propósito
#: (lo dice el `## OKF` del libro de estilo).
SIN_FRONTMATTER = ("AGENTS.md",)


@dataclass(frozen=True)
class Revision:
    """El resultado de una de las revisiones que corre el doctor."""

    nombre: str
    salida: str
    sano: bool


def tipos_declarados(types_md: str) -> list[str]:
    """Los `type` que declara la tabla de `reglas/types.md`, en orden.

    Cuenta desde la fila separadora, porque el encabezado de la tabla también
    lleva `type` entre backticks y si no se descarta se cuenta como un tipo más.
    Los callouts se saltan: son prosa dirigida al autor, no datos.
    """
    tipos: list[str] = []
    en_tabla = False
    for linea in types_md.splitlines():
        recortada = linea.strip()
        if recortada.startswith(">"):
            # Un callout es prosa para el autor. La tabla es lo único que se lee.
            continue
        if recortada.startswith("|") and set(recortada) <= set("| -: "):
            en_tabla = True
            continue
        if not recortada.startswith("|"):
            en_tabla = False
            continue
        if en_tabla and (m := _FILA.match(recortada)):
            tipos.append(m.group(1))
    return tipos


def revisar_tipos(types_md: str | None) -> Revision:
    """Verifica que la tabla de tipos exista y declare los tipos requeridos."""
    if types_md is None:
        return Revision(
            "types",
            "reglas/types.md: error: falta el archivo. "
            "Es donde vive la tabla de `type` que el libro de estilo transcluye.",
            False,
        )

    declarados = tipos_declarados(types_md)
    if not declarados:
        return Revision(
            "types",
            "reglas/types.md: error: no tiene tabla de tipos. "
            "Cada fila empieza con el `type` entre backticks.",
            False,
        )

    faltan = [t for t in TIPOS_REQUERIDOS if t not in declarados]
    if faltan:
        lista = ", ".join(f"`{t}`" for t in faltan)
        return Revision(
            "types",
            f"reglas/types.md: error: faltan tipos en la tabla: {lista}. "
            "Sin ellos hay archivos del vault que no se pueden describir.",
            False,
        )

    return Revision("types", f"types: {len(declarados)} tipos declarados.", True)


def comandos_de_despacho(agents_md: str) -> list[str]:
    """Los comandos que el `AGENTS.md` del vault nombra, sin repetir y en orden."""
    vistos: list[str] = []
    for m in _INVOCACION.finditer(agents_md):
        if m.group(1) not in vistos:
            vistos.append(m.group(1))
    return vistos


def revisar_despacho(agents_md: str | None, comandos: frozenset[str]) -> Revision:
    """Verifica que la tabla de despacho no nombre comandos que no existen.

    Es la revisión más barata del epic 003 y la que más sostiene: el `AGENTS.md`
    es lo único que hace que un agente cualquiera opere el vault igual, y si
    nombra un comando que no existe, ningún agente lo arregla. Un modelo que
    encuentra `tuku entry create` en la tabla lo va a correr, va a recibir un
    error de uso, y va a improvisar: casi siempre editando el archivo a mano,
    que es lo único que el vault prohíbe.

    Al revés no se afirma nada. Que el CLI tenga comandos que la tabla no nombra
    es lo normal: la tabla enruta lo que el autor dice, no documenta la
    superficie (`spec/despacho.md`).
    """
    if agents_md is None:
        return Revision(
            "despacho",
            "AGENTS.md: error: falta el archivo. Es lo que le dice a un agente a "
            "dónde va cada cosa; sin él, cada arnés opera el vault a su manera.",
            False,
        )

    nombrados = comandos_de_despacho(agents_md)
    if not nombrados:
        return Revision(
            "despacho",
            "AGENTS.md: error: no nombra ningún comando. La tabla de despacho es "
            "lo que traduce lo que el autor dice a una invocación de `tuku`.",
            False,
        )

    faltan = [c for c in nombrados if c not in comandos]
    if faltan:
        lista = ", ".join(f"`tuku {c}`" for c in faltan)
        return Revision(
            "despacho",
            f"AGENTS.md: error: nombra comandos que no existen: {lista}. "
            f"Corrige la tabla, o agrega el comando al CLI si es el que falta.",
            False,
        )

    return Revision("despacho", f"despacho: {len(nombrados)} comandos, todos existen.", True)


def tipo_declarado(texto: str) -> str | None:
    """El `type` del frontmatter de un archivo, o `None` si no lo tiene.

    Se mira solo el bloque de arriba: un `type:` en el cuerpo es prosa, no
    metadato, y confundirlos daría por bueno un archivo sin frontmatter.
    """
    if not texto.startswith("---\n"):
        return None
    fin = texto.find("\n---", 4)
    if fin == -1:
        return None
    m = _TYPE.search(texto[4:fin])
    return m.group(1) if m else None


def ausente(nombre: str, archivo: str) -> Revision:
    """La revisión que no se pudo correr porque su archivo no está."""
    return Revision(nombre, f"{nombre}: no se pudo revisar, falta {archivo}.", False)


def revisar_archivos(vault: Path) -> Revision:
    """Verifica que estén los archivos sin los cuales el vault no opera."""
    faltan = [r for r in ARCHIVOS_REQUERIDOS if not (vault / r).is_file()]
    if faltan:
        return Revision(
            "archivos",
            "\n".join(f"{r}: error: falta el archivo." for r in faltan),
            False,
        )
    salida = f"archivos: los {len(ARCHIVOS_REQUERIDOS)} requeridos están."
    return Revision("archivos", salida, True)


def revisar_frontmatter(vault: Path, *, tipos_validos: list[str]) -> Revision:
    """Revisa que cada archivo del vault declare un `type` que la tabla conozca.

    Recorre el vault entero, no solo `reglas/`. No exige un `type` concreto por
    carpeta: `reglas/plantilla/AHORA.md` es un `Logbook` aunque viva en
    `reglas/`, porque es el molde de uno. Lo que se exige es que el `type`
    exista y esté en la tabla, que es lo que hace legible el archivo para
    cualquier cosa que hable OKF.

    Los `AGENTS.md` quedan fuera: son reglas de operación, no conocimiento.
    """
    problemas: list[str] = []
    revisados = 0

    for archivo in sorted(vault.rglob("*.md")):
        if archivo.name in SIN_FRONTMATTER:
            continue
        revisados += 1
        ruta = archivo.relative_to(vault)
        tipo = tipo_declarado(archivo.read_text(encoding="utf-8"))
        if tipo is None:
            problemas.append(
                f"{ruta}: error: no declara `type` en su frontmatter. "
                f"Agrégalo con uno de los de `reglas/types.md`."
            )
        elif tipos_validos and tipo not in tipos_validos:
            problemas.append(
                f"{ruta}: error: `type: {tipo}` no está en `reglas/types.md`. "
                f"Usa uno de la tabla, o agrégalo ahí si falta."
            )

    if problemas:
        return Revision("frontmatter", "\n".join(problemas), False)
    return Revision("frontmatter", f"frontmatter: {revisados} archivos con `type`.", True)


def revisar_config(config_md: str | None) -> Revision:
    """Verifica que la tabla de `reglas/config.tuku.md` tenga sus campos."""
    if config_md is None:
        return Revision(
            "config",
            "reglas/config.tuku.md: error: falta el archivo. "
            "Es donde los comandos leen la zona horaria y el tipo de ciclo.",
            False,
        )

    from tuku.config import parsear_config_md

    campos = parsear_config_md(config_md)
    faltan = [c for c in CAMPOS_REQUERIDOS if not campos.get(c)]
    if faltan:
        lista = ", ".join(f"`{c}`" for c in faltan)
        return Revision(
            "config",
            f"reglas/config.tuku.md: error: faltan campos en la tabla: {lista}. "
            "Sin ellos los comandos adivinan, y adivinar la `TZ` vence pendientes.",
            False,
        )

    return Revision("config", f"config: {len(campos)} campos declarados.", True)


def fuente_de_referencia(variante: str = "vanilla") -> Path | None:
    """El template original con el que comparar un vault roto, si está.

    Es el mismo árbol del que salió el vault: `~/.tuku/` tras un `uv tool
    install`, el checkout en desarrollo. `None` si no se encuentra ninguno, que
    es el caso de un vault movido a una máquina sin TUKU instalado.
    """
    from tuku.init import TukuHomeInvalido, resolver_home

    try:
        candidato = resolver_home() / "template" / variante
    except TukuHomeInvalido:
        return None
    return candidato if candidato.is_dir() else None


def archivo_opcional(vault: Path, relativo: str) -> str | None:
    """El contenido de un archivo del vault, o `None` si no está."""
    p = vault / relativo
    return p.read_text(encoding="utf-8") if p.is_file() else None


def formatear(revisiones: list[Revision], *, fuente: Path | None = None) -> str:
    """El reporte completo, para persona y para agente.

    `fuente` es el template original. Solo aparece cuando algo falla: es ahí
    donde sirve, y en un vault sano sería ruido.
    """
    rotas = [r for r in revisiones if not r.sano]
    cuerpo = "\n".join(r.salida for r in revisiones)
    if not rotas:
        return f"{cuerpo}\ndoctor: el vault está sano."

    nombres = ", ".join(r.nombre for r in rotas)
    lineas = [cuerpo, f"doctor: {len(rotas)} revisión(es) con hallazgos: {nombres}."]
    if fuente is not None:
        lineas.append(
            f"El template original está en {fuente}. Compara contra él el archivo "
            f"que falle y copia a mano lo que le falte; el doctor no toca nada."
        )
    else:
        lineas.append(
            "No hay template original con el que comparar: ni `~/.tuku`, ni "
            "`TUKU_HOME`, ni un checkout. Reinstala TUKU para recuperarlo."
        )
    return "\n".join(lineas)


def revisar_vault(vault: Path, *, comandos: frozenset[str] | None = None) -> Resultado:
    """Corre todos los lint sobre el vault y revisa lo que ninguno cubre.

    **Ninguna revisión que falle detiene al resto.** Un archivo que falta es
    justo lo que el doctor existe para encontrar, así que aquí nada se lee con
    `archivo_vault`: eso aborta el comando con el vault a medio revisar, y el
    autor se queda sin el resto del diagnóstico.

    Ante hallazgos nombra el template original que `resolver_home` encuentra,
    para reparar comparando. Nunca copia: verificar y corregir son operaciones
    distintas.
    """
    from tuku import cyclelint, scope, style, todo
    from tuku.config import leer_config
    from tuku.lint import ERROR
    from tuku.lint import formatear as formatear_registros
    from tuku.lint import lint as lint_registros

    def leer(nombre: str) -> str | None:
        return archivo_opcional(vault, nombre)

    types_md = leer("reglas/types.md")
    revisiones = [
        revisar_config(leer("reglas/config.tuku.md")),
        revisar_tipos(types_md),
        revisar_archivos(vault),
        revisar_frontmatter(
            vault, tipos_validos=tipos_declarados(types_md) if types_md else []
        ),
    ]
    if comandos is not None:
        revisiones.append(revisar_despacho(leer("AGENTS.md"), comandos))

    ahora = leer("AHORA.md")
    if ahora is None:
        revisiones.append(ausente("cycle", "AHORA.md"))
        revisiones.append(ausente("entry", "AHORA.md"))
    else:
        h_cycle = cyclelint.lint(ahora)
        revisiones.append(Revision("cycle", cyclelint.formatear(h_cycle), not h_cycle))

        h_entry = lint_registros(ahora, abiertos=leer_config(vault).vocabularios_abiertos())
        revisiones.append(
            Revision(
                "entry",
                formatear_registros(h_entry),
                not any(h.grado == ERROR for h in h_entry),
            )
        )

    pendientes = leer("PENDIENTES.md")
    if pendientes is None:
        revisiones.append(ausente("todo", "PENDIENTES.md"))
    else:
        duplicados = todo.duplicados(pendientes)
        revisiones.append(
            Revision(
                "todo",
                "todo lint: sin hallazgos."
                if not duplicados
                else "\n".join([*duplicados, f"todo lint: {len(duplicados)} error(es)."]),
                not duplicados,
            )
        )

    libro = leer("LIBRO-DE-ESTILO.md")
    if libro is None:
        revisiones.append(ausente("style", "LIBRO-DE-ESTILO.md"))
    else:
        h_style = style.lint(libro)
        revisiones.append(
            Revision(
                "style",
                style.formatear(h_style),
                not any(h.grado == ERROR for h in h_style),
            )
        )

    h_scope = scope.lint(vault)
    revisiones.append(
        Revision(
            "scope",
            "scope lint: sin hallazgos."
            if not h_scope
            else "\n".join([*h_scope, f"scope lint: {len(h_scope)} error(es)."]),
            not h_scope,
        )
    )

    mensaje = formatear(revisiones, fuente=fuente_de_referencia())
    if all(r.sano for r in revisiones):
        return Resultado.hecho(mensaje)
    return Resultado.rechazo(mensaje, error=False)
