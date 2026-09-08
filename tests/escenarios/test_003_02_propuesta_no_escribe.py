"""Stub. Escenario en 003-02-propuesta-no-escribe.md. Falla a propósito."""

from __future__ import annotations

import pytest

SLUG = "003-02-propuesta-no-escribe"
PREVIO = "002-08-crear-nota"

FALTA = (
    "el paso de cadena de tests/scripts/; reglas/propuestas.tuku.md "
    "(la única consecuencia sin comando, a propósito)"
)


@pytest.mark.pendiente
def test_003_02_la_propuesta_espera_y_rechazarla_no_deja_rastro() -> None:
    raise AssertionError(f"{SLUG}: sin implementar. Falta {FALTA}.")


if __name__ == "__main__":
    test_003_02_la_propuesta_espera_y_rechazarla_no_deja_rastro()
