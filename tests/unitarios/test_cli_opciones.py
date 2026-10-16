"""Las opciones de los comandos que escriben un registro: entry add, todo open y todo close.

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

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent
HOY = "2026-08-11"
MARTES = "## Martes 11 de agosto"
PERSONAL = "[personal](ambitos/personal/personal.md)"
CUERPO = "avisar de los GGCC"

#: Cómo se escribe el registro de cada comando, después del ámbito.
REGISTRO = {
    "entry add": CUERPO,
    "todo open": f"**pendiente**: {CUERPO}",
    "todo close": f"(Hecho): ~~{CUERPO}~~",
}
COMANDOS = tuple(REGISTRO)


def _parsear(comando: str, *argv: str) -> argparse.Namespace:
    return cli._construir_parser().parse_args([*comando.split(), *argv, "--body", CUERPO])


# --- En memoria: lo que decide argparse ---------------------------------------


@pytest.mark.parametrize("comando", COMANDOS)
def test_sin_opciones_el_vault_es_el_directorio_actual(comando: str) -> None:
    args = _parsear(comando)
    assert (args.vault, args.scope, args.day, args.hour) == (Path("."), None, None, None)


@pytest.mark.parametrize("comando", COMANDOS)
def test_cada_opcion_llega_con_su_tipo(comando: str) -> None:
    args = _parsear(comando, "--vault", "v", "--scope", "casa", "--day", HOY, "--hour", "09:12")
    assert (args.vault, args.scope, args.day, args.hour, args.body) == (
        Path("v"),
        "casa",
        date(2026, 8, 11),
        "09:12",
        CUERPO,
    )


@pytest.mark.parametrize("comando", COMANDOS)
def test_los_alias_en_castellano_son_las_mismas_opciones(comando: str) -> None:
    ingles = ("--scope", "casa", "--day", HOY, "--hour", "09:12", "--body", CUERPO)
    castellano = ("--ambito", "casa", "--dia", HOY, "--hora", "09:12", "--cuerpo", CUERPO)
    parser = cli._construir_parser()
    assert parser.parse_args([*comando.split(), *ingles]) == parser.parse_args(
        [*comando.split(), *castellano]
    )


@pytest.mark.parametrize("comando", COMANDOS)
def test_la_hora_se_normaliza_a_dos_digitos(comando: str) -> None:
    assert _parsear(comando, "--hour", "9:05").hour == "09:05"


@pytest.mark.parametrize("comando", COMANDOS)
@pytest.mark.parametrize(
    "opcion", [("--day", "11-08-2026"), ("--hour", "las nueve"), ("--hour", "9:5")]
)
def test_una_fecha_o_una_hora_mal_escrita_es_error_de_uso(
    comando: str, opcion: tuple[str, str], capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(SystemExit) as e:
        _parsear(comando, *opcion)
    assert e.value.code == USO
    assert opcion[1] in capsys.readouterr().err


def test_todo_open_when_y_horizon() -> None:
    args = _parsear("todo open", "--when", "2026-08-20", "--horizonte", "próxima semana")
    assert (args.when, args.horizon) == ("2026-08-20", "próxima semana")
    sin = _parsear("todo open")
    assert (sin.when, sin.horizon) == ("", todo.ESTA_SEMANA)


@pytest.mark.parametrize("comando", ("todo open", "todo close"))
def test_no_propagate(comando: str) -> None:
    assert _parsear(comando, "--no-propagate").no_propagate
    assert not _parsear(comando).no_propagate


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
        abrir = ["todo", "open", "--day", "2026-08-10", "--hour", "08:00", "--body", CUERPO]
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
    assert _correr(comando, "--day", HOY, "--hour", "09:12") == EXITO
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


def test_vault_desde_otro_directorio(
    vault: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    assert _correr("entry add", "--vault", str(vault), "--day", HOY, "--hour", "09:12") == EXITO
    assert _martes(vault) == [f"- 09:12 - {PERSONAL} {CUERPO}"]


def test_sin_scope_default_el_registro_no_lleva_ambito(vault: Path) -> None:
    _config(vault, lambda t: "\n".join(x for x in t.splitlines() if "`scope_default`" not in x))
    assert _correr("entry add", "--day", HOY, "--hour", "09:12") == EXITO
    assert _martes(vault) == [f"- 09:12 - {CUERPO}"]


def test_un_scope_default_que_no_existe_nombra_scope_create(
    vault: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _config(vault, lambda t: t.replace("| `personal` ", "| `casa`     "))
    assert _correr("entry add", "--day", HOY, "--hour", "09:12") == RECHAZO
    assert "tuku scope create casa" in capsys.readouterr().err
    assert _martes(vault) == []


def test_no_propagate_no_toca_las_vistas(vault: Path) -> None:
    vista = vault / "ambitos" / "PENDIENTES-AMBITOS.md"
    antes = vista.read_bytes()
    assert _correr("todo open", "--no-propagate", "--day", HOY, "--hour", "09:12") == EXITO
    assert vista.read_bytes() == antes
    assert _martes(vault) == [f"- 09:12 - {PERSONAL} **pendiente**: {CUERPO}"]
