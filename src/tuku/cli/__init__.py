"""CLI de TUKU: capa fina de argparse sobre las funciones de `tuku/`.

`tuku <noun> <verb>`, todo en inglés. La lógica no vive acá: cada comando llama
a una función importable de `tuku/` y traduce su resultado a texto y a un código
de salida. El contrato de esa traducción está en `spec/cli.md`.

`init` es la excepción a la forma `<noun> <verb>`: siembra el vault y no opera
sobre uno, así que no tiene sustantivo sobre el que actuar.
"""

from __future__ import annotations

import argparse
import sys

from tuku.cli import entry, note, scope, system, todo
from tuku.cli.helpers import (
    ENTORNO,
    EXITO,
    RECHAZO,
    USO,
    Handler,
)
from tuku.cli.helpers import (
    cuerpo_de_la_nota as _cuerpo_de_la_nota,
)
from tuku.config import VaultInvalido
from tuku.init import MarcadorAutorFaltante
from tuku.todo import SinTabla
from tuku.vocab import VocabularioIncompleto

__all__ = [
    "ENTORNO",
    "EXITO",
    "RECHAZO",
    "USO",
    "_COMANDOS",
    "_construir_parser",
    "_cuerpo_de_la_nota",
    "comandos",
    "main",
]

_COMANDOS: dict[tuple[str, str | None], Handler] = {}


def comandos() -> frozenset[str]:
    """Todo lo invocable, como `"entry add"` o `"doctor"`.

    Sale del parser y no de una lista escrita aparte: una lista se desincroniza
    en silencio, y lo que `tuku doctor` afirma con esto es justamente que un
    documento del vault no nombre un comando que no existe.
    """
    if not _COMANDOS:
        _construir_parser()
    return frozenset(
        noun if verb is None else f"{noun} {verb}" for noun, verb in _COMANDOS
    )


def _construir_parser() -> argparse.ArgumentParser:
    global _COMANDOS
    parser = argparse.ArgumentParser(
        prog="tuku",
        description="TUKU — Management as Code para la vida personal.",
    )
    sub = parser.add_subparsers(dest="noun", required=True)

    cmds: dict[tuple[str, str | None], Handler] = {}
    cmds.update(system.registrar(sub, comandos))
    cmds.update(entry.registrar(sub))
    cmds.update(todo.registrar(sub))
    cmds.update(scope.registrar(sub))
    cmds.update(note.registrar(sub))

    _COMANDOS = cmds
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _construir_parser().parse_args(argv)
    comando = _COMANDOS[(args.noun, getattr(args, "verb", None))]
    try:
        return comando(args)
    except (
        VaultInvalido,
        VocabularioIncompleto,
        SinTabla,
        MarcadorAutorFaltante,
    ) as e:
        print(f"tuku {args.noun}: {e}", file=sys.stderr)
        return RECHAZO


if __name__ == "__main__":
    raise SystemExit(main())
