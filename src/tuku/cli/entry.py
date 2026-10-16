"""Comandos del sustantivo `entry`: registros de la bitácora."""

from __future__ import annotations

import argparse

from tuku import entry
from tuku.cli.helpers import Handler, Subparsers, traducir
from tuku.cli.opciones import Opciones
from tuku.config import ambito_por_defecto


def _cmd_entry_add(args: argparse.Namespace) -> int:
    return traducir(
        entry.add_al_vault(
            args.vault,
            body=args.body,
            scope=args.scope or ambito_por_defecto(args.vault),
            day=args.at.dia,
            hour=args.at.hora,
        ),
        "tuku entry add",
    )


def _cmd_entry_rename(args: argparse.Namespace) -> int:
    return traducir(
        entry.corregir_en_vault(
            args.vault, body=args.body, day=args.at.dia, hour=args.at.hora
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
    add = Opciones(add_p)
    add.vault("vault destino")
    add.body("la marca y el cuerpo: '**señal**: la administradora responde tarde'")
    add.scope()
    add.at()

    rename_p = entry_v.add_parser(
        "rename",
        help="corrige el cuerpo de un registro ya escrito",
        description=(
            "Reemplaza el cuerpo del registro de `AHORA.md` ubicado por `--at`, sin "
            "tocar hora ni ámbito. Si es un pendiente, reemplaza igual su fila en "
            "`PENDIENTES.md`: las dos copias deben coincidir carácter por carácter para "
            "que el pendiente se pueda cerrar."
        ),
    )
    rename = Opciones(rename_p)
    rename.vault()
    rename.body("el cuerpo corregido, con su marca si la lleva")
    rename.at("el registro a corregir: AAAA-MM-DD HH:MM, o HH:MM si es de hoy", con_hora=True)

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
    Opciones(lint_p).vault("vault a revisar")

    return {
        ("entry", "add"): _cmd_entry_add,
        ("entry", "rename"): _cmd_entry_rename,
        ("entry", "lint"): _cmd_entry_lint,
    }
