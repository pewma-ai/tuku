"""`scope create --since`: los registros de otros ámbitos que ya nombran al ámbito nuevo."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pytest

from tuku import entry, init, scope
from tuku.cli import EXITO, main

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    v = init.init(tmp_path / "v", home=RAIZ_REPO, desde=date.today())
    entry.add_al_vault(
        v, body="entregué 40 cuadernos al Colegio Los Robles", scope="personal", hour="09:10"
    )
    entry.add_al_vault(v, body="comí con la Paula", scope="personal", hour="13:00")
    return v


def test_lista_los_registros_de_otros_ambitos_que_nombran_al_nuevo(vault: Path) -> None:
    r = scope.crear_con_constancia(vault, "colegio-los-robles")
    assert r.ok
    hoy = date.today().isoformat()
    assert f"- {hoy} 09:10 (personal): entregué 40 cuadernos al Colegio Los Robles" in r.mensaje
    assert "comí con la Paula" not in r.mensaje
    assert "--scope colegio-los-robles" in r.mensaje


def test_sobre_un_ambito_existente_vuelve_a_listar_sin_crear(vault: Path) -> None:
    scope.crear_con_constancia(vault, "colegio-los-robles")
    antes = (vault / "AHORA.md").read_bytes()
    r = scope.crear_con_constancia(vault, "colegio-los-robles")
    assert "ya existe" in r.mensaje and "entregué 40 cuadernos" in r.mensaje
    assert (vault / "AHORA.md").read_bytes() == antes


def test_una_keyword_tambien_nombra_y_el_ya_movido_no_se_lista(vault: Path) -> None:
    entry.add_al_vault(vault, body="llamó don Rodolfo", scope="personal", hour="15:00")
    r = scope.crear_con_constancia(vault, "colegio-los-robles", palabras=["don Rodolfo"])
    assert "llamó don Rodolfo" in r.mensaje
    entry.mover_en_vault(vault, match="don Rodolfo", scope="colegio-los-robles")
    again = scope.crear_con_constancia(vault, "colegio-los-robles")
    assert "llamó don Rodolfo" not in again.mensaje


def test_since_busca_mas_atras_y_una_fecha_mala_se_rechaza(
    vault: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    ayer = (date.today() - timedelta(days=1)).isoformat()
    assert (
        main(["scope", "create", "colegio-los-robles", "--since", ayer, "--vault", str(vault)])
        == EXITO
    )
    assert not scope.crear_con_constancia(vault, "otro", since="ayer").ok
