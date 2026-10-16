"""El destino de `tuku init` nunca puede ser el home del usuario ni un ancestro."""

from __future__ import annotations

from pathlib import Path

import pytest

from tuku.init import DestinoProhibido, init


@pytest.fixture
def home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    h = tmp_path / "usuarios" / "ana"
    h.mkdir(parents=True)
    monkeypatch.setenv("HOME", str(h))
    monkeypatch.setenv("USERPROFILE", str(h))  # Windows
    return h


def test_rechaza_el_home(home: Path) -> None:
    with pytest.raises(DestinoProhibido):
        init(home)


def test_rechaza_el_home_aunque_sea_force(home: Path) -> None:
    (home / "documento.txt").write_text("importa", encoding="utf-8")
    with pytest.raises(DestinoProhibido):
        init(home, force=True)
    assert (home / "documento.txt").is_file()


def test_rechaza_un_ancestro_del_home(home: Path) -> None:
    with pytest.raises(DestinoProhibido):
        init(home.parent, force=True)


def test_rechaza_la_raiz_del_disco(home: Path) -> None:
    with pytest.raises(DestinoProhibido):
        init(Path(home.anchor), force=True)


def test_rechaza_el_home_por_un_symlink(home: Path, tmp_path: Path) -> None:
    enlace = tmp_path / "atajo"
    enlace.symlink_to(home, target_is_directory=True)
    with pytest.raises(DestinoProhibido):
        init(enlace, force=True)
