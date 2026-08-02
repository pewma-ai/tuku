"""Extracción de los bloques normativos de `spec/`.

`spec/README.md` declara que **los ejemplos son normativos**: los bloques de código
de una spec no son ilustraciones, son casos que el parser debe aceptar y el motor
reproducir.

Este módulo los lee directamente del Markdown en vez de copiarlos a `tests/fixtures/`.
La razón es la misma por la que TUKU no duplica datos: una copia se desincroniza.
Si alguien corrige un ejemplo en la spec, el test debe cambiar con él —y si el
ejemplo corregido rompe el parser, eso es exactamente lo que hay que enterarse.

Un bloque se marca como caso de test con un comentario HTML inmediatamente antes:

    <!-- tuku:caso id=tarea-minima tipo=tarea -->
    ```markdown
    - [ ] 2026-05-13 4h nucleo-datos - - - manual Texto ^t-2026-0104
    ```

Los bloques sin marca se ignoran: no todo bloque de una spec es un caso ejecutable
(hay árboles de directorios, YAML ilustrativo y fragmentos de prosa).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

SPEC_DIR = Path(__file__).resolve().parent.parent / "spec"

_MARCA = re.compile(
    r"<!--\s*tuku:caso\s+(?P<attrs>[^>]*?)-->\s*\n"
    r"```(?P<lang>\w*)\n(?P<cuerpo>.*?)```",
    re.DOTALL,
)
_ATTR = re.compile(r"(\w+)=([^\s]+)")


@dataclass(frozen=True)
class Caso:
    """Un bloque normativo extraído de una spec."""

    id: str
    tipo: str
    lang: str
    cuerpo: str
    spec: str
    linea: int

    def __str__(self) -> str:  # aparece en el nombre del test parametrizado
        return f"{self.spec}:{self.id}"


def casos(spec: str | None = None, tipo: str | None = None) -> list[Caso]:
    """Devuelve los casos marcados, opcionalmente filtrados por spec y tipo."""
    archivos = [SPEC_DIR / spec] if spec else sorted(SPEC_DIR.glob("*.md"))
    encontrados: list[Caso] = []
    for archivo in archivos:
        if not archivo.exists():
            continue
        texto = archivo.read_text(encoding="utf-8")
        for m in _MARCA.finditer(texto):
            attrs = dict(_ATTR.findall(m.group("attrs")))
            caso = Caso(
                id=attrs.get("id", "sin-id"),
                tipo=attrs.get("tipo", ""),
                lang=m.group("lang"),
                cuerpo=m.group("cuerpo"),
                spec=archivo.name,
                linea=texto[: m.start()].count("\n") + 1,
            )
            if tipo is None or caso.tipo == tipo:
                encontrados.append(caso)
    return encontrados


# ---------------------------------------------------------------------------
# Invariantes declaradas en las specs
# ---------------------------------------------------------------------------

_INVARIANTE = re.compile(
    r"^\|\s*\*{0,2}(?P<id>[A-Z]\d+)\*{0,2}\s*\|\s*(?P<texto>.+?)\s*\|\s*(?P<garante>.+?)\s*\|",
    re.MULTILINE,
)


@dataclass(frozen=True)
class Invariante:
    id: str
    texto: str
    garante: str
    spec: str


def invariantes(spec: str | None = None) -> list[Invariante]:
    """Lee las tablas de invariantes de las specs.

    Es lo que permite que `test_cobertura_specs.py` compare, sin mantener una
    lista a mano, qué invariantes tienen test y cuáles no.
    """
    archivos = [SPEC_DIR / spec] if spec else sorted(SPEC_DIR.glob("*.md"))
    salida: list[Invariante] = []
    for archivo in archivos:
        if not archivo.exists():
            continue
        for m in _INVARIANTE.finditer(archivo.read_text(encoding="utf-8")):
            salida.append(
                Invariante(
                    id=m.group("id"),
                    texto=m.group("texto"),
                    garante=m.group("garante"),
                    spec=archivo.name,
                )
            )
    return salida
