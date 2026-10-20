"""Tests del escenario 004-03-ratificar-tras-tres-giros.

Escenario: 004-03-ratificar-tras-tres-giros.md

Ratificar tras tres giros: propone jueves, viernes y lunes, y ratifica el lunes.

Conversa Damián (lo interpreta Claude con el plan del `.md`) y responde el
agente del arnés. Se evalúa la tabla de deltas por turno y `tuku doctor`; lo que
solo se juzga leyendo la conversación está en "Qué se mira a mano" del `.md`.

Ejecutable en pantalla: `uv run python tests/scripts/test-tui.py 004-03`
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

ID = "004-03"

sin_arnes = pytest.mark.skipif(
    not agente.disponible(), reason=agente.motivo_no_disponible() or ""
)


@pytest.mark.agentic
@sin_arnes
def test_004_03_cada_turno_deja_lo_que_dice_la_tabla_y_el_vault_queda_sano() -> None:
    c = conversacion.correr(ID)
    assert c.conclusion.ok, "no pasó:\n" + c.fallos()
