"""Stub. Escenario en 002-001-entrada-en-su-dia.md. Falla a propósito."""

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
