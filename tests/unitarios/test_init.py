"""`tuku init`: el destino prohibido, el autor y la zona horaria que siembra."""

from __future__ import annotations

import os
from pathlib import Path
from unittest import mock

import pytest

from tuku.config import parsear_config_md
from tuku.init import (
    TZ_FALLBACK,
    DestinoProhibido,
    MarcadorAutorFaltante,
    _sembrar_autor,
    init,
    tz_del_sistema,
)

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent


@pytest.fixture
def home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    h = tmp_path / "usuarios" / "ana"
    h.mkdir(parents=True)
    monkeypatch.setenv("HOME", str(h))
    monkeypatch.setenv("USERPROFILE", str(h))  # Windows
    return h


def test_el_destino_nunca_es_el_home_ni_un_ancestro_ni_la_raiz(
    home: Path, tmp_path: Path
) -> None:
    (home / "documento.txt").write_text("importa", encoding="utf-8")
    enlace = tmp_path / "atajo"
    enlace.symlink_to(home, target_is_directory=True)

    for destino, force in [
        (home, False),
        (home, True),
        (home.parent, True),
        (Path(home.anchor), True),
        (enlace, True),
    ]:
        with pytest.raises(DestinoProhibido):
            init(destino, force=force)
    assert (home / "documento.txt").is_file()


def test_sin_marcador_se_rechaza_nombrando_el_defecto(tmp_path: Path) -> None:
    (tmp_path / "LIBRO-DE-ESTILO.md").write_text("# Libro de estilo\n", encoding="utf-8")

    with pytest.raises(MarcadorAutorFaltante, match="Nombre del autor"):
        _sembrar_autor(tmp_path, "Arturo")


def test_la_zona_horaria_sale_del_entorno_o_del_sistema_o_del_fallback() -> None:
    with mock.patch.dict(os.environ, {"TZ": "Europe/Berlin"}):
        assert tz_del_sistema() == "Europe/Berlin"

    with mock.patch.dict(os.environ, {"TZ": ""}):
        zona = tz_del_sistema()
    assert zona and "\n" not in zona

    with mock.patch.dict(os.environ, {"TZ": ""}), mock.patch("tuku.init.Path") as fake:
        fake.return_value.is_symlink.return_value = False
        fake.return_value.is_file.return_value = False
        assert tz_del_sistema() == TZ_FALLBACK


def test_init_sustituye_el_placeholder_por_la_zona_real(tmp_path: Path) -> None:
    with mock.patch.dict(os.environ, {"TZ": "Pacific/Easter"}):
        vault = init(tmp_path / "v", home=RAIZ_REPO)

    config = vault / "reglas" / "config.tuku.md"
    campos = parsear_config_md(config.read_text(encoding="utf-8"))
    assert campos["TZ"] == "Pacific/Easter"
    assert campos["cycle_type"] == "semanal"
    assert campos["tuku_template"] == "vanilla"
