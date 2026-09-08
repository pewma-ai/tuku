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
from datetime import date, datetime
from pathlib import Path

from tuku import link, note, scope, style, todo, vocab
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
from tuku.propagate import propagar

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


def _cmd_init(args: argparse.Namespace) -> int:
    try:
        destino = init(args.dir, variant=args.variant, author=args.author, force=args.force)
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
        f"vault sembrado en {destino}. Abre {destino / 'AHORA.md'} y escribe tu primera línea."
    )
    return EXITO


def _cmd_entry_add(args: argparse.Namespace) -> int:
    ruta = _archivo(args.vault, "AHORA.md")
    dia = args.day if args.day is not None else _encabezado_de_hoy(date.today())
    try:
        texto = add(ruta.read_text(encoding="utf-8"), list(args.line), day=dia)
    except ValueError as e:
        print(f"tuku entry add: {e}", file=sys.stderr)
        return RECHAZO
    ruta.write_text(texto, encoding="utf-8")
    print(f"{len(args.line)} registro(s) en {dia.removeprefix('## ')}.")
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
    marca = _marca_o_rechazo(args.line, todo.ABRE, "open")
    if marca is None:
        return RECHAZO
    ruta = _archivo(args.vault, "PENDIENTES.md")
    ruta.write_text(
        todo.abrir(
            ruta.read_text(encoding="utf-8"),
            marca,
            horizon=args.horizon,
            when=args.when,
        ),
        encoding="utf-8",
    )
    print(f"pendiente abierto en «{args.horizon}»: {marca.cuerpo}")
    # Propagar es parte de abrir: si la vista quedara para un segundo comando,
    # el pendiente existiría sin aparecer en su día, que es la falla silenciosa
    # que `spec/pendientes.md` persigue. `--no-propagate` es la escotilla del
    # lote, que propaga una sola vez al final.
    if not args.no_propagate:
        propagar(args.vault)
    return EXITO


def _cmd_todo_propagate(args: argparse.Namespace) -> int:
    cambiados = propagar(args.vault)
    if not cambiados:
        print("todo propagate: las vistas ya estaban al día.")
        return EXITO
    print("\n".join(f"regenerado: {ruta}" for ruta in cambiados))
    return EXITO


def _cmd_todo_close(args: argparse.Namespace) -> int:
    marca = _marca_o_rechazo(args.line, todo.CIERRA, "close")
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
    if not args.no_propagate:
        propagar(args.vault)
    return EXITO


def _cmd_todo_lint(args: argparse.Namespace) -> int:
    pendientes = _archivo(args.vault, "PENDIENTES.md").read_text(encoding="utf-8")
    duplicados = todo.duplicados(pendientes)
    if not duplicados:
        print("todo lint: sin hallazgos.")
        return EXITO
    for cuerpo in duplicados:
        print(
            f"PENDIENTES.md: error: {cuerpo!r} aparece en más de una fila. "
            f"Déjalo en una sola: un pendiente está en exactamente un horizonte."
        )
    print(f"todo lint: {len(duplicados)} error(es).")
    return RECHAZO


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
    from tuku.cycle import CicloEnCurso, open_cycle

    try:
        ahora_path, creado = open_cycle(args.vault, args.date)
    except CicloEnCurso as e:
        print(f"tuku cycle open: {e}", file=sys.stderr)
        return RECHAZO
    if creado:
        print(f"ciclo abierto en {ahora_path}.")
    else:
        print("AHORA.md ya cubre la fecha requerida.")
    return EXITO


def _cmd_cycle_lint(args: argparse.Namespace) -> int:
    from tuku import cyclelint

    ahora = _archivo(args.vault, "AHORA.md").read_text(encoding="utf-8")
    hallazgos = cyclelint.lint(ahora)
    print(cyclelint.formatear(hallazgos))
    return RECHAZO if hallazgos else EXITO


def _cmd_doctor(args: argparse.Namespace) -> int:
    """Diagnostica el vault entero. Ninguna revisión que falle detiene al resto.

    Un archivo que falta es justo lo que el doctor existe para encontrar, así que
    aquí nada se lee con `_archivo`: eso aborta el comando con el vault a medio
    revisar, y el autor se queda sin el resto del diagnóstico.
    """
    from tuku import cyclelint, doctor, scope, style

    def leer(nombre: str) -> str | None:
        return doctor.archivo_opcional(args.vault, nombre)

    types_md = leer("reglas/types.md")
    revisiones = [
        doctor.revisar_config(leer("reglas/config.tuku.md")),
        doctor.revisar_tipos(types_md),
        doctor.revisar_archivos(args.vault),
        doctor.revisar_frontmatter(
            args.vault,
            tipos_validos=doctor.tipos_declarados(types_md) if types_md else [],
        ),
    ]

    ahora = leer("AHORA.md")
    if ahora is None:
        revisiones.append(doctor.ausente("cycle", "AHORA.md"))
        revisiones.append(doctor.ausente("entry", "AHORA.md"))
    else:
        h_cycle = cyclelint.lint(ahora)
        revisiones.append(doctor.Revision("cycle", cyclelint.formatear(h_cycle), not h_cycle))

        h_entry = lint(ahora, abiertos=_vocabulario_abierto(args.vault))
        revisiones.append(
            doctor.Revision(
                "entry", formatear(h_entry), not any(h.grado == ERROR for h in h_entry)
            )
        )

    pendientes = leer("PENDIENTES.md")
    if pendientes is None:
        revisiones.append(doctor.ausente("todo", "PENDIENTES.md"))
    else:
        duplicados = todo.duplicados(pendientes)
        salida_todo = (
            "todo lint: sin hallazgos."
            if not duplicados
            else "\n".join([*duplicados, f"todo lint: {len(duplicados)} error(es)."])
        )
        revisiones.append(doctor.Revision("todo", salida_todo, not duplicados))

    libro = leer("LIBRO-DE-ESTILO.md")
    if libro is None:
        revisiones.append(doctor.ausente("style", "LIBRO-DE-ESTILO.md"))
    else:
        h_style = style.lint(libro)
        revisiones.append(
            doctor.Revision(
                "style",
                style.formatear(h_style),
                not any(h.grado == ERROR for h in h_style),
            )
        )

    h_scope = scope.lint(args.vault)
    salida_scope = (
        "scope lint: sin hallazgos."
        if not h_scope
        else "\n".join([*h_scope, f"scope lint: {len(h_scope)} error(es)."])
    )
    revisiones.append(doctor.Revision("scope", salida_scope, not h_scope))

    print(doctor.formatear(revisiones, fuente=doctor.fuente_de_referencia()))
    return EXITO if all(r.sano for r in revisiones) else RECHAZO


