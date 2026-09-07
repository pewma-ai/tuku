"""CLI de TUKU: capa fina de argparse sobre las funciones de `tuku/`.

`tuku <noun> <verb>`, todo en inglés. Hoy solo está `tuku init`; los demás
nouns (`entry`, `todo`, `scope`) se conectan cuando su epic los necesite. La
lógica no vive acá: cada comando llama a una función importable de `tuku/`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tuku.init import DestinoNoVacio, TukuHomeInvalido, init


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
    return parser


def _cmd_init(args: argparse.Namespace) -> int:
    try:
        destino = init(
            args.dir, variante=args.variante, autor=args.autor, force=args.force
        )
    except DestinoNoVacio as e:
        print(f"tuku init: {e}", file=sys.stderr)
        return 1
    except TukuHomeInvalido as e:
        print(f"tuku init: {e}", file=sys.stderr)
        return 2
    print(
        f"vault sembrado en {destino}. "
        f"Abre {destino / 'AHORA.md'} y escribe tu primera línea."
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _construir_parser().parse_args(argv)
    if args.noun == "init":
        return _cmd_init(args)
    return 1  # argparse ya rechaza cualquier otro noun


if __name__ == "__main__":
    raise SystemExit(main())
