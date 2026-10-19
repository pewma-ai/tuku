"""CLI de TUKU: capa fina de argparse sobre las funciones de `tuku/`.

`tuku <noun> <verb>`, todo en inglés. La lógica no vive acá: cada comando llama
a una función importable de `tuku/` y traduce su resultado a texto y a un código
de salida. El contrato de esa traducción está en `spec/cli.md`.

`init` es la excepción a la forma `<noun> <verb>`: siembra el vault y no opera
sobre uno, así que no tiene sustantivo sobre el que actuar.
"""

from __future__ import annotations

import argparse
import functools
import sys
from datetime import datetime
from pathlib import Path

from tuku import archivo
from tuku.cli import ejemplos, entry, note, scope, system, todo
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
from tuku.cli.opciones import completar, sin_anio
from tuku.config import VaultInvalido, exigir_vault, hora_local, leer_preferencias, zona_valida
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
    """Todo lo invocable, como `"entry create"` o `"doctor"`.

    Sale del parser y no de una lista escrita aparte: una lista se desincroniza
    en silencio, y lo que `tuku doctor` afirma con esto es justamente que un
    documento del vault no nombre un comando que no existe.
    """
    if not _COMANDOS:
        _construir_parser()
    return frozenset(noun if verb is None else f"{noun} {verb}" for noun, verb in _COMANDOS)


@functools.cache
def _construir_parser() -> argparse.ArgumentParser:
    """El árbol entero de comandos. Se arma una vez por proceso.

    Armarlo cuesta tanto como el comando más común, y `main` se llama muchas
    veces en el mismo proceso cuando lo invocan los tests o un lote.
    """
    global _COMANDOS
    parser = argparse.ArgumentParser(
        prog="tuku",
        description=(
            "TUKU: gestión personal en archivos Markdown (Management as Code). Cada "
            "comando escribe o revisa archivos del vault que también se editan con "
            "cualquier editor; su ayuda dice cuáles y cómo."
        ),
    )
    sub = parser.add_subparsers(dest="noun", required=True)

    cmds: dict[tuple[str, str | None], Handler] = {}
    cmds.update(system.registrar(sub, comandos))
    cmds.update(entry.registrar(sub))
    cmds.update(todo.registrar(sub))
    cmds.update(scope.registrar(sub))
    cmds.update(note.registrar(sub))

    ejemplos.aplicar(parser)
    _COMANDOS = cmds
    return parser


def _reloj(args: argparse.Namespace) -> datetime:
    """The clock in the zone `TZ` of the vault's `reglas/config.tuku.md` names.

    Without a vault, a config or a valid zone it is the system's clock; an invalid
    zone is also reported, because it moves the day a todo is due.
    """
    vault = getattr(args, "vault", None)
    zona = leer_preferencias(vault).zona_horaria if vault is not None else ""
    if zona and not zona_valida(zona):
        print(
            f"tuku: la zona horaria «{zona}» de reglas/config.tuku.md no existe: "
            "se usa la del sistema. `tuku doctor config` la revisa.",
            file=sys.stderr,
        )
    return hora_local(zona)


def main(argv: list[str] | None = None, *, now: datetime | None = None) -> int:
    """Corre un comando. El reloj se lee acá, una vez, y baja como `args.now`.

    `now` lo fijan quienes necesitan un día determinado (el arnés de escenarios, con
    `TUKU_NOW`); sin él es la hora de la zona `TZ` del vault, o la del sistema.
    """
    argv = sys.argv[1:] if argv is None else argv
    args = _construir_parser().parse_args(argv)
    args.now = now or _reloj(args)
    completar(args, args.now)
    if error := sin_anio(args, argv):
        print(f"tuku: {error}", file=sys.stderr)
        return USO
    comando = _COMANDOS[(args.noun, getattr(args, "verb", None))]
    try:
        # `doctor note <archivo>` revisa un archivo suelto y no lee el vault.
        if getattr(args, "file", None) is None and (vault := getattr(args, "vault", None)):
            exigir_vault(vault)
        return archivo.con_reintentos(lambda: comando(args))
    except archivo.SinReintentos as e:
        nombre = " ".join(filter(None, (args.noun, getattr(args, "verb", None))))
        base = getattr(args, "vault", None) or Path()
        print(f"tuku {nombre}: {e.mensaje(base)}", file=sys.stderr)
        return RECHAZO
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
