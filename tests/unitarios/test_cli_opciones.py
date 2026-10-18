"""Las opciones de los comandos que escriben un registro: entry create, todo open y todo close.

Lo que decide argparse (alias, tipos, valores por defecto) se prueba en memoria.
En disco va solo lo que necesita un vault: la forma abreviada, que corre dentro
del vault y sin `--scope`, y lo que lee `reglas/config.tuku.md`.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable
from datetime import date
from pathlib import Path

import pytest

from conftest import AHORA
from tuku import cli, init
from tuku.cli import EXITO, RECHAZO, USO, main
from tuku.cli.opciones import Momento

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent
HOY = "2026-08-11"
MARTES = "## Martes 11 de agosto"
MIERCOLES = "## Miércoles 12 de agosto"
PERSONAL = "[personal](ambitos/personal/personal.md)"
CUERPO = "avisar de los GGCC"

COMANDOS = ("entry create", "todo open", "todo close")


def _parsear(comando: str, *argv: str) -> argparse.Namespace:
    """Parsea `comando`, con el cuerpo como `--body` o, en `todo close`, posicional."""
    extra = [CUERPO] if comando == "todo close" else ["--body", CUERPO]
    return cli._construir_parser().parse_args([*comando.split(), *argv, *extra])


def _cuerpo(args: argparse.Namespace) -> str:
    """El cuerpo parseado, bajo el nombre que le da cada comando."""
    return str(args.texto if hasattr(args, "texto") else args.body)


# --- En memoria: lo que decide argparse ---------------------------------------


def test_las_opciones_llegan_con_su_tipo_en_los_tres_comandos() -> None:
    for comando in COMANDOS:
        args = _parsear(comando)
        assert (args.vault, args.scope, args.at) == (Path("."), None, Momento()), comando

        args = _parsear(comando, "--vault", "v", "--scope", "casa", "--at", f"{HOY} 9:12")
        assert (args.vault, args.scope, args.at.dia, args.at.hora, _cuerpo(args)) == (
            Path("v"),
            "casa",
            date(2026, 8, 11),
            "09:12",
            CUERPO,
        )

    for comando in ("todo open", "todo close"):
        assert _parsear(comando, "--no-regenerate").no_regenerate
        assert not _parsear(comando).no_regenerate

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


def test_los_errores_de_uso_salen_con_el_codigo_de_uso(
    capsys: pytest.CaptureFixture[str],
) -> None:
    parser = cli._construir_parser()
    for argv in (
        *([noun] for noun in ("entry", "todo", "scope", "note")),
        ["fix"],
        ["doctor", "inexistente"],
        ["inexistente"],
    ):
        with pytest.raises(SystemExit) as e:
            cli.main(argv)
        assert e.value.code == USO, argv
    assert "invalid choice" in capsys.readouterr().err

    for comando in COMANDOS:
        with pytest.raises(SystemExit) as e:
            _parsear(comando, "--at", "11-08-2026")
        assert e.value.code == USO
        assert "11-08-2026" in capsys.readouterr().err

        for cuerpo in ["", "   ", "dos\nlíneas"]:
            extra = [cuerpo] if comando == "todo close" else ["--body", cuerpo]
            with pytest.raises(SystemExit) as e:
                parser.parse_args([*comando.split(), *extra])
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


def _correr(*argv: str) -> int:
    """`entry create` con el cuerpo de siempre, a las `AHORA` de `main`."""
    return main(["entry", "create", *argv, "--body", CUERPO], now=AHORA)


def _registros(vault: Path, dia: str = MARTES) -> list[str]:
    ahora = (vault / "AHORA.md").read_text(encoding="utf-8")
    region = ahora.split(dia, 1)[1].split("\n## ", 1)[0]
    return [linea for linea in region.splitlines() if linea.startswith("- ")]


def _config(vault: Path, cambiar: Callable[[str], str]) -> None:
    ruta = vault / "reglas" / "config.tuku.md"
    ruta.write_text(cambiar(ruta.read_text(encoding="utf-8")), encoding="utf-8")


def test_sin_at_es_el_instante_de_main_y_el_scope_default_viene_de_la_config(
    vault: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert _correr() == EXITO
    assert _registros(vault, MIERCOLES) == [f"- 09:00 - {PERSONAL} {CUERPO}"]
    assert (
        main(["todo", "open", "--body", "pagar", "--at", "2026-08-10 08:00"], now=AHORA)
        == EXITO
    )
    assert main(["todo", "close", "pagar"], now=AHORA) == EXITO
    assert _registros(vault, MIERCOLES)[-1] == f"- 09:00 - {PERSONAL} (Hecho): ~~pagar~~"

    config = (vault / "reglas" / "config.tuku.md").read_text(encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    assert _correr("--vault", str(vault), "--at", f"{HOY} 09:12") == EXITO
    assert _registros(vault) == [f"- 09:12 - {PERSONAL} {CUERPO}"], (
        "el vault viene de la opción"
    )

    _config(vault, lambda t: "\n".join(x for x in t.splitlines() if "`scope_default`" not in x))
    assert _correr("--vault", str(vault), "--at", f"{HOY} 10:00") == EXITO
    assert _registros(vault)[-1] == f"- 10:00 - {CUERPO}", "sin scope_default no lleva ámbito"

    antes = _registros(vault)
    _config(vault, lambda _t: config.replace("| `personal` ", "| `casa`     "))
    assert _correr("--vault", str(vault), "--at", f"{HOY} 11:00") == RECHAZO
    assert "tuku scope create casa" in capsys.readouterr().err
    assert _registros(vault) == antes
