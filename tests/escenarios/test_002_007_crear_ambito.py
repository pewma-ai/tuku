"""Stub. Escenario en 002-007-crear-ambito.md. Falla a propósito."""

from __future__ import annotations

SLUG = "002-007-crear-ambito"
PREVIO = "002-006-transclusiones-sincronizadas"
AMBITO = "depto-centro"
CATEGORIA = "depto-centro/gastos"
MENCION_SUELTA = "del depto centro"

FALTA = (
    "el paso de cadena de tests/scripts/; jntr.ambito-crear; "
    "jntr.menciones-enlazar; jntr.ambitos-lint"
)


def test_002_007_crear_ambito_deja_el_arbol_correcto_y_enlaza_hacia_atras() -> None:
    raise AssertionError(f"{SLUG}: sin implementar. Falta {FALTA}.")


if __name__ == "__main__":
    test_002_007_crear_ambito_deja_el_arbol_correcto_y_enlaza_hacia_atras()
