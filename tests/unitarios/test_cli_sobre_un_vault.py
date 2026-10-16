"""`main` sobre un vault: un rechazo no deja nada a medias; un renombre, nada colgando."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import pytest

from tuku import entry, init
from tuku.cli import EXITO, RECHAZO, main

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent
HOY = "2026-08-11"


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    return init.init(tmp_path / "v", home=RAIZ_REPO, desde=date(2026, 8, 10))


def _tuku(vault: Path, *argv: str) -> int:
    return main([*argv, "--vault", str(vault)])


def _foto(vault: Path) -> dict[str, bytes]:
    return {str(p.relative_to(vault)): p.read_bytes() for p in vault.rglob("*") if p.is_file()}


def _leer(vault: Path, *partes: str) -> str:
    return vault.joinpath(*partes).read_text(encoding="utf-8")


def test_entry_add_sin_dia_ni_hora_escribe_hoy_y_ahora(
    vault: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class Hoy(date):
        @classmethod
        def today(cls) -> Hoy:
            return cls(2026, 8, 11)

    class Ahora(datetime):
        @classmethod
        def now(cls, tz: object = None) -> Ahora:
            return cls(2026, 8, 11, 16, 45)

    monkeypatch.setattr(entry, "date", Hoy)
    monkeypatch.setattr(entry, "datetime", Ahora)

    assert (
        _tuku(
            vault, "entry", "add", "--scope", "personal", "--body", "revisé la correspondencia"
        )
        == EXITO
    )
    martes = _leer(vault, "AHORA.md").split("## Martes 11 de agosto", 1)[1]
    assert martes.lstrip().startswith(
        "- 16:45 - [personal](ambitos/personal/personal.md) revisé"
    )


def test_entry_add_a_un_ambito_que_no_existe_nombra_scope_create(
    vault: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    antes = _foto(vault)
    codigo = _tuku(
        vault,
        "entry",
        "add",
        "--day",
        HOY,
        "--hour",
        "09:00",
        "--scope",
        "depto centro",
        "--body",
        "llegó la boleta",
    )
    assert codigo == RECHAZO
    assert "tuku scope create depto-centro" in capsys.readouterr().err
    assert _foto(vault) == antes


def test_scope_create_escribe_con_guion_el_nombre_dicho_con_espacios(vault: Path) -> None:
    assert (
        _tuku(vault, "scope", "create", "depto centro", "--day", HOY, "--hour", "18:45")
        == EXITO
    )
    assert (vault / "ambitos" / "depto-centro" / "depto-centro.md").is_file()
    assert not (vault / "ambitos" / "depto centro").exists()


def test_scope_create_sin_tabla_de_pendientes_no_deja_la_carpeta(
    vault: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (vault / "PENDIENTES.md").write_text("---\ntype: Pending\n---\n", encoding="utf-8")
    assert (
        _tuku(vault, "scope", "create", "depto-centro", "--day", HOY, "--hour", "18:45")
        == RECHAZO
    )
    assert "tabla" in capsys.readouterr().err
    assert not (vault / "ambitos" / "depto-centro").exists()


def test_scope_create_fuera_del_ciclo_no_deja_la_carpeta(
    vault: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    codigo = _tuku(
        vault, "scope", "create", "depto-centro", "--day", "2026-09-01", "--hour", "10:00"
    )
    assert codigo == RECHAZO
    assert "fuera del ciclo" in capsys.readouterr().err
    assert not (vault / "ambitos" / "depto-centro").exists()


def test_note_create_sin_cuerpo_se_rechaza(
    vault: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert _tuku(vault, "note", "create", "una nota sin cuerpo", "--body", "") == RECHAZO
    salida = capsys.readouterr()
    assert "falta el cuerpo" in salida.err + salida.out
    assert not list((vault / "notas").glob("una-nota-sin-cuerpo*"))


def test_note_create_fuera_del_ciclo_no_deja_la_nota(
    vault: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    codigo = _tuku(
        vault,
        "note",
        "create",
        "una nota de otro ciclo",
        "--body",
        "da igual",
        "--day",
        "2026-09-01",
    )
    assert codigo == RECHAZO
    salida = capsys.readouterr()
    assert "fuera del ciclo abierto" in salida.err + salida.out
    assert "Traceback" not in salida.err + salida.out
    assert not list((vault / "notas").glob("una-nota-de-otro-ciclo*"))


def _con_depto_centro(vault: Path) -> None:
    assert (
        _tuku(vault, "scope", "create", "depto-centro", "--day", HOY, "--hour", "18:45")
        == EXITO
    )
    assert (
        _tuku(
            vault,
            "todo",
            "open",
            "--day",
            HOY,
            "--hour",
            "19:00",
            "--scope",
            "depto-centro",
            "--body",
            "pagar los gastos comunes",
        )
        == EXITO
    )


def test_scope_rename_arrastra_carpeta_links_y_ancla(
    vault: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _con_depto_centro(vault)
    assert _tuku(vault, "scope", "rename", "depto-centro", "depto-playa") == EXITO

    ambitos = vault / "ambitos"
    assert not (ambitos / "depto-centro").exists()
    for archivo in ("depto-playa.md", "AGENTS.md", "CADENCIAS.md"):
        assert (ambitos / "depto-playa" / archivo).is_file(), archivo
    colgando = [
        str(p.relative_to(vault))
        for p in vault.rglob("*.md")
        if "ambitos/depto-centro/" in (t := p.read_text(encoding="utf-8"))
        or "[depto-centro](" in t
        or "^depto-centro" in t
    ]
    assert colgando == []
    assert "#^depto-playa" in _leer(vault, "ambitos", "depto-playa", "depto-playa.md")
    assert "^depto-playa" in _leer(vault, "ambitos", "PENDIENTES-AMBITOS.md")

    capsys.readouterr()
    assert _tuku(vault, "scope", "lint") == EXITO
    assert "sin hallazgos" in capsys.readouterr().out


def test_scope_rename_sobre_un_nombre_ocupado_no_mueve_nada(
    vault: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _con_depto_centro(vault)
    antes = _foto(vault)
    assert _tuku(vault, "scope", "rename", "depto-centro", "personal") == RECHAZO
    assert "ya existe" in capsys.readouterr().err
    assert _foto(vault) == antes


def test_entry_rename_corrige_tambien_la_fila_del_pendiente(vault: Path) -> None:
    assert (
        _tuku(
            vault,
            "todo",
            "open",
            "--day",
            "2026-08-12",
            "--hour",
            "09:00",
            "--scope",
            "personal",
            "--body",
            "pagar la sesión con el psicólogo",
        )
        == EXITO
    )
    assert (
        _tuku(
            vault,
            "entry",
            "rename",
            "--day",
            "2026-08-12",
            "--hour",
            "09:00",
            "--body",
            "**pendiente**: pagar la sesión de terapia",
        )
        == EXITO
    )

    linea = next(x for x in _leer(vault, "AHORA.md").splitlines() if x.startswith("- 09:00 - "))
    assert linea.endswith(" **pendiente**: pagar la sesión de terapia"), linea
    pendientes = _leer(vault, "PENDIENTES.md")
    assert "pagar la sesión de terapia" in pendientes
    assert "psicólogo" not in pendientes
