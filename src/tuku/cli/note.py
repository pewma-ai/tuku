"""Comandos del sustantivo `note`: notas y zettelkasten en notas/."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tuku import note
from tuku.cli.helpers import (
    RECHAZO,
    Handler,
    Subparsers,
    cuerpo_de_la_nota,
    fecha,
    hora,
    traducir,
)


def _cmd_note_create(args: argparse.Namespace) -> int:
    cuerpo = cuerpo_de_la_nota(args)
    if cuerpo is None:
        print(
            "tuku note create: falta el cuerpo de la nota. "
            "Pasa --body, o --body-file con un archivo (`-` lee de stdin).",
            file=sys.stderr,
        )
        return RECHAZO
    return traducir(
        note.crear_con_constancia(
            args.vault,
            title=args.title,
            body=cuerpo,
            scope=args.scope,
            day=args.day,
            hour=args.hour,
            record=not args.no_record,
        ),
        "tuku note create",
    )


def _cmd_note_rename(args: argparse.Namespace) -> int:
    return traducir(
        note.renombrar_en_vault(args.vault, args.title, args.nuevo), "tuku note rename"
    )


def _cmd_note_lint(args: argparse.Namespace) -> int:
    return traducir(note.lint_del_vault(args.vault, args.file), "note lint")


def registrar(sub: Subparsers) -> dict[tuple[str, str | None], Handler]:
    note_p = sub.add_parser("note", help="notas en notas/")
    note_v = note_p.add_subparsers(dest="verb", required=True)

    note_create_p = note_v.add_parser(
        "create", help="crea una nota y deja constancia en la bitácora"
    )
    note_create_p.add_argument("title", help="título de la nota")
    note_create_p.add_argument(
        "--body", "--cuerpo", dest="body", default=None, help="cuerpo de la nota"
    )
    note_create_p.add_argument(
        "--body-file",
        "--cuerpo-archivo",
        dest="body_file",
        default=None,
        type=Path,
        help="archivo con el cuerpo de la nota; `-` lo lee de stdin",
    )
    note_create_p.add_argument(
        "--scope",
        "--ambito",
        dest="scope",
        default=None,
        help="ámbito al que pertenece la nota",
    )
    note_create_p.add_argument(
        "--day",
        "--dia",
        dest="day",
        type=fecha,
        default=None,
        help="día de la nota y de su constancia (AAAA-MM-DD); por defecto, hoy",
    )
    note_create_p.add_argument(
        "--hour",
        "--hora",
        dest="hour",
        type=hora,
        default=None,
        help="hora de la constancia (HH:MM); por defecto, ahora",
    )
    note_create_p.add_argument(
        "--no-record",
        "--sin-constancia",
        dest="no_record",
        action="store_true",
        help="no agrega registro de constancia en AHORA.md",
    )
    note_create_p.add_argument("--vault", default=".", type=Path, help="vault destino")

    note_rename_p = note_v.add_parser(
        "rename", help="renombra una nota y arregla lo que la enlazaba"
    )
    note_rename_p.add_argument("title", help="título actual de la nota")
    note_rename_p.add_argument("nuevo", help="título nuevo")
    note_rename_p.add_argument("--vault", default=".", type=Path, help="vault a modificar")

    note_lint_p = note_v.add_parser(
        "lint", help="revisa que la nota tenga 'Ver además' y motivos"
    )
    note_lint_p.add_argument(
        "file",
        nargs="?",
        default=None,
        type=Path,
        help="archivo de nota a revisar (opcional)",
    )
    note_lint_p.add_argument("--vault", default=".", type=Path, help="vault a revisar")

    return {
        ("note", "create"): _cmd_note_create,
        ("note", "rename"): _cmd_note_rename,
        ("note", "lint"): _cmd_note_lint,
    }
