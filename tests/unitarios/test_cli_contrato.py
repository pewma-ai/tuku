"""El contrato del CLI: códigos, uso, rechazo fuera de un vault, correcciones y propuestas."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pytest

from tuku import cli
from tuku.cli import ENTORNO, EXITO, RECHAZO, USO, main, manual
from tuku.lint import lint

RAIZ = Path(__file__).resolve().parent.parent.parent
PERSONAL = "[personal](ambitos/personal/personal.md)"


def test_los_cuatro_codigos_son_distintos() -> None:
    codigos = [EXITO, RECHAZO, USO, ENTORNO]
    assert len(set(codigos)) == len(codigos), "dos causas comparten código de salida"


def test_un_uso_incorrecto_es_error_de_uso(capsys: pytest.CaptureFixture[str]) -> None:
    for argv in (
        *([noun] for noun in ("entry", "todo", "scope", "note", "cycle", "vocab", "style")),
        ["fix"],
        ["doctor", "inexistente"],
    ):
        with pytest.raises(SystemExit) as salida:
            cli.main(argv)
        assert salida.value.code == USO, argv
    assert "invalid choice" in capsys.readouterr().err


def test_rechaza_fuera_de_un_vault_y_nombra_que_falta(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    for argv in (
        ["doctor"],
        ["doctor", "entry"],
        ["todo", "open", "--body", "x"],
        ["regenerate"],
        ["doctor", "note"],
    ):
        assert main([*argv, "--vault", str(tmp_path)]) == RECHAZO, argv
        err = capsys.readouterr().err
        assert "no es un vault de TUKU" in err
        assert "AHORA.md" in err and "tuku init" in err, "no dice qué falta ni qué hacer"
    assert list(tmp_path.iterdir()) == []


def test_note_lint_de_un_archivo_suelto_no_exige_vault(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    nota = tmp_path / "nota.md"
    nota.write_text("# Nota\n\ncuerpo\n\n## Ver además\n\n", encoding="utf-8")
    assert main(["doctor", "note", str(nota), "--vault", str(tmp_path)]) in (EXITO, RECHAZO)
    assert "no es un vault" not in capsys.readouterr().err


def test_todo_hallazgo_del_lint_nombra_la_correccion() -> None:
    ahora = (
        "## Martes 11 de agosto\n\n"
        f"- 12:05 - {PERSONAL} **cachureo**: ordené los cables\n"
        f"- 13:00 - {PERSONAL} **Cadencia**: comprar una maleta\n"
    )
    hallazgos = lint(ahora, abiertos=["progreso"])
    assert len(hallazgos) >= 2, hallazgos
    for h in hallazgos:
        assert h.correccion.strip(), f"hallazgo sin corrección: {h.defecto}"


def test_ningun_comando_escribe_una_propuesta() -> None:
    """La propuesta no tiene comando a propósito: se muestra y espera."""
    nombres = [e.nombre for e in manual.entradas(cli._construir_parser())]
    assert not any("propose" in n for n in nombres), nombres
    for fuente in (RAIZ / "src" / "tuku").rglob("*.py"):
        assert "propuestas/" not in fuente.read_text(encoding="utf-8"), fuente.name


def test_el_cuerpo_no_se_busca_en_stdin_sin_pedirlo(monkeypatch: pytest.MonkeyPatch) -> None:
    """`stdin` se lee solo con `--body-file -`: un pipe abierto y vacío colgaría el comando."""

    class StdinQueNadieDebeLeer:
        def isatty(self) -> bool:
            return False

        def read(self) -> str:
            raise AssertionError("leyó stdin sin que se lo pidieran")

    monkeypatch.setattr(sys, "stdin", StdinQueNadieDebeLeer())
    assert cli._cuerpo_de_la_nota(argparse.Namespace(body=None, body_file=None)) is None
