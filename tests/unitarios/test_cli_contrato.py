"""El contrato del CLI: rechazo fuera de un vault, correcciones y lectura del cuerpo."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pytest

from tuku import cli
from tuku.cli import EXITO, RECHAZO, main
from tuku.lint import lint

RAIZ = Path(__file__).resolve().parent.parent.parent
PERSONAL = "[personal](ambitos/personal/personal.md)"


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


def test_el_cuerpo_no_se_busca_en_stdin_sin_pedirlo(monkeypatch: pytest.MonkeyPatch) -> None:
    """`stdin` se lee solo con `--body-file -`: un pipe abierto y vacío colgaría el comando."""

    class StdinQueNadieDebeLeer:
        def isatty(self) -> bool:
            return False

        def read(self) -> str:
            raise AssertionError("leyó stdin sin que se lo pidieran")

    monkeypatch.setattr(sys, "stdin", StdinQueNadieDebeLeer())
    assert cli._cuerpo_de_la_nota(argparse.Namespace(body=None, body_file=None)) is None
