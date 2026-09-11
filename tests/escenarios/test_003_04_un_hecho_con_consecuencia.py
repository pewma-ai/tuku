"""Tests del escenario 003-04-un-hecho-con-consecuencia.

Escenario: 003-04-un-hecho-con-consecuencia.md

El escenario central del epic: dictado con compromiso pendiente. Se compila en
un solo `tuku entry add` con marca `**pendiente**`, estampando el registro en
`AHORA.md` y abriendo el pendiente en `PENDIENTES.md` de forma atómica.

Gemelo determinista: `002-04-abrir-pendiente`.

Ejecutable directo: `python3 tests/escenarios/test_003_04_un_hecho_con_consecuencia.py`
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

SLUG = "003-04-un-hecho-con-consecuencia"
TITULO = "lo que queda por hacer"
DIA = "## Martes 11 de agosto"

DELTA_DE_ABRIR = {
    "AHORA.md": "modificado",
    "PENDIENTES.md": "modificado",
    "ambitos/PENDIENTES-AMBITOS.md": "modificado",
    "ambitos/personal/personal.md": "modificado",
}

sin_arnes = pytest.mark.skipif(
    not agente.disponible(), reason=agente.motivo_no_disponible() or ""
)


def _registro_pendiente(corrida: gherkin.Corrida) -> str:
    ahora = corrida.ruta("mi-vault", "AHORA.md").read_text(encoding="utf-8")
    dia = ahora.split(DIA, 1)[1].split("\n## ", 1)[0]
    marcados = [x for x in dia.splitlines() if x.startswith("- 14:20 ")]
    assert len(marcados) == 1, f"un registro a las 14:20, y hay {len(marcados)}:\n{dia}"
    return marcados[0]


@pytest.mark.agentic
@sin_arnes
def test_003_04_la_traduccion_es_un_solo_comando() -> None:
    """Un dictado con compromiso produce un único entry add."""
    turno = gherkin.correr(SLUG, TITULO).turno
    assert turno.traduccion == ["entry add"], f"la traza dice: {turno.comandos}"


@pytest.mark.agentic
@sin_arnes
def test_003_04_el_registro_lleva_la_marca_de_lo_que_queda_abierto() -> None:
    linea = _registro_pendiente(gherkin.correr(SLUG, TITULO))
    assert todo.ABRE in linea, f"un hecho que deja algo por hacer lleva {todo.ABRE}: {linea}"


@pytest.mark.agentic
@sin_arnes
def test_003_04_la_fila_repite_el_cuerpo_del_registro() -> None:
    """El mismo texto en los dos sitios para permitir su cierre posterior."""
    corrida = gherkin.correr(SLUG, TITULO)
    marca = todo.parsear(_registro_pendiente(corrida))
    assert marca is not None, "el registro no tiene una marca que el comando reconozca"

    pendientes = corrida.ruta("mi-vault", "PENDIENTES.md").read_text(encoding="utf-8")
    assert todo.cuerpos(pendientes) == [marca.cuerpo], (
        f"la tabla no repite el cuerpo del registro:\n{pendientes}"
    )


@pytest.mark.agentic
@sin_arnes
def test_003_04_la_fila_entra_en_el_escalon_del_ciclo_en_curso() -> None:
    """El horizonte corresponde a la escalera de configuración del vault."""
    corrida = gherkin.correr(SLUG, TITULO)
    from tuku.config import leer_config

    escalera = todo.escalera_de(leer_config(corrida.ruta("mi-vault")).horizontes)
    pendientes = corrida.ruta("mi-vault", "PENDIENTES.md").read_text(encoding="utf-8")
    assert [f.horizonte for f in todo.filas(pendientes)] == [escalera[0]]


@pytest.mark.agentic
@sin_arnes
def test_003_04_no_quedo_ninguna_marca_sin_su_consecuencia() -> None:
    """No debe quedar ningún registro marcado sin su fila en PENDIENTES.md."""
    corrida = gherkin.correr(SLUG, TITULO)
    vault = corrida.ruta("mi-vault")
    faltan = todo.sin_consecuencia(
        (vault / "AHORA.md").read_text(encoding="utf-8"),
        (vault / "PENDIENTES.md").read_text(encoding="utf-8"),
    )
    assert faltan == [], (
        f"el agente escribió la marca y no aplicó su consecuencia: {faltan}. "
        f"Ejecutó: {corrida.turno.comandos}"
    )


@pytest.mark.agentic
@sin_arnes
def test_003_04_el_delta_es_el_del_gemelo() -> None:
    assert gherkin.correr(SLUG, TITULO).delta_de("mi-vault") == DELTA_DE_ABRIR


if __name__ == "__main__":
    if not agente.disponible():
        print(f"saltado: {agente.motivo_no_disponible()}")
        raise SystemExit(0)
    test_003_04_la_traduccion_es_un_solo_comando()
    test_003_04_el_registro_lleva_la_marca_de_lo_que_queda_abierto()
    test_003_04_la_fila_repite_el_cuerpo_del_registro()
    test_003_04_la_fila_entra_en_el_escalon_del_ciclo_en_curso()
    test_003_04_no_quedo_ninguna_marca_sin_su_consecuencia()
    test_003_04_el_delta_es_el_del_gemelo()
    print(f"ok: 6 afirmaciones (queda en playground/{SLUG}/)")
