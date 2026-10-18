"""Comandos del sustantivo `scope`: los frentes de actividad del autor."""

from __future__ import annotations

import argparse

from tuku import scope
from tuku.cli.helpers import Handler, Subparsers, sin_implementar, traducir
from tuku.cli.opciones import Opciones


def _cmd_scope_create(args: argparse.Namespace) -> int:
    return traducir(
        scope.crear_con_constancia(
            args.vault,
            args.name,
            parent=args.parent,
            day=args.at.dia,
            hour=args.at.hora,
            palabras=args.keyword,
            since=args.since,
        ),
        "tuku scope create",
    )


def _cmd_scope_update(args: argparse.Namespace) -> int:
    return traducir(scope.actualizar(args.vault, args.name, args.keyword), "tuku scope update")


def _cmd_scope_move(args: argparse.Namespace) -> int:
    return traducir(
        scope.mover_en_vault(args.vault, args.name, parent=args.parent), "tuku scope move"
    )


def _cmd_scope_rename(args: argparse.Namespace) -> int:
    return traducir(
        scope.renombrar_en_vault(args.vault, args.name, args.nuevo), "tuku scope rename"
    )


def _cmd_scope_lint(args: argparse.Namespace) -> int:
    return traducir(scope.lint_del_vault(args.vault), "scope lint")


def _cmd_scope_archive(args: argparse.Namespace) -> int:
    return sin_implementar(
        "tuku scope archive",
        "Archivar es decisión del autor: conversa con él qué pasa con los pendientes, "
        "las cadencias y los links de la rama (spec/ambitos.md, «Archivar es caro»).",
    )


def registrar(sub: Subparsers) -> dict[tuple[str, str | None], Handler]:
    scope_p = sub.add_parser(
        "scope",
        help="árbol de ámbitos y categorías",
        description=(
            "Un ámbito es un frente de actividad del autor con identidad propia (un "
            "trabajo, una casa, un proyecto): una carpeta de `ambitos/` con su página. Una "
            "carpeta sin página es una categoría y solo agrupa. Un ámbito puede ir dentro "
            "de otro. Estos comandos crean, mueven y renombran ámbitos sin romper sus "
            "links, y revisan el árbol."
        ),
    )
    scope_v = scope_p.add_subparsers(dest="verb", required=True)

    scope_create_p = scope_v.add_parser(
        "create",
        help="crea un ámbito bajo ambitos/",
        description=(
            "Crea `ambitos/<nombre>/` con su página `<nombre>.md` (`type: Scope`, "
            "`keywords: []` y la transclusión de su callout en "
            "`ambitos/PENDIENTES-AMBITOS.md`). Con `--parent`, la carpeta va dentro de la "
            "del ámbito padre, que debe existir. Registra en `AHORA.md` "
            "`**nota**: abrí el ámbito` (con `--parent`, `bajo` el padre) y no cambia "
            "nada de lo ya escrito. Sobre un ámbito existente no escribe nada. Sin "
            "`--keyword`, la salida pide preguntar al autor qué palabras, al mencionarlas, "
            "indican que algo es del ámbito."
        ),
    )
    scope_create_p.add_argument("name", help="nombre del ámbito")
    scope_create_p.add_argument(
        "--keyword",
        action="append",
        default=[],
        metavar="PALABRA",
        help="palabra que delata el ámbito (repetible, o varias separadas por coma)",
    )
    scope_create_p.add_argument(
        "--since",
        default=None,
        help=(
            "desde cuándo buscar registros que nombran al ámbito: un número de días o "
            "AAAA-MM-DD; por defecto, 7 días"
        ),
    )
    Opciones(scope_create_p).parent()
    Opciones(scope_create_p).at("cuándo se abre, para la constancia; lo que falte, hoy y ahora")
    Opciones(scope_create_p).vault("vault a modificar")

    scope_update_p = scope_v.add_parser(
        "update",
        help="suma keywords a la página de un ámbito",
        description=(
            "Suma cada `--keyword` a las `keywords` del frontmatter de la página del ámbito, "
            "que debe existir: siglas, sistemas, personas y proyectos que, al mencionarlos, "
            "indican que algo es de ese ámbito. Sirven para elegir el ámbito de lo que el "
            "autor dice. Cada `--keyword` admite varias palabras separadas por coma, y cada "
            "palabra va en kebab-case: minúsculas y guiones en lugar de espacios. Solo "
            "escribe la página del ámbito: `AHORA.md` y los registros no cambian. Lo que ya "
            "estaba no se repite, y si nada es nuevo no escribe nada."
        ),
    )
    scope_update_p.add_argument("name", help="nombre del ámbito")
    scope_update_p.add_argument(
        "--keyword",
        action="append",
        default=[],
        metavar="PALABRA",
        help="palabra que delata el ámbito (repetible, o varias separadas por coma)",
    )
    Opciones(scope_update_p).vault("vault a modificar")

    scope_move_p = scope_v.add_parser(
        "move",
        help="mueve un ámbito dentro de otro y arregla lo que lo enlazaba",
        description=(
            "Mueve la carpeta `ambitos/<nombre>/` dentro de la del ámbito `--parent`, o a la "
            "raíz de `ambitos/` si no se da. Recalcula la ruta de cada link del vault que "
            "apunta al ámbito, la de los links de sus propios archivos y la transclusión de "
            "su página. Si algo lo impide, rechaza sin tocar nada; si ya está ahí, no "
            "escribe nada."
        ),
    )
    scope_move_p.add_argument("name", help="nombre del ámbito a mover")
    Opciones(scope_move_p).parent()
    Opciones(scope_move_p).vault("vault a modificar")

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
        help="revisa categorías, transclusiones y callouts de los ámbitos",
        description=(
            "Revisa que ningún registro de `AHORA.md` apunte a una categoría (carpeta de "
            "`ambitos/` sin página propia), que cada página de ámbito transcluya sus "
            "pendientes y que cada ámbito tenga su callout en "
            "`ambitos/PENDIENTES-AMBITOS.md`. No escribe nada."
        ),
    )
    Opciones(scope_lint_p).vault("vault a revisar")

    scope_archive_p = scope_v.add_parser(
        "archive",
        help="archiva un ámbito (todavía no implementado)",
        description=(
            "Todavía no está implementado: avisa y no escribe nada. Cuando exista, moverá "
            "`ambitos/<nombre>/` a `archivado/` después de resolver con el autor sus "
            "pendientes de `PENDIENTES.md` y sus cadencias, y recalculará los links que lo "
            "apuntan, también en `bitacoras/`."
        ),
    )
    scope_archive_p.add_argument("name", help="nombre del ámbito")
    Opciones(scope_archive_p).vault("vault a modificar")

    return {
        ("scope", "create"): _cmd_scope_create,
        ("scope", "update"): _cmd_scope_update,
        ("scope", "move"): _cmd_scope_move,
        ("scope", "rename"): _cmd_scope_rename,
        ("scope", "lint"): _cmd_scope_lint,
        ("scope", "archive"): _cmd_scope_archive,
    }
