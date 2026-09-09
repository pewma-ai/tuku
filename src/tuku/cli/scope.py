"""Comandos de los sustantivos `scope` y `link`: frentes de actividad y enlaces."""

from __future__ import annotations

import argparse
from pathlib import Path

from tuku import link, scope
from tuku.cli.helpers import Handler, Subparsers, traducir


def _cmd_scope_create(args: argparse.Namespace) -> int:
    return traducir(scope.crear_con_enlazado(args.vault, args.name), "tuku scope create")


def _cmd_scope_rename(args: argparse.Namespace) -> int:
    return traducir(
        scope.renombrar_en_vault(args.vault, args.name, args.nuevo), "tuku scope rename"
    )


def _cmd_scope_lint(args: argparse.Namespace) -> int:
    return traducir(scope.lint_del_vault(args.vault), "scope lint")


def _cmd_link_backfill(args: argparse.Namespace) -> int:
    return traducir(
        link.backfill_en_vault(args.vault, args.scope), "tuku link backfill"
    )


def registrar(sub: Subparsers) -> dict[tuple[str, str | None], Handler]:
    scope_p = sub.add_parser("scope", help="árbol de ámbitos y categorías")
    scope_v = scope_p.add_subparsers(dest="verb", required=True)

    scope_create_p = scope_v.add_parser("create", help="crea un ámbito bajo ambitos/")
    scope_create_p.add_argument("name", help="nombre del ámbito")
    scope_create_p.add_argument("--vault", default=".", type=Path, help="vault a modificar")

    scope_rename_p = scope_v.add_parser(
        "rename", help="renombra un ámbito y arregla lo que lo enlazaba"
    )
    scope_rename_p.add_argument("name", help="nombre actual del ámbito")
    scope_rename_p.add_argument("nuevo", help="nombre nuevo")
    scope_rename_p.add_argument("--vault", default=".", type=Path, help="vault a modificar")

    scope_lint_p = scope_v.add_parser(
        "lint", help="revisa que ningún registro apunte a una categoría"
    )
    scope_lint_p.add_argument("--vault", default=".", type=Path, help="vault a revisar")

    link_p = sub.add_parser("link", help="enlazado y menciones")
    link_v = link_p.add_subparsers(dest="verb", required=True)
    link_backfill_p = link_v.add_parser(
        "backfill", help="convierte menciones sueltas en enlaces hacia atrás"
    )
    link_backfill_p.add_argument(
        "--scope",
        "--ambito",
        dest="scope",
        required=True,
        help="ámbito cuyas keywords se buscan",
    )
    link_backfill_p.add_argument("--vault", default=".", type=Path, help="vault a modificar")

    return {
        ("scope", "create"): _cmd_scope_create,
        ("scope", "rename"): _cmd_scope_rename,
        ("scope", "lint"): _cmd_scope_lint,
        ("link", "backfill"): _cmd_link_backfill,
    }
