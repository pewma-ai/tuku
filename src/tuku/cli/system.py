"""Comandos del sistema: `init`, `process`, `doctor`, `fix`, `regenerate`, `context`."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from pathlib import Path

from tuku import context
from tuku.cli import manual
from tuku.cli.helpers import (
    ENTORNO,
    EXITO,
    RECHAZO,
    Handler,
    Subparsers,
    traducir,
)
from tuku.cli.opciones import Opciones
from tuku.doctor import TEMAS as TEMAS_DOCTOR
from tuku.fix import TEMAS as TEMAS_FIX
from tuku.init import (
    DestinoNoVacio,
    DestinoProhibido,
    MarcadorAutorFaltante,
    TukuHomeInvalido,
    init,
)
from tuku.regenerate import TEMAS as TEMAS_REGENERATE


def _cmd_init(args: argparse.Namespace) -> int:
    try:
        destino = init(
            args.dir,
            variant=args.variant,
            author=args.author,
            desde=args.at.dia,
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


def _crear_cmd_context(parser: argparse.ArgumentParser) -> Handler:
    def _cmd_context(args: argparse.Namespace) -> int:
        if args.late and args.tema != "todo":
            parser.error("--late solo vale con el tema `todo`: `tuku context todo --late`")
        return traducir(
            context.del_vault(args.vault, args.tema, args.since, late=args.late),
            "tuku context",
        )

    return _cmd_context


def _cmd_process(args: argparse.Namespace) -> int:
    from tuku import process

    return traducir(process.listar(args.vault), "tuku process")


def _cmd_process_cycle(args: argparse.Namespace) -> int:
    from tuku import cycle

    return traducir(cycle.abrir_en_vault(args.vault, args.at.dia), "tuku process cycle")


def _crear_cmd_doctor(
    comandos_fn: Callable[[], frozenset[str]], parser: argparse.ArgumentParser
) -> Handler:
    def _cmd_doctor(args: argparse.Namespace) -> int:
        from tuku import doctor

        if args.file is not None and args.tema != "note":
            parser.error("ARCHIVO solo vale con el tema `note`: `tuku doctor note ARCHIVO`")
        return traducir(
            doctor.revisar_vault(
                args.vault,
                comandos=comandos_fn(),
                tema=args.tema,
                verbose=args.verbose,
                nota=args.file,
            ),
            "tuku doctor",
        )

    return _cmd_doctor


def _cmd_fix(args: argparse.Namespace) -> int:
    from tuku import fix

    return traducir(fix.corregir(args.vault, args.tema), f"tuku fix {args.tema}")


def _cmd_regenerate(args: argparse.Namespace) -> int:
    from tuku import regenerate

    nombre = f"tuku regenerate {args.tema}" if args.tema else "tuku regenerate"
    return traducir(
        regenerate.regenerar(args.vault, tema=args.tema, comandos=manual.del_cli()), nombre
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
        dest="variant",
        default="vanilla",
        help="variante de template/ a copiar",
    )
    init_p.add_argument(
        "--author",
        dest="author",
        default=None,
        help="nombre del autor para LIBRO-DE-ESTILO.md; opcional",
    )
    Opciones(init_p).at("un día de la semana del primer ciclo, AAAA-MM-DD; por defecto, hoy")
    init_p.add_argument(
        "--force",
        action="store_true",
        help="reemplaza el destino aunque ya tenga contenido",
    )

    process_p = sub.add_parser(
        "process",
        help="las rutinas con nombre: las de tuku y las de procesos/",
        description=(
            "Sin nombre, lista los procesos: los de `tuku`, que corren como comando, y los "
            "que el autor escribe en `procesos/`, que el agente ejecuta leyendo su archivo."
        ),
    )
    Opciones(process_p).vault("vault a leer")
    process_v = process_p.add_subparsers(dest="verb", required=False)
    process_cycle_p = process_v.add_parser(
        "cycle",
        help="abre o verifica el ciclo en AHORA.md",
        description=(
            "Copia `reglas/plantilla/AHORA.md` a `AHORA.md` con las fechas de la semana, de "
            "lunes a domingo, que contiene `--at`. Si el ciclo ya está abierto, solo lo "
            "verifica. Una fecha anterior al ciclo abierto se rechaza: un ciclo no se abre "
            "hacia atrás. Con una bitácora anterior en `bitacoras/`, abre en "
            "`PENDIENTES.md` el pendiente de revisarla."
        ),
    )
    Opciones(process_cycle_p).vault("vault a verificar o abrir")
    Opciones(process_cycle_p).at("un día de la semana a abrir, AAAA-MM-DD; por defecto, hoy")

    doctor_p = sub.add_parser(
        "doctor",
        help="corre todos los lint y revisa las tablas de contrato",
        description=(
            "Corre todos los lint y revisa el vault entero: archivos requeridos, "
            "`reglas/config.tuku.md`, los comandos que nombra cada `AGENTS.md`, la tabla "
            "de `reglas/types.md`, los links y la versión con que se sembró. Con un TEMA, "
            f"el nombre de una revisión ({', '.join(TEMAS_DOCTOR)}), informa solo esa "
            "parte. No escribe nada: cada hallazgo dice cómo corregirlo."
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
        "file",
        metavar="ARCHIVO",
        nargs="?",
        default=None,
        type=Path,
        help="solo con el tema `note`: la nota a revisar, aunque esté fuera de un vault",
    )
    doctor_p.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="muestra todas las revisiones; por defecto, solo hallazgos y avisos",
    )
    Opciones(doctor_p).vault("vault a revisar")

    context_p = sub.add_parser(
        "context",
        help="lo que el agente necesita para decidir, sin abrir archivos",
        description=(
            "Solo lee. `entry`: los registros desde `--since`, de `AHORA.md` y de las "
            "bitácoras de `bitacoras/` que cruza. `scope`: cada ámbito de `ambitos/` con "
            "su ruta y sus keywords. `todo`: los pendientes de `PENDIENTES.md`, con los "
            "atrasados marcados (con `--late`, solo esos). `style`: clasificaciones, "
            "horizontes y tipos de nota de `LIBRO-DE-ESTILO.md`. `note`: por cada "
            "tipo de nota enlazable, sus últimas notas de `notas/` con título y aliases "
            "(cuántas, `context_note_limit` de la config). Sin TEMA, todos."
        ),
    )
    context_p.add_argument(
        "tema",
        nargs="?",
        choices=context.TEMAS,
        default=None,
        help="solo este tema; sin tema, todos",
    )
    context_p.add_argument(
        "--since",
        default=None,
        help=(
            f"desde cuándo leer los registros: un número de días o AAAA-MM-DD; "
            f"por defecto, {context.DESDE_POR_DEFECTO} días"
        ),
    )
    context_p.add_argument(
        "--late",
        action="store_true",
        help="solo con el tema `todo`: únicamente los pendientes atrasados",
    )
    Opciones(context_p).vault("vault a leer")

    fix_p = sub.add_parser(
        "fix",
        help="repara lo que tuku doctor TEMA reporta",
        description=(
            "Repara lo que `tuku doctor TEMA` reportó. Tema `link`: reemplaza cada "
            "`[[nombre]]` por `[nombre](ruta/a/nombre.md)`, con la ruta relativa al "
            "archivo que lo contiene. Tema `todo`: borra de `AHORA.md` el registro "
            "`**pendiente**` de un pendiente cuyo `(Hecho)` está en el mismo día. Lo que "
            "pide una decisión del autor no se escribe: sale listado, con código 1."
        ),
    )
    fix_p.add_argument("tema", choices=tuple(TEMAS_FIX), help="el tema a reparar")
    Opciones(fix_p).vault("vault a reparar")

    regenerate_p = sub.add_parser(
        "regenerate",
        help="regenera lo derivado del vault desde el canónico",
        description=(
            "Reescribe lo que el vault deriva del canónico. Tema `todo`: bajo cada día "
            "de `AHORA.md`, el callout con los pendientes de esa fecha, y en "
            "`ambitos/PENDIENTES-AMBITOS.md`, un callout por ámbito con sus filas de "
            "`PENDIENTES.md`. Tema `scope`: la actividad de cada página de ámbito, "
            "tomada de los registros de `AHORA.md`, y el callout `En X:` de cada "
            "ámbito con las carpetas de sus ámbitos hijos, rehecho entero. Tema `comandos`: "
            "`reglas/comandos.tuku.md`, desde esta ayuda. Sin tema, los tres. Solo "
            "escribe lo que cambió; sobre un vault al día no toca nada."
        ),
    )
    regenerate_p.add_argument(
        "tema",
        nargs="?",
        choices=TEMAS_REGENERATE,
        default=None,
        help="regenerar solo este tema; sin tema, los tres",
    )
    Opciones(regenerate_p).vault("vault a regenerar")

    return {
        ("init", None): _cmd_init,
        ("process", None): _cmd_process,
        ("process", "cycle"): _cmd_process_cycle,
        ("doctor", None): _crear_cmd_doctor(comandos_fn, doctor_p),
        ("fix", None): _cmd_fix,
        ("regenerate", None): _cmd_regenerate,
        ("context", None): _crear_cmd_context(context_p),
    }
