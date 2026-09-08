"""Tests de la apertura de ciclo: qué pasa cuando ya hay uno abierto."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from tuku.cycle import CicloEnCurso, open_cycle, tiene_registros
from tuku.init import init

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent
SEMANA_1 = date(2026, 9, 7)
SEMANA_2 = date(2026, 9, 14)


def _vault(tmp: Path) -> Path:
    return init(tmp / "v", desde=SEMANA_1, home=RAIZ_REPO)


def test_tiene_registros_distingue_el_ciclo_vacio() -> None:
    assert not tiene_registros("## Lunes 7 de septiembre\n\n## Martes 8 de septiembre\n")
    assert tiene_registros("## Lunes 7 de septiembre\n- 09:00 - **nota**: cuerpo\n")


def test_abrir_el_mismo_ciclo_es_idempotente(tmp_path: Path) -> None:
    vault = _vault(tmp_path)

    _, creado = open_cycle(vault, SEMANA_1)

    assert not creado


def test_un_ciclo_vacio_se_regenera(tmp_path: Path) -> None:
    vault = _vault(tmp_path)

    _, creado = open_cycle(vault, SEMANA_2)

    assert creado
    assert "from: 2026-09-14" in (vault / "AHORA.md").read_text(encoding="utf-8")


def test_un_ciclo_con_registros_no_se_pisa(tmp_path: Path) -> None:
    vault = _vault(tmp_path)
    ahora = vault / "AHORA.md"
    ahora.write_text(
        ahora.read_text(encoding="utf-8").replace(
            "## Martes 8 de septiembre",
            "## Martes 8 de septiembre\n- 09:00 - **nota**: no se pierde",
        ),
        encoding="utf-8",
    )

    with pytest.raises(CicloEnCurso) as e:
        open_cycle(vault, SEMANA_2)

    assert "bitacoras/bitacora-2026-09-07-2026-09-13.md" in str(e.value)
    assert "no se pierde" in ahora.read_text(encoding="utf-8")
