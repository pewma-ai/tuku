"""Las firmas de `spec/tuku.md` y el árbol de argparse dicen los mismos comandos y opciones.

Lo marcado `# pendiente` no se exige en argparse; lo de "Lo que se retira" se tolera en él.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from tuku.cli import _construir_parser

SPEC = Path(__file__).resolve().parent.parent.parent / "spec" / "tuku.md"

#: Opciones que no son parte de ninguna firma: la ayuda, y `--vault`, que vale en todos.
_IMPLICITAS = {"--help", "--vault"}

_TOKEN = re.compile(r"--?[\w-]+|[A-ZÁÉÍÓÚÑ]{2,}|[a-z]+")


@dataclass
class Firma:
    ruta: str
    posicionales: list[str] = field(default_factory=list)
    opciones: set[str] = field(default_factory=set)
    pendiente: bool = False
    piezas_pendientes: set[str] = field(default_factory=set)


def firma(linea: str) -> Firma:
    """Lee `tuku scope create NOMBRE [--parent] … # pendiente: --since`."""
    texto, _, comentario = linea.partition("#")
    tokens = _TOKEN.findall(texto.removeprefix("tuku"))
    ruta: list[str] = []
    while tokens and re.fullmatch(r"[a-z]+", tokens[0]):
        ruta.append(tokens.pop(0))
    f = Firma(" ".join(ruta))
    anterior_es_opcion = False
    for t in tokens:
        if t.startswith("-"):
            f.opciones.add(t)
            anterior_es_opcion = True
        else:
            if not anterior_es_opcion:  # tras una opción es su metavar: `--match TEXTO`
                f.posicionales.append(t)
            anterior_es_opcion = False
    comentario = comentario.strip()
    if comentario == "pendiente":
        f.pendiente = True
    elif comentario.startswith("pendiente:"):
        f.piezas_pendientes = set(comentario.removeprefix("pendiente:").split())
    return f


def _bloques(texto: str) -> list[tuple[str, list[str]]]:
    """Cada bloque ```text con la sección `##` en que está, y sus líneas `tuku …`."""
    bloques: list[tuple[str, list[str]]] = []
    seccion, dentro = "", False
    lineas: list[str] = []
    for linea in texto.splitlines():
        if not dentro and linea.startswith("## "):
            seccion = linea.removeprefix("## ").strip()
        elif not dentro and linea.strip() == "```text":
            dentro, lineas = True, []
        elif dentro and linea.strip() == "```":
            dentro = False
            bloques.append((seccion, lineas))
        elif dentro and linea.startswith("tuku"):
            lineas.append(linea)
    return bloques


def spec(texto: str) -> tuple[dict[str, Firma], dict[str, set[str]]]:
    """Las firmas, y lo que se retira: ruta → opciones, vacío si se retira el comando."""
    firmas: dict[str, Firma] = {}
    retiro: dict[str, set[str]] = {}
    for seccion, lineas in _bloques(texto):
        for linea in lineas:
            if seccion == "Lo que se retira":
                f = firma(linea.partition("→")[0])
                retiro.setdefault(f.ruta, set()).update(f.opciones)
            else:
                f = firma(linea)
                assert f.ruta not in firmas, f"`tuku {f.ruta}` tiene dos firmas"
                firmas[f.ruta] = f
    return firmas, retiro


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
        if isinstance(a, argparse._SubParsersAction):
            continue
        if a.option_strings:
            f.opciones.add(max(a.option_strings, key=len))
        else:
            f.posicionales.append(a.dest)
    f.opciones -= _IMPLICITAS
    return f


FIRMAS, RETIRO = spec(SPEC.read_text(encoding="utf-8"))
CLI = argparse_(_construir_parser())


def test_lee_comandos_metavars_y_piezas_pendientes() -> None:
    f = firma("tuku entry update [CUÁNDO] --match TEXTO --body     # pendiente: CUÁNDO")
    assert (f.ruta, f.posicionales) == ("entry update", ["CUÁNDO"])
    assert f.opciones == {"--match", "--body"}
    assert f.piezas_pendientes == {"CUÁNDO"} and not f.pendiente
    f = firma("tuku note create TÍTULO (--body | --body-file) [--scope] [--keyword…]")
    assert f.posicionales == ["TÍTULO"]
    assert f.opciones == {"--body", "--body-file", "--scope", "--keyword"}
    assert firma("tuku process                    # pendiente").pendiente
    assert firma("tuku context").ruta == "context"


def test_la_spec_tiene_firmas_y_retiros() -> None:
    assert len(FIRMAS) > 15
    assert "scope create" in FIRMAS and "cycle lint" in RETIRO


def test_todo_comando_del_cli_tiene_firma_o_se_retira() -> None:
    sobran = sorted(set(CLI) - set(FIRMAS) - {r for r, o in RETIRO.items() if not o})
    assert not sobran, f"comandos del CLI sin firma en spec/tuku.md: {sobran}"


def test_lo_que_se_retira_sigue_en_el_cli() -> None:
    for ruta, opciones in RETIRO.items():
        assert ruta in CLI, f"`tuku {ruta}` ya salió del CLI: borra su línea de los retiros"
        assert opciones <= CLI[ruta].opciones, (
            f"`tuku {ruta}` ya no tiene {sorted(opciones - CLI[ruta].opciones)}: "
            "borra su línea de los retiros"
        )
    assert not {r for r, o in RETIRO.items() if not o} & set(FIRMAS), (
        "un comando no puede tener firma y retirarse a la vez"
    )


@pytest.mark.parametrize("ruta", sorted(r for r, f in FIRMAS.items() if not f.pendiente))
def test_cada_firma_implementada_calza_con_argparse(ruta: str) -> None:
    assert ruta in CLI, f"`tuku {ruta}` está en la spec y no en el CLI: márcalo `# pendiente`"
    esperada, real = FIRMAS[ruta], CLI[ruta]
    pendientes = esperada.piezas_pendientes
    assert esperada.opciones - pendientes == real.opciones - RETIRO.get(ruta, set())
    posicionales = [p for p in esperada.posicionales if p not in pendientes]
    assert len(posicionales) == len(real.posicionales), (
        f"`tuku {ruta}`: la spec y el CLI no tienen los mismos posicionales"
    )
