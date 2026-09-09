"""Comandos del sistema: `init`, `cycle`, `doctor`, `vocab` y `style`."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from datetime import date
from pathlib import Path

from tuku import style, vocab
from tuku.cli.helpers import (
    ENTORNO,
    EXITO,
    RECHAZO,
    Handler,
    Subparsers,
    traducir,
)
from tuku.init import (
    DestinoNoVacio,
    MarcadorAutorFaltante,
    TukuHomeInvalido,
    init,
)


def _cmd_init(args: argparse.Namespace) -> int:
    try:
        destino = init(
            args.dir,
            variant=args.variant,
            author=args.author,
            desde=args.date,
            force=args.force,
        )
    except (DestinoNoVacio, MarcadorAutorFaltante) as e:
        print(f"tuku init: {e}", file=sys.stderr)
        return RECHAZO
    except TukuHomeInvalido as e:
        print(f"tuku init: {e}", file=sys.stderr)
        return ENTORNO
    print(
        f"vault sembrado en {destino}. Abre {destino / 'AHORA.md'} y escribe tu primera línea."
    )
    return EXITO


def _cmd_vocab_show(args: argparse.Namespace) -> int:
    return traducir(vocab.mostrar_del_vault(args.vault), "tuku vocab show")


def _cmd_style_lint(args: argparse.Namespace) -> int:
    return traducir(style.lint_del_vault(args.vault), "tuku style lint")


def _cmd_cycle_open(args: argparse.Namespace) -> int:
    from tuku import cycle

    return traducir(cycle.abrir_en_vault(args.vault, args.date), "tuku cycle open")


def _cmd_cycle_lint(args: argparse.Namespace) -> int:
    from tuku import cyclelint

    return traducir(cyclelint.lint_del_vault(args.vault), "tuku cycle lint")


def _crear_cmd_doctor(comandos_fn: Callable[[], frozenset[str]]) -> Handler:
    def _cmd_doctor(args: argparse.Namespace) -> int:
        from tuku import doctor

        return traducir(doctor.revisar_vault(args.vault, comandos=comandos_fn()), "tuku doctor")

    return _cmd_doctor


def _cmd_rebuild(args: argparse.Namespace) -> int:
    from tuku import rebuild

    return traducir(rebuild.reconstruir(args.vault), "tuku rebuild")


def registrar(
    sub: Subparsers, comandos_fn: Callable[[], frozenset[str]]
) -> dict[tuple[str, str | None], Handler]:
    init_p = sub.add_parser(
        "init",
        help="siembra un vault nuevo en un directorio",
        epilog=(
            "A mano: copiar la carpeta `template/vanilla` al directorio destino "
            "y reemplazar las fechas en `AHORA.md`."
        ),
    )
    init_p.add_argument(
        "dir",
        nargs="?",
        default=".",
        type=Path,
        help="directorio destino (por defecto, el actual)",
    )
    init_p.add_argument(
        "--variant",
        "--variante",
        dest="variant",
        default="vanilla",
        help="variante de template/ a copiar",
    )
    init_p.add_argument(
        "--author",
        "--autor",
        dest="author",
        default=None,
        help="nombre del autor para LIBRO-DE-ESTILO.md; opcional",
    )
    init_p.add_argument(
        "--date",
        "--fecha",
        "--desde",
        dest="date",
        default=None,
        type=date.fromisoformat,
        help="primer día del ciclo sembrado (AAAA-MM-DD); por defecto, el lunes de esta semana",
    )
    init_p.add_argument(
        "--force",
        action="store_true",
        help="reemplaza el destino aunque ya tenga contenido",
    )

    cycle_p = sub.add_parser("cycle", help="gestión del ciclo en AHORA.md")
    cycle_v = cycle_p.add_subparsers(dest="verb", required=True)
    open_p = cycle_v.add_parser(
        "open",
        help="abre o verifica el ciclo en AHORA.md",
        epilog=(
            "A mano: copiar `reglas/plantilla/AHORA.md` a la raíz como `AHORA.md` "
            "sustituyendo las fechas de los siete días de la semana."
        ),
    )
    open_p.add_argument("--vault", default=".", type=Path, help="vault a verificar o abrir")
    open_p.add_argument(
        "--date",
        "--fecha",
        "--desde",
        dest="date",
        default=None,
        type=date.fromisoformat,
        help="fecha deseada (AAAA-MM-DD); por defecto, hoy",
    )

    cycle_lint_p = cycle_v.add_parser(
        "lint",
        help="revisa la estructura de AHORA.md y reporta; no escribe",
        epilog=(
            "A mano: abrir `AHORA.md` y verificar que los encabezados de día tengan "
            "fechas consecutivas y formato válido."
        ),
    )
    cycle_lint_p.add_argument("--vault", default=".", type=Path, help="vault a revisar")

    doctor_p = sub.add_parser(
        "doctor",
        help="corre todos los lint y revisa las tablas de contrato",
        epilog=(
            "A mano: revisar `AHORA.md` y `PENDIENTES.md` verificando que cada pendiente "
            "abierto tenga su fila en la tabla y que cada mención a un ámbito exista "
            "en `ambitos/`."
        ),
    )
    doctor_p.add_argument("--vault", default=".", type=Path, help="vault a revisar")

    rebuild_p = sub.add_parser(
        "rebuild",
        help="reconstruye los archivos y vistas derivadas del vault",
        epilog=(
            "A mano: en `ambitos/PENDIENTES-AMBITOS.md` escribir un callout por cada "
            "carpeta en `ambitos/` listando sus pendientes desde `PENDIENTES.md`."
        ),
    )
    rebuild_p.add_argument("--vault", default=".", type=Path, help="vault a reconstruir")

    vocab_p = sub.add_parser("vocab", help="vocabularios abiertos del autor")
    vocab_v = vocab_p.add_subparsers(dest="verb", required=True)
    show_p = vocab_v.add_parser(
        "show",
        help="muestra los vocabularios del libro de estilo",
        epilog=(
            "A mano: abrir `LIBRO-DE-ESTILO.md` y leer los vocabularios definidos "
            "en la sección de vocabulario."
        ),
    )
    show_p.add_argument("--vault", default=".", type=Path, help="vault a leer")

    style_p = sub.add_parser("style", help="libro de estilo y contratos de autor")
    style_v = style_p.add_subparsers(dest="verb", required=True)
    style_lint_p = style_v.add_parser(
        "lint",
        help="revisa contratos en LIBRO-DE-ESTILO.md",
        epilog=(
            "A mano: abrir `LIBRO-DE-ESTILO.md` y verificar que el formato de títulos, "
            "reglas y listas cumpla las convenciones de Markdown."
        ),
    )
    style_lint_p.add_argument("--vault", default=".", type=Path, help="vault a revisar")

    return {
        ("init", None): _cmd_init,
        ("cycle", "open"): _cmd_cycle_open,
        ("cycle", "lint"): _cmd_cycle_lint,
        ("doctor", None): _crear_cmd_doctor(comandos_fn),
        ("rebuild", None): _cmd_rebuild,
        ("vocab", "show"): _cmd_vocab_show,
        ("style", "lint"): _cmd_style_lint,
    }
