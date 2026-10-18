"""Las keywords de un ámbito: `scope create` las pide y `scope update` las suma."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from tuku import init, scope
from tuku.cli import EXITO, RECHAZO, main

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent
HOY = "2026-08-11"


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    return init.init(tmp_path / "v", home=RAIZ_REPO, desde=date(2026, 8, 10))


def _tuku(vault: Path, *argv: str) -> int:
    return main([*argv, "--vault", str(vault)])


def _crear(vault: Path, nombre: str, *extra: str) -> int:
    return _tuku(vault, "scope", "create", nombre, "--at", f"{HOY} 18:45", *extra)


def _keywords(vault: Path, *ruta: str) -> list[str]:
    return scope.keywords(vault.joinpath("ambitos", *ruta).read_text(encoding="utf-8"))


def _ahora(vault: Path) -> str:
    return (vault / "AHORA.md").read_text(encoding="utf-8")


def test_crear_un_ambito_sin_keywords_le_pide_al_agente_preguntarlas(
    vault: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert _crear(vault, "paranal") == EXITO
    salida = capsys.readouterr().out
    assert "Pregunta al autor" in salida
    assert "indican que algo es de 'paranal'" in salida, (
        "las keywords no son sinónimos del nombre"
    )
    assert "tuku scope update paranal --keyword PALABRA" in salida
    assert _keywords(vault, "paranal", "paranal.md") == []


def test_crear_un_ambito_con_keywords_las_deja_en_la_pagina_y_no_vuelve_a_pedirlas(
    vault: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert _crear(vault, "paranal", "--keyword", "vlti", "--keyword", "LCU") == EXITO
    assert "Pregunta al autor" not in capsys.readouterr().out
    assert _keywords(vault, "paranal", "paranal.md") == ["vlti", "LCU"]


def test_crear_sobre_un_ambito_existente_no_vuelve_a_pedir_keywords(
    vault: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert _crear(vault, "paranal") == EXITO
    capsys.readouterr()
    assert _crear(vault, "paranal") == EXITO
    assert "Pregunta al autor" not in capsys.readouterr().out


def test_keywords_suma_las_nuevas_sin_repetir_y_no_toca_la_bitacora(vault: Path) -> None:
    """Las keywords sirven para elegir el ámbito de lo que el autor dice, no para enlazar."""
    assert _crear(vault, "paranal") == EXITO
    assert (
        _tuku(
            vault, "entry", "create", "--at", f"{HOY} 19:00", "--scope", "personal",
            "--body", "revisé el LCU del VLTI",
        )
        == EXITO
    )  # fmt: skip
    antes = _ahora(vault)
    assert (
        _tuku(vault, "scope", "update", "paranal", "--keyword", "lcu,vlti", "--keyword", "TCS")
        == EXITO
    )
    assert _keywords(vault, "paranal", "paranal.md") == ["lcu", "vlti", "TCS"]
    assert _ahora(vault) == antes, "una keyword no modifica ni enlaza el body"

    assert (
        _tuku(vault, "scope", "update", "paranal", "--keyword", "LCU", "--keyword", "tcs")
        == EXITO
    )
    assert _keywords(vault, "paranal", "paranal.md") == ["lcu", "vlti", "TCS"]
    assert _tuku(vault, "doctor") == EXITO


def test_crear_un_ambito_no_enlaza_ni_modifica_lo_ya_escrito(vault: Path) -> None:
    body = "hablé de arriendo con Viana en el depto centro"
    assert (
        _tuku(
            vault,
            "entry",
            "create",
            "--at",
            f"{HOY} 17:00",
            "--scope",
            "personal",
            "--body",
            body,
        )
        == EXITO
    )
    assert _crear(vault, "depto-centro", "--keyword", "arriendo", "--keyword", "viana") == EXITO
    assert f") {body}\n" in _ahora(vault), "el body queda como lo dijo el autor"
    assert "[depto centro]" not in _ahora(vault)


def test_keywords_repetida_con_otra_grafia_no_escribe_nada(vault: Path) -> None:
    assert _crear(vault, "paranal", "--keyword", "casa matriz") == EXITO
    antes = (vault / "ambitos" / "paranal" / "paranal.md").read_bytes()
    assert _tuku(vault, "scope", "update", "paranal", "--keyword", "Casa-Matriz") == EXITO
    assert (vault / "ambitos" / "paranal" / "paranal.md").read_bytes() == antes


def test_keywords_rechaza_lo_que_no_cabe_o_no_existe(
    vault: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert _crear(vault, "paranal") == EXITO
    capsys.readouterr()
    casos = [
        (("scope", "update", "nada", "--keyword", "x"), "no existe el ámbito"),
        (("scope", "update", "paranal", "--keyword", "[a]"), "corchetes"),
        (("scope", "update", "paranal", "--keyword", " , "), "nada que actualizar"),
        (("scope", "update", "paranal"), "nada que actualizar"),
    ]
    for argv, dice in casos:
        assert _tuku(vault, *argv) == RECHAZO, argv
        assert dice in capsys.readouterr().err, argv
    assert _keywords(vault, "paranal", "paranal.md") == []


def test_renombrar_un_ambito_deja_sus_keywords_como_estaban(vault: Path) -> None:
    assert _crear(vault, "paranal", "--keyword", "vlti", "--keyword", "LCU") == EXITO
    assert _tuku(vault, "scope", "rename", "paranal", "cerro") == EXITO
    assert _keywords(vault, "cerro", "cerro.md") == ["vlti", "LCU"]
    assert _tuku(vault, "doctor") == EXITO


def test_un_pendiente_con_una_keyword_sigue_coincidiendo_con_su_fila(vault: Path) -> None:
    """El body del pendiente queda como lo dijo el autor, así que se puede cerrar."""
    assert _crear(vault, "depto-centro") == EXITO
    assert (
        _tuku(
            vault, "todo", "open", "--at", f"{HOY} 19:00", "--scope", "personal",
            "--body", "pagar los gastos comunes del depto centro",
        )
        == EXITO
    )  # fmt: skip
    assert (
        _tuku(vault, "scope", "update", "depto-centro", "--keyword", "gastos comunes") == EXITO
    )
    assert "**pendiente**: pagar los gastos comunes del depto centro" in _ahora(vault)
    assert _tuku(vault, "todo", "lint") == EXITO
    assert _tuku(vault, "doctor") == EXITO


def test_una_keyword_admite_varias_palabras_separadas_por_coma_y_los_espacios_pasan_a_guion(
    vault: Path,
) -> None:
    assert (
        _crear(vault, "paranal", "--keyword", "Los Robles, vlti", "--keyword", "gravity")
        == EXITO
    )
    assert _keywords(vault, "paranal", "paranal.md") == [
        "Los-Robles",
        "vlti",
        "gravity",
    ]
    assert _tuku(vault, "scope", "update", "paranal", "--keyword", "Paula  Reyes,LCU") == EXITO
    assert _keywords(vault, "paranal", "paranal.md")[-2:] == ["Paula-Reyes", "LCU"]


def test_scope_keywords_ya_no_existe(vault: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """La sintaxis se estabiliza sin retrocompatibilidad: una sola forma de dar keywords."""
    assert _crear(vault, "paranal") == EXITO
    capsys.readouterr()
    with pytest.raises(SystemExit):
        _tuku(vault, "scope", "keywords", "paranal", "vlti")
    assert "invalid choice" in capsys.readouterr().err


def test_una_keyword_que_repite_el_nombre_del_ambito_no_entra(vault: Path) -> None:
    assert _crear(vault, "casa-matriz", "--keyword", "Casa Matriz, sede") == EXITO
    assert _keywords(vault, "casa-matriz", "casa-matriz.md") == ["sede"]
    assert _tuku(vault, "scope", "update", "casa-matriz", "--keyword", "CASA-MATRIZ") == EXITO
    assert _keywords(vault, "casa-matriz", "casa-matriz.md") == ["sede"]
