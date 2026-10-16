"""Comandos del sustantivo `scope`: los frentes de actividad del autor."""

from __future__ import annotations

import argparse

from tuku import scope
from tuku.cli.helpers import Handler, Subparsers, traducir
from tuku.cli.opciones import Opciones


def _cmd_scope_create(args: argparse.Namespace) -> int:
    return traducir(
        scope.crear_con_enlazado(args.vault, args.name, day=args.at.dia, hour=args.at.hora),
        "tuku scope create",
    )


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
            "Un ámbito es un frente de actividad del autor con identidad propia (un "
            "trabajo, una casa, un proyecto): una carpeta de `ambitos/` con su página. Una "
            "carpeta sin página es una categoría y solo agrupa. Estos comandos crean y "
            "renombran ámbitos sin romper sus links, y revisan el árbol."
        ),
    )
    scope_v = scope_p.add_subparsers(dest="verb", required=True)

    scope_create_p = scope_v.add_parser(
        "create",
        help="crea un ámbito bajo ambitos/",
        description=(
            "Crea `ambitos/<nombre>/` con `AGENTS.md`, `CADENCIAS.md` y la página "
            "`<nombre>.md` (`type: Scope`, `keywords: [<nombre>]` y la transclusión de su "
            "callout en `ambitos/PENDIENTES-AMBITOS.md`). Convierte en link las menciones "
            "del ámbito que ya había en `AHORA.md` y registra ahí "
            "`**nota**: abrí el ámbito`. Sobre un ámbito existente no escribe nada."
        ),
    )
    scope_create_p.add_argument("name", help="nombre del ámbito")
    Opciones(scope_create_p).at("cuándo se abre, para la constancia; lo que falte, hoy y ahora")
    Opciones(scope_create_p).vault("vault a modificar")

    scope_rename_p = scope_v.add_parser(
        "rename",
        help="renombra un ámbito y arregla lo que lo enlazaba",
        description=(
            "Renombra `ambitos/<nombre>/` y su página, las `keywords`, el ancla de la "
            "transclusión y el texto y la ruta de cada link al ámbito en todo el vault. "
            "Si algo lo impide, rechaza sin tocar nada."
        ),
    )
    scope_rename_p.add_argument("name", help="nombre actual del ámbito")
    scope_rename_p.add_argument("nuevo", help="nombre nuevo")
    Opciones(scope_rename_p).vault("vault a modificar")

    scope_lint_p = scope_v.add_parser(
        "lint",
        help="revisa que ningún registro apunte a una categoría",
        description=(
            "Revisa que ningún registro de `AHORA.md` apunte a una categoría (carpeta de "
            "`ambitos/` sin página propia), que cada página de ámbito transcluya sus "
            "pendientes y que cada ámbito tenga su callout en "
            "`ambitos/PENDIENTES-AMBITOS.md`. No escribe nada."
        ),
    )
    Opciones(scope_lint_p).vault("vault a revisar")

    return {
        ("scope", "create"): _cmd_scope_create,
        ("scope", "rename"): _cmd_scope_rename,
        ("scope", "lint"): _cmd_scope_lint,
    }
