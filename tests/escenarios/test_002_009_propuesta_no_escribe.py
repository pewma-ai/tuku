"""Stub del escenario 002-009-propuesta-no-escribe.

Escenario: 002-009-propuesta-no-escribe.md

El principio 3 convertido en test, y el último paso determinista de la cadena:
su estado final es el que se revisa contra el criterio de salida del epic.

La entrada se registra, lo que sugiere se propone, y el diff contra el estado
anterior es exactamente esa línea de `AHORA.md`: `PENDIENTES.md`, `ambitos/` y
`notas/` quedan byte a byte iguales. Rechazar la propuesta da diff vacío.
Aprobarla abre el pendiente como en 002-003, y el test revierte esa rama para
que el estado heredado sea el del rechazo, que es como termina el día uno del
corpus.

Falla a propósito. El escenario está escrito y el mecanismo no existe todavía.
"""

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
