"""Stub del escenario 002-007-crear-ambito.

Escenario: 002-007-crear-ambito.md

Fase 3 en versión mínima. Crear `depto-centro` deja el directorio con sus dos
archivos obligatorios y su página propia (que es lo que lo hace ámbito y no
categoría), no toca `ambitos/personal/` y no crea ningún `CAPACIDAD.md`. El
enlazado retroactivo convierte la mención suelta que 002-001 dejó escrita en
el martes 11, sin reescribir el resto de la línea, y no sale de `AHORA.md`.

Segundo caso, negativo: un directorio sin página propia es categoría, y una
entrada que le apunta se reporta sin rechazarse.

Falla a propósito. El escenario está escrito y el mecanismo no existe todavía.
"""

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
