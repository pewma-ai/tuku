"""Comandos del sistema: `init`, `cycle`, `doctor`, `fix`, `rebuild`, `vocab` y `style`."""

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

    return traducir(rebuild.reconstruir(args.vault), "tuku rebuild")


def registrar(
    sub: Subparsers, comandos_fn: Callable[[], frozenset[str]]
) -> dict[tuple[str, str | None], Handler]:
    init_p = sub.add_parser(
        "init",
        help="siembra un vault nuevo en un directorio",
        description=(
            "Copia el template de TUKU al directorio destino y lo deja listo para "
            "escribir la primera línea: fija la zona horaria de esta máquina, el primer "
            "día del ciclo y, si se pide, el nombre del autor. No opera sobre un vault "
            "existente: rechaza un destino con contenido, y nunca el home del usuario."
        ),
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

    cycle_p = sub.add_parser(
        "cycle",
        help="gestión del ciclo en AHORA.md",
        description=(
            "El ciclo es el período de trabajo que `AHORA.md` registra, día por día. "
            "Estos comandos lo abren y revisan que su estructura sea válida."
        ),
    )
    cycle_v = cycle_p.add_subparsers(dest="verb", required=True)
    open_p = cycle_v.add_parser(
        "open",
        help="abre o verifica el ciclo en AHORA.md",
        description=(
            "Abre el ciclo desde la plantilla, con las fechas de sus siete días, o "
            "verifica el que ya está abierto. Es idempotente: correrlo dos veces no "
            "duplica nada."
        ),
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
        description=(
            "Revisa que los encabezados de día de `AHORA.md` tengan fechas consecutivas "
            "y formato válido. No escribe nada."
        ),
        epilog=(
            "A mano: abrir `AHORA.md` y verificar que los encabezados de día tengan "
            "fechas consecutivas y formato válido."
        ),
    )
    cycle_lint_p.add_argument("--vault", default=".", type=Path, help="vault a revisar")

    doctor_p = sub.add_parser(
        "doctor",
        help="corre todos los lint y revisa las tablas de contrato",
        description=(
            "Revisa el vault entero y reporta lo que encuentra: archivos que faltan, "
            "campos de configuración, comandos nombrados en `AGENTS.md`, marcas sin su "
            "consecuencia, links y la versión con que se sembró. Con un TEMA revisa solo "
            "esa parte. Sin --verbose muestra solo los hallazgos y los avisos; con "
            "--verbose, todas las revisiones. No escribe nada: cada hallazgo nombra la "
            "corrección, y si el "
            "tema tiene `tuku fix TEMA`, es ese comando."
        ),
        epilog=(
            "A mano: revisar `AHORA.md` y `PENDIENTES.md` verificando que cada pendiente "
            "abierto tenga su fila en la tabla y que cada mención a un ámbito exista "
            "en `ambitos/`."
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
            "Repara un tema que `tuku doctor TEMA` reportó. Lo determinista se aplica; "
            "lo que requiere una decisión del autor no se escribe y sale listado como "
            "decisión, con código 1. Existe porque verificar y reparar son operaciones "
            "distintas, y quien corre TUKU suele ser un agente que no debe decidir por "
            "el autor. Es idempotente."
        ),
        epilog=(
            "A mano: buscar cada `[[nombre]]` y reemplazarlo por "
            "`[nombre](ruta/hasta/nombre.md)`, con la ruta calculada desde el archivo."
        ),
    )
    fix_p.add_argument("tema", choices=TEMAS_DOCTOR, help="el tema a reparar")
    fix_p.add_argument("--vault", default=".", type=Path, help="vault a reparar")

    rebuild_p = sub.add_parser(
        "rebuild",
        help="reconstruye los archivos y vistas derivadas del vault",
        description=(
            "Borra y regenera desde sus fuentes todo lo que el vault deriva, como "
            "`ambitos/PENDIENTES-AMBITOS.md`. Existe porque lo derivado se regenera y "
            "no se repara: el resultado debe ser el mismo byte a byte. Es idempotente."
        ),
        epilog=(
            "A mano: en `ambitos/PENDIENTES-AMBITOS.md` escribir un callout por cada "
            "carpeta en `ambitos/` listando sus pendientes desde `PENDIENTES.md`."
        ),
    )
    rebuild_p.add_argument("--vault", default=".", type=Path, help="vault a reconstruir")

    vocab_p = sub.add_parser(
        "vocab",
        help="vocabularios abiertos del autor",
        description=(
            "Los vocabularios abiertos son las listas de términos que el autor declara "
            "en su libro de estilo (clasificaciones, horizontes, tipos de nota)."
        ),
    )
    vocab_v = vocab_p.add_subparsers(dest="verb", required=True)
    show_p = vocab_v.add_parser(
        "show",
        help="muestra los vocabularios del libro de estilo",
        description=(
            "Muestra las tres tablas de vocabulario de `LIBRO-DE-ESTILO.md`, para saber "
            "con qué términos se clasifica sin inventar otros."
        ),
        epilog=(
            "A mano: abrir `LIBRO-DE-ESTILO.md` y leer los vocabularios definidos "
            "en la sección de vocabulario."
        ),
    )
    show_p.add_argument("--vault", default=".", type=Path, help="vault a leer")

    style_p = sub.add_parser(
        "style",
        help="libro de estilo y contratos de autor",
        description=(
            "El libro de estilo es el contrato del autor con el sistema: sus "
            "vocabularios y sus reglas de escritura. Este comando lo revisa."
        ),
    )
    style_v = style_p.add_subparsers(dest="verb", required=True)
    style_lint_p = style_v.add_parser(
        "lint",
        help="revisa contratos en LIBRO-DE-ESTILO.md",
        description=(
            "Revisa que `LIBRO-DE-ESTILO.md` cumpla el contrato que los demás comandos "
            "leen: el marcador del autor y las tres tablas (Clasificaciones, Horizontes "
            "y Tipos de nota). No escribe nada."
        ),
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
        ("fix", None): _cmd_fix,
        ("rebuild", None): _cmd_rebuild,
        ("vocab", "show"): _cmd_vocab_show,
        ("style", "lint"): _cmd_style_lint,
    }
