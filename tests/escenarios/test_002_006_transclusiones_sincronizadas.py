"""Stub. Escenario en 002-006-transclusiones-sincronizadas.md. Falla a propósito."""

from __future__ import annotations

SLUG = "002-006-transclusiones-sincronizadas"
PREVIO = "002-005-escribir-en-un-dia-fecha"
ANCLA_VIVA = "^2026-08-12"
ANCLA_INEXISTENTE = "^2026-08-14"

FALTA = "el paso de cadena de tests/scripts/; tuku transclusion sync"


def test_002_006_las_dos_direcciones_de_falla_se_reparan() -> None:
    raise AssertionError(f"{SLUG}: sin implementar. Falta {FALTA}.")


if __name__ == "__main__":
    test_002_006_las_dos_direcciones_de_falla_se_reparan()
