from pathlib import Path

import pytest

from tuku.cli import main


def test_cli_init(tmp_path: Path) -> None:
    target = tmp_path / "perfil"
    code = main(["init", str(target)])
    assert code == 0
    assert (target / ".tuku" / "config.yaml").exists()


def test_cli_sync(tmp_path: Path) -> None:
    target = tmp_path / "perfil"
    main(["init", str(target)])
    code = main(["-p", str(target), "sync"])
    assert code == 0


def test_cli_doctor(tmp_path: Path) -> None:
    target = tmp_path / "perfil"
    main(["init", str(target)])
    code = main(["-p", str(target), "doctor"])
    assert code == 0


def test_cli_help_general(capsys: pytest.CaptureFixture[str]) -> None:
    """F0.6: tuku --help mudo muestra uso, epílogo con ejemplos y lista subcomandos."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    output = captured.out
    assert "TUKU — Management as Code" in output
    assert "Ejemplos:" in output
    assert "init" in output
    assert "sync" in output
    assert "doctor" in output


@pytest.mark.parametrize("subcommand", ["init", "sync", "doctor"])
def test_cli_help_subcomandos(subcommand: str, capsys: pytest.CaptureFixture[str]) -> None:
    """F0.6: Cada subcomando de suku tiene ayuda documentada con descripcion explícita."""
    with pytest.raises(SystemExit) as exc_info:
        main([subcommand, "--help"])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    output = captured.out
    assert f"usage: tuku {subcommand}" in output
    assert len(output.strip().splitlines()) >= 3
