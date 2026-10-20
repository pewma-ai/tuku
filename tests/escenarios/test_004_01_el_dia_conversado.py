"""Tests del escenario 004-01-el-dia-conversado.

Escenario: 004-01-el-dia-conversado.md

El día conversado: doce turnos de consulta, duda, interrupción y ratificación.

Conversa Damián (lo interpreta Claude con el plan del `.md`) y responde el
agente del arnés. Se evalúa la tabla de deltas por turno y `tuku doctor`; lo que
solo se juzga leyendo la conversación está en "Qué se mira a mano" del `.md`.

Ejecutable en pantalla: `uv run python tests/scripts/test-tui.py 004-01`
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

ID = "004-01"

sin_arnes = pytest.mark.skipif(
    not agente.disponible(), reason=agente.motivo_no_disponible() or ""
)


@pytest.mark.agentic
@sin_arnes
def test_004_01_cada_turno_deja_lo_que_dice_la_tabla_y_el_vault_queda_sano() -> None:
    c = conversacion.correr(ID)
    assert c.conclusion.ok, "no pasó:\n" + c.fallos()


#: La tabla de verdad del `.md` (miércoles 12): hora, ámbito y marca cerrada.
VERDAD = [
    ("10:15", "tesis-javier-castro", True),
    ("10:30", "tesis-javier-castro", False),
    ("10:35", "tesis-javier-castro", False),
    ("11:00", "transformacion-digital", False),
    ("11:45", "transformacion-digital", False),
    ("15:00", "faena-ai", True),
]


@pytest.mark.agentic
@sin_arnes
def test_004_01_el_vault_final_coincide_con_la_tabla_de_verdad() -> None:
    c = conversacion.correr(ID)
    ahora = (c.vault / "AHORA.md").read_text(encoding="utf-8")
    assert "## Miércoles 12 de agosto" in ahora, "no hay día 12 en AHORA.md"
    dia = ahora.split("## Miércoles 12 de agosto", 1)[1].split("\n## ", 1)[0]
    lineas = {x[2:7]: x for x in dia.splitlines() if x.startswith("- ")}
    for hora, ambito, cierra in VERDAD:
        assert hora in lineas, f"falta el registro de las {hora}:\n{dia}"
        assert f"[{ambito}]" in lineas[hora], f"las {hora} no son de {ambito}: {lineas[hora]}"
        assert ("(Hecho)" in lineas[hora]) == cierra, f"marca de las {hora}: {lineas[hora]}"
    ambitos = sorted(p.name for p in (c.vault / "ambitos").iterdir() if p.is_dir())
    assert ambitos == ["faena", "personal", "tuku"], ambitos
    hijos = sorted(p.name for p in (c.vault / "ambitos" / "faena").iterdir() if p.is_dir())
    assert hijos == ["faena-ai", "tesis-javier-castro", "transformacion-digital"], hijos
