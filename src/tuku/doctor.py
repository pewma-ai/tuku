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

#: Los campos de `config.tuku.md` sin los cuales los comandos no pueden operar.
CAMPOS_REQUERIDOS = ("TZ", "cycle_type", "tuku_template")

#: Los `type` sin los cuales un vault no se puede describir entero.
TIPOS_REQUERIDOS = ("Logbook", "Pending", "Scope", "Note", "Cadence", "Config", "Style Guide")

_FILA = re.compile(r"^\|\s*`([^`]+)`\s*\|")

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
