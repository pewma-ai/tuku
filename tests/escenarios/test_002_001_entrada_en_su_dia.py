"""Stub del escenario 002-001-entrada-en-su-dia.

Escenario: 002-001-entrada-en-su-dia.md

Primer paso de la cadena del epic 002. Instala el fixture `vacio` con
`--desde 2026-08-11` (el mismo estado con que cerró el epic 001), inyecta tres
entradas fuera de orden y afirma tres cosas: caen en el día de hoy, quedan
ordenadas por hora, y el diff contra el estado inicial toca `AHORA.md` y nada
más. Esa última es el criterio de corte de la fase 1.

Falla a propósito. El escenario está escrito y el mecanismo no existe todavía.
"""

from __future__ import annotations

SLUG = "002-001-entrada-en-su-dia"
PREVIO = None  # arranca del fixture `vacio`, no de otro paso
DESDE = "2026-08-11"
HOY = "2026-08-11"

FALTA = (
    "el paso de cadena de tests/scripts/ (heredar el estado del paso previo a "
    "playground/<slug>/ y comparar el delta entre dos estados); "
    "el fixture fixtures/002-010-dictado-del-dia-uno/entradas.md; "
    "jntr.entrada-insertar"
)


def test_002_001_las_entradas_caen_en_su_dia_y_en_orden() -> None:
    raise AssertionError(f"{SLUG}: sin implementar. Falta {FALTA}.")


if __name__ == "__main__":
    test_002_001_las_entradas_caen_en_su_dia_y_en_orden()
