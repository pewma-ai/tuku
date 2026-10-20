"""Un escenario de conversación (epic 004) corrido sin pantalla, para pytest.

Hace lo que `test-tui.py` en pantalla: Damián lo interpreta Claude con el plan
del `.md`, responde el agente del arnés, y al final se evalúa contra la tabla del
escenario. Se cachea por escenario: la conversación se paga una vez aunque varios
tests la pidan.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any

import conversar
import gherkin
import tui


@dataclass
class Conversacion:
    plan: tui.Plan
    conclusion: tui.Conclusion
    turnos: list[dict[str, Any]]
    vault: Path

    def fallos(self) -> str:
        """Los chequeos que no pasaron, uno por línea."""
        return "\n".join(c for ok, c in self.conclusion.chequeos if not ok)


@cache
def correr(
    id: str, titulo: str | None = None, modelo: str = "sonnet", esfuerzo: str = "low"
) -> Conversacion:
    """El escenario `id` (por ejemplo `004-03`), de principio a fin."""
    planes = tui.leer_planes(id)
    if titulo:
        planes = [p for p in planes if titulo.lower() in p.titulo.lower()]
    plan = planes[0]
    slug = plan.archivo.stem
    escenario = gherkin.slugificar(plan.titulo)
    v = conversar.preparar(tui.asegurar_base(plan), slug, escenario)
    historia: list[tuple[str, str]] = []
    registros: list[dict[str, Any]] = []
    for n in range(1, len(plan.pasos) + 1):
        prompt = tui.prompt_de_damian(plan, historia, n, zona=tui.zona_del_vault(v))
        frase = tui.frase_de_damian(prompt, modelo, esfuerzo)
        registro = conversar.turno(v, frase, plan.ahora_en(n))
        registros.append(registro)
        historia.append((frase, registro["agente"]))
    destino = conversar.cerrar(v, slug, f"Conversación {slug} · {plan.titulo}")
    archivado = destino / escenario / "mi-vault" if destino else v
    conclusion = tui.evaluar(plan, registros, tui.correr_doctor(archivado))
    return Conversacion(plan, conclusion, registros, archivado)
