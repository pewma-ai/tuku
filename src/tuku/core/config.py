"""Configuración del perfil y lectura de `.tuku/config.yaml`.

Implementa las reglas de `spec/perfil.md`, ADR 0003 (versionado) y ADR 0017 (Pydantic v2).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator

SCHEMA_VERSION_MIN = 0
SCHEMA_VERSION_MAX = 0


class ConfigError(Exception):
    """Error al cargar o validar la configuración del perfil."""


class DerivationConfig(BaseModel):
    target: str
    sources: list[str]
    build: str
    filter: str | None = None


class ProfileConfig(BaseModel):
    schema_version: int
    profile_name: str = "personal"
    clasificaciones: list[str] = Field(
        default_factory=lambda: ["hito", "decision", "senal", "msg"]
    )
    task_archive_delay: str = "7d"
    derivations: list[DerivationConfig] = Field(default_factory=list)

    @field_validator("schema_version")
    @classmethod
    def validate_schema_version(cls, v: int) -> int:
        if v < SCHEMA_VERSION_MIN or v > SCHEMA_VERSION_MAX:
            raise ValueError(
                f"Versión de esquema {v} fuera de rango soportado "
                f"({SCHEMA_VERSION_MIN}-{SCHEMA_VERSION_MAX}). "
                "Ejecute 'tuku doctor' o 'tuku migrate'."
            )
        return v

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

        schema_ver = data.get("schema_version")
        if not isinstance(schema_ver, int) or isinstance(schema_ver, bool):
            raise ConfigError(
                f"'schema_version' debe ser un entero no negativo, recibido: {schema_ver!r}"
            )

        try:
            return cls.model_validate(data)
        except Exception as err:
            raise ConfigError(f"Error de validación en {path}: {err}") from err
