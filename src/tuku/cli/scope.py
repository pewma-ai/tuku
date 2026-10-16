"""Comandos del sustantivo `scope`: los frentes de actividad del autor."""

from __future__ import annotations

import argparse
from pathlib import Path

from tuku import scope
from tuku.cli.helpers import Handler, Subparsers, traducir


def _cmd_scope_create(args: argparse.Namespace) -> int:
    return traducir(scope.crear_con_enlazado(args.vault, args.name), "tuku scope create")


def _cmd_scope_rename(args: argparse.Namespace) -> int:
    return traducir(
        scope.renombrar_en_vault(args.vault, args.name, args.nuevo), "tuku scope rename"
    )


def _cmd_scope_lint(args: argparse.Namespace) -> int:
    return traducir(scope.lint_del_vault(args.vault), "scope lint")


def registrar(sub: Subparsers) -> dict[tuple[str, str | None], Handler]:
    scope_p = sub.add_parser(
        "scope",
        help="árbol de ámbitos y categorías",
        description=(
            "Un ámbito es un frente de actividad del autor (un trabajo, una casa, un "
            "proyecto) con su carpeta en `ambitos/`. Estos comandos crean ámbitos, los "
            "renombran sin romper los links que los nombran y revisan que los registros "
            "apunten a uno que exista."
        ),
    )
    scope_v = scope_p.add_subparsers(dest="verb", required=True)

    scope_create_p = scope_v.add_parser(
        "create",
        help="crea un ámbito bajo ambitos/",
        description=(
            "Crea la carpeta del ámbito con su página, `AGENTS.md` y `CADENCIAS.md`, y "
            "enlaza hacia atrás las menciones que ya había en `AHORA.md`. Existe porque "
            "un ámbito no es solo una carpeta: es también su transclusión de pendientes "
            "y su callout. Es idempotente."
        ),
        epilog=(
            "A mano: crear la carpeta en `ambitos/<nombre>/` con su página `<nombre>.md`, "
            "`AGENTS.md` y `CADENCIAS.md`."
        ),
    )
    scope_create_p.add_argument("name", help="nombre del ámbito")
    scope_create_p.add_argument("--vault", default=".", type=Path, help="vault a modificar")

    scope_rename_p = scope_v.add_parser(
        "rename",
        help="renombra un ámbito y arregla lo que lo enlazaba",
        description=(
            "Renombra un ámbito entero: la carpeta, la página, el ancla de la "
            "transclusión y el texto y la ruta de cada link que lo nombra en el vault. "
            "Existe porque hacerlo a mano deja links rotos que nadie ve hasta que hacen "
            "falta. Se rechaza antes de tocar nada si algo lo impide."
        ),
        epilog=(
            "A mano: renombrar la carpeta en `ambitos/` y su archivo `.md`, actualizar "
            "las cabeceras internas y reemplazar en todos los links del vault el nombre y la "
            "ruta viejos por los nuevos."
        ),
    )
    scope_rename_p.add_argument("name", help="nombre actual del ámbito")
    scope_rename_p.add_argument("nuevo", help="nombre nuevo")
    scope_rename_p.add_argument("--vault", default=".", type=Path, help="vault a modificar")

    scope_lint_p = scope_v.add_parser(
        "lint",
        help="revisa que ningún registro apunte a una categoría",
        description=(
            "Revisa el árbol de ámbitos y reporta: que ningún registro apunte a una "
            "categoría, que cada página transcluya sus pendientes y que cada ámbito "
            "tenga su callout. No escribe nada."
        ),
        epilog=(
            "A mano: revisar `ambitos/` verificando que cada carpeta tenga su página "
            "y que todos los enlaces en la bitácora apunten a ámbitos existentes."
        ),
    )
    scope_lint_p.add_argument("--vault", default=".", type=Path, help="vault a revisar")

    return {
        ("scope", "create"): _cmd_scope_create,
        ("scope", "rename"): _cmd_scope_rename,
        ("scope", "lint"): _cmd_scope_lint,
    }
