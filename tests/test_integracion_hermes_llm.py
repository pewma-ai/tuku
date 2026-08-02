"""Tests de integración — Fase 5, llamadas reales a Hermes (LLM).

Todo test aquí invoca un modelo de verdad y gasta tokens. Marcados
`@pytest.mark.agentic`, excluidos por defecto (`-m "not agentic"` en
pyproject.toml); se activan con `pytest -m agentic`.

Cada uno tiene su gemelo determinista en `test_integracion_agentica.py`.

Ver `devel/checklist-implementacion.md` §F5 y ADR 0018.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from tuku.core.agent import registrar_conversacional

pytestmark = pytest.mark.agentic


def test_registrar_con_agente_produce_canonica(hermes_efimero: dict) -> None:
    """[AGENTE] registrar_conversacional con agente produce forma canónica parseable."""
    if shutil.which("hermes") is None:
        pytest.skip("hermes no instalado")

    from tuku.io.entry import Entry

    profile_dir = Path(hermes_efimero["HERMES_HOME"]).parent

    tipo, canonico = registrar_conversacional(
        profile_dir,
        "Cerramos el mes con muy buenos resultados. #hito",
        sin_agente=False,
    )

    assert tipo in ("entrada", "tarea")
    if tipo == "entrada":
        # Debe ser parseable
        entry = Entry.parse_line(canonico)
        assert entry.text


def test_hermes_mantiene_sesion_entre_llamadas(hermes_efimero: dict) -> None:
    """[AGENTE] run_hermes con --continue mantiene contexto entre llamadas."""
    if shutil.which("hermes") is None:
        pytest.skip("hermes no instalado")

    from tuku.core.agent import run_hermes

    profile_dir = Path(hermes_efimero["HERMES_HOME"]).parent

    run_hermes(profile_dir, "Recuerda el número 42 para la siguiente pregunta.")
    r2 = run_hermes(profile_dir, "¿Qué número te pedí que recordaras?")

    # La respuesta al segundo turno debe mencionar 42
    assert "42" in r2, f"Hermes no mantuvo el contexto: {r2!r}"
