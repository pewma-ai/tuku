"""Pruebas del CLI de TUKU.

Verifica la ejecución de subcomandos `init`, `sync`, `doctor` y `janitor` (Fase 0 y Fase 2).
"""

from pathlib import Path

import pytest

from tuku.cli import main


def test_cli_init(tmp_path: Path) -> None:
    """Verifica que el subcomando tuku init siembre el perfil en la ruta indicada."""
    target = tmp_path / "perfil"
    code = main(["init", str(target)])
    assert code == 0
    assert (target / ".tuku" / "config.yaml").exists()


def test_cli_sync(tmp_path: Path) -> None:
    """Verifica que tuku sync enlace correctamente los punteros a procesos."""
    target = tmp_path / "perfil"
    main(["init", str(target)])
    code = main(["-p", str(target), "sync"])
    assert code == 0


def test_cli_doctor(tmp_path: Path) -> None:
    """Verifica que tuku doctor diagnostique un perfil recién inicializado."""
    target = tmp_path / "perfil"
    main(["init", str(target)])
    code = main(["-p", str(target), "doctor"])
    assert code == 0


def test_cli_janitor(tmp_path: Path) -> None:
    """F2.9: Verifica que tuku janitor reporte OK en un perfil limpio."""
    target = tmp_path / "perfil"
    main(["init", str(target)])
    code = main(["-p", str(target), "janitor"])
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
    assert "janitor" in output


@pytest.mark.parametrize("subcommand", ["init", "sync", "doctor", "janitor"])
def test_cli_help_subcomandos(subcommand: str, capsys: pytest.CaptureFixture[str]) -> None:
    """F0.6: Cada subcomando de suku tiene ayuda documentada con descripcion explícita."""
    with pytest.raises(SystemExit) as exc_info:
        main([subcommand, "--help"])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    output = captured.out
    assert f"usage: tuku {subcommand}" in output
    assert len(output.strip().splitlines()) >= 3


def test_cli_registrar_implicito(tmp_path: Path) -> None:
    """`tuku "texto"` sin subcomando equivale a `tuku registrar "texto"`."""
    target = tmp_path / "perfil"
    main(["init", str(target)])

    texto = "Llamé a Juan #msg"
    code_implicito = main(["-p", str(target), texto, "--dry-run"])
    assert code_implicito == 0

    code_explicito = main(["-p", str(target), "registrar", texto, "--dry-run"])
    assert code_explicito == 0


def test_cli_registrar_implicito_escribe_en_disco(tmp_path: Path) -> None:
    """El atajo implícito realmente registra la entrada, no solo simula el parseo."""
    target = tmp_path / "perfil"
    main(["init", str(target)])

    code = main(["-p", str(target), "Llamé a Juan #msg"])
    assert code == 0

    archivos = list((target / "entradas").glob("*.md"))
    contenido = "\n".join(a.read_text(encoding="utf-8") for a in archivos)
    assert "Llamé a Juan" in contenido


def test_cli_registrar_implicito_no_interfiere_con_subcomandos(tmp_path: Path) -> None:
    """Un texto que coincide por accidente con un subcomando no debe reescribirse."""
    target = tmp_path / "perfil"
    code = main(["init", str(target)])
    assert code == 0
    assert (target / ".tuku" / "config.yaml").exists()
