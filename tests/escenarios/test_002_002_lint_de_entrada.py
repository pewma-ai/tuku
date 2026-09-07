"""Stub. Escenario en 002-002-lint-de-entrada.md. Falla a propósito."""

from __future__ import annotations

SLUG = "002-002-lint-de-entrada"
PREVIO = "002-001-entrada-en-su-dia"

FALTA = "el paso de cadena de tests/scripts/; jntr.entrada-lint"


def test_002_002_cerrada_estricta_abierta_permisiva() -> None:
    raise AssertionError(f"{SLUG}: sin implementar. Falta {FALTA}.")


if __name__ == "__main__":
    test_002_002_cerrada_estricta_abierta_permisiva()
