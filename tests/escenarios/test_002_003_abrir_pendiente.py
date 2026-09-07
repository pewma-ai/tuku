"""Stub. Escenario en 002-003-abrir-pendiente.md. Falla a propósito."""

from __future__ import annotations

SLUG = "002-003-abrir-pendiente"
PREVIO = "002-002-lint-de-registro"
CUERPO = "avisar de los GGCC a la administradora"

FALTA = (
    "resolver la ambigüedad #REVISAR de spec/pendientes.md (hoy: horizonte o fecha); "
    "el paso de cadena de tests/scripts/; jntr.pendiente-abrir"
)


def test_002_003_abrir_copia_el_cuerpo_literal_en_sin_fecha() -> None:
    raise AssertionError(f"{SLUG}: sin implementar. Falta {FALTA}.")


if __name__ == "__main__":
    test_002_003_abrir_copia_el_cuerpo_literal_en_sin_fecha()
