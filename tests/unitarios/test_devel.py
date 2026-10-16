"""`DEVEL.md`: la tabla de artefactos nombra archivos y comandos que existen."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tuku.cli import manual

RAIZ = Path(__file__).resolve().parents[2]
DEVEL = (RAIZ / "DEVEL.md").read_text(encoding="utf-8")
FILAS = [f for f in DEVEL.splitlines() if f.startswith("| `")]


def test_la_tabla_de_artefactos_esta_en_devel() -> None:
    assert any("`PENDIENTES.md`" in f for f in FILAS)


@pytest.mark.parametrize("enlace", re.findall(r"\]\(([^)#]+)[^)]*\)", DEVEL))
def test_cada_enlace_de_devel_existe(enlace: str) -> None:
    if "://" not in enlace:
        assert (RAIZ / enlace).exists()


@pytest.mark.parametrize(
    "comando", sorted(set(re.findall(r"`(tuku [a-z]+(?: [a-z]+)?)`", DEVEL)))
)
def test_cada_comando_de_devel_existe(comando: str) -> None:
    assert comando in manual.del_cli()
