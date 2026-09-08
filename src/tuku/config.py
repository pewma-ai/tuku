"""Lectura centralizada de configuración, libro de estilo y reglas de un vault.

Reúne en un solo lugar todas las lecturas de los archivos normativos del vault
(`reglas/config.tuku.md`, `LIBRO-DE-ESTILO.md` y `reglas/plantilla/AHORA.md`).
Permite testear el comportamiento en memoria y desacopla la ubicación física
de los archivos del resto de los comandos de TUKU.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from tuku import vocab
from tuku.init import resolver_home

_PAR_CLAVE_VALOR = re.compile(r"^\*\*([^:]+):\*\*\s*(.+)$")
_MARCADOR_AUTOR = "**Nombre del autor:**"


class VaultInvalido(Exception):
    """El directorio no es un vault de TUKU: le falta un archivo canónico."""


def archivo_vault(vault: Path, nombre: str) -> Path:
    """Resuelve un archivo canónico dentro del vault o lanza VaultInvalido."""
    ruta = vault / nombre
    if not ruta.is_file():
        raise VaultInvalido(
            f"{vault} no parece un vault de TUKU: falta {nombre}. "
            f"Siémbralo con `tuku init {vault}`, o corre el comando dentro de un vault."
        )
    return ruta


@dataclass(frozen=True)
class Configuracion:
    """Configuración consolidada de un vault."""

    vault: Path
    # De reglas/config.tuku.md
    zona_horaria: str
    tipo_ciclo: str
    datos: dict[str, str]
    # De LIBRO-DE-ESTILO.md
    autor: str | None
    vocabularios: dict[str, list[str]]
    clasificaciones: list[str]
    horizontes: list[str]
    tipos_nota: list[str]
    # De reglas/plantilla/
    plantilla_ahora: str

    def vocabularios_abiertos(self) -> list[str]:
        """Términos declarados en todas las tablas del libro de estilo."""
        return [t for terminos in self.vocabularios.values() for t in terminos]


def parsear_config_md(texto: str) -> dict[str, str]:
    """Parsea pares `**Clave:** Valor` de la sección de datos de config.tuku.md."""
    pares: dict[str, str] = {}
    for linea in texto.splitlines():
        m = _PAR_CLAVE_VALOR.match(linea.strip())
        if m:
            pares[m.group(1).strip()] = m.group(2).strip()
    return pares


def parsear_autor(texto_libro: str) -> str | None:
    """Extrae el nombre del autor si fue declarado en LIBRO-DE-ESTILO.md."""
    for linea in texto_libro.splitlines():
        if linea.lstrip().startswith(_MARCADOR_AUTOR):
            resto = linea.split(_MARCADOR_AUTOR, 1)[1].strip()
            if resto and not resto.lower().startswith("por declarar"):
                return resto
    return None


def resolver_plantilla_ahora(vault: Path) -> str:
    """Busca la plantilla de AHORA.md en el vault o en el fallback de TUKU."""
    local = vault / "reglas" / "plantilla" / "AHORA.md"
    if local.is_file():
        return local.read_text(encoding="utf-8")
    fallback = resolver_home() / "template" / "vanilla" / "reglas" / "plantilla" / "AHORA.md"
    if fallback.is_file():
        return fallback.read_text(encoding="utf-8")
    raise FileNotFoundError(
        f"no se encontró la plantilla de AHORA.md en {local} ni en {fallback}"
    )


def leer_config(
    vault: Path,
    *,
    texto_config: str | None = None,
    texto_libro: str | None = None,
    texto_plantilla_ahora: str | None = None,
) -> Configuracion:
    """Lee y consolida configuración, libro de estilo y plantillas de un vault."""
    vault = Path(vault)

    # 1. reglas/config.tuku.md
    if texto_config is None:
        ruta_config = vault / "reglas" / "config.tuku.md"
        texto_config = ruta_config.read_text(encoding="utf-8") if ruta_config.is_file() else ""
    datos = parsear_config_md(texto_config)
    zona_horaria = datos.get("Zona horaria", "America/Santiago")
    tipo_ciclo = datos.get("Tipo de ciclo", "semanal")

    # 2. LIBRO-DE-ESTILO.md
    if texto_libro is None:
        ruta_libro = archivo_vault(vault, "LIBRO-DE-ESTILO.md")
        texto_libro = ruta_libro.read_text(encoding="utf-8")
    autor = parsear_autor(texto_libro)
    vocabs = vocab.leer(texto_libro) if texto_libro else {}

    # 3. Plantilla AHORA.md
    if texto_plantilla_ahora is None:
        try:
            plantilla_ahora = resolver_plantilla_ahora(vault)
        except FileNotFoundError:
            plantilla_ahora = ""
    else:
        plantilla_ahora = texto_plantilla_ahora

    return Configuracion(
        vault=vault,
        zona_horaria=zona_horaria,
        tipo_ciclo=tipo_ciclo,
        datos=datos,
        autor=autor,
        vocabularios=vocabs,
        clasificaciones=vocabs.get("clasificaciones", []),
        horizontes=vocabs.get("horizontes", []),
        tipos_nota=vocabs.get("tipos-de-nota", []),
        plantilla_ahora=plantilla_ahora,
    )
