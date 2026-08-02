"""CLI principal de TUKU.

Integra los subcomandos `init`, `sync` y `doctor` (Fase 0).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tuku.core.doctor import run_doctor
from tuku.core.init import init_perfil
from tuku.core.sync import sync_perfil


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tuku",
        description=(
            "TUKU — Management as Code (MaC) para la vida personal.\n\n"
            "Sistema de gestión basado en archivos Markdown planos versionados en Git,\n"
            "operado mediante janitors deterministas y asistencia conversacional."
        ),
        epilog=(
            "Ejemplos:\n"
            "  tuku init                  Siembra un nuevo perfil en el CWD\n"
            "  tuku init ~/mi-perfil      Siembra un perfil en la ruta dada\n"
            "  tuku doctor                Diagnostica la salud del perfil\n"
            "  tuku -p ~/perfil doctor    Diagnostica un perfil específico\n"
            "  tuku sync                  Sincroniza punteros a procesos\n\n"
            "Documentación: https://github.com/pewma-ai/tuku"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-p",
        "--profile",
        type=Path,
        default=Path.cwd(),
        help="Ruta al perfil TUKU (default: directorio actual)",
    )

    subparsers = parser.add_subparsers(dest="command", title="Subcomandos")

    # init
    parser_init = subparsers.add_parser(
        "init",
        help="Siembra un nuevo perfil TUKU con la estructura canónica",
        description=(
            "Inicializa el árbol de directorios (entradas/, tareas/, ciclos/, entidades/,\n"
            "estrategia/, notas/) y siembra los archivos iniciales, incluyendo .gitignore\n"
            "y .tuku/config.yaml."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser_init.add_argument(
        "target",
        type=Path,
        nargs="?",
        default=Path.cwd(),
        help="Directorio destino donde sembrar el perfil (default: directorio actual)",
    )

    # sync
    subparsers.add_parser(
        "sync",
        help="Sincroniza punteros a procesos y assets de agente",
        description=(
            "Genera y actualiza los punteros en .tuku/procesos/ e instrucciones AGENTS.md\n"
            "desde el motor instalado hacia el perfil, sin vendorizar código ejecutable."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # doctor
    subparsers.add_parser(
        "doctor",
        help="Diagnóstico de salud del perfil y versión del motor",
        description=(
            "Verifica la versión del motor, commit/rama Git de build,\n"
            "validez de .tuku/config.yaml y presencia de canónicos."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    args = parser.parse_args(argv)

    if args.command == "init":
        target = args.target if args.target else args.profile
        init_perfil(target)
        print(f"Perfil TUKU inicializado en {target.resolve()}")
        return 0

    if args.command == "sync":
        res = sync_perfil(args.profile)
        p_cnt, a_cnt = res["procesos"], res["agents"]
        print(f"Sincronización completada: {p_cnt} procesos, {a_cnt} agentes.")
        return 0

    if args.command == "doctor":
        res_doc = run_doctor(args.profile)
        print(f"TUKU v{res_doc.version} ({res_doc.commit} en {res_doc.branch})")
        print(f"Perfil: {res_doc.profile_path}")
        if res_doc.valid_config:
            print(f"Configuración: válida (schema_version={res_doc.schema_version})")
        else:
            print("Configuración: INVÁLIDA")

        if res_doc.issues:
            print("\nProblemas detectados:")
            for issue in res_doc.issues:
                print(f" - {issue}")
            return 1

        print("Estado: OK")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
