"""Tests del escenario 003-11-el-dia-que-no-se-dicta.

Escenario: 003-11-el-dia-que-no-se-dicta.md

El día se dicta por su nombre ("el viernes pasado"), no por su fecha: el agente
la deriva del calendario y el registro cae en ese día de `AHORA.md`.

Ejecutable directo: `python3 tests/escenarios/test_003_11_el_dia_que_no_se_dicta.py`
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

SLUG = "003-11-el-dia-que-no-se-dicta"
TITULO = "el registro va al viernes pasado"
VIERNES = "## Viernes 21 de agosto"

#: Lo que toca un registro sin consecuencia en `depto-centro`, del gemelo `002-13`.
DELTA_SIN_CONSECUENCIA = {
    "AHORA.md": "modificado",
    "ambitos/depto-centro/depto-centro.md": "modificado",
}

sin_arnes = pytest.mark.skipif(
    not agente.disponible(), reason=agente.motivo_no_disponible() or ""
)


def _ahora(corrida: gherkin.Corrida) -> str:
    return corrida.ruta("mi-vault", "AHORA.md").read_text(encoding="utf-8")


def _viernes(corrida: gherkin.Corrida) -> list[str]:
    dia = _ahora(corrida).split(VIERNES, 1)[1].split("\n## ", 1)[0]
    return [x for x in dia.splitlines() if x.startswith("- ")]


@pytest.mark.agentic
@sin_arnes
def test_003_11_un_solo_comando() -> None:
    turno = gherkin.correr(SLUG, TITULO).turno
    assert turno.traduccion == ["entry create"], f"la traza dice: {turno.comandos}"


@pytest.mark.agentic
@sin_arnes
def test_003_11_el_registro_abre_el_viernes_y_no_nace_el_martes() -> None:
    corrida = gherkin.correr(SLUG, TITULO)
    registros = _viernes(corrida)
    horas = [x[2:7] for x in registros]
    assert horas[0] == "17:00" and "09:30" in horas, (
        f"el registro de las 17:00 debía abrir el viernes:\n{registros}"
    )
    assert not any(m in registros[0] for m in (todo.ABRE, todo.CIERRA)), registros[0]
    assert "## Martes 25 de agosto" not in _ahora(corrida), "el hecho no era de hoy"


@pytest.mark.agentic
@sin_arnes
def test_003_11_el_delta_es_el_de_un_registro_sin_consecuencia() -> None:
    assert gherkin.correr(SLUG, TITULO).delta_de("mi-vault") == DELTA_SIN_CONSECUENCIA


if __name__ == "__main__":
    if not agente.disponible():
        print(f"saltado: {agente.motivo_no_disponible()}")
        raise SystemExit(0)
    test_003_11_un_solo_comando()
    test_003_11_el_registro_abre_el_viernes_y_no_nace_el_martes()
    test_003_11_el_delta_es_el_de_un_registro_sin_consecuencia()
    print(f"ok: 3 afirmaciones (queda en playground/{SLUG}/)")
