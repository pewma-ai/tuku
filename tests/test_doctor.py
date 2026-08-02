"""Pruebas del diagnóstico de perfil `tuku doctor` (F0.5).

Verifica el reporte de versión del motor, commit/branch Git y validez de la configuración.
"""

from pathlib import Path

from tuku.core.doctor import run_doctor
from tuku.core.init import init_perfil


def test_doctor_reporta_salud_perfil_valido(tmp_path: Path) -> None:
    """F0.5: Verifica que doctor apruebe un perfil recién inicializado."""
    perfil_dir = init_perfil(tmp_path / "mi-tuku")

    result = run_doctor(perfil_dir)
    assert result.valid_config is True
    assert result.schema_version == 0
    assert len(result.issues) == 0
    assert result.commit != ""


def test_doctor_detecta_config_invalida(tmp_path: Path) -> None:
    """F0.5: Verifica que doctor reporte problemas ante una configuración inválida."""
    perfil_dir = init_perfil(tmp_path / "mi-tuku")
    cfg_file = perfil_dir / ".tuku" / "config.yaml"
    cfg_file.write_text("schema_version: invalido\n", encoding="utf-8")

    result = run_doctor(perfil_dir)
    assert result.valid_config is False
    assert len(result.issues) > 0
    assert any("schema_version" in issue for issue in result.issues)
