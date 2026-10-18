"""`~/.tuku` lleva sello de versión, se refresca y el vault registra de dónde salió."""

from __future__ import annotations

from pathlib import Path

import pytest

from conftest import AHORA
from tuku import _pack, init
from tuku.config import parsear_config_md

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent


@pytest.fixture
def entorno(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    """Un `$HOME` falso y un árbol empaquetado falso. Devuelve (~/.tuku, empaquetado)."""
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))  # Windows
    monkeypatch.delenv("TUKU_HOME", raising=False)
    empaquetado = tmp_path / "_home"
    (empaquetado / "template").mkdir(parents=True)
    (empaquetado / "template" / "nuevo.md").write_text("nuevo", encoding="utf-8")
    monkeypatch.setattr(init, "_HOME_EMPAQUETADO", empaquetado)
    monkeypatch.setattr(init, "version_de_tuku", lambda: "2.0")
    return home / ".tuku", empaquetado


def test_el_home_se_materializa_se_sella_y_se_refresca_solo_si_cambia(
    entorno: tuple[Path, Path], tmp_path: Path
) -> None:
    tuku_home, empaquetado = entorno
    viejo = tuku_home / "template" / "viejo.md"
    assert init.version_del_home(tmp_path) is None

    assert init.resolver_home() == tuku_home
    assert (tuku_home / "template" / "nuevo.md").is_file()
    assert init.version_del_home(tuku_home) == "2.0"

    extra = tuku_home / "template" / "extra.md"
    extra.write_text("sigue", encoding="utf-8")
    init.resolver_home()
    assert extra.is_file(), "con el sello igual no se toca"

    (tuku_home / init.SELLO).write_text("1.0\n", encoding="utf-8")
    viejo.write_text("viejo", encoding="utf-8")
    init.resolver_home()
    assert not viejo.exists() and (tuku_home / "template" / "nuevo.md").is_file()
    assert init.version_del_home(tuku_home) == "2.0", "el sello difiere"

    viejo.write_text("viejo", encoding="utf-8")
    (tuku_home / init.SELLO).unlink()
    init.resolver_home()
    assert not viejo.exists(), "sin sello"

    (empaquetado / "template" / "nuevo.md").write_text("cambiado", encoding="utf-8")
    init.resolver_home()
    assert (tuku_home / "template" / "nuevo.md").read_text(encoding="utf-8") == "cambiado"


def test_el_paquete_lleva_docs_y_spec(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    raiz = tmp_path / "repo"
    for carpeta in ("template", "docs", "spec"):
        (raiz / carpeta).mkdir(parents=True)
        (raiz / carpeta / "x.md").write_text(carpeta, encoding="utf-8")
    destino = tmp_path / "_home"
    monkeypatch.setattr(_pack, "DESTINO", destino)
    assert _pack.empaquetar(raiz) == destino
    for carpeta in ("template", "docs", "spec"):
        assert (destino / carpeta / "x.md").is_file()


def test_init_registra_version_y_origen(tmp_path: Path) -> None:
    destino = init.init(tmp_path / "vault", home=RAIZ_REPO, desde=AHORA.date())
    campos = parsear_config_md((destino / "reglas" / "config.tuku.md").read_text("utf-8"))
    assert campos["tuku_version"] == init.version_de_tuku()
    assert campos["origen"] == init.ORIGEN
