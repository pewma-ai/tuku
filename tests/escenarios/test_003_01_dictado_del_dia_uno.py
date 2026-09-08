"""Stub. Escenario en 003-01-dictado-del-dia-uno.md. Falla a propósito."""

from __future__ import annotations

SLUG = "003-01-dictado-del-dia-uno"
PREVIO = None  # corre sobre el fixture `vacio`, no sobre el estado heredado
DESDE = "2026-08-11"
FIXTURE = "fixtures/003-01-dictado-del-dia-uno"

FALTA = (
    "la decisión 3 del epic (arnés de agente y su aislamiento); "
    f"el fixture {FIXTURE}/ (dictado.md y registros.md); "
    "la marca de pytest que lo deja fuera de la corrida por defecto"
)


def test_003_01_el_agente_reproduce_los_registros_congelados() -> None:
    raise AssertionError(f"{SLUG}: sin implementar. Falta {FALTA}.")


if __name__ == "__main__":
    test_003_01_el_agente_reproduce_los_registros_congelados()
