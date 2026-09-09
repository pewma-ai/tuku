"""Tests del escenario 003-02-el-agente-lee-el-vault.

Escenario: 003-02-el-agente-lee-el-vault.md

Primer turno del epic 003. El autor pregunta, el agente responde y el vault no
cambia: el diff vacío es por construcción, y lo que se mide es si el agente leyó
el `AGENTS.md` que tiene al lado.

El turno sale del bloque `agente` del `.md`, igual que los comandos salen de los
bloques `bash`.

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
    """Una pregunta no se traduce en ningún comando, que es lo que dice el `.md`."""
    turno = gherkin.correr(SLUG, TITULO).turno
    assert turno.traduccion == [], (
        f"el autor pidió no hacerlo todavía y ejecutó: {turno.comandos}"
    )


@pytest.mark.agentic
@sin_arnes
def test_003_02_la_respuesta_nombra_los_dos_destinos() -> None:
    """Que sean dos pasos es lo primero que el `AGENTS.md` tiene que transmitir.

    `tuku entry add` escribe el registro y nada más: es `tuku todo open` el que
    abre el pendiente. Un agente que solo nombra la bitácora va a dejar el vault
    a medias en cuanto se le pida de verdad, y eso no deja señal.
    """
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
    print("ok: el agente leyó el vault y no lo tocó")
