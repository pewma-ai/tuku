"""Pruebas del cargador y validador de configuración `.tuku/config.yaml` (F0.2).

Verifica la carga de configuración, derivaciones y validación de `schema_version` (ADR 0003).
"""

from pathlib import Path

import pytest

from tuku.core.config import SCHEMA_VERSION_MAX, ConfigError, ProfileConfig


def test_cargar_configuracion_valida(tmp_path: Path) -> None:
    """F0.2: Carga configuración válida con derivaciones y clasificaciones."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        """
schema_version: 0
profile_name: "test-profile"
clasificaciones:
  - hito
  - decision
task_archive_delay: "14d"
derivations:
  - target: "ciclos/plan.md#tareas"
    sources: ["tareas/tareas.md"]
    build: "tareas_del_ciclo"
""",
        encoding="utf-8",
    )

    config = ProfileConfig.from_yaml(config_file)
    assert config.schema_version == 0
    assert config.profile_name == "test-profile"
    assert config.clasificaciones == ["hito", "decision"]
    assert config.task_archive_delay == "14d"
    assert len(config.derivations) == 1
    assert config.derivations[0].build == "tareas_del_ciclo"


def test_falta_schema_version_lanza_error_claro(tmp_path: Path) -> None:
    """F0.2: Rechaza configuraciones que omitan el campo obligatorio schema_version."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("profile_name: test\n", encoding="utf-8")

    with pytest.raises(ConfigError, match="Falta 'schema_version'"):
        ProfileConfig.from_yaml(config_file)


def test_schema_version_fuera_de_rango_lanza_error_claro(tmp_path: Path) -> None:
    """F0.2 / ADR 0003: Rechaza esquemas con versión superior a la soportada por el motor."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(f"schema_version: {SCHEMA_VERSION_MAX + 1}\n", encoding="utf-8")

    with pytest.raises(ConfigError, match="fuera de rango soportado"):
        ProfileConfig.from_yaml(config_file)


def test_archivo_inexistente_lanza_config_error(tmp_path: Path) -> None:
    """F0.2: Lanza ConfigError al intentar cargar un archivo que no existe."""
    config_file = tmp_path / "no_existe.yaml"
    with pytest.raises(ConfigError, match="no encontrado"):
        ProfileConfig.from_yaml(config_file)
