"""`~/.tuku` lleva sello de versión, se refresca y el vault registra de dónde salió."""

from __future__ import annotations

from pathlib import Path

import pytest

from tuku import _pack, doctor, init
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


def test_materializa_y_sella_si_no_existe(entorno: tuple[Path, Path]) -> None:
    tuku_home, _ = entorno
    assert init.resolver_home() == tuku_home
    assert (tuku_home / "template" / "nuevo.md").is_file()
    assert init.version_del_home(tuku_home) == "2.0"


def test_refresca_si_el_sello_difiere(entorno: tuple[Path, Path]) -> None:
    tuku_home, _ = entorno
    (tuku_home / "template").mkdir(parents=True)
    (tuku_home / "template" / "viejo.md").write_text("viejo", encoding="utf-8")
    (tuku_home / init.SELLO).write_text("1.0\n", encoding="utf-8")
    init.resolver_home()
    assert not (tuku_home / "template" / "viejo.md").exists()
    assert (tuku_home / "template" / "nuevo.md").is_file()
    assert init.version_del_home(tuku_home) == "2.0"


def test_refresca_si_no_tiene_sello(entorno: tuple[Path, Path]) -> None:
    tuku_home, _ = entorno
    (tuku_home / "template").mkdir(parents=True)
    (tuku_home / "template" / "viejo.md").write_text("viejo", encoding="utf-8")
    init.resolver_home()
    assert not (tuku_home / "template" / "viejo.md").exists()
    assert init.version_del_home(tuku_home) == "2.0"


def test_no_toca_si_el_sello_coincide(entorno: tuple[Path, Path]) -> None:
    tuku_home, _ = entorno
    init.resolver_home()
    extra = tuku_home / "template" / "extra.md"
    extra.write_text("sigue", encoding="utf-8")
    init.resolver_home()
    assert extra.is_file()


def test_version_del_home_sin_sello_es_none(tmp_path: Path) -> None:
    assert init.version_del_home(tmp_path) is None


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
    destino = init.init(tmp_path / "vault", home=RAIZ_REPO)
    campos = parsear_config_md((destino / "reglas" / "config.tuku.md").read_text("utf-8"))
    assert campos["tuku_version"] == init.version_de_tuku()
    assert campos["origen"] == init.ORIGEN


CONFIG = "| Campo | Valor |\n| --- | --- |\n| `tuku_version` | `{}` |\n"


def test_doctor_avisa_si_el_vault_es_anterior() -> None:
    r = doctor.revisar_version(CONFIG.format("1.0"), "2.0")
    assert r.sano
    assert "1.0" in r.salida and "2.0" in r.salida and "~/.tuku" in r.salida


def test_doctor_calla_si_coinciden() -> None:
    r = doctor.revisar_version(CONFIG.format("2.0"), "2.0")
    assert r.sano
    assert "al día" in r.salida


def test_doctor_sin_referencia_no_compara() -> None:
    r = doctor.revisar_version(CONFIG.format("1.0"), None)
    assert r.sano
    assert "sin sello" in r.salida


def test_doctor_sin_config_no_falla_aqui() -> None:
    assert doctor.revisar_version(None, "2.0").sano
