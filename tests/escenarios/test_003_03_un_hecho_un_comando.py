"""Tests del escenario 003-03-un-hecho-un-comando.

Escenario: 003-03-un-hecho-un-comando.md

El primer turno que escribe. Un hecho que no deja nada abierto tiene que ser una
línea en `AHORA.md` y nada más, y tiene que llegar por `tuku entry add`: un vault
correcto con la traza vacía es un fallo, porque significa que el agente editó el
archivo a mano.

Gemelo determinista: `002-02-registro-en-su-dia`.

Ejecutable directo: `python3 tests/escenarios/test_003_03_un_hecho_un_comando.py`
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

SLUG = "003-03-un-hecho-un-comando"
TITULO = "un hecho que no deja nada abierto"
DIA = "## Martes 11 de agosto"

#: Lo que toca escribir un registro, verificado contra el gemelo determinista
#: (`002-02`): la bitácora y la vista del ámbito, que `tuku entry add` regenera.
#: Cualquier otra cosa en el delta la hizo el agente sin que nadie se la pidiera.
DELTA_DE_UN_REGISTRO = {
    "AHORA.md": "modificado",
    "ambitos/personal/personal.md": "modificado",
}

#: Las marcas que tienen consecuencia. Ninguna corresponde acá: el autor contó
#: algo que pasó y no dejó nada por hacer ni dio nada por cerrado.
MARCAS_CERRADAS = ("**pendiente**", "~~(Hecho)~~", "**cadencia**")

sin_arnes = pytest.mark.skipif(
    not agente.disponible(), reason=agente.motivo_no_disponible() or ""
)


def _linea_nueva(corrida: gherkin.Corrida) -> str:
    """La línea que el turno agregó bajo el día de hoy."""
    ahora = (corrida.ruta("mi-vault", "AHORA.md")).read_text(encoding="utf-8")
    dia = ahora.split(DIA, 1)[1].split("\n## ", 1)[0]
    lineas = [x for x in dia.splitlines() if x.startswith("- ")]
    assert len(lineas) == 1, f"se esperaba un registro y hay {len(lineas)}:\n{dia}"
    return lineas[0]


@pytest.mark.agentic
@sin_arnes
def test_003_03_el_registro_queda_en_su_dia_y_a_su_hora() -> None:
    linea = _linea_nueva(gherkin.correr(SLUG, TITULO))
    assert linea.startswith("- 09:12 - "), f"la hora dicha no llegó al registro: {linea}"
    assert "administradora" in linea, f"el cuerpo no dice de qué se trata: {linea}"


@pytest.mark.agentic
@sin_arnes
def test_003_03_llego_por_un_comando_y_no_por_una_edicion() -> None:
    turno = gherkin.correr(SLUG, TITULO).turno
    assert len(turno.invocaciones_de("entry", "add")) == 1, (
        f"un hecho es un `tuku entry add`, y la traza dice: {turno.comandos}"
    )


@pytest.mark.agentic
@sin_arnes
def test_003_03_no_invento_una_consecuencia() -> None:
    """Un hecho que ocurrió y no dejó nada abierto no lleva marca ni abre nada."""
    corrida = gherkin.correr(SLUG, TITULO)
    linea = _linea_nueva(corrida)
    puestas = [m for m in MARCAS_CERRADAS if m in linea]
    assert not puestas, f"marcó {puestas} un hecho que no dejó nada abierto: {linea}"
    abrio = corrida.turno.invocaciones_de("todo", "open")
    assert not abrio, f"abrió un pendiente que nadie pidió: {abrio}"


@pytest.mark.agentic
@sin_arnes
def test_003_03_solo_cambio_la_bitacora() -> None:
    """El delta es el del gemelo determinista, ni más ni menos."""
    corrida = gherkin.correr(SLUG, TITULO)
    assert corrida.delta_de("mi-vault") == DELTA_DE_UN_REGISTRO


if __name__ == "__main__":
    if not agente.disponible():
        print(f"saltado: {agente.motivo_no_disponible()}")
        raise SystemExit(0)
    test_003_03_el_registro_queda_en_su_dia_y_a_su_hora()
    test_003_03_llego_por_un_comando_y_no_por_una_edicion()
    test_003_03_no_invento_una_consecuencia()
    test_003_03_solo_cambio_la_bitacora()
    print("ok: un hecho, un comando, una línea")