def _cmd_scope_create(args: argparse.Namespace) -> int:
    directorio = scope.crear(args.vault, args.name)
    ahora_path = args.vault / "AHORA.md"
    menciones = 0
    if ahora_path.is_file():
        pagina_path = directorio / f"{args.name}.md"
        if pagina_path.is_file():
            kws = scope.keywords(pagina_path.read_text(encoding="utf-8"))
            texto, n = link.backfill(
                ahora_path.read_text(encoding="utf-8"),
                scope=args.name,
                keywords=kws,
            )
            if n > 0:
                ahora_path.write_text(texto, encoding="utf-8")
                menciones = n
    if menciones > 0:
        print(f"ámbito creado en {directorio} ({menciones} mención(es) enlazada(s)).")
    else:
        print(f"ámbito creado en {directorio}.")
    return EXITO


def _cmd_scope_lint(args: argparse.Namespace) -> int:
    hallazgos = scope.lint(args.vault)
    if not hallazgos:
        print("scope lint: sin hallazgos.")
        return EXITO
    for h in hallazgos:
        print(h)
    return RECHAZO


def _cmd_link_backfill(args: argparse.Namespace) -> int:
    ahora_file = _archivo(args.vault, "AHORA.md")
    pagina = args.vault / "ambitos" / args.scope / f"{args.scope}.md"
    if not pagina.is_file():
        print(
            f"tuku link backfill: no existe el ámbito {args.scope!r} "
            f"o falta su página {pagina.name}. Créalo primero con 'tuku scope create'.",
            file=sys.stderr,
        )
        return RECHAZO
    kws = scope.keywords(pagina.read_text(encoding="utf-8"))
    texto, n = link.backfill(
        ahora_file.read_text(encoding="utf-8"),
        scope=args.scope,
        keywords=kws,
    )
    if n > 0:
        ahora_file.write_text(texto, encoding="utf-8")
    print(f"link backfill: {n} mención(es) enlazada(s).")
    return EXITO


def _cmd_note_create(args: argparse.Namespace) -> int:
    cuerpo = ""
    if args.body_file is not None:
        cuerpo = args.body_file.read_text(encoding="utf-8")
    elif args.body is not None:
        cuerpo = args.body
    elif not sys.stdin.isatty():
        cuerpo = sys.stdin.read()
    else:
        print(
            "tuku note create: falta el cuerpo de la nota. "
            "Pasa --body, --body-file o escribe por stdin.",
            file=sys.stderr,
        )
        return RECHAZO

    hoy = args.today or date.today()
    hora = args.time or datetime.now().strftime("%H:%M")
    ruta = note.crear(
        args.vault,
        title=args.title,
        body=cuerpo,
        scope=args.scope,
        today=hoy,
    )

    if not args.no_record:
        ahora_path = args.vault / "AHORA.md"
        if ahora_path.is_file():
            constancia = note.registro_de_constancia(ruta, time=hora, scope=args.scope)
            texto = ahora_path.read_text(encoding="utf-8")
            if constancia not in texto:
                dia = args.day or _encabezado_de_hoy(hoy)
                ahora_path.write_text(add(texto, [constancia], day=dia), encoding="utf-8")

    print(f"nota creada en {ruta}.")
    return EXITO


def _cmd_note_lint(args: argparse.Namespace) -> int:
    rutas: list[Path] = []
    if args.file is not None:
        rutas.append(args.file)
    else:
        dir_notas = args.vault / "notas"
        if dir_notas.is_dir():
            rutas.extend(sorted(dir_notas.glob("*.md")))

    if not rutas:
        print("note lint: sin notas que revisar.")
        return EXITO

    todos_hallazgos: list[str] = []
    for ruta in rutas:
        contenido = ruta.read_text(encoding="utf-8")
        h = note.lint(contenido)
        for error in h:
            todos_hallazgos.append(f"{ruta.name}: {error}")

    if not todos_hallazgos:
        print("note lint: sin hallazgos.")
        return EXITO

    for hallazgo in todos_hallazgos:
        print(hallazgo)
    return RECHAZO


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
