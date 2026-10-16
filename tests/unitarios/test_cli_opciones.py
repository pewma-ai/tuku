"""Las opciones de los comandos que escriben un registro: entry add, todo open y todo close.

La forma abreviada corre dentro del vault y sin `--scope`; cada opción se prueba
por separado, con su alias en castellano.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime
from pathlib import Path

import pytest

from tuku import entry, init, todo
from tuku.cli import EXITO, RECHAZO, USO, main

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent
HOY = "2026-08-11"
MARTES = "## Martes 11 de agosto"
PERSONAL = "[personal](ambitos/personal/personal.md)"
DEPTO = "[depto-centro](ambitos/depto-centro/depto-centro.md)"
CUERPO = "avisar de los GGCC"

#: Cómo se escribe el registro de cada comando, después del ámbito.
REGISTRO = {
    "entry add": CUERPO,
    "todo open": f"**pendiente**: {CUERPO}",
    "todo close": f"(Hecho): ~~{CUERPO}~~",
}
COMANDOS = tuple(REGISTRO)


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    return init.init(tmp_path / "v", home=RAIZ_REPO, desde=date(2026, 8, 10))


@pytest.fixture
def reloj(monkeypatch: pytest.MonkeyPatch) -> None:
    """Hoy es el martes 11 de agosto de 2026, a las 16:45."""

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


def _correr(comando: str, *argv: str) -> int:
    """Corre `comando`; un `todo close` cierra el pendiente que abre antes, en otro día."""
    if comando == "todo close":
        assert (
            main(
                [
                    "todo",
                    "open",
                    "--day",
                    "2026-08-10",
                    "--hour",
                    "08:00",
                    *_vault_de(argv),
                    "--body",
                    CUERPO,
                ]
            )
            == EXITO
        )
    return main([*comando.split(), *argv, "--body", CUERPO])


def _vault_de(argv: tuple[str, ...]) -> list[str]:
    return (
        [*argv[argv.index("--vault") : argv.index("--vault") + 2]] if "--vault" in argv else []
    )


def _martes(vault: Path) -> list[str]:
    ahora = (vault / "AHORA.md").read_text(encoding="utf-8")
    region = ahora.split(MARTES, 1)[1].split("\n## ", 1)[0]
    return [linea for linea in region.splitlines() if linea.startswith("- ")]


def _config(vault: Path, cambiar: Callable[[str], str]) -> None:
    ruta = vault / "reglas" / "config.tuku.md"
    ruta.write_text(cambiar(ruta.read_text(encoding="utf-8")), encoding="utf-8")


@pytest.mark.parametrize("comando", COMANDOS)
def test_abreviado_dentro_del_vault_va_al_ambito_por_defecto(
    comando: str, vault: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(vault)
    assert _correr(comando, "--day", HOY, "--hour", "09:12") == EXITO
    assert _martes(vault) == [f"- 09:12 - {PERSONAL} {REGISTRO[comando]}"]


@pytest.mark.parametrize("comando", COMANDOS)
def test_vault_desde_otro_directorio(
    comando: str, vault: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    assert _correr(comando, "--vault", str(vault), "--day", HOY, "--hour", "09:12") == EXITO
    assert _martes(vault) == [f"- 09:12 - {PERSONAL} {REGISTRO[comando]}"]


@pytest.mark.parametrize("comando", COMANDOS)
def test_scope_nombra_otro_ambito(
    comando: str, vault: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(vault)
    assert (
        main(["scope", "create", "depto-centro", "--day", "2026-08-10", "--hour", "07:00"])
        == EXITO
    )
    assert _correr(comando, "--scope", "depto-centro", "--day", HOY, "--hour", "09:12") == EXITO
    assert _martes(vault) == [f"- 09:12 - {DEPTO} {REGISTRO[comando]}"]


@pytest.mark.parametrize("comando", COMANDOS)
def test_sin_scope_default_el_registro_no_lleva_ambito(
    comando: str, vault: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(vault)
    _config(vault, lambda t: "\n".join(x for x in t.splitlines() if "`scope_default`" not in x))
    assert _correr(comando, "--day", HOY, "--hour", "09:12") == EXITO
    assert _martes(vault) == [f"- 09:12 - {REGISTRO[comando]}"]


def test_un_scope_default_que_no_existe_nombra_scope_create(
    vault: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(vault)
    _config(vault, lambda t: t.replace("| `personal` ", "| `casa`     "))
    assert _correr("entry add", "--day", HOY, "--hour", "09:12") == RECHAZO
    assert "tuku scope create casa" in capsys.readouterr().err
    assert _martes(vault) == []


@pytest.mark.parametrize("comando", COMANDOS)
def test_sin_day_ni_hour_es_hoy_y_ahora(
    comando: str, vault: Path, monkeypatch: pytest.MonkeyPatch, reloj: None
) -> None:
    monkeypatch.chdir(vault)
    assert _correr(comando) == EXITO
    assert _martes(vault) == [f"- 16:45 - {PERSONAL} {REGISTRO[comando]}"]


@pytest.mark.parametrize("comando", COMANDOS)
def test_los_alias_en_castellano(
    comando: str, vault: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(vault)
    argv = [*comando.split(), "--dia", HOY, "--hora", "09:12", "--ambito", "personal"]
    if comando == "todo close":
        assert (
            main(["todo", "open", "--day", "2026-08-10", "--hour", "08:00", "--body", CUERPO])
            == EXITO
        )
    assert main([*argv, "--cuerpo", CUERPO]) == EXITO
    assert _martes(vault) == [f"- 09:12 - {PERSONAL} {REGISTRO[comando]}"]


@pytest.mark.parametrize("comando", COMANDOS)
def test_la_hora_se_normaliza_a_dos_digitos(
    comando: str, vault: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(vault)
    assert _correr(comando, "--day", HOY, "--hour", "9:05") == EXITO
    assert _martes(vault) == [f"- 09:05 - {PERSONAL} {REGISTRO[comando]}"]


@pytest.mark.parametrize("comando", COMANDOS)
@pytest.mark.parametrize("opcion", [("--day", "11-08-2026"), ("--hour", "las nueve")])
def test_una_fecha_o_una_hora_mal_escrita_es_error_de_uso(
    comando: str, opcion: tuple[str, str], vault: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(vault)
    antes = (vault / "AHORA.md").read_bytes()
    with pytest.raises(SystemExit) as e:
        main([*comando.split(), *opcion, "--body", CUERPO])
    assert e.value.code == USO
    assert (vault / "AHORA.md").read_bytes() == antes


def _fila(vault: Path) -> todo.Fila:
    (fila,) = todo.filas((vault / "PENDIENTES.md").read_text(encoding="utf-8"))
    return fila


def test_todo_open_sin_fecha_va_a_esta_semana(
    vault: Path, monkeypatch: pytest.MonkeyPatch, reloj: None
) -> None:
    monkeypatch.chdir(vault)
    assert _correr("todo open") == EXITO
    assert (_fila(vault).horizonte, _fila(vault).cuando) == (todo.ESTA_SEMANA, "")


def test_todo_open_con_un_day_futuro_queda_con_fecha(
    vault: Path, monkeypatch: pytest.MonkeyPatch, reloj: None
) -> None:
    monkeypatch.chdir(vault)
    assert _correr("todo open", "--day", "2026-08-13", "--hour", "10:00") == EXITO
    assert (_fila(vault).horizonte, _fila(vault).cuando) == ("con fecha", "2026-08-13")


def test_todo_open_when_fecha_el_pendiente(
    vault: Path, monkeypatch: pytest.MonkeyPatch, reloj: None
) -> None:
    monkeypatch.chdir(vault)
    assert _correr("todo open", "--when", "2026-08-20") == EXITO
    assert (_fila(vault).horizonte, _fila(vault).cuando) == ("con fecha", "2026-08-20")
    assert _martes(vault) == [f"- 16:45 - {PERSONAL} **pendiente**: {CUERPO}"]


def test_todo_open_horizon_elige_el_horizonte(
    vault: Path, monkeypatch: pytest.MonkeyPatch, reloj: None
) -> None:
    monkeypatch.chdir(vault)
    assert _correr("todo open", "--horizonte", "próxima semana") == EXITO
    assert _fila(vault).horizonte == "próxima semana"


@pytest.mark.parametrize("comando", ("todo open", "todo close"))
def test_no_propagate_no_toca_las_vistas(
    comando: str, vault: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(vault)
    if comando == "todo close":
        assert (
            main(["todo", "open", "--day", "2026-08-10", "--hour", "08:00", "--body", CUERPO])
            == EXITO
        )
    vista = vault / "ambitos" / "PENDIENTES-AMBITOS.md"
    antes = vista.read_bytes()
    assert (
        main(
            [
                *comando.split(),
                "--no-propagate",
                "--day",
                HOY,
                "--hour",
                "09:12",
                "--body",
                CUERPO,
            ]
        )
        == EXITO
    )
    assert vista.read_bytes() == antes
    assert _martes(vault) == [f"- 09:12 - {PERSONAL} {REGISTRO[comando]}"]
