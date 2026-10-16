"""Comandos del sistema: `init`, `cycle`, `doctor`, `fix`, `rebuild`, `vocab` y `style`."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from datetime import date
from pathlib import Path

from tuku import style, vocab
from tuku.cli import manual
from tuku.cli.helpers import (
    ENTORNO,
    EXITO,
    RECHAZO,
    Handler,
    Subparsers,
    traducir,
)
from tuku.doctor import TEMAS as TEMAS_DOCTOR
from tuku.init import (
    DestinoNoVacio,
    DestinoProhibido,
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
            comandos=manual.del_cli(),
        )
    except (DestinoNoVacio, DestinoProhibido, MarcadorAutorFaltante) as e:
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

        return traducir(
            doctor.revisar_vault(
                args.vault, comandos=comandos_fn(), tema=args.tema, verbose=args.verbose
            ),
            "tuku doctor",
        )

    return _cmd_doctor


def _cmd_fix(args: argparse.Namespace) -> int:
    from tuku import fix

    return traducir(fix.corregir(args.vault, args.tema), f"tuku fix {args.tema}")


def _cmd_rebuild(args: argparse.Namespace) -> int:
    from tuku import rebuild

    return traducir(
        rebuild.reconstruir(args.vault, comandos=manual.del_cli()), "tuku rebuild"
    )


def registrar(
    sub: Subparsers, comandos_fn: Callable[[], frozenset[str]]
) -> dict[tuple[str, str | None], Handler]:
    init_p = sub.add_parser(
        "init",
        help="siembra un vault nuevo en un directorio",
        description=(
            "Copia el template al directorio destino. Escribe `AHORA.md` desde "
            "`reglas/plantilla/AHORA.md` con las fechas del primer ciclo, la zona horaria "
            "de esta máquina en `reglas/config.tuku.md` y, si se da, el autor en "
            "`LIBRO-DE-ESTILO.md`. Rechaza un destino con contenido y el home del usuario."
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

    cycle_p = sub.add_parser(
        "cycle",
        help="gestión del ciclo en AHORA.md",
        description=(
            "Un ciclo es la ventana de tiempo que `AHORA.md` registra día por día, semanal "
            "por defecto. Estos comandos lo abren y revisan su estructura."
        ),
    )
    cycle_v = cycle_p.add_subparsers(dest="verb", required=True)
    open_p = cycle_v.add_parser(
        "open",
        help="abre o verifica el ciclo en AHORA.md",
        description=(
            "Copia `reglas/plantilla/AHORA.md` a `AHORA.md` con las fechas de los siete "
            "días del ciclo. Si el ciclo ya está abierto, solo lo verifica."
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
        description=(
            "Revisa el frontmatter de `AHORA.md` y que sus encabezados de día tengan "
            "fechas consecutivas y bien escritas. No escribe nada."
        ),
    )
    cycle_lint_p.add_argument("--vault", default=".", type=Path, help="vault a revisar")

    doctor_p = sub.add_parser(
        "doctor",
        help="corre todos los lint y revisa las tablas de contrato",
        description=(
            "Corre todos los lint y revisa el vault entero: archivos requeridos, "
            "`reglas/config.tuku.md`, los comandos que nombra cada `AGENTS.md`, la tabla "
            "de `reglas/types.md`, los links y la versión con que se sembró. Con un TEMA "
            "revisa solo esa parte. No escribe nada: cada hallazgo dice cómo corregirlo."
        ),
    )
    doctor_p.add_argument(
        "tema",
        nargs="?",
        choices=TEMAS_DOCTOR,
        default=None,
        help="revisar solo este tema; sin tema, todo",
    )
    doctor_p.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="muestra todas las revisiones; por defecto, solo hallazgos y avisos",
    )
    doctor_p.add_argument("--vault", default=".", type=Path, help="vault a revisar")

    fix_p = sub.add_parser(
        "fix",
        help="repara lo que tuku doctor TEMA reporta",
        description=(
            "Repara lo que `tuku doctor TEMA` reportó. Tema `link`: reemplaza cada "
            "`[[nombre]]` por `[nombre](ruta/a/nombre.md)`, con la ruta relativa al "
            "archivo que lo contiene. Lo que pide una decisión del autor no se escribe: "
            "sale listado, con código 1."
        ),
    )
    fix_p.add_argument("tema", choices=TEMAS_DOCTOR, help="el tema a reparar")
    fix_p.add_argument("--vault", default=".", type=Path, help="vault a reparar")

    rebuild_p = sub.add_parser(
        "rebuild",
        help="reconstruye los archivos y vistas derivadas del vault",
        description=(
            "Borra y regenera lo que el vault deriva: `ambitos/PENDIENTES-AMBITOS.md`, "
            "con un callout por ámbito que lista sus filas de `PENDIENTES.md`; en la "
            "página de cada ámbito, la actividad tomada de `AHORA.md`; y "
            "`reglas/comandos.tuku.md`, desde esta ayuda. Dos corridas dejan los mismos "
            "bytes."
        ),
    )
    rebuild_p.add_argument("--vault", default=".", type=Path, help="vault a reconstruir")

    vocab_p = sub.add_parser(
        "vocab",
        help="vocabularios abiertos del autor",
        description=(
            "Los vocabularios del autor son las tablas Clasificaciones, Horizontes y Tipos "
            "de nota de `LIBRO-DE-ESTILO.md`, y crecen con el uso. Este comando los "
            "muestra."
        ),
    )
    vocab_v = vocab_p.add_subparsers(dest="verb", required=True)
    show_p = vocab_v.add_parser(
        "show",
        help="muestra los vocabularios del libro de estilo",
        description=(
            "Muestra las tablas Clasificaciones, Horizontes y Tipos de nota de "
            "`LIBRO-DE-ESTILO.md`: los términos con que se clasifica."
        ),
    )
    show_p.add_argument("--vault", default=".", type=Path, help="vault a leer")

    style_p = sub.add_parser(
        "style",
        help="libro de estilo y contratos de autor",
        description=(
            "`LIBRO-DE-ESTILO.md` es el contrato del autor con el sistema: cómo escribe y "
            "sus vocabularios. Este comando revisa que tenga lo que los demás comandos "
            "leen."
        ),
    )
    style_v = style_p.add_subparsers(dest="verb", required=True)
    style_lint_p = style_v.add_parser(
        "lint",
        help="revisa contratos en LIBRO-DE-ESTILO.md",
        description=(
            "Revisa que `LIBRO-DE-ESTILO.md` tenga lo que leen los demás comandos: la "
            "línea del autor y las tablas Clasificaciones, Horizontes y Tipos de nota. "
            "No escribe nada."
        ),
    )
    style_lint_p.add_argument("--vault", default=".", type=Path, help="vault a revisar")

    return {
        ("init", None): _cmd_init,
        ("cycle", "open"): _cmd_cycle_open,
        ("cycle", "lint"): _cmd_cycle_lint,
        ("doctor", None): _crear_cmd_doctor(comandos_fn),
        ("fix", None): _cmd_fix,
        ("rebuild", None): _cmd_rebuild,
        ("vocab", "show"): _cmd_vocab_show,
        ("style", "lint"): _cmd_style_lint,
    }
