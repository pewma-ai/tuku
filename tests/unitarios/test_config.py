"""Tests de la lectura centralizada de configuración, libro de estilo y reglas."""

from __future__ import annotations

import argparse
from datetime import timedelta
from pathlib import Path

import pytest

from tuku.cli import _reloj
from tuku.config import (
    VaultInvalido,
    archivo_vault,
    exigir_vault,
    hora_local,
    leer_config,
    leer_preferencias,
    parsear_autor,
    parsear_config_md,
    zona_valida,
)
from tuku.doctor import revisar_config

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent


def test_parsear_la_config_y_el_autor() -> None:
    texto = (
        "# Configuración\n\n"
        "Prosa explicativa que no debe interferir.\n\n"
        "> [!info] Un callout tampoco interfiere\n"
        "> Ni siquiera si menciona `TZ`.\n\n"
        "| Campo | Valor |\n"
        "| --- | --- |\n"
        "| `TZ` | `America/Santiago` |\n"
        "| `cycle_name` | `semana` |\n"
        "| `Campo extra` | valor personalizado |\n\n"
        "## Otra sección\n"
    )
    datos = parsear_config_md(texto)
    assert datos == {
        "TZ": "America/Santiago",
        "cycle_name": "semana",
        "Campo extra": "valor personalizado",
    }
    assert parsear_config_md("") == {}
    assert parsear_config_md("Solo prosa sin formato.") == {}

    assert parsear_autor("**Nombre del autor:** Juan Pérez") == "Juan Pérez"
    assert parsear_autor("**Nombre del autor:** por declarar. El instalador...") is None
    assert parsear_autor("**Nombre del autor:**") is None
    assert parsear_autor("# Sin marcador") is None


def test_leer_config_sobre_template_vanilla() -> None:
    vanilla = RAIZ_REPO / "template" / "vanilla"
    cfg = leer_config(vanilla)

    assert cfg.vault == vanilla
    # En el template la zona es el placeholder; `tuku init` la sustituye al sembrar.
    assert cfg.zona_horaria == "TZ-DEL-SISTEMA"
    assert cfg.nombres_de_ciclo == ("semana",)
    assert cfg.autor is None

    assert "progreso" in cfg.clasificaciones
    assert "esta semana" in cfg.horizontes
    assert "persona" in cfg.tipos_nota

    abiertos = cfg.vocabularios_abiertos()
    assert "progreso" in abiertos
    assert "esta semana" in abiertos
    assert "persona" in abiertos

    assert "## Lunes DD de mes" in cfg.plantilla_ahora
    assert "## Domingo DD de mes" in cfg.plantilla_ahora


def test_leer_config_en_memoria_sin_disco(tmp_path: Path) -> None:
    texto_cfg = (
        "| Campo | Valor |\n| --- | --- |\n"
        "| `TZ` | `UTC` |\n| `cycle_name` | `turno, descanso` |\n"
    )
    textos_reglas = {
        "reglas/autor.md": "## Autor\n\n**Nombre del autor:** Test Bot\n",
        "reglas/bitacora.md": (
            "## Clasificaciones\n\n"
            "| Clasificación | Significa |\n| --- | --- |\n| `alfa` | primera |\n"
        ),
        "reglas/pendientes.md": (
            "## Horizontes\n\n| Horizonte | Significa |\n| --- | --- |\n| `hoy` | de hoy |\n"
        ),
        "reglas/notas.md": (
            "## Tipos de nota\n\n| Tipo | Significa |\n| --- | --- |\n| `persona` | alguien |\n"
        ),
    }
    texto_plantilla = "PLANTILLA PERSONALIZADA"

    # tmp_path vacío no tiene archivos, pero con overrides en memoria no toca disco
    cfg = leer_config(
        tmp_path,
        texto_config=texto_cfg,
        textos_reglas=textos_reglas,
        texto_plantilla_ahora=texto_plantilla,
    )
    assert cfg.zona_horaria == "UTC"
    assert cfg.nombres_de_ciclo == ("turno", "descanso")
    assert cfg.autor == "Test Bot"
    assert cfg.clasificaciones == ["alfa"]
    assert cfg.plantilla_ahora == "PLANTILLA PERSONALIZADA"


