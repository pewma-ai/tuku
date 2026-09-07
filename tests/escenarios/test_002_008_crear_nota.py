"""Stub. Escenario en 002-008-crear-nota.md. Falla a propósito."""

from __future__ import annotations

SLUG = "002-008-crear-nota"
PREVIO = "002-007-crear-ambito"
NOTA = "notas/gastos-comunes-en-copropiedad.md"
AMBITO = "depto-centro"

FALTA = (
    "la consecuencia 'nota' en spec/flujo-informacion.md y su reglas/notas.tuku.md; "
    "el paso de cadena de tests/scripts/; tuku note lint"
)


def test_002_008_la_nota_queda_escrita_enlazada_y_con_constancia() -> None:
    raise AssertionError(f"{SLUG}: sin implementar. Falta {FALTA}.")


if __name__ == "__main__":
    test_002_008_la_nota_queda_escrita_enlazada_y_con_constancia()
