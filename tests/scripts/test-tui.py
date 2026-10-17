#!/usr/bin/env python3
"""Corre una conversación del epic 004 en pantalla, con todo lo que hace el agente.

    uv run python tests/scripts/test-tui.py 004-03
    uv run python tests/scripts/test-tui.py 004-01 --turnos 3
    uv run python tests/scripts/test-tui.py 004-03 --manual
    uv run python tests/scripts/test-tui.py 004-03 --raw

Damián lo interpreta Claude (Sonnet, esfuerzo bajo) con el plan del escenario;
con `--manual` las frases las escribes tú. Responde el agente del arnés
(`TUKU_AGENTE`, `agy` por defecto). Al terminar deja el vault y el
`conversation-log.md` en `playground/`, como la conversación a mano.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import agente
import conversar
import gherkin
import tui


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    p.add_argument("id", help="el escenario, por ejemplo 004-03")
    p.add_argument("--turnos", type=int, help="solo los primeros N turnos")
    p.add_argument("--manual", action="store_true", help="las frases de Damián las escribes tú")
    p.add_argument("--raw", action="store_true", help="el JSON del arnés, sin dar formato")
    p.add_argument("--modelo-damian", default="sonnet")
    p.add_argument("--esfuerzo-damian", default="low")
    args = p.parse_args(argv)

    motivo = agente.motivo_no_disponible()
    if motivo is not None:
        print(f"test-tui: {motivo}", file=sys.stderr)
        return 1
    try:
        plan = tui.leer_plan(args.id)
        base = tui.asegurar_base(plan)
    except tui.EscenarioNoEncontrado as e:
        print(f"test-tui: {e}", file=sys.stderr)
        return 1

    vista = tui.Vista(raw=args.raw)
    slug = plan.archivo.stem
    escenario = gherkin.slugificar(plan.titulo)
    v = conversar.preparar(base, slug, escenario)
    total = min(args.turnos or len(plan.pasos), len(plan.pasos))
    vista.nota(f"{plan.archivo.name} · {plan.titulo}")
    vista.nota(f"vault en {v}")

    historia: list[tuple[str, str]] = []
    registros: list[dict[str, Any]] = []
    for n in range(1, total + 1):
        vista.turno(n, total, plan.ahora)
        if args.manual:
            vista.nota(f"plan: {plan.pasos[n - 1]}")
            frase = input("Damián> ").strip()
            if not frase:
                break
            vista.damian(frase)
        else:
            prompt = tui.prompt_de_damian(plan, historia, n)
            inicio = time.monotonic()
            frase = tui.frase_de_damian(prompt, args.modelo_damian, args.esfuerzo_damian)
            vista.damian(frase, time.monotonic() - inicio)
        registro = conversar.turno(
            v, frase, plan.ahora, en_vivo=vista.evento, en_error=vista.error
        )
        vista.cierre(registro)
        registros.append(registro)
        historia.append((frase, registro["agente"]))

    destino = conversar.cerrar(v, slug, f"Conversación {slug} · {plan.titulo}")
    archivado = destino / escenario / "mi-vault" if destino else v
    conclusion = tui.evaluar(plan, registros, tui.correr_doctor(archivado))
    vista.conclusion(conclusion, plan, archivado / conversar.LOG)
    return 0 if conclusion.ok else 2
    return 0


def _correr(argv: list[str]) -> int:
    try:
        return main(argv)
    except KeyboardInterrupt:
        print(
            "\ntest-tui: interrumpido. El agente se detuvo. El vault quedó en el banco "
            "(/tmp/tuku-banco) y `playground/` no se tocó.",
            file=sys.stderr,
        )
        return 130


if __name__ == "__main__":
    sys.exit(_correr(sys.argv[1:]))
