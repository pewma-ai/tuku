"""Test del escenario 002-02-registro-en-su-dia.

Escenario: 002-02-registro-en-su-dia.md

Segundo paso de la cadena del epic 002. Hereda de 002-01-abrir-ciclo, inyecta
tres líneas fuera de orden bajo el día de hoy con tuku entry add y afirma: caen
en su día ordenados por hora, el de las 18:40 no se reescribe, los demás días
siguen vacíos, PENDIENTES.md no se toca, y la línea sin ámbito ni clasificación
queda escrita igual.

Ejecutable directo: python3 tests/escenarios/test_002_02_registro_en_su_dia.py
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

from cadena import correr_cli, delta, instantanea, preparar_paso  # noqa: E402

from tuku.cli import EXITO  # noqa: E402

SLUG = "002-02-registro-en-su-dia"
PREVIO = "002-01-abrir-ciclo"
DESDE = date(2026, 8, 11)
HOY = "## Martes 11 de agosto"

#: Las tres líneas del escenario, en el orden en que se inyectan (no el
#: cronológico). Escritas a mano acá, como los días de test_001_01: son la
#: rebanada mínima que este paso necesita. El día uno completo, generado por
#: un agente desde el corpus, vive en 003-01.
REGISTROS = [
    "- 18:40 - le mandé la boleta de gastos comunes del depto centro a la administradora por WhatsApp",  # noqa: E501
    "- 09:12 - [[personal]] **señal**: la administradora responde los mensajes con varios días de atraso",  # noqa: E501
    "- 11:30 - hice la consulta presencial por el standing desk",
]
ORDEN_ESPERADO = ["09:12", "11:30", "18:40"]


def _sembrar_registros() -> Path:
    vault = preparar_paso(SLUG, previo=PREVIO, desde=DESDE)
    codigo, _, err = correr_cli(
        ["entry", "add", "--vault", str(vault), "--dia", HOY, *REGISTROS]
    )
    assert codigo == EXITO, err
    return vault


def _lineas_del_dia(ahora: str, encabezado: str) -> list[str]:
    lineas = ahora.splitlines()
    ini = lineas.index(encabezado)
    fin = next(
        (i for i in range(ini + 1, len(lineas)) if lineas[i].startswith("## ")),
        len(lineas),
    )
    return [linea for linea in lineas[ini + 1 : fin] if linea.startswith("- ")]


def test_002_02_los_registros_caen_en_su_dia_y_en_orden() -> None:
    ahora = (_sembrar_registros() / "AHORA.md").read_text(encoding="utf-8")

    deldia = _lineas_del_dia(ahora, HOY)
    assert [linea[2:7] for linea in deldia] == ORDEN_ESPERADO, deldia
    assert REGISTROS[0] in deldia, "la línea de las 18:40 no quedó verbatim"

    lineas = ahora.splitlines()
    resto = lineas[lineas.index(HOY) + len(deldia) + 1 :]
    assert [linea for linea in resto if linea.startswith("- ")] == [], "se escribió en otro día"


def test_002_02_la_fase_1_no_toca_pendientes() -> None:
    vault = preparar_paso(SLUG, previo=PREVIO, desde=DESDE)
    antes = instantanea(vault)
    codigo, _, err = correr_cli(
        ["entry", "add", "--vault", str(vault), "--dia", HOY, *REGISTROS]
    )
    assert codigo == EXITO, err
    assert delta(antes, instantanea(vault)) == {"AHORA.md": "modificado"}


def test_002_02_registro_sin_ambito_ni_clasificacion_queda_escrito() -> None:
    ahora = (_sembrar_registros() / "AHORA.md").read_text(encoding="utf-8")
    assert "- 11:30 - hice la consulta presencial por el standing desk" in ahora


if __name__ == "__main__":
    test_002_02_los_registros_caen_en_su_dia_y_en_orden()
    test_002_02_la_fase_1_no_toca_pendientes()
    test_002_02_registro_sin_ambito_ni_clasificacion_queda_escrito()
    print(f"ok: 3 afirmaciones (queda en playground/{SLUG}/)")
