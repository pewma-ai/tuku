"""CLI de TUKU: capa fina de argparse sobre las funciones de `tuku/`.

`tuku <noun> <verb>`, todo en inglés. La lógica no vive acá: cada comando llama
a una función importable de `tuku/` y traduce su resultado a texto y a un código
de salida. El contrato de esa traducción está en `spec/cli.md`.

`init` es la excepción a la forma `<noun> <verb>`: siembra el vault y no opera
sobre uno, así que no tiene sustantivo sobre el que actuar.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from tuku import entry, link, note, scope, style, todo, vocab
from tuku.config import VaultInvalido
from tuku.init import (
    DestinoNoVacio,
    MarcadorAutorFaltante,
    TukuHomeInvalido,
    init,
)
from tuku.resultado import Resultado

#: Códigos de salida. Son contrato con quien invoca, persona o agente, y están
#: fijados en `spec/cli.md`. El 2 queda reservado a argparse, que lo emite ante
#: una invocación mal formada: ningún comando puede devolverlo por otra causa,
#: o quien invoca no puede distinguir "me equivoqué al escribir el comando" de
#: "el comando se negó".
EXITO = 0
RECHAZO = 1  # el comando entendió y se negó por el estado del vault
USO = 2  # reservado a argparse
ENTORNO = 3  # la instalación de TUKU no está donde debería

def _construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tuku",
        description="TUKU — Management as Code para la vida personal.",
    )
    sub = parser.add_subparsers(dest="noun", required=True)

    init_p = sub.add_parser("init", help="siembra un vault nuevo en un directorio")
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

    entry_p = sub.add_parser("entry", help="registros de la bitácora")
    entry_v = entry_p.add_subparsers(dest="verb", required=True)

    add_p = entry_v.add_parser("add", help="escribe registros ya formados en su día")
    add_p.add_argument("line", nargs="+", help="línea de registro, '- HH:MM - ...'")
    add_p.add_argument("--vault", default=".", type=Path, help="vault destino")
    add_p.add_argument(
        "--day",
        "--dia",
        dest="day",
        default=None,
        help="encabezado del día (por defecto, el de hoy)",
    )

    lint_p = entry_v.add_parser("lint", help="revisa los registros y reporta; no escribe")
    lint_p.add_argument("--vault", default=".", type=Path, help="vault a revisar")

    todo_p = sub.add_parser("todo", help="pendientes de PENDIENTES.md")
    todo_v = todo_p.add_subparsers(dest="verb", required=True)

    for verbo, ayuda in (
        (
            "open",
            "abre el pendiente de un registro **pendiente** y propaga las vistas",
        ),
        ("close", "cierra el pendiente de un registro ~~(Hecho)~~"),
    ):
        p = todo_v.add_parser(verbo, help=ayuda)
        p.add_argument("line", help="la línea del registro que lleva la marca")
        p.add_argument("--vault", default=".", type=Path, help="vault a modificar")
        p.add_argument(
            "--no-propagate",
            action="store_true",
            help="no regenera las vistas derivadas; para el lote, que propaga al final",
        )
        if verbo == "open":
            p.add_argument(
                "--horizon",
                "--horizonte",
                dest="horizon",
                default=todo.ESTA_SEMANA,
                help="horizonte destino: el encabezado bajo el que va la fila",
            )
            p.add_argument(
                "--when",
                default="",
                help="fecha del pendiente, AAAA-MM-DD; vacío si no la tiene",
            )

    todo_prop = todo_v.add_parser(
        "propagate", help="regenera las vistas derivadas de PENDIENTES.md"
    )
    todo_prop.add_argument("--vault", default=".", type=Path, help="vault a modificar")

    todo_lint = todo_v.add_parser("lint", help="revisa los pendientes y reporta; no escribe")
    todo_lint.add_argument("--vault", default=".", type=Path, help="vault a revisar")

    cycle_p = sub.add_parser("cycle", help="gestión del ciclo en AHORA.md")
    cycle_v = cycle_p.add_subparsers(dest="verb", required=True)
    open_p = cycle_v.add_parser("open", help="abre o verifica el ciclo en AHORA.md")
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
        "lint", help="revisa la estructura de AHORA.md y reporta; no escribe"
    )
    cycle_lint_p.add_argument("--vault", default=".", type=Path, help="vault a revisar")

    doctor_p = sub.add_parser(
        "doctor", help="corre todos los lint y revisa las tablas de contrato"
    )
    doctor_p.add_argument("--vault", default=".", type=Path, help="vault a revisar")

    vocab_p = sub.add_parser("vocab", help="vocabularios abiertos del autor")
    vocab_v = vocab_p.add_subparsers(dest="verb", required=True)
    show_p = vocab_v.add_parser("show", help="muestra los vocabularios del libro de estilo")
    show_p.add_argument("--vault", default=".", type=Path, help="vault a leer")

    style_p = sub.add_parser("style", help="libro de estilo y contratos de autor")
    style_v = style_p.add_subparsers(dest="verb", required=True)
    style_lint_p = style_v.add_parser("lint", help="revisa contratos en LIBRO-DE-ESTILO.md")
    style_lint_p.add_argument("--vault", default=".", type=Path, help="vault a revisar")

    scope_p = sub.add_parser("scope", help="árbol de ámbitos y categorías")
    scope_v = scope_p.add_subparsers(dest="verb", required=True)
    scope_create_p = scope_v.add_parser("create", help="crea un ámbito bajo ambitos/")
    scope_create_p.add_argument("name", help="nombre del ámbito")
    scope_create_p.add_argument("--vault", default=".", type=Path, help="vault a modificar")
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
        help="archivo con el cuerpo de la nota",
    )
    note_create_p.add_argument(
        "--scope",
        "--ambito",
        dest="scope",
        default=None,
        help="ámbito al que pertenece la nota",
    )
    note_create_p.add_argument(
        "--today",
        "--hoy",
        dest="today",
        default=None,
        type=date.fromisoformat,
        help="fecha de creación (AAAA-MM-DD); por defecto, hoy",
    )
    note_create_p.add_argument(
        "--time",
        "--hora",
        dest="time",
        default=None,
        help="hora para el registro de constancia (HH:MM); por defecto, la actual",
    )
    note_create_p.add_argument(
        "--day",
        "--dia",
        dest="day",
        default=None,
        help="encabezado del día en AHORA.md para la constancia",
    )
    note_create_p.add_argument(
        "--no-record",
        "--sin-constancia",
        dest="no_record",
        action="store_true",
        help="no agrega registro de constancia en AHORA.md",
    )
    note_create_p.add_argument("--vault", default=".", type=Path, help="vault destino")

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

    return parser


def _traducir(r: Resultado, prefijo: str) -> int:
    """Escribe lo que dejó una operación y devuelve su código de salida.

    Es toda la lógica que le queda al CLI después de despachar: un rechazo por el
    estado del vault va a `stderr` con el nombre del comando delante, y todo lo
    demás a `stdout`. Los lint son el caso intermedio, y por eso `Resultado`
    lleva `error` aparte de `ok`: reportan hallazgos por `stdout` y aun así
    salen con `RECHAZO`.
    """
    if r.error:
        print(f"{prefijo}: {r.mensaje}", file=sys.stderr)
    else:
        print(r.mensaje)
    return EXITO if r.ok else RECHAZO


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


def _cmd_entry_add(args: argparse.Namespace) -> int:
    return _traducir(
        entry.add_al_vault(args.vault, list(args.line), day=args.day), "tuku entry add"
    )


def _cmd_entry_lint(args: argparse.Namespace) -> int:
    return _traducir(entry.lint_del_vault(args.vault), "tuku entry lint")


def _cmd_todo_open(args: argparse.Namespace) -> int:
    return _traducir(
        todo.abrir_en_vault(
            args.vault,
            args.line,
            horizon=args.horizon,
            when=args.when,
            propagate=not args.no_propagate,
        ),
        "tuku todo open",
    )


def _cmd_todo_close(args: argparse.Namespace) -> int:
    return _traducir(
        todo.cerrar_en_vault(args.vault, args.line, propagate=not args.no_propagate),
        "todo close",
    )


def _cmd_todo_propagate(args: argparse.Namespace) -> int:
    return _traducir(todo.propagar_vistas(args.vault), "todo propagate")


def _cmd_todo_lint(args: argparse.Namespace) -> int:
    return _traducir(todo.lint_del_vault(args.vault), "todo lint")


def _cmd_vocab_show(args: argparse.Namespace) -> int:
    return _traducir(vocab.mostrar_del_vault(args.vault), "tuku vocab show")


def _cmd_style_lint(args: argparse.Namespace) -> int:
    return _traducir(style.lint_del_vault(args.vault), "tuku style lint")


def _cmd_cycle_open(args: argparse.Namespace) -> int:
    from tuku import cycle

    return _traducir(cycle.abrir_en_vault(args.vault, args.date), "tuku cycle open")


def _cmd_cycle_lint(args: argparse.Namespace) -> int:
    from tuku import cyclelint

    return _traducir(cyclelint.lint_del_vault(args.vault), "tuku cycle lint")


def _cmd_doctor(args: argparse.Namespace) -> int:
    from tuku import doctor

    return _traducir(doctor.revisar_vault(args.vault), "tuku doctor")


def _cmd_scope_create(args: argparse.Namespace) -> int:
    return _traducir(scope.crear_con_enlazado(args.vault, args.name), "tuku scope create")


def _cmd_scope_lint(args: argparse.Namespace) -> int:
    return _traducir(scope.lint_del_vault(args.vault), "scope lint")


def _cmd_link_backfill(args: argparse.Namespace) -> int:
    return _traducir(
        link.backfill_en_vault(args.vault, args.scope), "tuku link backfill"
    )


def _cmd_note_create(args: argparse.Namespace) -> int:
    cuerpo = _cuerpo_de_la_nota(args)
    if cuerpo is None:
        print(
            "tuku note create: falta el cuerpo de la nota. "
            "Pasa --body, --body-file o escribe por stdin.",
            file=sys.stderr,
        )
        return RECHAZO
    return _traducir(
        note.crear_con_constancia(
            args.vault,
            title=args.title,
            body=cuerpo,
            scope=args.scope,
            today=args.today,
            time=args.time,
            day=args.day,
            record=not args.no_record,
        ),
        "tuku note create",
    )


def _cuerpo_de_la_nota(args: argparse.Namespace) -> str | None:
    """De dónde sale el cuerpo: un archivo, la línea de comandos o `stdin`.

    Se queda en el CLI porque es una decisión sobre cómo llegó el texto, no
    sobre qué hace TUKU con él.
    """
    if args.body_file is not None:
        return str(args.body_file.read_text(encoding="utf-8"))
    if args.body is not None:
        return str(args.body)
    if not sys.stdin.isatty():
        return sys.stdin.read()
    return None


def _cmd_note_lint(args: argparse.Namespace) -> int:
    return _traducir(note.lint_del_vault(args.vault, args.file), "note lint")


_COMANDOS = {
    ("init", None): _cmd_init,
    ("doctor", None): _cmd_doctor,
    ("cycle", "open"): _cmd_cycle_open,
    ("cycle", "lint"): _cmd_cycle_lint,
    ("entry", "add"): _cmd_entry_add,
    ("entry", "lint"): _cmd_entry_lint,
    ("todo", "open"): _cmd_todo_open,
    ("todo", "close"): _cmd_todo_close,
    ("todo", "propagate"): _cmd_todo_propagate,
    ("todo", "lint"): _cmd_todo_lint,
    ("vocab", "show"): _cmd_vocab_show,
    ("style", "lint"): _cmd_style_lint,
    ("scope", "create"): _cmd_scope_create,
    ("scope", "lint"): _cmd_scope_lint,
    ("link", "backfill"): _cmd_link_backfill,
    ("note", "create"): _cmd_note_create,
    ("note", "lint"): _cmd_note_lint,
}


def main(argv: list[str] | None = None) -> int:
    args = _construir_parser().parse_args(argv)
    comando = _COMANDOS[(args.noun, getattr(args, "verb", None))]
    try:
        return comando(args)
    except (
        VaultInvalido,
        vocab.VocabularioIncompleto,
        todo.SinTabla,
        MarcadorAutorFaltante,
    ) as e:
        print(f"tuku {args.noun}: {e}", file=sys.stderr)
        return RECHAZO


if __name__ == "__main__":
    raise SystemExit(main())
