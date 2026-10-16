"""Tests del escenario 001-01-instalacion-con-uv-tool.

Instala TUKU por las tres vías (`uv tool` y `pipx` desde git, `pipx` desde este
checkout) y afirma que `tuku --help` responde, que `tuku init` siembra un vault
operable y que deja `~/.tuku/template/vanilla/` poblado. `HOME` y los
directorios de herramientas van a un tempdir.

Este arnés no toma los comandos del `.md`, porque lo que prueba es el ejecutable
instalado y no `tuku` en proceso. El `.md` manda.

Se corre con el marcador `red`: `uv run pytest tests/escenarios/ -k 001_01 -m red`
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

from vault import placeholders_sin_sustituir  # noqa: E402

GIT_URL = "git+https://github.com/pewma-ai/tuku.git@devel"


@contextmanager
def _entorno_aislado() -> Iterator[tuple[Path, dict[str, str], Path]]:
    """Un `HOME` y unos directorios de herramientas propios, en un tempdir.

    Devuelve la raíz temporal, el entorno para los subprocesos y el directorio
    donde va a quedar el ejecutable. `PATH` lleva ese bin dir adelante, así que
    `tuku` se resuelve al recién instalado y no a uno que el autor ya tuviera.
    """
    with tempfile.TemporaryDirectory() as tmp:
        raiz_tmp = Path(tmp)
        home = raiz_tmp / "home"
        bin_dir = raiz_tmp / "bin"
        for d in (home, bin_dir):
            d.mkdir()

        entorno = {
            **os.environ,
            "HOME": str(home),
            "UV_TOOL_DIR": str(raiz_tmp / "uv-tools"),
            "UV_TOOL_BIN_DIR": str(bin_dir),
            "PIPX_HOME": str(raiz_tmp / "pipx"),
            "PIPX_BIN_DIR": str(bin_dir),
            "PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}",
        }
        # Que no herede un TUKU_HOME del entorno del autor: se prueba la
        # resolución a ~/.tuku (aquí, home/.tuku) desde la copia empaquetada.
        entorno.pop("TUKU_HOME", None)
        yield raiz_tmp, entorno, bin_dir


def _correr(argv: list[str], entorno: dict[str, str], *, timeout: int = 600) -> None:
    proceso = subprocess.run(
        argv, env=entorno, capture_output=True, text=True, timeout=timeout
    )
    assert proceso.returncode == 0, (
        f"`{' '.join(argv)}` falló ({proceso.returncode}):\n{proceso.stderr}"
    )


def _verificar_instalacion(raiz_tmp: Path, entorno: dict[str, str], bin_dir: Path) -> None:
    """Las tres afirmaciones, iguales para las tres vías de instalación."""
    tuku = bin_dir / "tuku"
    assert tuku.is_file(), (
        f"no quedó el ejecutable tuku en {bin_dir}: {list(bin_dir.iterdir())}"
    )

    ayuda = subprocess.run(
        [str(tuku), "--help"], env=entorno, capture_output=True, text=True, timeout=30
    )
    assert ayuda.returncode == 0, f"`tuku --help` falló: {ayuda.stderr}"
    assert "init" in ayuda.stdout, f"`tuku --help` no menciona init: {ayuda.stdout!r}"

    vault = raiz_tmp / "mi-vault"
    _correr([str(tuku), "init", str(vault)], entorno, timeout=30)

    for archivo in ("AHORA.md", "PENDIENTES.md", "AGENTS.md", "LIBRO-DE-ESTILO.md"):
        assert (vault / archivo).is_file(), f"falta {archivo} en el vault sembrado"
    assert not placeholders_sin_sustituir(vault), "quedaron placeholders vivos"
    assert "DD de mes" not in (vault / "AHORA.md").read_text(encoding="utf-8")

    poblado = Path(entorno["HOME"]) / ".tuku" / "template" / "vanilla"
    assert poblado.is_dir(), (
        f"tuku init no pobló ~/.tuku desde la copia empaquetada: {poblado} no existe"
    )
    # La plantilla del ciclo, que es lo que `tuku init` lee para sembrar `AHORA.md`.
    assert (poblado / "reglas" / "plantilla" / "AHORA.md").is_file(), (
        f"la copia empaquetada no trae la plantilla del ciclo: {list(poblado.iterdir())}"
    )
    assert (poblado / "LIBRO-DE-ESTILO.md").is_file()


@pytest.mark.red
@pytest.mark.lento
def test_001_01_uv_tool_install_desde_git() -> None:
    if shutil.which("uv") is None:
        pytest.skip("uv no está en el PATH")

    with _entorno_aislado() as (raiz_tmp, entorno, bin_dir):
        _correr(["uv", "tool", "install", "--force", GIT_URL], entorno)
        _verificar_instalacion(raiz_tmp, entorno, bin_dir)


@pytest.mark.red
@pytest.mark.lento
def test_001_01_pipx_install_desde_git() -> None:
    if shutil.which("pipx") is None:
        pytest.skip("pipx no está en el PATH")

    with _entorno_aislado() as (raiz_tmp, entorno, bin_dir):
        _correr(["pipx", "install", "--force", GIT_URL], entorno)
        _verificar_instalacion(raiz_tmp, entorno, bin_dir)


@pytest.mark.red
@pytest.mark.lento
def test_001_01_pipx_install_desde_este_repositorio() -> None:
    """El único que prueba el código de este checkout, sin commitear ni empujar."""
    if shutil.which("pipx") is None:
        pytest.skip("pipx no está en el PATH")

    with _entorno_aislado() as (raiz_tmp, entorno, bin_dir):
        _correr(["pipx", "install", "--force", str(RAIZ)], entorno)
        _verificar_instalacion(raiz_tmp, entorno, bin_dir)


if __name__ == "__main__":
    test_001_01_uv_tool_install_desde_git()
    test_001_01_pipx_install_desde_git()
    test_001_01_pipx_install_desde_este_repositorio()
    print("ok: las tres instalaciones dejan tuku, siembran el vault y pueblan ~/.tuku")
