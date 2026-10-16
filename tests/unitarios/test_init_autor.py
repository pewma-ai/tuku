"""Tests del nombre del autor que `tuku init --author` siembra en el libro de estilo."""

from __future__ import annotations

from pathlib import Path

import pytest

from tuku.init import MarcadorAutorFaltante, _sembrar_autor


def test_sin_marcador_se_rechaza_nombrando_el_defecto(tmp_path: Path) -> None:
    (tmp_path / "LIBRO-DE-ESTILO.md").write_text("# Libro de estilo\n", encoding="utf-8")

    with pytest.raises(MarcadorAutorFaltante, match="Nombre del autor"):
        _sembrar_autor(tmp_path, "Arturo")
