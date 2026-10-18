#!/usr/bin/env python3
"""Corre un escenario agéntico en pantalla, con todo lo que hace el agente.

    uv run python tests/scripts/test-tui.py 004-03
    uv run python tests/scripts/test-tui.py 004-01 --turnos 3
    uv run python tests/scripts/test-tui.py 004-03 --manual
    uv run python tests/scripts/test-tui.py 004-03 --raw
    uv run python tests/scripts/test-tui.py 005-06
    uv run python tests/scripts/test-tui.py 005-06 --escenario Paula

Sirve para cualquier escenario con agente. En una conversación (epic 004, plan
```autor```), Damián lo interpreta Claude (Sonnet, esfuerzo bajo) con el plan;
con `--manual` las frases las escribes tú. En uno que dicta frases literales
(```agente```, epics 003 y 005), el autor dice exactamente lo que el escenario
escribe, y un archivo con varios escenarios corre todos o el que `--escenario`
nombre. Responde el agente del arnés
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
    p.add_argument("id", help="el escenario, por ejemplo 004-03 o 005-06")
    p.add_argument(
        "--escenario", help="solo el escenario del archivo cuyo título contiene esto"
    )
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
        planes = tui.leer_planes(args.id)
        if args.escenario:
            planes = [x for x in planes if args.escenario.lower() in x.titulo.lower()]
            if not planes:
                raise tui.EscenarioNoEncontrado(
                    f"ningún escenario de {args.id} contiene {args.escenario!r}"
                )
        if args.manual and any(x.literal for x in planes):
            raise tui.EscenarioNoEncontrado(
                f"{planes[0].archivo.name} dicta frases literales: --manual no aplica"
            )
    except tui.EscenarioNoEncontrado as e:
        print(f"test-tui: {e}", file=sys.stderr)
        return 1

    vista = tui.Vista(raw=args.raw)
    try:
        resultados = [_correr_plan(plan, args, vista) for plan in planes]
    except tui.EscenarioNoEncontrado as e:
        print(f"test-tui: {e}", file=sys.stderr)
        return 1
    if len(resultados) > 1:
        vista.resumen([(x.titulo, c.ok) for x, c in zip(planes, resultados, strict=True)])
    return 0 if all(c.ok for c in resultados) else 2


def _correr_plan(plan: tui.Plan, args: argparse.Namespace, vista: tui.Vista) -> tui.Conclusion:
    """Un escenario en pantalla: sus turnos, el cierre y la conclusión."""
    slug = plan.archivo.stem
    escenario = gherkin.slugificar(plan.titulo)
    if plan.literal:
        v = tui.sembrar(plan, slug, escenario)
    else:
        v = conversar.preparar(tui.asegurar_base(plan), slug, escenario)
    total = min(args.turnos or len(plan.pasos), len(plan.pasos))
    vista.nota(f"{plan.archivo.name} · {plan.titulo}")
    vista.nota(f"vault en {v}")

    historia: list[tuple[str, str]] = []
    registros: list[dict[str, Any]] = []
    for n in range(1, total + 1):
        vista.turno(n, total, plan.ahora_en(n))
        if plan.literal:
            frase = plan.pasos[n - 1]
            vista.damian(frase, quien="Autor")
        elif args.manual:
            vista.nota(f"plan: {plan.pasos[n - 1]}")
            frase = input("Damián> ").strip()
            if not frase:
                break
            vista.damian(frase)
        else:
            prompt = tui.prompt_de_damian(plan, historia, n, zona=tui.zona_del_vault(v))
            inicio = time.monotonic()
            frase = tui.frase_de_damian(prompt, args.modelo_damian, args.esfuerzo_damian)
            vista.damian(frase, time.monotonic() - inicio)
        registro = conversar.turno(
            v, frase, plan.ahora_en(n), en_vivo=vista.evento, en_error=vista.error
        )
        vista.cierre(registro)
        registros.append(registro)
        historia.append((frase, registro["agente"]))

    destino = conversar.cerrar(v, slug, f"Conversación {slug} · {plan.titulo}")
    archivado = destino / escenario / "mi-vault" if destino else v
    conclusion = tui.evaluar(plan, registros, tui.correr_doctor(archivado))
    vista.conclusion(conclusion, plan, archivado / conversar.LOG)
    return conclusion


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
