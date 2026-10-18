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
    sin_implementar,
    traducir,
)
from tuku.cli.opciones import Opciones


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
            day=args.at.dia,
            hour=args.at.hora,
            record=not args.no_record,
            subtype=args.subtype,
            now=args.now,
        ),
        "tuku note create",
    )


def _cmd_note_rename(args: argparse.Namespace) -> int:
    return traducir(
        note.renombrar_en_vault(args.vault, args.title, args.nuevo, now=args.now),
        "tuku note rename",
    )


def _cmd_note_archive(args: argparse.Namespace) -> int:
    return sin_implementar(
        "tuku note archive", "Mientras tanto, la nota queda en `notas/` tal como está."
    )


def registrar(sub: Subparsers) -> dict[tuple[str, str | None], Handler]:
    note_p = sub.add_parser(
        "note",
        help="notas en notas/",
        description=(
            "Una nota es una idea que vale más allá de un día, en `notas/`, cerrada con `## "
            "Ver además`. Estos comandos crean notas registrándolas en la bitácora, las "
            "renombran sin romper sus links y revisan su estructura."
        ),
    )
    note_v = note_p.add_subparsers(dest="verb", required=True)

    note_create_p = note_v.add_parser(
        "create",
        help="crea una nota y deja constancia en la bitácora",
        description=(
            "Escribe `notas/<título sin tildes, en minúsculas y con guiones>.md` con "
            "frontmatter (`type: Note`, `subtype` si se pasa, `created` y `updated`), "
            "el cuerpo y la sección `## Ver además`, que lista el ámbito y los links "
            "del cuerpo. Registra en `AHORA.md` "
            "`**nota**: escribí la nota [título](notas/...)`. Una nota que ya existe no "
            "se reescribe."
        ),
    )
    note_create_p.add_argument("title", help="título de la nota")
    crear = Opciones(note_create_p)
    crear.body("cuerpo de la nota", requerido=False, una_linea=False)
    note_create_p.add_argument(
        "--body-file",
        dest="body_file",
        default=None,
        type=Path,
        help="archivo con el cuerpo de la nota; `-` lo lee de stdin",
    )
    crear.scope("ámbito al que pertenece la nota")
    note_create_p.add_argument(
        "--subtype",
        default=None,
        help=(
            "tipo de la nota, una fila de `### Tipos de nota` del libro de estilo "
            "(por ejemplo `persona`); agrega `subtype` al frontmatter"
        ),
    )
    crear.at("cuándo se escribe, para la nota y su constancia; lo que falte, hoy y ahora")
    note_create_p.add_argument(
        "--no-record",
        dest="no_record",
        action="store_true",
        help="no agrega registro de constancia en AHORA.md",
    )
    crear.vault("vault destino")

    note_rename_p = note_v.add_parser(
        "rename",
        help="renombra una nota y arregla lo que la enlazaba",
        description=(
            "Renombra el archivo de la nota en `notas/`, su título y el texto y la ruta "
            "de cada link a ella en todo el vault."
        ),
    )
    note_rename_p.add_argument("title", help="título actual de la nota")
    note_rename_p.add_argument("nuevo", help="título nuevo")
    Opciones(note_rename_p).vault("vault a modificar")

    note_archive_p = note_v.add_parser(
        "archive",
        help="archiva una nota (todavía no implementado)",
        description=(
            "Todavía no está implementado: avisa y no escribe nada. Cuando exista, "
            "archivará `notas/<título>.md` sin romper los links que la apuntan."
        ),
    )
    note_archive_p.add_argument("title", help="título de la nota")
    Opciones(note_archive_p).vault("vault a modificar")

    return {
        ("note", "create"): _cmd_note_create,
        ("note", "rename"): _cmd_note_rename,
        ("note", "archive"): _cmd_note_archive,
    }
