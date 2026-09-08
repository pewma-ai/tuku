"""Tests del escenario 002-02-registro-en-su-dia.

Escenario: 002-02-registro-en-su-dia.md

Segundo paso de la cadena, punto 1 del epic: el registro queda en el día
correcto y en orden cronológico, aunque llegue desordenado.

Los comandos y las tres líneas de registro salen del `.md`, que es la fuente
ejecutable, incluida la copia del estado que dejó `002-01`. Este arnés afirma
sobre lo que quedó.

El criterio de corte de la fase 1 es el delta: si algo escribe en
`PENDIENTES.md`, el corte está mal hecho.

Ejecutable directo: `python3 tests/escenarios/test_002_02_registro_en_su_dia.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import gherkin  # noqa: E402

from tuku.cli import EXITO  # noqa: E402

SLUG = "002-02-registro-en-su-dia"
HOY = "## Martes 11 de agosto"
ORDEN_ESPERADO = ["09:12", "11:30", "18:40"]
LINEA_1840 = (
    "- 18:40 - le mandé la boleta de gastos comunes del depto centro "
    "a la administradora por WhatsApp"
)
LINEA_1130 = "- 11:30 - hice la consulta presencial por el standing desk"


def _lineas_del_dia(ahora: str, encabezado: str) -> list[str]:
    lineas = ahora.splitlines()
    ini = lineas.index(encabezado)
    fin = next(
        (i for i in range(ini + 1, len(lineas)) if lineas[i].startswith("## ")),
        len(lineas),
    )
    return [linea for linea in lineas[ini + 1 : fin] if linea.startswith("- ")]


def test_002_02_los_registros_caen_en_su_dia_y_en_orden() -> None:
    corrida = gherkin.correr(SLUG, "tres registros caen en el día de hoy")
    assert corrida.codigo == EXITO, corrida.stderr

    ahora = corrida.ruta("mi-vault", "AHORA.md").read_text(encoding="utf-8")
    deldia = _lineas_del_dia(ahora, HOY)
    assert [linea[2:7] for linea in deldia] == ORDEN_ESPERADO, deldia
    assert LINEA_1840 in deldia, "la línea de las 18:40 no quedó verbatim"

    lineas = ahora.splitlines()
    resto = lineas[lineas.index(HOY) + len(deldia) + 1 :]
    assert [linea for linea in resto if linea.startswith("- ")] == [], "se escribió en otro día"


def test_002_02_la_fase_1_no_toca_pendientes() -> None:
    corrida = gherkin.correr(SLUG, "no toca PENDIENTES.md")
    assert corrida.codigo == EXITO, corrida.stderr
    assert corrida.delta_de("mi-vault") == {
        "AHORA.md": "modificado",
        "ambitos/personal/personal.md": "modificado",
    }

    personal = corrida.ruta("mi-vault", "ambitos", "personal", "personal.md").read_text(
        encoding="utf-8"
    )
    assert "## Esta semana" in personal
    assert (
        "- **señal**: la administradora responde los mensajes con varios días de atraso"
        in personal
    )
    assert "[[personal]]" not in personal
    assert "- 09:12 - " not in personal


def test_002_02_registro_sin_ambito_ni_clasificacion_queda_escrito() -> None:
    corrida = gherkin.correr(SLUG, "sin ámbito y sin clasificación es válido")
    assert corrida.codigo == EXITO, corrida.stderr

    ahora = corrida.ruta("mi-vault", "AHORA.md").read_text(encoding="utf-8")
    assert LINEA_1130 in ahora


if __name__ == "__main__":
    test_002_02_los_registros_caen_en_su_dia_y_en_orden()
    test_002_02_la_fase_1_no_toca_pendientes()
    test_002_02_registro_sin_ambito_ni_clasificacion_queda_escrito()
    print(f"ok: 3 afirmaciones (queda en playground/{SLUG}/)")
