"""`tuku regenerate`: valida el canónico antes de escribir."""

from __future__ import annotations

from pathlib import Path

from tuku.regenerate import regenerar


def test_rechaza_si_no_hay_tabla_de_pendientes(tmp_path: Path) -> None:
    (tmp_path / "PENDIENTES.md").write_text("sin tabla", encoding="utf-8")
    r = regenerar(tmp_path)
    assert not r.ok
    assert "PENDIENTES.md" in r.mensaje
