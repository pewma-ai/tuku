"""El mapa de `spec/tuku.md` y el árbol de argparse dicen los mismos comandos.

La spec lista los comandos con sus opciones principales; el detalle de cada opción vive en la
ayuda. Lo marcado `# pendiente` no se exige en argparse.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path

from tuku.cli import _construir_parser

SPEC = Path(__file__).resolve().parent.parent.parent / "spec" / "tuku.md"

#: Opciones que no son parte de ninguna firma: la ayuda, y `--vault`, que vale en todos.
_IMPLICITAS = {"--help", "--vault"}

_TOKEN = re.compile(r"--?[\w-]+|[A-ZÁÉÍÓÚÑ]{2,}|[a-z]+")


@dataclass
class Firma:
    ruta: str
    opciones: set[str] = field(default_factory=set)
    pendiente: bool = False


def firma(linea: str) -> Firma:
    """Lee `tuku scope create NOMBRE [--parent] … # pendiente`."""
    texto, _, comentario = linea.partition("#")
    tokens = _TOKEN.findall(texto.removeprefix("tuku"))
    ruta: list[str] = []
    while tokens and re.fullmatch(r"[a-z]+", tokens[0]):
        ruta.append(tokens.pop(0))
    return Firma(
        " ".join(ruta),
        {t for t in tokens if t.startswith("-")},
        comentario.strip() == "pendiente",
    )


def spec(texto: str) -> dict[str, Firma]:
    """Cada línea `tuku …` de un bloque ```text, por su ruta."""
    firmas: dict[str, Firma] = {}
    dentro = False
    for linea in texto.splitlines():
        if linea.strip() == "```text":
            dentro = True
        elif dentro and linea.strip() == "```":
            dentro = False
        elif dentro and linea.startswith("tuku"):
            f = firma(linea)
            assert f.ruta not in firmas, f"`tuku {f.ruta}` tiene dos firmas"
            firmas[f.ruta] = f
    return firmas


def argparse_(parser: argparse.ArgumentParser, ruta: str = "") -> dict[str, Firma]:
    """El árbol de argparse como firmas: cada comando invocable con sus opciones largas."""
    subs = [a for a in parser._actions if isinstance(a, argparse._SubParsersAction)]
    if subs:
        propio = {} if subs[0].required else {ruta: _firma_de(parser, ruta)}
        return propio | {
            r: f
            for nombre, sub in subs[0].choices.items()
            for r, f in argparse_(sub, f"{ruta} {nombre}".strip()).items()
        }
    return {ruta: _firma_de(parser, ruta)}


def _firma_de(parser: argparse.ArgumentParser, ruta: str) -> Firma:
    f = Firma(ruta)
    for a in parser._actions:
        if not isinstance(a, argparse._SubParsersAction) and a.option_strings:
            f.opciones.add(max(a.option_strings, key=len))
    f.opciones -= _IMPLICITAS
    return f


FIRMAS = spec(SPEC.read_text(encoding="utf-8"))
CLI = argparse_(_construir_parser())


def test_lee_comandos_opciones_y_pendientes() -> None:
    f = firma("tuku entry update [CUÁNDO] --match TEXTO --body")
    assert f.ruta == "entry update" and f.opciones == {"--match", "--body"}
    f = firma("tuku note create TÍTULO (--body | --body-file) [--scope] [--alias…]")
    assert f.opciones == {"--body", "--body-file", "--scope", "--alias"}
    assert firma("tuku todo update TEXTO [--horizon]    # pendiente").pendiente
    assert firma("tuku context").ruta == "context"


def test_la_spec_tiene_firmas() -> None:
    assert len(FIRMAS) > 15
    assert "scope create" in FIRMAS


def test_todo_comando_del_cli_esta_en_el_mapa() -> None:
    sobran = sorted(set(CLI) - set(FIRMAS))
    assert not sobran, f"comandos del CLI sin firma en spec/tuku.md: {sobran}"


def test_cada_comando_del_mapa_existe_con_sus_opciones() -> None:
    for ruta, esperada in sorted(FIRMAS.items()):
        if esperada.pendiente:
            continue
        assert ruta in CLI, f"`tuku {ruta}` está en la spec y no en el CLI: márcalo pendiente"
        faltan = esperada.opciones - CLI[ruta].opciones
        assert not faltan, f"`tuku {ruta}`: la spec nombra {sorted(faltan)}, el CLI no"
