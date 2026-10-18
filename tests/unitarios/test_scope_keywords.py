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


def test_crear_pide_las_keywords_solo_si_faltan(
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

    assert _crear(vault, "paranal") == EXITO
    assert "Pregunta al autor" not in capsys.readouterr().out, "ya existe"

    assert _crear(vault, "cerro", "--keyword", "vlti", "--keyword", "LCU") == EXITO
    assert "Pregunta al autor" not in capsys.readouterr().out
    assert _keywords(vault, "cerro", "cerro.md") == ["vlti", "lcu"]


def test_una_keyword_no_modifica_ni_enlaza_lo_ya_escrito(vault: Path) -> None:
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
    assert _keywords(vault, "paranal", "paranal.md") == ["lcu", "vlti", "tcs"]
    assert _ahora(vault) == antes, "una keyword no modifica ni enlaza el body"
    assert (
        _tuku(vault, "scope", "update", "paranal", "--keyword", "LCU", "--keyword", "tcs")
        == EXITO
    )
    assert _keywords(vault, "paranal", "paranal.md") == ["lcu", "vlti", "tcs"]

    body = "hablé de arriendo con Viana en el depto centro"
    assert (
        _tuku(
            vault, "entry", "create", "--at", f"{HOY} 20:00", "--scope", "personal",
            "--body", body,
        )
        == EXITO
    )  # fmt: skip
    assert _crear(vault, "depto-centro", "--keyword", "arriendo", "--keyword", "viana") == EXITO
    assert f") {body}\n" in _ahora(vault), "el body queda como lo dijo el autor"
    assert "[depto centro]" not in _ahora(vault)

    assert (
        _tuku(
            vault, "todo", "open", "--at", f"{HOY} 21:00", "--scope", "personal",
            "--body", "pagar los gastos comunes del depto centro",
        )
        == EXITO
    )  # fmt: skip
    assert (
        _tuku(vault, "scope", "update", "depto-centro", "--keyword", "gastos comunes") == EXITO
    )
    assert "**pendiente**: pagar los gastos comunes del depto centro" in _ahora(vault)
    assert _tuku(vault, "doctor", "todo") == EXITO
    assert _tuku(vault, "doctor") == EXITO


def test_las_keywords_se_normalizan_y_no_se_repiten(vault: Path) -> None:
    assert _crear(vault, "paranal", "--keyword", "casa matriz") == EXITO
    pagina = vault / "ambitos" / "paranal" / "paranal.md"
    antes = pagina.read_bytes()
    assert _tuku(vault, "scope", "update", "paranal", "--keyword", "Casa-Matriz") == EXITO
    assert pagina.read_bytes() == antes, "otra grafía de la misma keyword no escribe"

    assert (
        _crear(vault, "cerro", "--keyword", "Los Robles, vlti", "--keyword", "gravity") == EXITO
    )
    assert _keywords(vault, "cerro", "cerro.md") == ["los-robles", "vlti", "gravity"]
    assert _tuku(vault, "scope", "update", "cerro", "--keyword", "Paula  Reyes,LCU") == EXITO
    assert _keywords(vault, "cerro", "cerro.md")[-2:] == ["paula-reyes", "lcu"]

    assert _crear(vault, "casa-matriz", "--keyword", "Casa Matriz, sede") == EXITO
    assert _keywords(vault, "casa-matriz", "casa-matriz.md") == ["sede"]
    assert _tuku(vault, "scope", "update", "casa-matriz", "--keyword", "CASA-MATRIZ") == EXITO
    assert _keywords(vault, "casa-matriz", "casa-matriz.md") == ["sede"]


def test_una_keyword_que_ya_nombra_a_otro_ambito_avisa_y_escribe(
    vault: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert _crear(vault, "catalogo-marzo", "--keyword", "paula") == EXITO
    assert capsys.readouterr().err == ""
    assert _crear(vault, "escuela-los-maitenes") == EXITO
    capsys.readouterr()

    assert (
        _tuku(vault, "scope", "update", "escuela-los-maitenes", "--keyword", "Paula") == EXITO
    )
    err = capsys.readouterr().err
    assert "warning" in err and "'paula'" in err and "catalogo-marzo" in err
    assert _keywords(vault, "escuela-los-maitenes", "escuela-los-maitenes.md") == ["paula"]

    assert _crear(vault, "liceo", "--keyword", "paula") == EXITO
    assert "catalogo-marzo y escuela-los-maitenes" in capsys.readouterr().err

    assert _tuku(vault, "scope", "update", "liceo", "--keyword", "paula") == EXITO
    assert capsys.readouterr().err == "", "lo que ya estaba no vuelve a avisar"

    assert _crear(vault, "bodega") == EXITO
    avisos = scope.avisos_de_keywords(vault, "paranal", ["bodega"])
    assert len(avisos) == 1 and "bodega" in avisos[0], "el nombre de un ámbito también cuenta"
    assert scope.avisos_de_keywords(vault, "bodega", ["bodega"]) == ()


def test_doctor_scope_pregunta_por_la_keyword_repetida_y_no_falla(vault: Path) -> None:
    from tuku import doctor

    _crear(vault, "catalogo-marzo", "--keyword", "paula")
    _crear(vault, "escuela-los-maitenes", "--keyword", "paula")
    r = doctor.revisar_vault(vault, tema="scope")
    assert r.ok, "una pregunta no hace fallar"
    assert "scope: pregunta:" in r.mensaje and "'paula'" in r.mensaje
    assert "1 pregunta(s)" in r.mensaje
    assert main(["doctor", "scope", "--vault", str(vault)]) == EXITO


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
