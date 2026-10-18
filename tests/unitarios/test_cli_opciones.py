"""Las opciones de los comandos que escriben un registro: entry create, todo open y todo close.

Lo que decide argparse (alias, tipos, valores por defecto) se prueba en memoria.
En disco va solo lo que necesita un vault: la forma abreviada, que corre dentro
del vault y sin `--scope`, y lo que lee `reglas/config.tuku.md`.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable
from datetime import date, datetime
from pathlib import Path

import pytest

from tuku import cli, entry, init, todo
from tuku.cli import EXITO, RECHAZO, USO, main
from tuku.cli.opciones import Momento

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent
HOY = "2026-08-11"
MARTES = "## Martes 11 de agosto"
PERSONAL = "[personal](ambitos/personal/personal.md)"
CUERPO = "avisar de los GGCC"

#: Cómo se escribe el registro de cada comando, después del ámbito.
REGISTRO = {
    "entry create": CUERPO,
    "todo open": f"**pendiente**: {CUERPO}",
    "todo close": f"(Hecho): ~~{CUERPO}~~",
}
COMANDOS = tuple(REGISTRO)


def _parsear(comando: str, *argv: str) -> argparse.Namespace:
    return cli._construir_parser().parse_args([*comando.split(), *argv, "--body", CUERPO])


# --- En memoria: lo que decide argparse ---------------------------------------


def test_las_opciones_llegan_con_su_tipo_en_los_tres_comandos() -> None:
    for comando in COMANDOS:
        args = _parsear(comando)
        assert (args.vault, args.scope, args.at) == (Path("."), None, Momento()), comando

        args = _parsear(comando, "--vault", "v", "--scope", "casa", "--at", f"{HOY} 9:12")
        assert (args.vault, args.scope, args.at.dia, args.at.hora, args.body) == (
            Path("v"),
            "casa",
            date(2026, 8, 11),
            "09:12",
            CUERPO,
        )

    for comando in ("todo open", "todo close"):
        assert _parsear(comando, "--no-propagate").no_propagate
        assert not _parsear(comando).no_propagate

    assert _parsear("todo open", "--due", f"{HOY} 09:00").due.celda() == f"{HOY} 09:00"
    assert _parsear("todo open", "--horizon", "próxima semana").horizon == "próxima semana"
    sin = _parsear("todo open")
    assert (sin.due, sin.horizon) == (Momento(), None)


def test_cada_opcion_tiene_una_sola_forma_en_ingles(capsys: pytest.CaptureFixture[str]) -> None:
    """Sin alias en español: la sintaxis se estabiliza con un nombre por opción."""
    parser = cli._construir_parser()
    casos = (
        ("todo open --body x", "--cuerpo", "--ambito", "--cuando", "--vence", "--horizonte"),
        ("scope create x", "--padre"),
        ("note create x", "--cuerpo-archivo", "--sin-constancia"),
        ("init", "--variante", "--autor"),
    )
    for comando, *alias in casos:
        for opcion in alias:
            with pytest.raises(SystemExit):
                parser.parse_args([*comando.split(), opcion, "x"])
            assert opcion in capsys.readouterr().err, (comando, opcion)


def test_los_errores_de_opciones_son_error_de_uso(capsys: pytest.CaptureFixture[str]) -> None:
    parser = cli._construir_parser()
    for comando in COMANDOS:
        with pytest.raises(SystemExit) as e:
            _parsear(comando, "--at", "11-08-2026")
        assert e.value.code == USO
        assert "11-08-2026" in capsys.readouterr().err

        for cuerpo in ["", "   ", "dos\nlíneas"]:
            with pytest.raises(SystemExit) as e:
                parser.parse_args([*comando.split(), "--body", cuerpo])
            assert e.value.code == USO, (comando, cuerpo)

    with pytest.raises(SystemExit) as e:
        _parsear("todo open", "--due", HOY, "--horizon", "fin de mes")
    assert e.value.code == USO
    assert "--horizon" in capsys.readouterr().err

    with pytest.raises(SystemExit) as e:
        parser.parse_args(["entry", "rename", "--at", HOY, "--body", "x"])
    assert e.value.code == USO


# --- En disco: lo que necesita un vault ----------------------------------------


@pytest.fixture
def vault(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Un vault sembrado, y el directorio actual dentro de él."""
    v = init.init(tmp_path / "v", home=RAIZ_REPO, desde=date(2026, 8, 10))
    monkeypatch.chdir(v)
    return v


def _correr(comando: str, *argv: str) -> int:
    """Corre `comando` dentro del vault; un `todo close` cierra lo que abre antes, otro día."""
    if comando == "todo close":
        abrir = ["todo", "open", "--at", "2026-08-10 08:00", "--body", CUERPO]
        assert main(abrir) == EXITO
    return main([*comando.split(), *argv, "--body", CUERPO])


