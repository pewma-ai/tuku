"""Comandos del sustantivo `entry`: registros de la bitácora."""

from __future__ import annotations

import argparse
from pathlib import Path

from tuku import entry
from tuku.cli.helpers import Handler, Subparsers, fecha, hora, traducir


def _cmd_entry_add(args: argparse.Namespace) -> int:
    return traducir(
        entry.add_al_vault(
            args.vault,
            body=args.body,
            scope=args.scope,
            day=args.day,
            hour=args.hour,
            horizon=args.horizon,
            when=args.when,
        ),
        "tuku entry add",
    )


def _cmd_entry_rename(args: argparse.Namespace) -> int:
    return traducir(
        entry.corregir_en_vault(
            args.vault, body=args.body, day=args.day, hour=args.hour
        ),
        "tuku entry rename",
    )


def _cmd_entry_lint(args: argparse.Namespace) -> int:
    return traducir(entry.lint_del_vault(args.vault), "tuku entry lint")


def registrar(sub: Subparsers) -> dict[tuple[str, str | None], Handler]:
    entry_p = sub.add_parser(
        "entry",
        help="registros de la bitácora",
        description=(
            "Un registro es una línea de `AHORA.md` que cuenta un hecho: hora, ámbito, "
            "marca y cuerpo. Estos comandos escriben y corrigen registros con el "
            "formato canónico, y revisan los que ya están."
        ),
    )
    entry_v = entry_p.add_subparsers(dest="verb", required=True)

    add_p = entry_v.add_parser(
        "add",
        help="escribe un registro en la bitácora",
        description=(
            "Compone la línea canónica a partir de los campos (hora, ámbito con su link, "
            "marca y cuerpo), la inserta en su día por orden de hora y aplica lo que la "
            "marca implica: un `**pendiente**` abre su fila y un `(Hecho)` la cierra. "
            "Existe para que quien dicta aporte el juicio y el comando, la forma."
        ),
        epilog=(
            "A mano: abrir `AHORA.md`, buscar el día correspondiente y agregar una línea "
            "bajo la sección con formato `- HH:MM - [ambito](ruta) **marca**: cuerpo`."
        ),
    )
    add_p.add_argument("--vault", default=".", type=Path, help="vault destino")
    add_p.add_argument(
        "--body",
        "--cuerpo",
        dest="body",
        required=True,
        help="la marca y el cuerpo: '**pendiente**: avisar de los gastos comunes'",
    )
    add_p.add_argument(
        "--scope", "--ambito", dest="scope", default=None, help="ámbito, sin corchetes"
    )
    add_p.add_argument(
        "--day",
        "--dia",
        dest="day",
        default=None,
        type=fecha,
        help="día del registro (AAAA-MM-DD); por defecto, hoy",
    )
    add_p.add_argument(
        "--hour",
        "--hora",
        dest="hour",
        default=None,
        type=hora,
        help="hora del registro (HH:MM); por defecto, ahora",
    )
    add_p.add_argument(
        "--horizon",
        "--horizonte",
        dest="horizon",
        default=None,
        help="para un **pendiente**: el escalón donde nace; por defecto, el del ciclo",
    )
    add_p.add_argument(
        "--when",
        "--cuando",
        dest="when",
        default="",
        help="para un **pendiente**: su fecha (AAAA-MM-DD), si la tiene",
    )

    rename_p = entry_v.add_parser(
        "rename",
        help="corrige el cuerpo de un registro ya escrito",
        description=(
            "Reemplaza el cuerpo de un registro, ubicado por su día y su hora, y actualiza "
            "la fila de `PENDIENTES.md` si era un pendiente. Existe porque las dos copias "
            "deben decir lo mismo carácter por carácter o el pendiente deja de poder "
            "cerrarse. La hora y el ámbito no se tocan."
        ),
        epilog=(
            "A mano: abrir `AHORA.md`, ubicar el registro por su hora y editar su texto. "
            "Si era un pendiente, buscar la fila en `PENDIENTES.md` y actualizarla para "
            "que coincida palabra por palabra."
        ),
    )
    rename_p.add_argument("--vault", default=".", type=Path, help="vault a modificar")
    rename_p.add_argument(
        "--body",
        "--cuerpo",
        dest="body",
        required=True,
        help="el cuerpo corregido, con su marca si la lleva",
    )
    rename_p.add_argument(
        "--day",
        "--dia",
        dest="day",
        default=None,
        type=fecha,
        help="día del registro (AAAA-MM-DD); por defecto, hoy",
    )
    rename_p.add_argument(
        "--hour", "--hora", dest="hour", required=True, help="hora del registro (HH:MM)"
    )

    lint_p = entry_v.add_parser(
        "lint",
        help="revisa los registros y reporta; no escribe",
        description=(
            "Revisa que cada registro de `AHORA.md` tenga la forma canónica y use marcas "
            "válidas. Solo la ontología cerrada se rechaza; un vocabulario abierto "
            "desconocido se reporta para preguntar. No escribe nada."
        ),
        epilog=(
            "A mano: abrir `AHORA.md` y revisar que cada registro empiece con "
            "`- HH:MM - ` y use marcas válidas."
        ),
    )
    lint_p.add_argument("--vault", default=".", type=Path, help="vault a revisar")

    return {
        ("entry", "add"): _cmd_entry_add,
        ("entry", "rename"): _cmd_entry_rename,
        ("entry", "lint"): _cmd_entry_lint,
    }
