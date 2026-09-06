"""Stub del escenario 002-002-lint-de-entrada.

Escenario: 002-002-lint-de-entrada.md

Tres casos del linter en el mismo paso, y cada uno tiene que fallar por
separado: un tipo abierto desconocido se reporta sin rechazar, una marca
cerrada mal escrita (`**Pendiente**`) se reporta como error y sobre todo **no
abre ningún pendiente**, y una entrada fechada fuera del ciclo abierto se
reporta. El cuarto assert es que el lint no escribe: dos corridas seguidas
dejan diff vacío y reporte idéntico.

Falla a propósito. El escenario está escrito y el mecanismo no existe todavía.
"""

from __future__ import annotations

SLUG = "002-002-lint-de-entrada"
PREVIO = "002-001-entrada-en-su-dia"

FALTA = "el paso de cadena de tests/scripts/; jntr.entrada-lint"


def test_002_002_cerrada_estricta_abierta_permisiva() -> None:
    raise AssertionError(f"{SLUG}: sin implementar. Falta {FALTA}.")


if __name__ == "__main__":
    test_002_002_cerrada_estricta_abierta_permisiva()