def _martes(vault: Path) -> list[str]:
    ahora = (vault / "AHORA.md").read_text(encoding="utf-8")
    region = ahora.split(MARTES, 1)[1].split("\n## ", 1)[0]
    return [linea for linea in region.splitlines() if linea.startswith("- ")]


def _config(vault: Path, cambiar: Callable[[str], str]) -> None:
    ruta = vault / "reglas" / "config.tuku.md"
    ruta.write_text(cambiar(ruta.read_text(encoding="utf-8")), encoding="utf-8")


@pytest.mark.parametrize("comando", COMANDOS)
def test_abreviado_dentro_del_vault_va_al_ambito_por_defecto(comando: str, vault: Path) -> None:
    assert _correr(comando, "--at", f"{HOY} 09:12") == EXITO
    assert _martes(vault) == [f"- 09:12 - {PERSONAL} {REGISTRO[comando]}"]


@pytest.mark.parametrize("comando", COMANDOS)
def test_sin_day_ni_hour_es_hoy_y_ahora(
    comando: str, vault: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class Hoy(date):
        @classmethod
        def today(cls) -> Hoy:
            return cls(2026, 8, 11)

    class Ahora(datetime):
        @classmethod
        def now(cls, tz: object = None) -> Ahora:
            return cls(2026, 8, 11, 16, 45)

    for modulo in (entry, todo):
        monkeypatch.setattr(modulo, "date", Hoy)
        monkeypatch.setattr(modulo, "datetime", Ahora)

    assert _correr(comando) == EXITO
    assert _martes(vault) == [f"- 16:45 - {PERSONAL} {REGISTRO[comando]}"]


def test_el_vault_viene_de_la_opcion_y_sin_scope_default_el_registro_no_lleva_ambito(
    vault: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    assert _correr("entry create", "--vault", str(vault), "--at", f"{HOY} 09:12") == EXITO
    assert _martes(vault) == [f"- 09:12 - {PERSONAL} {CUERPO}"]

    _config(vault, lambda t: "\n".join(x for x in t.splitlines() if "`scope_default`" not in x))
    assert _correr("entry create", "--vault", str(vault), "--at", f"{HOY} 10:00") == EXITO
    assert _martes(vault)[-1] == f"- 10:00 - {CUERPO}"


def test_un_scope_default_que_no_existe_nombra_scope_create(
    vault: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _config(vault, lambda t: t.replace("| `personal` ", "| `casa`     "))
    assert _correr("entry create", "--at", f"{HOY} 09:12") == RECHAZO
    assert "tuku scope create casa" in capsys.readouterr().err
    assert _martes(vault) == []


def test_no_propagate_no_toca_las_vistas(vault: Path) -> None:
    vista = vault / "ambitos" / "PENDIENTES-AMBITOS.md"
    antes = vista.read_bytes()
    assert _correr("todo open", "--no-propagate", "--at", f"{HOY} 09:12") == EXITO
    assert vista.read_bytes() == antes
    assert _martes(vault) == [f"- 09:12 - {PERSONAL} **pendiente**: {CUERPO}"]


def _pendientes(vault: Path) -> list[str]:
    texto = (vault / "PENDIENTES.md").read_text(encoding="utf-8")
    return [linea for linea in texto.splitlines() if CUERPO in linea]


def test_due_fecha_el_pendiente_y_el_registro_queda_cuando_se_prometio(vault: Path) -> None:
    assert _correr("todo open", "--at", f"{HOY} 21:30", "--due", "2026-08-13") == EXITO
    assert _martes(vault) == [f"- 21:30 - {PERSONAL} **pendiente**: {CUERPO}"]
    assert _pendientes(vault) == [
        f"| con fecha | 2026-08-13 | [personal](ambitos/personal/personal.md) | {CUERPO} |"
    ]


def test_un_day_futuro_se_rechaza_y_nombra_due(
    vault: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    class Hoy(date):
        @classmethod
        def today(cls) -> Hoy:
            return cls(2026, 8, 11)

    monkeypatch.setattr(todo, "date", Hoy)
    antes = (vault / "AHORA.md").read_bytes()
    assert _correr("todo open", "--at", "2026-08-12 09:00") == RECHAZO
    assert "--due 2026-08-12" in capsys.readouterr().err
    assert (vault / "AHORA.md").read_bytes() == antes
    assert _pendientes(vault) == []


def test_sin_due_ni_horizon_va_al_primer_escalon_del_autor(vault: Path) -> None:
    estilo = vault / "LIBRO-DE-ESTILO.md"
    estilo.write_text(
        estilo.read_text(encoding="utf-8").replace("`esta semana`", "`esta quincena`"),
        encoding="utf-8",
    )
    assert _correr("todo open", "--at", f"{HOY} 09:12") == EXITO
    assert _pendientes(vault)[0].startswith("| esta quincena |")
