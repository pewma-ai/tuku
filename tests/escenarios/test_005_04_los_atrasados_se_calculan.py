"""Tests del escenario 005-04-los-atrasados-se-calculan.

Estar atrasado se calcula desde la fila y un comando lo informa sin mover nada.

Ejecutable directo: `python3 tests/escenarios/test_005_04_los_atrasados_se_calculan.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import gherkin  # noqa: E402

from tuku.cli import EXITO  # noqa: E402

SLUG = "005-04-los-atrasados-se-calculan"
BASE = "005-01-las-dos-semanas-de-andrea"
CADENA_BASE = (
    "el árbol de Andrea nace con su negocio",
    "la primera semana se registra día por día",
    "la semana se cierra a mano y abre la siguiente",
    "la segunda semana cae sobre lo ya escrito",
)
DICE_QUE_VENCIO = "el comando dice qué venció y deja las filas donde están"
VENCE_HOY = "un pendiente que vence hoy todavía no está atrasado"
REVISION = "revisar la bitácora anterior"
CARTULINA = "recibir el pedido de cartulina de color"


def _correr(titulo: str) -> gherkin.Corrida:
    for previo in CADENA_BASE:
        gherkin.correr(BASE, previo)
    return gherkin.correr(SLUG, titulo)


def test_005_04_el_comando_nombra_lo_que_venció() -> None:
    corrida = _correr(DICE_QUE_VENCIO)
    assert corrida.codigo == EXITO
    salida = corrida.stdout + corrida.stderr
    assert REVISION in salida and "atrasado" in salida


def test_005_04_lo_que_todavia_no_vence_queda_fuera_de_la_lista() -> None:
    salida = _correr(DICE_QUE_VENCIO)
    texto = salida.stdout + salida.stderr
    for pendiente in (
        "fotografiar el mobiliario",
        "ofrecer reposición",
        "decidir si se acepta",
    ):
        assert pendiente not in texto


def test_005_04_informar_el_atraso_deja_las_filas_donde_estan() -> None:
    corrida = _correr(DICE_QUE_VENCIO)
    assert corrida.delta_de("mi-vault") == {}


def test_005_04_vence_hoy_esta_al_dia_y_vence_ayer_esta_atrasado() -> None:
    corrida = _correr(VENCE_HOY)
    lints = [r for r in corrida.resultados if r.comando.endswith("tuku context todo --late")]
    hoy, manana = lints
    assert CARTULINA not in hoy.stdout + hoy.stderr
    assert CARTULINA in manana.stdout + manana.stderr
