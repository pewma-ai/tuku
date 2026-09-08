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

from tuku import style, todo, transclusion, vocab
from tuku.config import VaultInvalido, archivo_vault, leer_config
from tuku.entry import add
from tuku.init import (
    DIAS,
    MESES,
    DestinoNoVacio,
    MarcadorAutorFaltante,
    TukuHomeInvalido,
    init,
)
from tuku.lint import ERROR, formatear, lint

#: Códigos de salida. Son contrato con quien invoca, persona o agente, y están
#: fijados en `spec/cli.md`. El 2 queda reservado a argparse, que lo emite ante
#: una invocación mal formada: ningún comando puede devolverlo por otra causa,
#: o quien invoca no puede distinguir "me equivoqué al escribir el comando" de
#: "el comando se negó".
EXITO = 0
RECHAZO = 1  # el comando entendió y se negó por el estado del vault
USO = 2  # reservado a argparse
ENTORNO = 3  # la instalación de TUKU no está donde debería

_archivo = archivo_vault


def _encabezado_de_hoy(hoy: date) -> str:
    return f"## {DIAS[hoy.weekday()]} {hoy.day} de {MESES[hoy.month - 1]}"


def _vocabulario_abierto(vault: Path) -> list[str]:
    return leer_config(vault).vocabularios_abiertos()


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
        "--variante", default="vanilla", help="variante de template/ a copiar"
    )
    init_p.add_argument(
        "--author",
        "--autor",
        dest="autor",
        default=None,
        help="nombre del autor para LIBRO-DE-ESTILO.md; opcional",
    )
    init_p.add_argument(
        "--force",
        action="store_true",
        help="reemplaza el destino aunque ya tenga contenido",
    )

    entry_p = sub.add_parser("entry", help="registros de la bitácora")
    entry_v = entry_p.add_subparsers(dest="verb", required=True)

    add_p = entry_v.add_parser("add", help="escribe registros ya formados en su día")
    add_p.add_argument("linea", nargs="+", help="línea de registro, '- HH:MM - ...'")
    add_p.add_argument("--vault", default=".", type=Path, help="vault destino")
    add_p.add_argument(
        "--dia", default=None, help="encabezado del día (por defecto, el de hoy)"
    )

    lint_p = entry_v.add_parser("lint", help="revisa los registros y reporta; no escribe")
    lint_p.add_argument("--vault", default=".", type=Path, help="vault a revisar")

    todo_p = sub.add_parser("todo", help="pendientes de PENDIENTES.md")
    todo_v = todo_p.add_subparsers(dest="verb", required=True)

    for verbo, ayuda in (
        ("open", "abre el pendiente de un registro **pendiente**"),
        ("close", "cierra el pendiente de un registro ~~(Hecho)~~"),
    ):
        p = todo_v.add_parser(verbo, help=ayuda)
        p.add_argument("linea", help="la línea del registro que lleva la marca")
        p.add_argument("--vault", default=".", type=Path, help="vault a modificar")
        if verbo == "open":
            p.add_argument(
                "--ancla",
                default=todo.SIN_FECHA,
                help="callout destino: un horizonte, o una fecha AAAA-MM-DD",
            )

    todo_lint = todo_v.add_parser("lint", help="revisa los pendientes y reporta; no escribe")
    todo_lint.add_argument("--vault", default=".", type=Path, help="vault a revisar")

    trans_p = sub.add_parser(
        "transclusion", help="transclusiones entre AHORA.md y PENDIENTES.md"
    )
    trans_v = trans_p.add_subparsers(dest="verb", required=True)
    sync_p = trans_v.add_parser("sync", help="cuadra las transclusiones de los días")
    sync_p.add_argument("--vault", default=".", type=Path, help="vault a cuadrar")

    cycle_p = sub.add_parser("cycle", help="gestión del ciclo en AHORA.md")
    cycle_v = cycle_p.add_subparsers(dest="verb", required=True)
    open_p = cycle_v.add_parser("open", help="abre o verifica el ciclo en AHORA.md")
    open_p.add_argument("--vault", default=".", type=Path, help="vault a verificar o abrir")
    open_p.add_argument(
        "--fecha",
        "--date",
        "--desde",
        dest="fecha",
        default=None,
        type=date.fromisoformat,
        help="fecha deseada (AAAA-MM-DD); por defecto, hoy",
    )

    vocab_p = sub.add_parser("vocab", help="vocabularios abiertos del autor")
    vocab_v = vocab_p.add_subparsers(dest="verb", required=True)
    show_p = vocab_v.add_parser("show", help="muestra los vocabularios del libro de estilo")
    show_p.add_argument("--vault", default=".", type=Path, help="vault a leer")

    style_p = sub.add_parser("style", help="libro de estilo y contratos de autor")
    style_v = style_p.add_subparsers(dest="verb", required=True)
    style_lint_p = style_v.add_parser("lint", help="revisa contratos en LIBRO-DE-ESTILO.md")
    style_lint_p.add_argument("--vault", default=".", type=Path, help="vault a revisar")

    return parser




