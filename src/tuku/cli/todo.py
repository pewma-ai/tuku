"""Comandos del sustantivo `todo`: compromisos abiertos en PENDIENTES.md."""

from __future__ import annotations

import argparse
from pathlib import Path

from tuku import todo as core_todo
from tuku.cli.helpers import Handler, Subparsers, traducir


def _cmd_todo_open(args: argparse.Namespace) -> int:
    return traducir(
        core_todo.abrir_en_vault(
            args.vault,
            body=args.body,
            scope=args.scope,
            horizon=args.horizon,
            when=args.when,
            propagate=not args.no_propagate,
        ),
        "tuku todo open",
    )


def _cmd_todo_close(args: argparse.Namespace) -> int:
    return traducir(
        core_todo.cerrar_en_vault(args.vault, body=args.body, propagate=not args.no_propagate),
        "todo close",
    )


def _cmd_todo_propagate(args: argparse.Namespace) -> int:
    return traducir(core_todo.propagar_vistas(args.vault), "todo propagate")


def _cmd_todo_lint(args: argparse.Namespace) -> int:
    return traducir(core_todo.lint_del_vault(args.vault), "todo lint")


def registrar(sub: Subparsers) -> dict[tuple[str, str | None], Handler]:
    todo_p = sub.add_parser("todo", help="pendientes de PENDIENTES.md")
    todo_v = todo_p.add_subparsers(dest="verb", required=True)

    for verbo, ayuda, epilogo in (
        (
            "open",
            "abre el pendiente de un registro **pendiente** y propaga las vistas",
            (
                "A mano: abrir `PENDIENTES.md` y agregar una fila a la tabla con el ámbito, "
                "cuerpo y plazo."
            ),
        ),
        (
            "close",
            "cierra el pendiente de un registro ~~(Hecho)~~",
            (
                "A mano: abrir `PENDIENTES.md` y eliminar la fila correspondiente; en "
                "`AHORA.md` agregar la constancia de cierre con `~~(Hecho)~~`."
            ),
        ),
    ):
        p = todo_v.add_parser(verbo, help=ayuda, epilog=epilogo)
        p.add_argument(
            "--body", "--cuerpo", dest="body", required=True, help="el texto del pendiente"
        )
        p.add_argument("--vault", default=".", type=Path, help="vault a modificar")
        p.add_argument(
            "--no-propagate",
            action="store_true",
            help="no regenera las vistas derivadas; para el lote, que propaga al final",
        )
        if verbo == "open":
            p.add_argument(
                "--scope", "--ambito", dest="scope", default=None, help="ámbito, sin corchetes"
            )
            p.add_argument(
                "--horizon",
                "--horizonte",
                dest="horizon",
                default=core_todo.ESTA_SEMANA,
                help="horizonte destino: el encabezado bajo el que va la fila",
            )
            p.add_argument(
                "--when",
                "--cuando",
                dest="when",
                default="",
                help="fecha del pendiente, AAAA-MM-DD; vacío si no la tiene",
            )

    todo_prop = todo_v.add_parser(
        "propagate",
        help="regenera las vistas derivadas de PENDIENTES.md",
        epilog=(
            "A mano: bajo cada día de `AHORA.md` copiar los pendientes con esa fecha, "
            "y en `ambitos/PENDIENTES-AMBITOS.md` escribir un callout por ámbito."
        ),
    )
    todo_prop.add_argument("--vault", default=".", type=Path, help="vault a modificar")

    todo_lint = todo_v.add_parser(
        "lint",
        help="revisa los pendientes y reporta; no escribe",
        epilog=(
            "A mano: abrir `PENDIENTES.md` y verificar que las columnas de la tabla "
            "estén completas y alineadas."
        ),
    )
    todo_lint.add_argument("--vault", default=".", type=Path, help="vault a revisar")

    return {
        ("todo", "open"): _cmd_todo_open,
        ("todo", "close"): _cmd_todo_close,
        ("todo", "propagate"): _cmd_todo_propagate,
        ("todo", "lint"): _cmd_todo_lint,
    }
