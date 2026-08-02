from pathlib import Path

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
