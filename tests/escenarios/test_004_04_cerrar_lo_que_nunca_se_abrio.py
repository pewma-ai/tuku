"""Tests del escenario 004-04-cerrar-lo-que-nunca-se-abrio.

Escenario: 004-04-cerrar-lo-que-nunca-se-abrio.md

Cerrar lo que nunca se abrió: da por hecho lo que no estaba pendiente.

Conversa Damián (lo interpreta Claude con el plan del `.md`) y responde el
agente del arnés. Se evalúa la tabla de deltas por turno y `tuku doctor`; lo que
solo se juzga leyendo la conversación está en "Qué se mira a mano" del `.md`.

Ejecutable en pantalla: `uv run python tests/scripts/test-tui.py 004-04`
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import agente  # noqa: E402
import conversacion  # noqa: E402

ID = "004-04"

sin_arnes = pytest.mark.skipif(
    not agente.disponible(), reason=agente.motivo_no_disponible() or ""
)


@pytest.mark.agentic
@sin_arnes
def test_004_04_cada_turno_deja_lo_que_dice_la_tabla_y_el_vault_queda_sano() -> None:
    c = conversacion.correr(ID)
    assert c.conclusion.ok, "no pasó:\n" + c.fallos()
