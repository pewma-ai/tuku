"""Stub del escenario 002-006-transclusiones-sincronizadas.

Escenario: 002-006-transclusiones-sincronizadas.md

Las dos direcciones de falla de la regla 6 de `spec/pendientes.md`, ambas
inyectadas por la segunda vía: se rompe el archivo a mano y se invoca el
janitor, sin pasar por la bitácora.

1. Callout sin transclusión (la silenciosa): se borra la línea de transclusión
   y el janitor la repone. El diff contra el estado heredado vuelve a vacío.
2. Transclusión sin callout (la visible): se agrega un embed a un ancla que no
   existe y el janitor lo quita, sin crear el callout para justificarlo.

El estado final tiene que quedar indistinguible del que dejó 002-005, y eso se
afirma con el diff, no leyendo archivo por archivo.

Falla a propósito. El escenario está escrito y el mecanismo no existe todavía.
"""

from __future__ import annotations

SLUG = "002-006-transclusiones-sincronizadas"
PREVIO = "002-005-escribir-en-un-dia-fecha"
ANCLA_VIVA = "^2026-08-12"
ANCLA_INEXISTENTE = "^2026-08-14"

FALTA = "el paso de cadena de tests/scripts/; jntr.transclusiones-sync"


def test_002_006_las_dos_direcciones_de_falla_se_reparan() -> None:
    raise AssertionError(f"{SLUG}: sin implementar. Falta {FALTA}.")


if __name__ == "__main__":
    test_002_006_las_dos_direcciones_de_falla_se_reparan()
