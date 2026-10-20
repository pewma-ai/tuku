"""El criterio del evaluador: la lectura del veredicto y el prompt, sin llamar a Claude."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))

import criterio


def test_un_nivel_razonable_o_discutible_pasa_y_uno_inaceptable_no() -> None:
    assert criterio.leer_veredicto("NIVEL: RAZONABLE\nRAZÓN: otro orden.").pasa
    v = criterio.leer_veredicto("NIVEL: DISCUTIBLE\nRAZÓN: preguntó de más.")
    assert v.pasa and v.razon == "preguntó de más."
    assert not criterio.leer_veredicto("NIVEL: INACEPTABLE\nRAZÓN: editó a mano.").pasa


def test_lo_que_el_evaluador_no_dijo_con_claridad_es_inaceptable() -> None:
    assert not criterio.leer_veredicto("Creo que está bien.").pasa


def test_el_prompt_lleva_el_escenario_la_falla_y_lo_que_quedo() -> None:
    p = criterio.armar_prompt("ESCENARIO", "FALLA", "ESTADO")
    assert all(x in p for x in ("ESCENARIO", "FALLA", "ESTADO", "RAZONABLE", "INACEPTABLE"))
    assert "PermissionError" in p and "olvida eso" in p, "falta la guía de ejemplos"


def test_el_escenario_sale_de_la_linea_del_modulo() -> None:
    slug, texto = criterio.escenario_de(
        '"""Tests.\n\nEscenario: 004-01-el-dia-conversado.md\n"""'
    )
    assert slug == "004-01-el-dia-conversado" and texto.startswith("# 004-01")
