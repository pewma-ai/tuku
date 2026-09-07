"""Stub. Escenario en 002-002-lint-de-registro.md. Falla a propósito."""

from __future__ import annotations

SLUG = "002-002-lint-de-registro"
PREVIO = "002-001-registro-en-su-dia"

FALTA = "el paso de cadena de tests/scripts/; tuku entry lint"


def test_002_002_cerrada_estricta_abierta_permisiva() -> None:
    raise AssertionError(f"{SLUG}: sin implementar. Falta {FALTA}.")


if __name__ == "__main__":
    test_002_002_cerrada_estricta_abierta_permisiva()
