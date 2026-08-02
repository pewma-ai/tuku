"""Diagnóstico de perfil y motor `tuku doctor`.

Implementa las verificaciones descritas en `docs/deployment.md` §2.3.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from tuku.core.config import ConfigError, ProfileConfig


def get_git_info(cwd: Path) -> tuple[str, str, str]:
    """Retorna (version/tag, commit_hash, branch) del repositorio Git.

    Si no se está en un repo Git o falla la consulta, retorna valores por defecto.
    """
    devnull = subprocess.DEVNULL
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=cwd, text=True, stderr=devnull
        ).strip()
    except Exception:
        commit = "unknown"

    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd, text=True, stderr=devnull
        ).strip()
    except Exception:
        branch = "unknown"

    try:
        version = subprocess.check_output(
            ["git", "describe", "--tags", "--always"], cwd=cwd, text=True, stderr=devnull
        ).strip()
    except Exception:
        version = commit

    return version, commit, branch


@dataclass
class DoctorResult:
    version: str
    commit: str
    branch: str
    profile_path: Path
    valid_config: bool
    schema_version: int | None = None
    issues: list[str] = field(default_factory=list)


def run_doctor(profile_dir: Path) -> DoctorResult:
    """Ejecuta diagnósticos sobre el perfil indicado y reporta su salud."""
    profile_dir = profile_dir.resolve()
    version, commit, branch = get_git_info(profile_dir)

    issues: list[str] = []
    config_path = profile_dir / ".tuku" / "config.yaml"
    schema_version: int | None = None
    valid_config = False

    if not config_path.exists():
        issues.append(f"Falta archivo de configuración: {config_path}")
    else:
        try:
            cfg = ProfileConfig.from_yaml(config_path)
            schema_version = cfg.schema_version
            valid_config = True
        except ConfigError as err:
            issues.append(f"Error de configuración: {err}")

    # Verificar existencia de archivos canónicos mínimos
    canónicos = [
        profile_dir / "entradas" / "entradas.md",
        profile_dir / "tareas" / "tareas.md",
        profile_dir / "estrategia" / "capacidad.md",
    ]
    for p in canónicos:
        if not p.exists():
            issues.append(f"Falta archivo canónico: {p.relative_to(profile_dir)}")

    return DoctorResult(
        version=version,
        commit=commit,
        branch=branch,
        profile_path=profile_dir,
        valid_config=valid_config,
        schema_version=schema_version,
        issues=issues,
    )
