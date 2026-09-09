"""Tests de la función pura y de reconstrucción de derivados."""

from __future__ import annotations

from pathlib import Path

from tuku.rebuild import archivos_derivados, reconstruir


def test_archivos_derivados_lista_los_derivados_del_sistema() -> None:
    vault = Path("/dummy/vault")
    derivados = archivos_derivados(vault)
    assert vault / "ambitos" / "PENDIENTES-AMBITOS.md" in derivados


def test_reconstruir_rechaza_si_no_hay_tabla_pendientes(tmp_path: Path) -> None:
    (tmp_path / "PENDIENTES.md").write_text("sin tabla", encoding="utf-8")
    r = reconstruir(tmp_path)
    assert not r.ok
    assert "error" in r.mensaje
    assert "PENDIENTES.md" in r.mensaje
