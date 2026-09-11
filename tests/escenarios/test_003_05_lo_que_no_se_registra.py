"""Tests del escenario 003-05-lo-que-no-se-registra.

Escenario: 003-05-lo-que-no-se-registra.md

Casos negativos: discriminación entre hechos reales, preguntas e instrucciones.
Se comprueba que la instrucción al modelo no contamine la bitácora, que no se
cierren pendientes sin pareja y que la tabla de pendientes quede intacta.

Gemelos deterministas: `002-03` (lint) y `002-05` (cierre sin pareja).

Ejecutable directo: `python3 tests/escenarios/test_003_05_lo_que_no_se_registra.py`
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

from tuku import todo  # noqa: E402

SLUG = "003-05-lo-que-no-se-registra"
TITULO = "la instrucción y la pregunta"
DIA = "## Martes 11 de agosto"

DELTA_SIN_CONSECUENCIA = {
    "AHORA.md": "modificado",
    "ambitos/personal/personal.md": "modificado",
}

sin_arnes = pytest.mark.skipif(
    not agente.disponible(), reason=agente.motivo_no_disponible() or ""
)


def _dia_de(corrida: gherkin.Corrida) -> str:
    ahora = corrida.ruta("mi-vault", "AHORA.md").read_text(encoding="utf-8")
    return ahora.split(DIA, 1)[1].split("\n## ", 1)[0]


@pytest.mark.agentic
@sin_arnes
def test_003_05_solo_el_hecho_se_traduce_en_un_comando() -> None:
    turno = gherkin.correr(SLUG, TITULO).turno
    assert turno.traduccion == ["entry add"], (
        f"tres frases y un solo hecho, pero ejecutó: {turno.comandos}"
    )


@pytest.mark.agentic
@sin_arnes
def test_003_05_un_hecho_que_nunca_estuvo_pendiente_no_es_un_cierre() -> None:
    """Marcarlo con cierre haría mentir al vault sobre su pasado."""
    dia = _dia_de(gherkin.correr(SLUG, TITULO))
    nuevo = [x for x in dia.splitlines() if x.startswith("- 12:05 ")]
    assert len(nuevo) == 1, f"se esperaba el registro de las 12:05:\n{dia}"
    puestas = [m for m in (todo.ABRE, todo.CIERRA, "**cadencia**") if m in nuevo[0]]
    assert not puestas, f"marcó {puestas} algo que no abrió ni cerró nada: {nuevo[0]}"


@pytest.mark.agentic
@sin_arnes
def test_003_05_la_instruccion_al_agente_no_es_parte_del_dia() -> None:
    """"Recuérdame" va dirigido al modelo y no forma parte del hecho."""
    dia = _dia_de(gherkin.correr(SLUG, TITULO))
    assert "recuérdame" not in dia.lower(), f"escribió la instrucción como un hecho:\n{dia}"


@pytest.mark.agentic
@sin_arnes
def test_003_05_ni_la_pregunta_ni_la_instruccion_tocan_los_pendientes() -> None:
    """El pendiente heredado permanece intacto en la tabla."""
    corrida = gherkin.correr(SLUG, TITULO)
    assert "PENDIENTES.md" not in corrida.delta_de("mi-vault"), "tocó los pendientes"

    pendientes = corrida.ruta("mi-vault", "PENDIENTES.md").read_text(encoding="utf-8")
    assert len(todo.filas(pendientes)) == 1, f"la tabla cambió:\n{pendientes}"


@pytest.mark.agentic
@sin_arnes
def test_003_05_el_delta_es_el_de_un_registro_sin_consecuencia() -> None:
    assert gherkin.correr(SLUG, TITULO).delta_de("mi-vault") == DELTA_SIN_CONSECUENCIA


if __name__ == "__main__":
    if not agente.disponible():
        print(f"saltado: {agente.motivo_no_disponible()}")
        raise SystemExit(0)
    test_003_05_solo_el_hecho_se_traduce_en_un_comando()
    test_003_05_un_hecho_que_nunca_estuvo_pendiente_no_es_un_cierre()
    test_003_05_la_instruccion_al_agente_no_es_parte_del_dia()
    test_003_05_ni_la_pregunta_ni_la_instruccion_tocan_los_pendientes()
    test_003_05_el_delta_es_el_de_un_registro_sin_consecuencia()
    print(f"ok: 5 afirmaciones (queda en playground/{SLUG}/)")
