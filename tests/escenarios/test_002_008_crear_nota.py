"""Stub del escenario 002-008-crear-nota.

Escenario: 002-008-crear-nota.md

Fase 5 en versión mínima. La nota pedida queda escrita con `created` en su
frontmatter, deja una entrada de constancia en la bitácora que enlaza a ella,
queda enlazada a su ámbito porque la petición lo nombró, y pasa el lint de
"Ver además" (presencia de la sección y de texto de motivo tras cada enlace).
Repetir la operación da diff vacío y no duplica la entrada de constancia.

**Este escenario mueve la spec.** La consecuencia "nota" no existe en la tabla
de `spec/flujo-informacion.md`, y el punto 5 del epic la exige. Antes de
implementar el test hay que agregar `reglas/notas.tuku.md` y su fila, que es
la primera cosa que el epic 002 cambia en el diseño.

Falla a propósito. El escenario está escrito y el mecanismo no existe todavía.
"""

from __future__ import annotations

SLUG = "002-008-crear-nota"
PREVIO = "002-007-crear-ambito"
NOTA = "notas/gastos-comunes-en-copropiedad.md"
AMBITO = "depto-centro"

FALTA = (
    "la consecuencia 'nota' en spec/flujo-informacion.md y su reglas/notas.tuku.md; "
    "el paso de cadena de tests/scripts/; jntr.notas-lint"
)


def test_002_008_la_nota_queda_escrita_enlazada_y_con_constancia() -> None:
    raise AssertionError(f"{SLUG}: sin implementar. Falta {FALTA}.")


if __name__ == "__main__":
    test_002_008_la_nota_queda_escrita_enlazada_y_con_constancia()
