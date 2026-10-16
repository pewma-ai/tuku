"""Comandos del sustantivo `todo`: compromisos abiertos en PENDIENTES.md."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from tuku import todo as core_todo
from tuku.cli.helpers import Handler, Subparsers, traducir


def _cmd_todo_open(args: argparse.Namespace) -> int:
    day = date.fromisoformat(args.day) if args.day else None
    return traducir(
        core_todo.abrir_en_vault(
            args.vault,
            body=args.body,
            scope=args.scope,
            horizon=args.horizon,
            when=args.when,
            propagate=not args.no_propagate,
            day=day,
            hour=args.hour,
        ),
        "tuku todo open",
    )


def _cmd_todo_close(args: argparse.Namespace) -> int:
    day = date.fromisoformat(args.day) if args.day else None
    return traducir(
        core_todo.cerrar_en_vault(
            args.vault,
            body=args.body,
            propagate=not args.no_propagate,
            day=day,
            hour=args.hour,
            scope=args.scope,
        ),
        "todo close",
    )


def _cmd_todo_propagate(args: argparse.Namespace) -> int:
    return traducir(core_todo.propagar_vistas(args.vault), "todo propagate")


def _cmd_todo_lint(args: argparse.Namespace) -> int:
    return traducir(core_todo.lint_del_vault(args.vault), "todo lint")


def registrar(sub: Subparsers) -> dict[tuple[str, str | None], Handler]:
    todo_p = sub.add_parser(
        "todo",
        help="pendientes de PENDIENTES.md",
        description=(
            "`PENDIENTES.md` es la única fuente de verdad de lo que está por hacer. Estos "
            "comandos abren y cierran pendientes, regeneran las vistas que se derivan de "
            "esa tabla y revisan que sea coherente."
        ),
    )
    todo_v = todo_p.add_subparsers(dest="verb", required=True)

    for verbo, ayuda, descripcion in (
        (
            "open",
            "abre un pendiente: registro **pendiente** y fila en PENDIENTES.md",
            (
                "Escribe en `AHORA.md`, bajo el día y en orden de hora, el registro "
                "`- HH:MM - [ámbito](ruta) **pendiente**: cuerpo`, agrega la fila a la "
                "tabla de `PENDIENTES.md` bajo su horizonte y regenera las vistas como "
                "`tuku todo propagate`. Un día posterior a hoy es la fecha del pendiente. "
                "Si el registro ya estaba, no lo repite."
            ),
        ),
        (
            "close",
            "cierra un pendiente: registro (Hecho) y fila borrada",
            (
                "Escribe en `AHORA.md` el registro `- HH:MM - [ámbito](ruta) (Hecho): "
                "~~cuerpo~~`, borra de `PENDIENTES.md` la fila cuyo detalle coincide "
                "palabra por palabra y regenera las vistas. Si ninguna fila coincide, lo "
                "reporta y deja solo el registro."
            ),
        ),
    ):
        p = todo_v.add_parser(verbo, help=ayuda, description=descripcion)
        p.add_argument(
            "--body", "--cuerpo", dest="body", required=True, help="el texto del pendiente"
        )
        p.add_argument("--vault", default=".", type=Path, help="vault a modificar")
        p.add_argument(
            "--no-propagate",
            action="store_true",
            help="no regenera las vistas derivadas; para el lote, que propaga al final",
        )
        p.add_argument(
            "--day", "--dia", dest="day", default=None, help="día de registro, AAAA-MM-DD"
        )
        p.add_argument(
            "--hour", "--hora", dest="hour", default=None, help="hora en que se registra, HH:MM"
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
        elif verbo == "close":
            p.add_argument(
                "--scope", "--ambito", dest="scope", default=None, help="ámbito, sin corchetes"
            )

    todo_prop = todo_v.add_parser(
        "propagate",
        help="regenera las vistas derivadas de PENDIENTES.md",
        description=(
            "Regenera desde `PENDIENTES.md` sus dos vistas: bajo cada día de `AHORA.md`, "
            "los pendientes con esa fecha; en `ambitos/PENDIENTES-AMBITOS.md`, un callout "
            "por ámbito con sus filas. Sobre un vault al día no cambia nada."
        ),
    )
    todo_prop.add_argument("--vault", default=".", type=Path, help="vault a modificar")

    todo_lint = todo_v.add_parser(
        "lint",
        help="revisa los pendientes y reporta; no escribe",
        description=(
            "Revisa que ningún pendiente esté en dos filas de `PENDIENTES.md`, que cada "
            "`**pendiente**` de `AHORA.md` tenga su fila y que las vistas estén al día "
            "con la tabla. No escribe nada."
        ),
    )
    todo_lint.add_argument("--vault", default=".", type=Path, help="vault a revisar")

    return {
        ("todo", "open"): _cmd_todo_open,
        ("todo", "close"): _cmd_todo_close,
        ("todo", "propagate"): _cmd_todo_propagate,
        ("todo", "lint"): _cmd_todo_lint,
    }