def test_se_exige_un_vault_y_se_nombra_lo_que_falta(tmp_path: Path) -> None:
    with pytest.raises(VaultInvalido) as exc:
        archivo_vault(tmp_path, "LIBRO-DE-ESTILO.md")
    assert "no parece un vault de TUKU" in str(exc.value)

    with pytest.raises(VaultInvalido, match="no es un vault de TUKU"):
        exigir_vault(tmp_path)
    with pytest.raises(VaultInvalido):
        exigir_vault(tmp_path / "no-existe")

    (tmp_path / "AHORA.md").write_text("", encoding="utf-8")
    exigir_vault(tmp_path)  # un vault incompleto se acepta


def test_las_preferencias_salen_de_un_solo_lector_con_su_default(tmp_path: Path) -> None:
    por_defecto = leer_preferencias(tmp_path)
    assert (por_defecto.zona_horaria, por_defecto.nombres_de_ciclo) == ("", ("semana",))
    assert por_defecto.ambito_por_defecto is None
    assert (por_defecto.formato_fecha, por_defecto.limite_de_notas) == ("MMM/DD", 25)

    texto = (
        "| Campo | Valor | Qué |\n| --- | --- | --- |\n"
        "| `TZ` | `Europe/Madrid` | x |\n| `cycle_name` | `turno, descanso` | x |\n"
        "| `scope_default` | `casa` | x |\n| `date_format` | `DD/MM` | x |\n"
        "| `context_note_limit` | `diez` | x |\n"
    )
    prefs = leer_preferencias(texto=texto)
    assert prefs.zona_horaria == "Europe/Madrid"
    assert prefs.nombres_de_ciclo == ("turno", "descanso")
    assert (prefs.ambito_por_defecto, prefs.formato_fecha) == ("casa", "DD/MM")
    assert prefs.limite_de_notas == 25, "un límite que no es un entero cae al default"


def test_el_reloj_sigue_la_zona_de_la_config_y_una_invalida_avisa(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert zona_valida("America/Santiago")
    assert not any(zona_valida(z) for z in ("TZ-DEL-SISTEMA", "Mundo/Nada", "../etc"))
    este, oeste = hora_local("Pacific/Kiritimati"), hora_local("Etc/GMT+12")
    assert abs((este - oeste) - timedelta(hours=26)) < timedelta(minutes=1)
    assert hora_local("Mundo/Nada").tzinfo is None, "sin zona válida, el reloj del sistema"

    config = tmp_path / "reglas" / "config.tuku.md"
    config.parent.mkdir()
    args = argparse.Namespace(vault=tmp_path)
    config.write_text("| `TZ` | `Mundo/Nada` | x |\n", encoding="utf-8")
    _reloj(args)
    assert "«Mundo/Nada»" in capsys.readouterr().err
    config.write_text("| `TZ` | `Pacific/Kiritimati` | x |\n", encoding="utf-8")
    assert _reloj(args) - hora_local("Etc/GMT+12") > timedelta(hours=25)
    assert capsys.readouterr().err == ""


def test_doctor_rechaza_una_tz_que_el_sistema_no_conoce() -> None:
    def config(tz: str) -> str:
        filas = (f"`TZ` | `{tz}`", "`tuku_template` | `vanilla`", "`tuku_version` | `1`")
        return "".join(f"| {fila} | x |\n" for fila in filas)

    assert revisar_config(config("America/Santiago")).sano
    malo = revisar_config(config("TZ-DEL-SISTEMA"))
    assert not malo.sano and "«TZ-DEL-SISTEMA»" in malo.salida
