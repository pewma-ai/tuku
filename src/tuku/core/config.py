"""Configuración del perfil y lectura de `.tuku/config.yaml`.

Implementa las reglas de `spec/perfil.md` y ADR 0003 (versionado de esquema).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

# Rango de versiones de esquema soportadas por esta versión del motor.
SCHEMA_VERSION_MIN = 0
SCHEMA_VERSION_MAX = 0


class ConfigError(Exception):
    """Error al cargar o validar la configuración del perfil."""


@dataclass
class DerivationConfig:
    target: str
    sources: list[str]
    build: str
    filter: str | None = None


@dataclass
class ProfileConfig:
    schema_version: int
    profile_name: str = "personal"
    clasificaciones: list[str] = field(
        default_factory=lambda: ["hito", "decision", "senal", "msg"]
    )
    task_archive_delay: str = "7d"
    derivations: list[DerivationConfig] = field(default_factory=list)

    @classmethod
    def from_yaml(cls, path: Path) -> ProfileConfig:
        if not path.exists():
            raise ConfigError(f"Archivo de configuración no encontrado: {path}")

        try:
            content = path.read_text(encoding="utf-8")
            data: dict[str, Any] = yaml.safe_load(content) or {}
        except Exception as err:
            raise ConfigError(f"Error al leer YAML en {path}: {err}") from err

        if "schema_version" not in data:
            raise ConfigError(f"Falta 'schema_version' obligatorio en {path}")

        schema_ver = data["schema_version"]
        if not isinstance(schema_ver, int) or isinstance(schema_ver, bool):
            raise ConfigError(
                f"'schema_version' debe ser un entero no negativo, recibido: {schema_ver!r}"
            )

        if schema_ver < SCHEMA_VERSION_MIN or schema_ver > SCHEMA_VERSION_MAX:
            raise ConfigError(
                f"Versión de esquema {schema_ver} fuera de rango soportado "
                f"({SCHEMA_VERSION_MIN}-{SCHEMA_VERSION_MAX}). "
                "Ejecute 'tuku doctor' o 'tuku migrate'."
            )

        derivations_data = data.get("derivations", [])
        derivations: list[DerivationConfig] = []
        for d in derivations_data:
            if isinstance(d, dict) and "target" in d and "sources" in d and "build" in d:
                derivations.append(
                    DerivationConfig(
                        target=str(d["target"]),
                        sources=[str(s) for s in d["sources"]],
                        build=str(d["build"]),
                        filter=str(d["filter"]) if "filter" in d else None,
                    )
                )

        clasificaciones_default = ["hito", "decision", "senal", "msg"]
        clasificaciones = [
            str(c) for c in data.get("clasificaciones", clasificaciones_default)
        ]

        return cls(
            schema_version=schema_ver,
            profile_name=str(data.get("profile_name", "personal")),
            clasificaciones=clasificaciones,
            task_archive_delay=str(data.get("task_archive_delay", "7d")),
            derivations=derivations,
        )
