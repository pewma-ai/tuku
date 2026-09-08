"""Tests de la lectura centralizada de configuración, libro de estilo y reglas."""

from __future__ import annotations

from pathlib import Path

import pytest

from tuku.config import (
    VaultInvalido,
    archivo_vault,
    leer_config,
    parsear_autor,
    parsear_config_md,
)

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent


def test_parsear_config_md_extrae_pares_clave_valor() -> None:
    texto = (
        "# Configuración\n\n"
        "Prosa explicativa que no debe interferir.\n\n"
        "**Zona horaria:** America/Santiago\n"
        "**Tipo de ciclo:** semanal\n"
        "**Campo extra:** valor personalizado\n\n"
        "## Otra sección\n"
    )
    datos = parsear_config_md(texto)
    assert datos == {
        "Zona horaria": "America/Santiago",
        "Tipo de ciclo": "semanal",
        "Campo extra": "valor personalizado",
    }


def test_parsear_config_md_vacio() -> None:
    assert parsear_config_md("") == {}
    assert parsear_config_md("Solo prosa sin formato.") == {}


def test_parsear_autor() -> None:
    assert parsear_autor("**Nombre del autor:** Juan Pérez") == "Juan Pérez"
    assert parsear_autor("**Nombre del autor:** por declarar. El instalador...") is None
    assert parsear_autor("**Nombre del autor:**") is None
    assert parsear_autor("# Sin marcador") is None


def test_leer_config_sobre_template_vanilla() -> None:
    vanilla = RAIZ_REPO / "template" / "vanilla"
    cfg = leer_config(vanilla)

    assert cfg.vault == vanilla
    assert cfg.zona_horaria == "America/Santiago"
    assert cfg.tipo_ciclo == "semanal"
    assert cfg.autor is None

    assert "progreso" in cfg.clasificaciones
    assert "esta-semana" in cfg.horizontes
    assert "persona" in cfg.tipos_nota

    abiertos = cfg.vocabularios_abiertos()
    assert "progreso" in abiertos
    assert "esta-semana" in abiertos
    assert "persona" in abiertos

    assert "## Lunes DD de mes" in cfg.plantilla_ahora
    assert "## Domingo DD de mes" in cfg.plantilla_ahora


def test_leer_config_en_memoria_sin_disco(tmp_path: Path) -> None:
    texto_cfg = "**Zona horaria:** UTC\n**Tipo de ciclo:** mensual\n"
    texto_libro = (
        "## El autor\n\n"
        "**Nombre del autor:** Test Bot\n\n"
        "### Clasificaciones\n"
        "| Clasificación | Significa |\n"
        "| --- | --- |\n"
        "| `alfa` | primera |\n\n"
        "### Horizontes\n"
        "| Horizonte | Significa |\n"
        "| --- | --- |\n"
        "| `hoy` | de hoy |\n\n"
        "### Tipos de nota\n"
        "| Tipo | Significa |\n"
        "| --- | --- |\n"
        "| `persona` | alguien |\n"
    )
    texto_plantilla = "PLANTILLA PERSONALIZADA"

    # tmp_path vacío no tiene archivos, pero con overrides en memoria no toca disco
    cfg = leer_config(
        tmp_path,
        texto_config=texto_cfg,
        texto_libro=texto_libro,
        texto_plantilla_ahora=texto_plantilla,
    )
    assert cfg.zona_horaria == "UTC"
    assert cfg.tipo_ciclo == "mensual"
    assert cfg.autor == "Test Bot"
    assert cfg.clasificaciones == ["alfa"]
    assert cfg.plantilla_ahora == "PLANTILLA PERSONALIZADA"


def test_archivo_vault_y_vault_invalido(tmp_path: Path) -> None:
    with pytest.raises(VaultInvalido) as exc:
        archivo_vault(tmp_path, "LIBRO-DE-ESTILO.md")
    assert "no parece un vault de TUKU" in str(exc.value)
