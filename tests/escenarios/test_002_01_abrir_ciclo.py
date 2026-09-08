"""Tests del escenario 002-01-abrir-ciclo.

Escenario: 002-01-abrir-ciclo.md

Primer paso de la cadena del epic 002. `AHORA.md` no se genera por código
rígido: se instancia desde la plantilla editable en `reglas/plantilla/AHORA.md`.
`tuku cycle open` verifica si hay un ciclo que cubra la fecha y lo crea con su
semana completa si falta.

Los comandos salen del `.md`, que es la fuente ejecutable. El runner ejecuta el
`## Estado inicial` del archivo antes de cada escenario, toma la instantánea del
vault justo antes del primer `Cuando`, y `corrida.delta` dice qué cambió: el
assert es el diff entre dos estados, como pide el README de escenarios.

Ejecutable directo: `python3 tests/escenarios/test_002_01_abrir_ciclo.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import gherkin  # noqa: E402
from vault import placeholders_sin_sustituir  # noqa: E402

from tuku.cli import EXITO  # noqa: E402

SLUG = "002-01-abrir-ciclo"

DIAS = [
    "## Lunes 10 de agosto",
    "## Martes 11 de agosto",
    "## Miércoles 12 de agosto",
    "## Jueves 13 de agosto",
    "## Viernes 14 de agosto",
    "## Sábado 15 de agosto",
    "## Domingo 16 de agosto",
]


def test_002_01_crea_ahora_desde_plantilla_si_no_existe() -> None:
    corrida = gherkin.correr(SLUG, "crear AHORA.md a partir de la plantilla cuando no existe")
    assert corrida.codigo == EXITO, corrida.stderr
    assert corrida.delta_de("mi-vault") == {"AHORA.md": "nuevo"}, corrida.delta

    vault = corrida.ruta("mi-vault")
    texto = (vault / "AHORA.md").read_text(encoding="utf-8")
    assert "from: 2026-08-10" in texto
    assert "to: 2026-08-16" in texto
    for dia in DIAS:
        assert dia in texto, f"falta {dia} en el ciclo abierto"
    assert not placeholders_sin_sustituir(vault), "quedaron placeholders en el vault"


def test_002_01_idempotente_si_ahora_ya_cubre_la_fecha() -> None:
    corrida = gherkin.correr(SLUG, "sin modificarlo (idempotencia)")
    assert corrida.codigo == EXITO, corrida.stderr
    assert corrida.delta_de("mi-vault") == {}, "modificó AHORA.md cuando ya cubría la fecha"


if __name__ == "__main__":
    test_002_01_crea_ahora_desde_plantilla_si_no_existe()
    test_002_01_idempotente_si_ahora_ya_cubre_la_fecha()
    print(f"ok: 2 afirmaciones (queda en playground/{SLUG}/)")
