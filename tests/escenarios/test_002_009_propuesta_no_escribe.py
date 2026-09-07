"""Stub. Escenario en 002-009-propuesta-no-escribe.md. Falla a propósito."""

from __future__ import annotations

SLUG = "002-009-propuesta-no-escribe"
PREVIO = "002-008-crear-nota"

FALTA = (
    "el paso de cadena de tests/scripts/; reglas/propuestas.tuku.md "
    "(la única consecuencia sin janitor, a propósito)"
)


def test_002_009_la_propuesta_espera_y_rechazarla_no_deja_rastro() -> None:
    raise AssertionError(f"{SLUG}: sin implementar. Falta {FALTA}.")


if __name__ == "__main__":
    test_002_009_la_propuesta_espera_y_rechazarla_no_deja_rastro()