def _cmd_init(args: argparse.Namespace) -> int:
    try:
        destino = init(
            args.dir, variante=args.variante, autor=args.autor, force=args.force
        )
    except DestinoNoVacio as e:
        print(f"tuku init: {e}", file=sys.stderr)
        return RECHAZO
    except MarcadorAutorFaltante as e:
        print(f"tuku init: {e}", file=sys.stderr)
        return RECHAZO
    except TukuHomeInvalido as e:
        print(f"tuku init: {e}", file=sys.stderr)
        return ENTORNO
    print(
        f"vault sembrado en {destino}. "
        f"Abre {destino / 'AHORA.md'} y escribe tu primera línea."
    )
    return EXITO


def _cmd_entry_add(args: argparse.Namespace) -> int:
    ruta = _archivo(args.vault, "AHORA.md")
    dia = args.dia if args.dia is not None else _encabezado_de_hoy(date.today())
    try:
        texto = add(ruta.read_text(encoding="utf-8"), list(args.linea), dia=dia)
    except ValueError as e:
        print(f"tuku entry add: {e}", file=sys.stderr)
        return RECHAZO
    ruta.write_text(texto, encoding="utf-8")
    print(f"{len(args.linea)} registro(s) en {dia.removeprefix('## ')}.")
    return EXITO


def _cmd_entry_lint(args: argparse.Namespace) -> int:
    ahora = _archivo(args.vault, "AHORA.md").read_text(encoding="utf-8")
    hallazgos = lint(ahora, abiertos=_vocabulario_abierto(args.vault))
    print(formatear(hallazgos))
    return RECHAZO if any(h.grado == ERROR for h in hallazgos) else EXITO


def _marca_o_rechazo(linea: str, esperada: str, verbo: str) -> todo.Marca | None:
    marca = todo.parsear(linea)
    if marca is None or marca.marca != esperada:
        print(
            f"tuku todo {verbo}: la línea no lleva {esperada}. "
            f"Escríbela exactamente así, o usa el otro verbo.",
            file=sys.stderr,
        )
        return None
    return marca


def _cmd_todo_open(args: argparse.Namespace) -> int:
    marca = _marca_o_rechazo(args.linea, todo.ABRE, "open")
    if marca is None:
        return RECHAZO
    ruta = _archivo(args.vault, "PENDIENTES.md")
    ruta.write_text(
        todo.abrir(ruta.read_text(encoding="utf-8"), marca, ancla=args.ancla), encoding="utf-8"
    )
    print(f"pendiente abierto en ^{args.ancla}: {marca.cuerpo}")
    # `todo open` no escribe la transclusión: la cuadra el otro comando (regla 6
    # de `spec/pendientes.md`). Recordarlo acá evita la falla silenciosa, que es
    # que el pendiente exista y no aparezca en su día.
    print("Corre `tuku transclusion sync` para que aparezca en su día.")
    return EXITO


