"""Test del escenario 002-001-entrada-en-su-dia.

Escenario: 002-001-entrada-en-su-dia.md

Primer paso de la cadena del epic 002. Instala vanilla con --desde 2026-08-11,
inyecta tres líneas fuera de orden bajo el día de hoy con jntr.entrada-insertar
y afirma: caen en su día ordenadas por hora, la de las 18:40 no se reescribe,
los otros seis días siguen vacíos, PENDIENTES.md no se toca, y la línea sin
ámbito ni clasificación queda escrita igual.

Ejecutable directo: python3 tests/escenarios/test_002_001_entrada_en_su_dia.py
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

from cadena import delta, instantanea, preparar_paso  # noqa: E402

from jntr.entrada_insertar import insertar  # noqa: E402

SLUG = "002-001-entrada-en-su-dia"
PREVIO = None
DESDE = date(2026, 8, 11)
HOY = "## Martes 11 de agosto"

#: Las tres líneas del escenario, en el orden en que se inyectan (no el
#: cronológico). Escritas a mano acá, como los días de test_001_001: son la
#: rebanada mínima que este paso necesita. El día uno completo, generado por
#: un agente desde el corpus, vive en 002-010.
ENTRADAS = [
    "- 18:40 - le mandé la boleta de gastos comunes del depto centro a la administradora por WhatsApp",  # noqa: E501
    "- 09:12 - [[personal]] **señal**: la administradora responde los mensajes con varios días de atraso",  # noqa: E501
    "- 11:30 - hice la consulta presencial por el standing desk",
]
ORDEN_ESPERADO = ["09:12", "11:30", "18:40"]


def _sembrar_entradas() -> Path:
    vault = preparar_paso(SLUG, previo=PREVIO, desde=DESDE)
    ahora = vault / "AHORA.md"
    ahora.write_text(
        insertar(ahora.read_text(encoding="utf-8"), ENTRADAS, dia=HOY),
        encoding="utf-8",
    )
    return vault


def _lineas_del_dia(ahora: str, encabezado: str) -> list[str]:
    lineas = ahora.splitlines()
    ini = lineas.index(encabezado)
    fin = next(
        (i for i in range(ini + 1, len(lineas)) if lineas[i].startswith("## ")),
        len(lineas),
    )
    return [linea for linea in lineas[ini + 1 : fin] if linea.startswith("- ")]


def test_002_001_las_entradas_caen_en_su_dia_y_en_orden() -> None:
    ahora = (_sembrar_entradas() / "AHORA.md").read_text(encoding="utf-8")

    deldia = _lineas_del_dia(ahora, HOY)
    assert [linea[2:7] for linea in deldia] == ORDEN_ESPERADO, deldia
    assert ENTRADAS[0] in deldia, "la línea de las 18:40 no quedó verbatim"

    lineas = ahora.splitlines()
    resto = lineas[lineas.index(HOY) + len(deldia) + 1 :]
    assert [linea for linea in resto if linea.startswith("- ")] == [], "se escribió en otro día"


def test_002_001_la_fase_1_no_toca_pendientes() -> None:
    vault = preparar_paso(SLUG, previo=PREVIO, desde=DESDE)
    antes = instantanea(vault)
    ahora = vault / "AHORA.md"
    ahora.write_text(
        insertar(ahora.read_text(encoding="utf-8"), ENTRADAS, dia=HOY),
        encoding="utf-8",
    )
    assert delta(antes, instantanea(vault)) == {"AHORA.md": "modificado"}


def test_002_001_entrada_sin_ambito_ni_clasificacion_queda_escrita() -> None:
    ahora = (_sembrar_entradas() / "AHORA.md").read_text(encoding="utf-8")
    assert "- 11:30 - hice la consulta presencial por el standing desk" in ahora


if __name__ == "__main__":
    test_002_001_las_entradas_caen_en_su_dia_y_en_orden()
    test_002_001_la_fase_1_no_toca_pendientes()
    test_002_001_entrada_sin_ambito_ni_clasificacion_queda_escrita()
    print(f"ok: 3 afirmaciones (queda en playground/{SLUG}/)")
