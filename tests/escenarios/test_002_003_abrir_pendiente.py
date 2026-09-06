"""Stub del escenario 002-003-abrir-pendiente.

Escenario: 002-003-abrir-pendiente.md

Una entrada `**pendiente**` deja el ítem en `^sin-fecha` con el cuerpo copiado
literal, sin fecha en el ítem, y el diff toca `AHORA.md` y `PENDIENTES.md` y
nada más. Los cinco horizontes permanentes siguen existiendo aunque estén
vacíos, y correr el janitor dos veces da diff vacío.

**Bloqueado por una ambigüedad de `spec/`**, marcada con `#REVISAR` en el
escenario: `spec/pendientes.md` dice a la vez que un dictado de hoy cae en
`^sin-fecha` (su ejemplo) y que escribir en el día de hoy fecha el pendiente
(su regla). Este test afirma `^sin-fecha`. Si la spec se resuelve al revés,
este escenario cambia y el epic 002 se queda sin ninguna vía de entrada a
`^sin-fecha`.

Falla a propósito. El escenario está escrito y el mecanismo no existe todavía.
"""

from __future__ import annotations

SLUG = "002-003-abrir-pendiente"
PREVIO = "002-002-lint-de-entrada"
CUERPO = "avisar de los GGCC a la administradora"

FALTA = (
    "resolver la ambigüedad #REVISAR de spec/pendientes.md (hoy: horizonte o fecha); "
    "el paso de cadena de tests/scripts/; jntr.pendiente-abrir"
)


def test_002_003_abrir_copia_el_cuerpo_literal_en_sin_fecha() -> None:
    raise AssertionError(f"{SLUG}: sin implementar. Falta {FALTA}.")


if __name__ == "__main__":
    test_002_003_abrir_copia_el_cuerpo_literal_en_sin_fecha()
