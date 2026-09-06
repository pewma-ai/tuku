"""Stub del escenario 002-005-escribir-en-un-dia-fecha.

Escenario: 002-005-escribir-en-un-dia-fecha.md

El punto 3 del epic, y el escenario que más diseño ejercita. Escribir un
`**pendiente**` bajo un día futuro de `AHORA.md` hace nacer el callout de
fecha `^2026-08-12`, lo transcluye al inicio de ese día, y el pendiente no
queda además en `^sin-fecha` ni en ningún horizonte: fechar mueve, nunca
copia. Los cinco horizontes permanentes no se desplazan, el movimiento de
escalón no deja entrada en la bitácora, y la segunda corrida da diff vacío.

Falla a propósito. El escenario está escrito y el mecanismo no existe todavía.
"""

from __future__ import annotations

SLUG = "002-005-escribir-en-un-dia-fecha"
PREVIO = "002-004-cerrar-pendiente"
DIA_FUTURO = "2026-08-12"
ANCLA = "^2026-08-12"
CUERPO = "pagar la sesión con el psicólogo"

FALTA = (
    "el paso de cadena de tests/scripts/; jntr.pendiente-abrir con fecha desde el día; "
    "jntr.transclusiones-sync; jntr.pendientes-lint"
)


def test_002_005_escribir_en_un_dia_futuro_fecha_el_pendiente() -> None:
    raise AssertionError(f"{SLUG}: sin implementar. Falta {FALTA}.")


if __name__ == "__main__":
    test_002_005_escribir_en_un_dia_futuro_fecha_el_pendiente()
