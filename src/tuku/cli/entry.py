"""Comandos del sustantivo `entry`: registros de la bitácora."""

from __future__ import annotations

import argparse

from tuku import entry
from tuku.cli.helpers import Handler, Subparsers, traducir
from tuku.cli.opciones import Momento, Opciones, momento_pasado
from tuku.config import ambito_por_defecto


def _cmd_entry_create(args: argparse.Namespace) -> int:
    return traducir(
        entry.add_al_vault(
            args.vault,
            body=args.body,
            scope=args.scope or ambito_por_defecto(args.vault),
            day=args.at.dia,
            hour=args.at.hora,
            now=args.now,
        ),
        "tuku entry create",
    )


def _cmd_entry_update(args: argparse.Namespace) -> int:
    return traducir(
        entry.actualizar_en_vault(
            args.vault, match=args.match, body=args.body, day=args.at.dia, hour=args.at.hora
        ),
        "tuku entry update",
    )


def _cmd_entry_move(args: argparse.Namespace) -> int:
    return traducir(
        entry.mover_en_vault(
            args.vault, match=args.match, scope=args.scope, day=args.at.dia, hour=args.at.hora
        ),
        "tuku entry move",
    )


def _ubicacion(o: Opciones) -> None:
    """`CUÁNDO` y `--match`: cómo `update` y `move` encuentran el registro."""
    o.parser.add_argument(
        "at",
        nargs="?",
        metavar="CUÁNDO",
        default=Momento(),
        type=momento_pasado,
        help="el día, o el día y la hora, donde buscar: AAAA-MM-DD o 'AAAA-MM-DD HH:MM'",
    )
    o.parser.add_argument(
        "--match",
        required=True,
        metavar="TEXTO",
        help="un fragmento del cuerpo actual; se elige el último registro que calza",
    )


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

    create_p = entry_v.add_parser(
        "create",
        help="escribe un registro en la bitácora",
        description=(
            "Escribe en `AHORA.md`, bajo el día y en orden de hora, la línea "
            "`- HH:MM - [ámbito](ambitos/ámbito/ámbito.md) **marca**: cuerpo`. Quien "
            "invoca decide los campos; el comando les da la forma. Un `**pendiente**` o "
            "un `(Hecho)` se rechaza: abrir y cerrar pendientes es de `tuku todo open` "
            "y `tuku todo close`."
        ),
    )
    create = Opciones(create_p)
    create.vault("vault destino")
    create.body("la marca y el cuerpo: '**señal**: la administradora responde tarde'")
    create.scope()
    create.at()

    update_p = entry_v.add_parser(
        "update",
        help="corrige el cuerpo de un registro ya escrito",
        description=(
            "Reemplaza el cuerpo del último registro de `AHORA.md` que contiene el "
            "fragmento de `--match` (sin distinguir mayúsculas ni tildes), sin tocar hora "
            "ni ámbito. `CUÁNDO` acota la búsqueda a un día o a un minuto. Si es un "
            "pendiente, reemplaza igual su fila en `PENDIENTES.md`: las dos copias deben "
            "coincidir para que el pendiente se pueda cerrar."
        ),
    )
    update = Opciones(update_p)
    _ubicacion(update)
    update.body("el cuerpo corregido, con su marca si la lleva")
    update.vault()

    move_p = entry_v.add_parser(
        "move",
        help="cambia el ámbito de un registro ya escrito",
        description=(
            "Cambia el link de ámbito del último registro de `AHORA.md` que contiene el "
            "fragmento de `--match`, sin tocar hora ni cuerpo. Con `CUÁNDO` fuera del "
            "ciclo en curso, busca en la bitácora de `bitacoras/` que cubre ese día. Si es "
            "un pendiente abierto, su fila de `PENDIENTES.md` cambia de ámbito con él."
        ),
    )
    move = Opciones(move_p)
    _ubicacion(move)
    move_p.add_argument("--scope", required=True, help="el ámbito al que pasa el registro")
    move.vault()

    return {
        ("entry", "create"): _cmd_entry_create,
        ("entry", "update"): _cmd_entry_update,
        ("entry", "move"): _cmd_entry_move,
    }
