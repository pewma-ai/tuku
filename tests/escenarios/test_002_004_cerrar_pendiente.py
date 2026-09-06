"""Stub del escenario 002-004-cerrar-pendiente.

Escenario: 002-004-cerrar-pendiente.md

Dos afirmaciones y la segunda es la que importa. La primera: `~~(Hecho)~~` con
el mismo cuerpo borra el ítem del callout donde esté, dejando el callout vacío
en pie. La segunda: un cierre que no empareja con ningún pendiente abierto se
**reporta**, deja `PENDIENTES.md` byte a byte igual, no inventa el pendiente
que falta y no borra ningún otro ítem. La línea queda escrita, porque un error
del autor se reporta y nunca se rechaza.

Ese caso negativo es el que el vault real del autor rompía (lección 4 de
`devel/lecciones-macjpgil.md`), y con `PENDIENTES.md` como fuente de verdad
cuesta más caro que allá.

Falla a propósito. El escenario está escrito y el mecanismo no existe todavía.
"""

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
