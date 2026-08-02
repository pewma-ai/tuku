"""Pruebas del subcomando de sincronización `tuku sync` (F0.4).

Verifica la sincronización de punteros a procesos e instrucciones AGENTS.md.
"""

from pathlib import Path

from tuku.core.init import init_perfil
from tuku.core.sync import sync_perfil


def test_sync_perfil_es_idempotente(tmp_path: Path) -> None:
    """F0.4: Verifica la idempotencia de tuku sync en múltiples ejecuciones sucesivas."""
    perfil_dir = init_perfil(tmp_path / "mi-tuku")

    # Primera corrida
    res1 = sync_perfil(perfil_dir)
    assert res1["agents"] == 0  # Ya existía por init

    # Segunda corrida sin cambios
    res2 = sync_perfil(perfil_dir)
    assert res2["procesos"] == 0
    assert res2["agents"] == 0
