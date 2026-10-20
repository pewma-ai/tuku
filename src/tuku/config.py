"""Lectura centralizada de configuración, libro de estilo y reglas de un vault.

Reúne en un solo lugar todas las lecturas de los archivos normativos del vault
(`reglas/config.tuku.md`, los archivos del autor en `reglas/` y
`reglas/plantilla/AHORA.md`).
Permite testear el comportamiento en memoria y desacopla la ubicación física
de los archivos del resto de los comandos de TUKU.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from tuku import archivo, capitulos, vocab
from tuku.init import MESES, resolver_home

#: Fila de la tabla de configuración: `| `Campo` | `Valor` |`.
_FILA_CONFIG = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*`?([^`|]*?)`?\s*\|")
#: Lo que el autor no ha declarado en la fila `Nombre` de `reglas/autor.user.md`.
_SIN_DECLARAR = ("pedir al autor", "no especificado", "por declarar")


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


def exigir_vault(vault: Path) -> None:
    """Lanza VaultInvalido si `vault` no tiene nada de lo que un vault trae.

    Basta con que exista uno de los archivos requeridos: un vault al que le
    falta alguno sigue siendo un vault, y es justo el que `tuku doctor` debe
    poder diagnosticar. Lo que no puede hacer ningún comando es recorrer un
    directorio cualquiera, como el `~` desde donde se invocó sin querer.
    """
    from tuku.doctor import ARCHIVOS_REQUERIDOS

    if not any((vault / r).is_file() for r in ARCHIVOS_REQUERIDOS):
        raise VaultInvalido(
            f"{vault.resolve()} no es un vault de TUKU: no tiene ninguno de sus archivos "
            f"({', '.join(ARCHIVOS_REQUERIDOS[:2])}, ...). "
            "Entra a un vault, pasa `--vault <ruta>`, o siembra uno con `tuku init <dir>`."
        )


@dataclass(frozen=True)
class Configuracion:
    """Configuración consolidada de un vault."""

    vault: Path
    # De reglas/config.tuku.md
    zona_horaria: str
    nombres_de_ciclo: tuple[str, ...]
    datos: dict[str, str]
    # De los archivos del autor en reglas/
    autor: str | None
    vocabularios: dict[str, list[str]]
    clasificaciones: list[str]
    horizontes: list[str]
    tipos_nota: list[str]
    tipos_enlazables: list[str]
    # De reglas/plantilla/
    plantilla_ahora: str

    def vocabularios_abiertos(self) -> list[str]:
        """Términos declarados en todas las tablas del libro de estilo."""
        return [t for terminos in self.vocabularios.values() for t in terminos]


#: Cómo se escribe una fecha corta si `config.tuku.md` no declara `date_format`.
FORMATO_FECHA = "MMM/DD"

_MESES_CORTOS = tuple(m[:3].capitalize() for m in MESES)


def fecha_corta(fecha: date, formato: str = FORMATO_FECHA) -> str:
    """La fecha con el formato del vault.

    `MMM` es el mes abreviado (`Ago`), `MM` el mes en dos dígitos, `DD` el día
    en dos dígitos y `AAAA` el año.
    """
    return (
        (formato or FORMATO_FECHA)
        .replace("AAAA", f"{fecha.year:04d}")
        .replace("MMM", "\0")
        .replace("MM", f"{fecha.month:02d}")
        .replace("DD", f"{fecha.day:02d}")
        .replace("\0", _MESES_CORTOS[fecha.month - 1])
    )


#: Cuántas notas por tipo trae `tuku context note` si la config no dice otra cosa.
LIMITE_DE_NOTAS = 25

#: Cómo se llama el ciclo si `reglas/ciclo.user.md` no lo dice.
CICLO_POR_DEFECTO = "semana"


@dataclass(frozen=True)
class Preferencias:
    """What `reglas/config.tuku.md` decides, each field with its default.

    The one reader of that table: every command that needs a preference asks
    here, so a default is written once. An empty `zona_horaria` means the
    system's own.
    """

    zona_horaria: str = ""
    ambito_por_defecto: str | None = None
    formato_fecha: str = FORMATO_FECHA
    limite_de_notas: int = LIMITE_DE_NOTAS
    datos: dict[str, str] = field(default_factory=dict)


def _limpio(datos: dict[str, str], campo: str) -> str:
    return datos.get(campo, "").strip("`").strip()


def leer_preferencias(vault: Path | None = None, *, texto: str | None = None) -> Preferencias:
    """The preferences of `vault`, or the defaults if its config is missing or incomplete.

    `texto` replaces the file, for callers that already hold it.
    """
    if texto is None:
        ruta = Path(vault) / "reglas" / "config.tuku.md" if vault is not None else None
        texto = archivo.leer(ruta) if ruta is not None and ruta.is_file() else ""
    datos = parsear_config_md(texto)
    limite = _limpio(datos, "context_note_limit")
    return Preferencias(
        zona_horaria=_limpio(datos, "TZ"),
        ambito_por_defecto=_limpio(datos, "scope_default") or None,
        formato_fecha=_limpio(datos, "date_format") or FORMATO_FECHA,
        limite_de_notas=int(limite)
        if limite.isdigit() and int(limite) > 0
        else LIMITE_DE_NOTAS,
        datos=datos,
    )


def formato_fecha(vault: Path) -> str:
    """El `date_format` de `reglas/config.tuku.md`, o el de por defecto."""
    return leer_preferencias(vault).formato_fecha


def ambito_por_defecto(vault: Path) -> str | None:
    """El `scope_default` de `reglas/config.tuku.md`: el ámbito de lo que no nombra otro."""
    return leer_preferencias(vault).ambito_por_defecto


def limite_de_notas(vault: Path) -> int:
    """El `context_note_limit` de `reglas/config.tuku.md`, o 25 si falta o no es un entero."""
    return leer_preferencias(vault).limite_de_notas


def zona_valida(zona: str) -> bool:
    """Whether `zona` is an IANA name this machine knows (`America/Santiago`)."""
    try:
        ZoneInfo(zona)
    except ZoneInfoNotFoundError, ValueError, OSError:
        return False
    return True


def hora_local(zona: str) -> datetime:
    """The wall-clock now in `zona`, naive like every datetime in `tuku`.

    An empty or unknown zone gives the system's clock: `doctor config` and
    `main` are who tell the author that the zone is wrong.
    """
    if zona and zona_valida(zona):
        return datetime.now(ZoneInfo(zona)).replace(tzinfo=None)
    return datetime.now()


def parsear_config_md(texto: str) -> dict[str, str]:
    """Los campos de la tabla de `config.tuku.md`.

    Se leen solo las filas cuyo primer campo va entre backticks, así el
    encabezado y los callouts quedan fuera sin tener que reconocerlos.
    """
    pares: dict[str, str] = {}
    for linea in texto.splitlines():
        if m := _FILA_CONFIG.match(linea.strip()):
            pares[m.group(1).strip()] = m.group(2).strip()
    return pares


def parsear_autor(texto_autor: str) -> str | None:
    """El nombre del autor: la fila `Nombre` de `reglas/autor.user.md`, si se declaró."""
    tabla = capitulos.primera_tabla(texto_autor)
    for fila in tabla[1:] if tabla else []:
        if len(fila) > 1 and fila[0].lower() == "nombre":
            valor = fila[1].strip()
            if valor and not valor.lower().startswith(_SIN_DECLARAR):
                return valor
    return None


def resolver_plantilla_ahora(vault: Path) -> str:
    """Busca la plantilla de AHORA.md en el vault o en el fallback de TUKU."""
    local = vault / "reglas" / "plantilla" / "AHORA.md"
    if local.is_file():
        return archivo.leer(local)
    fallback = resolver_home() / "template" / "vanilla" / "reglas" / "plantilla" / "AHORA.md"
    if fallback.is_file():
        return archivo.leer(fallback)
    raise FileNotFoundError(
        f"no se encontró la plantilla de AHORA.md en {local} ni en {fallback}"
    )


def leer_config(
    vault: Path,
    *,
    texto_config: str | None = None,
    textos_reglas: Mapping[str, str] | None = None,
    texto_plantilla_ahora: str | None = None,
) -> Configuracion:
    """Lee y consolida configuración, archivos del autor y plantillas de un vault.

    `textos_reglas` reemplaza archivos de `reglas/` por su ruta (`reglas/autor.user.md`),
    para quien ya los tiene en memoria.
    """
    vault = Path(vault)

    # 1. reglas/config.tuku.md
    if texto_config is None:
        ruta_config = vault / "reglas" / "config.tuku.md"
        texto_config = archivo.leer(ruta_config) if ruta_config.is_file() else ""
    prefs = leer_preferencias(texto=texto_config)

    # 2. Los archivos del autor en reglas/
    def regla(ruta: str) -> str:
        if textos_reglas is not None and ruta in textos_reglas:
            return textos_reglas[ruta]
        return archivo.leer(archivo_vault(vault, ruta))

    autor = parsear_autor(regla("reglas/autor.user.md"))
    vocabs = vocab.leer({ruta: regla(ruta) for ruta in vocab.ARCHIVOS})

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
        zona_horaria=prefs.zona_horaria,
        nombres_de_ciclo=tuple(vocabs.get("ciclos", [])) or (CICLO_POR_DEFECTO,),
        datos=prefs.datos,
        autor=autor,
        vocabularios=vocabs,
        clasificaciones=vocabs.get("clasificaciones", []),
        horizontes=vocabs.get("horizontes", []),
        tipos_nota=vocabs.get("tipos-de-nota", []),
        tipos_enlazables=vocab.enlazables(regla("reglas/notas.user.md")),
        plantilla_ahora=plantilla_ahora,
    )
