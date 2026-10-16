"""Comandos del sustantivo `todo`: compromisos abiertos en PENDIENTES.md."""

from __future__ import annotations

import argparse
from pathlib import Path

from tuku import todo as core_todo
from tuku.cli.helpers import Handler, Subparsers, fecha, hora, traducir
from tuku.config import ambito_por_defecto


def _cmd_todo_open(args: argparse.Namespace) -> int:
    return traducir(
        core_todo.abrir_en_vault(
            args.vault,
            body=args.body,
            scope=args.scope or ambito_por_defecto(args.vault),
            horizon=args.horizon,
            due=args.due,
            propagate=not args.no_propagate,
            day=args.day,
            hour=args.hour,
        ),
        "tuku todo open",
    )


def _cmd_todo_close(args: argparse.Namespace) -> int:
    return traducir(
        core_todo.cerrar_en_vault(
            args.vault,
            body=args.body,
            propagate=not args.no_propagate,
            day=args.day,
            hour=args.hour,
            scope=args.scope or ambito_por_defecto(args.vault),
        ),
        "todo close",
    )


def _cmd_todo_lint(args: argparse.Namespace) -> int:
    return traducir(core_todo.lint_del_vault(args.vault), "todo lint")


def registrar(sub: Subparsers) -> dict[tuple[str, str | None], Handler]:
    todo_p = sub.add_parser(
        "todo",
        help="pendientes de PENDIENTES.md",
        description=(
            "Un pendiente es un compromiso abierto: una fila de `PENDIENTES.md`, la única "
            "fuente de lo que está por hacer, y su registro `**pendiente**` en `AHORA.md`. "
            "Estos comandos abren y cierran pendientes y revisan la tabla; sus vistas las "
            "regenera `tuku regenerate todo`."
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
                "`tuku regenerate todo`. El día y la hora son cuándo se prometió; la fecha "
                "del pendiente va en `--due`. Si el registro ya estaba, no lo repite."
            ),
        ),
        (
            "close",
            "cierra un pendiente: registro (Hecho) y fila borrada",
            (
                "Escribe en `AHORA.md` el registro `- HH:MM - [ámbito](ruta) (Hecho): "
                "~~cuerpo~~`, borra de `PENDIENTES.md` la fila cuyo detalle coincide "
                "palabra por palabra y regenera las vistas. Si el pendiente se abrió ese "
                "mismo día, borra el registro que lo abrió. Si ninguna fila coincide, lo "
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
            "--day",
            "--dia",
            dest="day",
            default=None,
            type=fecha,
            help="día en que se registra, AAAA-MM-DD; por defecto, hoy",
        )
        p.add_argument(
            "--hour",
            "--hora",
            dest="hour",
            default=None,
            type=hora,
            help="hora en que se registra, HH:MM; por defecto, ahora",
        )
        if verbo == "open":
            p.add_argument(
                "--scope",
                "--ambito",
                dest="scope",
                default=None,
                help="ámbito, sin corchetes; por defecto, `scope_default` de la config",
            )
            plazo = p.add_mutually_exclusive_group()
            plazo.add_argument(
                "--due",
                "--vence",
                dest="due",
                default=None,
                type=fecha,
                help="día en que vence, AAAA-MM-DD; el horizonte pasa a `con fecha`",
            )
            plazo.add_argument(
                "--horizon",
                "--horizonte",
                dest="horizon",
                default=None,
                help=(
                    "escalón del pendiente sin fecha, de `### Horizontes` en el libro de "
                    "estilo; por defecto, el primero"
                ),
            )
        elif verbo == "close":
            p.add_argument(
                "--scope",
                "--ambito",
                dest="scope",
                default=None,
                help="ámbito, sin corchetes; por defecto, `scope_default` de la config",
            )

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
        ("todo", "lint"): _cmd_todo_lint,
    }
