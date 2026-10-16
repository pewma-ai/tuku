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

    for verbo, ayuda, descripcion, epilogo in (
        (
            "open",
            "abre el pendiente de un registro **pendiente** y propaga las vistas",
            (
                "Agrega una fila a la tabla de `PENDIENTES.md` bajo su horizonte, estampa "
                "la constancia en la bitácora y propaga las vistas derivadas. Normalmente "
                "lo llama `tuku entry add`; existe como comando para corregir a mano. "
                "Es idempotente."
            ),
            (
                "A mano: abrir `PENDIENTES.md` y agregar una fila a la tabla con el ámbito, "
                "cuerpo y plazo."
            ),
        ),
        (
            "close",
            "cierra el pendiente de un registro (Hecho)",
            (
                "Borra la fila cuyo detalle coincide palabra por palabra con el cierre, "
                "estampa la constancia y propaga las vistas. Un cierre sin pareja no es "
                "un fallo: se reporta y no se inventa nada. Es idempotente."
            ),
            (
                "A mano: abrir `PENDIENTES.md` y eliminar la fila correspondiente; en "
                "`AHORA.md` agregar la constancia de cierre con `(Hecho)`."
            ),
        ),
    ):
        p = todo_v.add_parser(verbo, help=ayuda, description=descripcion, epilog=epilogo)
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
            "Regenera, desde la tabla de `PENDIENTES.md`, las dos vistas derivadas: la "
            "región de cada día en `AHORA.md` y `ambitos/PENDIENTES-AMBITOS.md`. Las "
            "vistas se regeneran y no se reparan; sobre un vault cuadrado no cambia "
            "ningún archivo."
        ),
        epilog=(
            "A mano: bajo cada día de `AHORA.md` copiar los pendientes con esa fecha, "
            "y en `ambitos/PENDIENTES-AMBITOS.md` escribir un callout por ámbito."
        ),
    )
    todo_prop.add_argument("--vault", default=".", type=Path, help="vault a modificar")

    todo_lint = todo_v.add_parser(
        "lint",
        help="revisa los pendientes y reporta; no escribe",
        description=(
            "Revisa la tabla de `PENDIENTES.md`: que cada pendiente esté en exactamente "
            "una fila. No escribe nada."
        ),
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
