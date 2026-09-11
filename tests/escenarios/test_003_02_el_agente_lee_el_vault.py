"""Tests del escenario 003-02-el-agente-lee-el-vault.

Escenario: 003-02-el-agente-lee-el-vault.md

Primer turno agéntico del epic 003. El autor pregunta, el agente responde y el
vault no cambia: el diff es vacío por construcción y se verifica que el agente
haya leído `AGENTS.md` para identificar el destino del hecho y su consecuencia.

El turno sale del bloque `agente` del `.md`.

Ejecutable directo: `python3 tests/escenarios/test_003_02_el_agente_lee_el_vault.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import agente  # noqa: E402
import gherkin  # noqa: E402

SLUG = "003-02-el-agente-lee-el-vault"
TITULO = "el agente dice qué haría"

sin_arnes = pytest.mark.skipif(
    not agente.disponible(), reason=agente.motivo_no_disponible() or ""
)


@pytest.mark.agentic
@sin_arnes
def test_003_02_preguntar_no_cambia_el_vault() -> None:
    corrida = gherkin.correr(SLUG, TITULO)
    assert corrida.delta_de("mi-vault") == {}, "preguntar no puede cambiar el vault"


@pytest.mark.agentic
@sin_arnes
def test_003_02_la_traduccion_esta_vacia() -> None:
    """Una pregunta no se traduce en ningún comando."""
    turno = gherkin.correr(SLUG, TITULO).turno
    assert turno.traduccion == [], (
        f"el autor pidió no hacerlo todavía y ejecutó: {turno.comandos}"
    )


@pytest.mark.agentic
@sin_arnes
def test_003_02_la_respuesta_nombra_los_dos_destinos() -> None:
    """El agente debe identificar la bitácora y la tabla de pendientes."""
    turno = gherkin.correr(SLUG, TITULO).turno
    dijo = turno.stdout
    assert "AHORA.md" in dijo, f"no nombró dónde va el registro:\n{dijo}"
    assert "PENDIENTES.md" in dijo, f"no nombró dónde va la consecuencia:\n{dijo}"


if __name__ == "__main__":
    if not agente.disponible():
        print(f"saltado: {agente.motivo_no_disponible()}")
        raise SystemExit(0)
    test_003_02_preguntar_no_cambia_el_vault()
    test_003_02_la_traduccion_esta_vacia()
    test_003_02_la_respuesta_nombra_los_dos_destinos()
    print(f"ok: 3 afirmaciones (queda en playground/{SLUG}/)")
