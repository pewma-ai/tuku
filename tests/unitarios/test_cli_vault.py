"""`main` rechaza fuera de un vault, salvo `note lint <archivo>`."""

from __future__ import annotations

from pathlib import Path

import pytest

from tuku.cli import EXITO, RECHAZO, main


@pytest.mark.parametrize(
    "argv",
    [
        ["doctor"],
        ["entry", "lint"],
        ["todo", "open", "--body", "x"],
        ["regenerate"],
        ["note", "lint"],
    ],
)
def test_rechaza_fuera_de_un_vault(
    argv: list[str], tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main([*argv, "--vault", str(tmp_path)]) == RECHAZO
    err = capsys.readouterr().err
    assert "no es un vault de TUKU" in err
    assert "AHORA.md" in err and "tuku init" in err, "el error no dice qué falta ni qué hacer"
    assert list(tmp_path.iterdir()) == []


def test_note_lint_de_un_archivo_suelto_no_exige_vault(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    nota = tmp_path / "nota.md"
    nota.write_text("# Nota\n\ncuerpo\n\n## Ver además\n\n", encoding="utf-8")
    codigo = main(["note", "lint", str(nota), "--vault", str(tmp_path)])
    assert codigo in (EXITO, RECHAZO)
    assert "no es un vault" not in capsys.readouterr().err