def _cmd_todo_close(args: argparse.Namespace) -> int:
    marca = _marca_o_rechazo(args.linea, todo.CIERRA, "close")
    if marca is None:
        return RECHAZO
    ruta = _archivo(args.vault, "PENDIENTES.md")
    texto, hubo_pareja = todo.cerrar(ruta.read_text(encoding="utf-8"), marca)
    if not hubo_pareja:
        # El registro queda escrito y PENDIENTES.md intacto: un cierre sin pareja
        # es el caso normal del día uno, no un fallo del autor (`devel/epics.md`).
        print(
            f"todo close: no había ningún pendiente abierto con el cuerpo "
            f"{marca.cuerpo!r}, así que no se borró nada. El registro queda escrito. "
            f"Si esperabas cerrarlo, revisa que el texto coincida palabra por palabra."
        )
        return EXITO
    ruta.write_text(texto, encoding="utf-8")
    print(f"pendiente cerrado: {marca.cuerpo}")
    return EXITO


def _cmd_todo_lint(args: argparse.Namespace) -> int:
    pendientes = _archivo(args.vault, "PENDIENTES.md").read_text(encoding="utf-8")
    duplicados = todo.duplicados(pendientes)
    if not duplicados:
        print("todo lint: sin hallazgos.")
        return EXITO
    for cuerpo in duplicados:
        print(
            f"PENDIENTES.md: error: {cuerpo!r} aparece en más de un callout. "
            f"Déjalo en uno solo: un pendiente está en exactamente un callout."
        )
    print(f"todo lint: {len(duplicados)} error(es).")
    return RECHAZO


def _cmd_transclusion_sync(args: argparse.Namespace) -> int:
    ahora = _archivo(args.vault, "AHORA.md")
    pendientes = _archivo(args.vault, "PENDIENTES.md").read_text(encoding="utf-8")
    texto, reparaciones = transclusion.sync(ahora.read_text(encoding="utf-8"), pendientes)
    if reparaciones:
        ahora.write_text(texto, encoding="utf-8")
    print(transclusion.formatear(reparaciones))
    return EXITO


def _cmd_vocab_show(args: argparse.Namespace) -> int:
    cfg = leer_config(args.vault)
    print(vocab.formatear(cfg.vocabularios))
    return EXITO


def _cmd_style_lint(args: argparse.Namespace) -> int:
    libro = _archivo(args.vault, "LIBRO-DE-ESTILO.md").read_text(encoding="utf-8")
    hallazgos = style.lint(libro)
    print(style.formatear(hallazgos))
    return RECHAZO if any(h.grado == ERROR for h in hallazgos) else EXITO


def _cmd_cycle_open(args: argparse.Namespace) -> int:
    from tuku.cycle import open_cycle
    ahora_path, creado = open_cycle(args.vault, args.fecha)
    if creado:
        print(f"ciclo abierto en {ahora_path}.")
    else:
        print("AHORA.md ya cubre la fecha requerida.")
    return EXITO


_COMANDOS = {
    ("init", None): _cmd_init,
    ("cycle", "open"): _cmd_cycle_open,
    ("entry", "add"): _cmd_entry_add,
    ("entry", "lint"): _cmd_entry_lint,
    ("todo", "open"): _cmd_todo_open,
    ("todo", "close"): _cmd_todo_close,
    ("todo", "lint"): _cmd_todo_lint,
    ("transclusion", "sync"): _cmd_transclusion_sync,
    ("vocab", "show"): _cmd_vocab_show,
    ("style", "lint"): _cmd_style_lint,
}



def main(argv: list[str] | None = None) -> int:
    args = _construir_parser().parse_args(argv)
    comando = _COMANDOS[(args.noun, getattr(args, "verb", None))]
    try:
        return comando(args)
    except (
        VaultInvalido,
        vocab.VocabularioIncompleto,
        todo.SinCallout,
        MarcadorAutorFaltante,
    ) as e:
        print(f"tuku {args.noun}: {e}", file=sys.stderr)
        return RECHAZO


if __name__ == "__main__":
    raise SystemExit(main())
