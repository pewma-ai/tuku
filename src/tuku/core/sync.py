"""Sincronización del perfil con los assets del motor instalado.

Implementa `tuku sync` acorde a `docs/deployment.md` §3 y ADR 0002.
"""

from __future__ import annotations

import importlib.resources
from pathlib import Path


def sync_perfil(target_dir: Path) -> dict[str, int]:
    """Sincroniza punteros a procesos y assets de agente del motor instalado hacia el perfil.

    Garantiza descrubibilidad por agentes sin vendorizar código ejecutable (ADR 0002).
    Es idempotente: correrlo múltiples veces produce diff cero si no hay cambios.
    """
    target_dir = target_dir.resolve()
    procesos_dir = target_dir / ".tuku" / "procesos"
    procesos_dir.mkdir(parents=True, exist_ok=True)

    synced_procesos = 0
    synced_agents = 0

    # 1. Sincronizar plantillas de procesos desde site-packages/tuku/procesos/
    try:
        procesos_pkg = importlib.resources.files("tuku").joinpath("procesos")
        if procesos_pkg.is_dir():
            for p_file in procesos_pkg.iterdir():
                if p_file.name.endswith(".md"):
                    content = p_file.read_text(encoding="utf-8")
                    dest_file = procesos_dir / p_file.name
                    needs_update = (
                        not dest_file.exists()
                        or dest_file.read_text(encoding="utf-8") != content
                    )
                    if needs_update:
                        dest_file.write_text(content, encoding="utf-8")
                        synced_procesos += 1
    except (ModuleNotFoundError, TypeError, FileNotFoundError):
        pass

    # 2. Asegurar AGENTS.md raíz si falta
    raiz_agents = target_dir / "AGENTS.md"
    if not raiz_agents.exists():
        raiz_agents.write_text(
            "# TUKU Agent Instructions\n\nEste repositorio es un perfil de TUKU.\n",
            encoding="utf-8",
        )
        synced_agents += 1

    return {"procesos": synced_procesos, "agents": synced_agents}
