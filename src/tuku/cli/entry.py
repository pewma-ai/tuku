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
            "clasificación y cuerpo. Estos comandos los escriben, corrigen y revisan. Los "
            "pendientes se abren y cierran con `tuku todo open` y `tuku todo close`."
        ),
    )
    entry_v = entry_p.add_subparsers(dest="verb", required=True)

    add_p = entry_v.add_parser(
        "add",
        help="escribe un registro en la bitácora",
        description=(
            "Escribe en `AHORA.md`, bajo el día y en orden de hora, la línea "
            "`- HH:MM - [ámbito](ambitos/ámbito/ámbito.md) **marca**: cuerpo`. Quien "
            "invoca decide los campos; el comando les da la forma. Un `**pendiente**` o "
            "un `(Hecho)` se rechaza: abrir y cerrar pendientes es de `tuku todo open` "
            "y `tuku todo close`."
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

    rename_p = entry_v.add_parser(
        "rename",
        help="corrige el cuerpo de un registro ya escrito",
        description=(
            "Reemplaza el cuerpo del registro de `AHORA.md` ubicado por día y hora, sin "
            "tocar hora ni ámbito. Si es un pendiente, reemplaza igual su fila en "
            "`PENDIENTES.md`: las dos copias deben coincidir carácter por carácter para "
            "que el pendiente se pueda cerrar."
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
            "Revisa que cada registro de `AHORA.md` tenga la forma "
            "`- HH:MM - [ámbito](ruta) **marca**: cuerpo` y que su marca exista en "
            "`LIBRO-DE-ESTILO.md`. Una marca de la ontología cerrada mal escrita se "
            "rechaza; un término abierto desconocido se reporta para preguntar al autor. "
            "No escribe nada."
        ),
    )
    lint_p.add_argument("--vault", default=".", type=Path, help="vault a revisar")

    return {
        ("entry", "add"): _cmd_entry_add,
        ("entry", "rename"): _cmd_entry_rename,
        ("entry", "lint"): _cmd_entry_lint,
    }
