"""`main` sobre un vault: un rechazo no deja nada a medias; un renombre, nada colgando."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import pytest

from tuku import entry, init, todo
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
        "--at",
        f"{HOY} 09:00",
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
        _tuku(vault, "scope", "create", "depto centro", "--at", f"{HOY} 18:45")
        == EXITO
    )
    assert (vault / "ambitos" / "depto-centro" / "depto-centro.md").is_file()
    assert not (vault / "ambitos" / "depto centro").exists()


def test_scope_create_sin_tabla_de_pendientes_no_deja_la_carpeta(
    vault: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (vault / "PENDIENTES.md").write_text("---\ntype: Pending\n---\n", encoding="utf-8")
    assert (
        _tuku(vault, "scope", "create", "depto-centro", "--at", f"{HOY} 18:45")
        == RECHAZO
    )
    assert "tabla" in capsys.readouterr().err
    assert not (vault / "ambitos" / "depto-centro").exists()


def test_scope_create_fuera_del_ciclo_no_deja_la_carpeta(
    vault: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    codigo = _tuku(
        vault, "scope", "create", "depto-centro", "--at", "2026-09-01 10:00"
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
        "--at",
        "2026-09-01",
    )
    assert codigo == RECHAZO
    salida = capsys.readouterr()
    assert "fuera del ciclo abierto" in salida.err + salida.out
    assert "Traceback" not in salida.err + salida.out
    assert not list((vault / "notas").glob("una-nota-de-otro-ciclo*"))


def _con_depto_centro(vault: Path) -> None:
    assert (
        _tuku(vault, "scope", "create", "depto-centro", "--at", f"{HOY} 18:45")
        == EXITO
    )
    assert (
        _tuku(
            vault,
            "todo",
            "open",
            "--at",
            f"{HOY} 19:00",
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
            "--at",
            "2026-08-12 09:00",
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
            "--at",
            "2026-08-12 09:00",
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


@pytest.mark.parametrize("titulo", ["", "  ", "¿?"])
def test_una_nota_sin_titulo_se_rechaza_sin_escribir(vault: Path, titulo: str) -> None:
    antes = _foto(vault)
    codigo = _tuku(vault, "note", "create", titulo, "--body", "x", "--at", f"{HOY} 10:00")
    assert codigo == RECHAZO
    assert _foto(vault) == antes


def _congelar(monkeypatch: pytest.MonkeyPatch, modulo: object, dia: date, hora: str) -> None:
    h, m = hora.split(":")

    class Hoy(date):
        @classmethod
        def today(cls) -> Hoy:
            return cls(dia.year, dia.month, dia.day)

    class Ahora(datetime):
        @classmethod
        def now(cls, tz: object = None) -> Ahora:
            return cls(dia.year, dia.month, dia.day, int(h), int(m))

    monkeypatch.setattr(modulo, "date", Hoy)
    monkeypatch.setattr(modulo, "datetime", Ahora)


# --- los ámbitos no distinguen mayúsculas -----------------------------------


def test_un_ambito_que_solo_difiere_en_mayusculas_choca_con_el_existente(
    vault: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    antes = _foto(vault)
    assert _tuku(vault, "scope", "create", "PERSONAL", "--at", f"{HOY} 10:00") == RECHAZO
    assert "personal" in capsys.readouterr().err
    assert _foto(vault) == antes


def test_el_ambito_se_encuentra_sin_distinguir_mayusculas(vault: Path) -> None:
    assert _tuku(vault, "scope", "create", "Ñandú Rojo", "--at", f"{HOY} 10:00") == EXITO
    for cuerpo, hora, nombre in (("uno", "11:00", "ñandú rojo"), ("dos", "12:00", "PERSONAL")):
        argv = ("entry", "add", "--scope", nombre, "--body", cuerpo, "--at", f"{HOY} {hora}")
        assert _tuku(vault, *argv) == EXITO
    ahora = _leer(vault, "AHORA.md")
    assert "[Ñandú-Rojo](ambitos/Ñandú-Rojo/Ñandú-Rojo.md) uno" in ahora
    assert "[personal](ambitos/personal/personal.md) dos" in ahora


def test_renombrar_solo_las_mayusculas_de_un_ambito(vault: Path) -> None:
    assert _tuku(vault, "scope", "create", "casa", "--at", f"{HOY} 10:00") == EXITO
    assert _tuku(vault, "scope", "rename", "casa", "Casa") == EXITO
    assert "Casa" in [p.name for p in (vault / "ambitos").iterdir()]
    assert "Casa.md" in [p.name for p in (vault / "ambitos" / "Casa").iterdir()]


def test_renombrar_a_un_nombre_que_choca_por_mayusculas_se_rechaza(vault: Path) -> None:
    for nombre in ("casa", "taller"):
        assert _tuku(vault, "scope", "create", nombre, "--at", f"{HOY} 10:00") == EXITO
    antes = _foto(vault)
    assert _tuku(vault, "scope", "rename", "taller", "CASA") == RECHAZO
    assert _foto(vault) == antes


# --- un registro cuenta lo que ya pasó --------------------------------------


def test_entry_add_en_un_dia_futuro_se_rechaza_y_nombra_todo_open(
    vault: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _congelar(monkeypatch, entry, date(2026, 8, 11), "21:30")
    antes = _foto(vault)
    assert _tuku(vault, "entry", "add", "--body", "x", "--at", "2026-08-12 09:00") == RECHAZO
    assert "todo open --due 2026-08-12" in capsys.readouterr().err
    assert _foto(vault) == antes


# --- avisos: el comando procede y alerta por stderr -------------------------


def test_un_cierre_sin_pareja_avisa_y_sale_bien(
    vault: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    argv = ("todo", "close", "--body", "algo que nunca se abrió", "--at", f"{HOY} 10:00")
    assert _tuku(vault, *argv) == EXITO
    salida = capsys.readouterr()
    assert "warning" in salida.err and "palabra por palabra" in salida.err
    assert "warning" not in salida.out
    assert "algo que nunca se abrió" in _leer(vault, "AHORA.md")


def test_un_cierre_con_pareja_no_avisa(vault: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert _tuku(vault, "todo", "open", "--body", "pagar", "--at", f"{HOY} 09:00") == EXITO
    assert _tuku(vault, "todo", "close", "--body", "pagar", "--at", f"{HOY} 10:00") == EXITO
    assert "warning" not in capsys.readouterr().err


@pytest.mark.parametrize(
    ("argv", "dice"),
    [
        (("--due", "2026-08-10"), "ya pasó"),
        (("--at", "2026-08-11 10:00", "--due", "2026-08-11 09:00"), "antes de"),
    ],
)
def test_un_due_absurdo_avisa_y_el_pendiente_se_abre(
    vault: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    argv: tuple[str, ...],
    dice: str,
) -> None:
    _congelar(monkeypatch, todo, date(2026, 8, 11), "21:30")
    assert _tuku(vault, "todo", "open", "--body", "pagar la luz", *argv) == EXITO
    err = capsys.readouterr().err
    assert "warning" in err and dice in err
    assert "pagar la luz" in _leer(vault, "PENDIENTES.md")


def test_un_due_futuro_no_avisa(
    vault: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _congelar(monkeypatch, todo, date(2026, 8, 11), "21:30")
    argv = ("todo", "open", "--body", "pagar la luz", "--due", "2026-08-12 09:00")
    assert _tuku(vault, *argv) == EXITO
    assert "warning" not in capsys.readouterr().err
