"""CLI principal de TUKU.

Integra los subcomandos `init`, `sync`, `doctor`, `radar`, `janitor`,
`registrar`, `abrir` y `cerrar` (Fases 0–5).
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
            "  tuku sync                  Sincroniza punteros a procesos\n"
            "  tuku registrar \"Reunión con cliente #hito\"   Captura conversacional\n"
            "  tuku abrir 2026-W32 --tipo semana             Abre un ciclo\n"
            "  tuku cerrar 2026-W32                          Cierra un ciclo\n\n"
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

    # radar
    subparsers.add_parser(
        "radar",
        help="Consulta determinista en vivo del estado del perfil (sin escrituras en disco)",
        description=(
            "Calcula el estado actual bajo demanda: tareas abiertas, tareas bloqueadas\n"
            "por blockuntil y seguimientos vencidos (ADR 0011 / arquitectura §11)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # janitor
    parser_janitor = subparsers.add_parser(
        "janitor",
        help="Ejecuta verificaciones de invariantes sobre el perfil",
        description=(
            "Inspecciona el perfil en búsqueda de violaciones a las invariantes de spec/\n"
            "y permite reparación automática idempotente con --fix."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser_janitor.add_argument(
        "--fix",
        action="store_true",
        help="Aplica reparaciones automáticas de forma idempotente",
    )

    # registrar (F5.2)
    parser_registrar = subparsers.add_parser(
        "registrar",
        help="Captura conversacional: convierte texto natural a entrada o tarea canónica",
        description=(
            "Convierte una descripción en lenguaje natural a la forma canónica del perfil\n"
            "(entrada de bitácora o tarea posicional). Verifica que los ids de entidad\n"
            "citados existen en el perfil (capa factual)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser_registrar.add_argument(
        "texto",
        help="Texto a registrar en lenguaje natural",
    )
    parser_registrar.add_argument(
        "--sin-agente",
        action="store_true",
        default=True,
        help="Usar heurísticas deterministas (sin llamada a Hermes) [defecto]",
    )
    parser_registrar.add_argument(
        "--con-agente",
        action="store_true",
        default=False,
        help="Usar Hermes para normalizar el texto (gasta tokens)",
    )
    parser_registrar.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostrar la línea canónica sin escribir en disco",
    )

    # abrir (F5.3)
    parser_abrir = subparsers.add_parser(
        "abrir",
        help="Abre un nuevo ciclo sembrando plan_<nombre>.md con estructura canónica",
        description=(
            "Siembra `plan_<nombre>.md` en ciclos/ con front matter completo y las\n"
            "secciones obligatorias (Intención, No entra, Restricciones y contexto)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser_abrir.add_argument(
        "nombre",
        help="Nombre del ciclo, p.ej. 2026-W32 o 2026-08",
    )
    parser_abrir.add_argument(
        "--tipo",
        default="semana",
        help="Tipo de ciclo: semana, mes, turno, mision … (default: semana)",
    )
    parser_abrir.add_argument(
        "--inicio",
        default=None,
        help="Fecha de inicio del ciclo YYYY-MM-DD (default: hoy)",
    )
    parser_abrir.add_argument(
        "--fin",
        default=None,
        help="Fecha de fin del ciclo YYYY-MM-DD (default: hoy)",
    )

    # cerrar (F5.3)
    parser_cerrar = subparsers.add_parser(
        "cerrar",
        help="Cierra un ciclo sembrando resultados_<nombre>.md con estructura canónica",
        description=(
            "Siembra `resultados_<nombre>.md` en ciclos/ con las cinco secciones\n"
            "obligatorias (C7) y marca el plan correspondiente como cerrado."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser_cerrar.add_argument(
        "nombre",
        help="Nombre del ciclo a cerrar, debe coincidir con el plan_<nombre>.md",
    )
    parser_cerrar.add_argument(
        "--tipo",
        default="semana",
        help="Tipo de ciclo (debe coincidir con el plan) (default: semana)",
    )
    parser_cerrar.add_argument(
        "--inicio",
        default=None,
        help="Fecha de inicio del ciclo YYYY-MM-DD",
    )
    parser_cerrar.add_argument(
        "--fin",
        default=None,
        help="Fecha de fin del ciclo YYYY-MM-DD",
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

    if args.command == "radar":
        from tuku.core.cadence import radar_query

        rad = radar_query(args.profile)
        print("RADAR — Estado del perfil bajo demanda:")
        print(f" - Tareas abiertas: {rad.open_tasks}")
        print(f" - Tareas bloqueadas (blockuntil): {len(rad.blocked_tasks)}")
        for b in rad.blocked_tasks:
            print(f"   • {b}")
        print(f" - Seguimientos vencidos (followup): {len(rad.followup_due)}")
        for f in rad.followup_due:
            print(f"   • {f}")
        return 0

    if args.command == "janitor":
        from tuku.core.janitor import Janitor

        janitor = Janitor(args.profile)
        report = janitor.run_all(fix=args.fix)
        if report.is_clean:
            print("Janitor: perfil limpio sin violaciones de invariantes.")
            return 0

        print(f"Janitor: {len(report.violations)} violaciones detectadas:")
        for v in report.violations:
            rel = v.file_path.relative_to(args.profile.resolve())
            print(f" - [{v.invariant_id}] {rel}: {v.message}")

        return 1

    if args.command == "registrar":
        from tuku.core.agent import AgentError, escribir_registro, registrar_conversacional

        sin_agente = not getattr(args, "con_agente", False)
        try:
            tipo, canonico = registrar_conversacional(
                args.profile,
                args.texto,
                sin_agente=sin_agente,
            )
        except AgentError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

        if getattr(args, "dry_run", False):
            print(f"[{tipo}] {canonico}")
            return 0

        destino = escribir_registro(args.profile, tipo, canonico)
        rel = destino.relative_to(args.profile.resolve())
        print(f"Registrado como {tipo} en {rel}")
        print(f"  {canonico}")
        return 0

    if args.command == "abrir":
        from tuku.core.cadence import abrir_ciclo

        ruta = abrir_ciclo(
            args.profile,
            args.nombre,
            cycle_type=args.tipo,
            cycle_start=args.inicio,
            cycle_end=args.fin,
        )
        rel = ruta.relative_to(args.profile.resolve())
        print(f"Ciclo abierto: {rel}")
        return 0

    if args.command == "cerrar":
        from tuku.core.cadence import cerrar_ciclo

        ruta = cerrar_ciclo(
            args.profile,
            args.nombre,
            cycle_type=args.tipo,
            cycle_start=args.inicio,
            cycle_end=args.fin,
        )
        rel = ruta.relative_to(args.profile.resolve())
        print(f"Ciclo cerrado: {rel}")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
