"""`main` sobre un vault: un rechazo no deja nada a medias; un renombre, nada colgando."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from conftest import AHORA
from tuku import init, scope
from tuku.cli import EXITO, RECHAZO, main

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent
HOY = "2026-08-11"


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    return init.init(tmp_path / "v", home=RAIZ_REPO, desde=date(2026, 8, 10))


def _tuku(vault: Path, *argv: str) -> int:
    return main([*argv, "--vault", str(vault)], now=AHORA)


def _foto(vault: Path) -> dict[str, bytes]:
    return {str(p.relative_to(vault)): p.read_bytes() for p in vault.rglob("*") if p.is_file()}


def _leer(vault: Path, *partes: str) -> str:
    return vault.joinpath(*partes).read_text(encoding="utf-8")


def test_un_rechazo_no_deja_nada_a_medias(
    vault: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    casos: list[tuple[tuple[str, ...], str]] = [
        (
            (
                "entry",
                "create",
                "--at",
                f"{HOY} 09:00",
                "--scope",
                "depto centro",
                "--body",
                "x",
            ),
            "tuku scope create depto-centro",
        ),
        (
            ("entry", "create", "--body", "x", "--at", "2026-08-13 09:00"),
            "todo open --due 2026-08-13",
        ),
        (("scope", "create", "depto-centro", "--at", "2026-09-01 10:00"), "fuera del ciclo"),
        (("note", "create", "una nota sin cuerpo", "--body", ""), "falta el cuerpo"),
        (
            ("note", "create", "otra nota", "--body", "da igual", "--at", "2026-09-01"),
            "fuera del ciclo abierto",
        ),
        *(
            (("note", "create", t, "--body", "x", "--at", f"{HOY} 10:00"), "")
            for t in ("", "  ", "¿?")
        ),
    ]
    for argv, dice in casos:
        antes = _foto(vault)
        assert _tuku(vault, *argv) == RECHAZO, argv
        salida = capsys.readouterr()
        assert dice in salida.err + salida.out, argv
        assert "Traceback" not in salida.err + salida.out
        assert _foto(vault) == antes, argv

    (vault / "PENDIENTES.md").write_text("---\ntype: Pending\n---\n", encoding="utf-8")
    assert _tuku(vault, "scope", "create", "depto-centro", "--at", f"{HOY} 18:45") == RECHAZO
    assert "tabla" in capsys.readouterr().err
    assert not (vault / "ambitos" / "depto-centro").exists()


def test_el_nombre_de_un_ambito_va_en_kebab_case_y_no_distingue_mayusculas(vault: Path) -> None:
    assert scope.normalizar("depto centro") == "depto-centro"
    assert scope.normalizar("  depto   centro ") == "depto-centro"
    assert scope.normalizar("[[depto centro]]") == "depto-centro"
    assert scope.normalizar("personal") == "personal"
    assert scope.normalizar("depto-centro") == "depto-centro"
    assert scope.normalizar("") == scope.normalizar("   ") == ""

    antes = sorted(p.name for p in (vault / "ambitos").iterdir())
    assert _tuku(vault, "scope", "create", "PERSONAL", "--at", f"{HOY} 10:00") == EXITO
    assert sorted(p.name for p in (vault / "ambitos").iterdir()) == antes

    assert _tuku(vault, "scope", "create", "Depto  Centro", "--at", f"{HOY} 18:45") == EXITO
    assert (vault / "ambitos" / "depto-centro" / "depto-centro.md").is_file()
    assert not (vault / "ambitos" / "depto centro").exists()

    assert _tuku(vault, "scope", "create", "Ñandú Rojo", "--at", f"{HOY} 10:00") == EXITO
    for cuerpo, hora, nombre in (("uno", "11:00", "ñandú rojo"), ("dos", "12:00", "PERSONAL")):
        argv = ("entry", "create", "--scope", nombre, "--body", cuerpo, "--at", f"{HOY} {hora}")
        assert _tuku(vault, *argv) == EXITO
    ahora = _leer(vault, "AHORA.md")
    assert "[ñandú-rojo](ambitos/ñandú-rojo/ñandú-rojo.md) uno" in ahora
    assert "[personal](ambitos/personal/personal.md) dos" in ahora


def test_scope_rename_arrastra_carpeta_links_y_ancla(
    vault: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    crear = ("scope", "create", "depto-centro", "--at", f"{HOY} 18:45")
    assert _tuku(vault, *crear, "--keyword", "gastos", "--keyword", "LCU") == EXITO
    argv = ("todo", "open", "--at", f"{HOY} 19:00", "--scope", "depto-centro")
    assert _tuku(vault, *argv, "--body", "pagar los gastos comunes") == EXITO
    assert _tuku(vault, "scope", "rename", "depto-centro", "depto-playa") == EXITO

    ambitos = vault / "ambitos"
    assert not (ambitos / "depto-centro").exists()
    assert (ambitos / "depto-playa" / "depto-playa.md").is_file()
    colgando = [
        str(p.relative_to(vault))
        for p in vault.rglob("*.md")
        if "ambitos/depto-centro/" in (t := p.read_text(encoding="utf-8"))
        or "[depto-centro](" in t
        or "^depto-centro" in t
    ]
    assert colgando == []
    assert "#^depto-playa" in _leer(vault, "ambitos", "depto-playa", "depto-playa.md")
    assert scope.keywords(_leer(vault, "ambitos", "depto-playa", "depto-playa.md")) == [
        "gastos",
        "lcu",
    ]
    assert "^depto-playa" in _leer(vault, "ambitos", "PENDIENTES-AMBITOS.md")
    capsys.readouterr()
    assert _tuku(vault, "doctor", "scope") == EXITO
    assert "sin hallazgos" in capsys.readouterr().out

    # un nombre ocupado, también escrito en mayúsculas, no mueve nada
    assert _tuku(vault, "scope", "create", "casa", "--at", f"{HOY} 10:00") == EXITO
    antes = _foto(vault)
    for destino in ("personal", "CASA"):
        assert _tuku(vault, "scope", "rename", "depto-playa", destino) == RECHAZO, destino
        assert "ya existe" in capsys.readouterr().err
        assert _foto(vault) == antes

    # y el nombre nuevo se escribe en kebab-case
    assert _tuku(vault, "scope", "rename", "casa", "Casa Playa") == EXITO
    assert "casa-playa.md" in [p.name for p in (ambitos / "casa-playa").iterdir()]


def test_entry_update_corrige_tambien_la_fila_del_pendiente(vault: Path) -> None:
    abrir = ("todo", "open", "--at", "2026-08-12 09:00", "--scope", "personal")
    assert _tuku(vault, *abrir, "--body", "pagar la sesión con el psicólogo") == EXITO
    corregir = ("entry", "update", "2026-08-12", "--match", "psicólogo")
    assert (
        _tuku(vault, *corregir, "--body", "**pendiente**: pagar la sesión de terapia") == EXITO
    )

    linea = next(x for x in _leer(vault, "AHORA.md").splitlines() if x.startswith("- 09:00 - "))
    assert linea.endswith(" **pendiente**: pagar la sesión de terapia"), linea
    pendientes = _leer(vault, "PENDIENTES.md")
    assert "pagar la sesión de terapia" in pendientes
    assert "psicólogo" not in pendientes
