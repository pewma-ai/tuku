"""Stub. Escenario en 002-004-cerrar-pendiente.md. Falla a propósito."""

from __future__ import annotations

SLUG = "002-004-cerrar-pendiente"
PREVIO = "002-003-abrir-pendiente"
CUERPO_ABIERTO = "avisar de los GGCC a la administradora"
CUERPO_SIN_PAREJA = "comprar una maleta"

FALTA = "el paso de cadena de tests/scripts/; jntr.pendiente-cerrar; jntr.pendientes-lint"


def test_002_004_cerrar_borra_el_item_y_el_cierre_sin_pareja_se_reporta() -> None:
    raise AssertionError(f"{SLUG}: sin implementar. Falta {FALTA}.")


if __name__ == "__main__":
    test_002_004_cerrar_borra_el_item_y_el_cierre_sin_pareja_se_reporta()
