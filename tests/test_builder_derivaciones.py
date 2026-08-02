"""Pruebas del motor de builders y derivaciones (Fase 3).

Verifica aciclicidad de derivaciones, builders deterministas y diff cero en regeneración.
"""

from pathlib import Path

import pytest

from tuku.core.builder import BuilderEngine, calculate_sources_hash, check_acyclic_derivations
from tuku.core.config import ConfigError, DerivationConfig, ProfileConfig
from tuku.core.init import init_perfil


def test_F3_1_grafo_derivaciones_ciclico_lanza_error() -> None:
    """F3.1: Grafo con ciclo en config.yaml lanza ConfigError al validar."""
    config = ProfileConfig(
        schema_version=0,
        derivations=[
            DerivationConfig(target="a.md", sources=["b.md"], build="dummy"),
            DerivationConfig(target="b.md", sources=["a.md"], build="dummy"),
        ],
    )
    with pytest.raises(ConfigError, match="Ciclo detectado"):
        check_acyclic_derivations(config)


def test_F3_6_hash_de_fuentes_es_determinista() -> None:
    """F3.6: Hash MD5 de fuentes es determinista de 8 caracteres."""
    h1 = calculate_sources_hash("contenido fuente 1")
    h2 = calculate_sources_hash("contenido fuente 1")
    assert len(h1) == 8
    assert h1 == h2


def test_F3_2_F3_5_builder_engine_regenera_con_diff_cero(tmp_path: Path) -> None:
    """F3.2-F3.5: BuilderEngine siembra y proyecta zonas derivadas con diff cero."""
    perfil_dir = init_perfil(tmp_path / "perfil")
    config_path = perfil_dir / ".tuku" / "config.yaml"

    cfg_text = (
        "schema_version: 0\n"
        "derivations:\n"
        "  - target: entradas/entradas.md\n"
        "    sources: [entradas/entradas.md]\n"
        "    build: bitacora_entidad\n"
    )
    config_path.write_text(cfg_text, encoding="utf-8")

    doc_entrada = (
        "---\nid: entradas\ntype: entradas\n---\n"
        "# Bitácora\n"
        "<!-- tuku:derived id=entradas hash=00000000 -->\n"
        "<!-- /tuku:derived -->\n"
    )
    (perfil_dir / "entradas" / "entradas.md").write_text(doc_entrada, encoding="utf-8")

    engine = BuilderEngine(profile_dir=perfil_dir)
    res1 = engine.build_all()
    assert "entradas/entradas.md" in res1

    text_after = (perfil_dir / "entradas" / "entradas.md").read_text(encoding="utf-8")
    assert "hash=" in text_after
    assert "hash=00000000" not in text_after

    # Segunda corrida sin cambios de fuente produce el mismo resultado (diff cero)
    engine.build_all()
    text_after_2 = (perfil_dir / "entradas" / "entradas.md").read_text(encoding="utf-8")
    assert text_after == text_after_2
