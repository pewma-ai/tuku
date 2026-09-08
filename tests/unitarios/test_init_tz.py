"""Tests de la zona horaria que `tuku init` escribe al sembrar."""

from __future__ import annotations

import os
from pathlib import Path
from unittest import mock

from tuku.config import parsear_config_md
from tuku.init import TZ_FALLBACK, init, tz_del_sistema

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent


def test_tz_del_entorno_manda() -> None:
    with mock.patch.dict(os.environ, {"TZ": "Europe/Berlin"}):
        assert tz_del_sistema() == "Europe/Berlin"


def test_sin_entorno_devuelve_una_zona_no_vacia() -> None:
    with mock.patch.dict(os.environ, {"TZ": ""}):
        zona = tz_del_sistema()

    assert zona
    assert "\n" not in zona


def test_sin_nada_que_leer_cae_al_fallback() -> None:
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
