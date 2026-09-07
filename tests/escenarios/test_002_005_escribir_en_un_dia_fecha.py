"""Stub. Escenario en 002-005-escribir-en-un-dia-fecha.md. Falla a propósito."""

from __future__ import annotations

SLUG = "002-005-escribir-en-un-dia-fecha"
PREVIO = "002-004-cerrar-pendiente"
DIA_FUTURO = "2026-08-12"
ANCLA = "^2026-08-12"
CUERPO = "pagar la sesión con el psicólogo"

FALTA = (
    "el paso de cadena de tests/scripts/; tuku todo open con fecha desde el día; "
    "tuku transclusion sync; tuku todo lint"
)


def test_002_005_escribir_en_un_dia_futuro_fecha_el_pendiente() -> None:
    raise AssertionError(f"{SLUG}: sin implementar. Falta {FALTA}.")


if __name__ == "__main__":
    test_002_005_escribir_en_un_dia_futuro_fecha_el_pendiente()
