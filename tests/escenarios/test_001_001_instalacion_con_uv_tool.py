"""Test del escenario 001-001-instalacion-con-uv-tool.

Escenario: 001-001-instalacion-con-uv-tool.md

El único test del epic que instala TUKU de verdad: `uv tool install --force`
desde `git+https://github.com/pewma-ai/tuku.git@devel`. Descarga y compila, así
que lleva el marcador `red` (además de `lento`) y **no corre en la corrida por
defecto**: `pyproject.toml` la excluye con `-m "not agentic and not red"`. Para
correrlo:

    uv run pytest tests/escenarios/ -k 001_001 -m red

Todo queda aislado: `HOME`, `UV_TOOL_DIR` y `UV_TOOL_BIN_DIR` apuntan a un
tempdir, así que la instalación no toca el `~` real ni las tools que el autor ya
tenga. El branch `devel` tiene que estar empujado a GitHub para que esto
resuelva.

Afirma tres cosas, el camino completo de la decisión 1 del epic:

1. `uv tool install` deja el ejecutable `tuku` en el bin dir y `tuku --help`
   responde.
2. `tuku init <dir>` sobre un directorio vacío siembra un vault operable
   (`AHORA.md` con los días resueltos, sin placeholders).
3. Esa primera siembra deja `~/.tuku/template/vanilla/` poblado desde la copia
   que el wheel trae empaquetada (decisión 2): el árbol queda a la vista y
   editable, sin que `tuku init` toque la red.

Ejecutable directo (corre igual que con pytest, sin el filtro de marcador):
`python3 tests/escenarios/test_001_001_instalacion_con_uv_tool.py`
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

from vault import placeholders_sin_sustituir  # noqa: E402

GIT_URL = "git+https://github.com/pewma-ai/tuku.git@devel"


@pytest.mark.red
@pytest.mark.lento
def test_001_001_uv_tool_install_deja_tuku_y_puebla_tuku_home() -> None:
    if shutil.which("uv") is None:
        pytest.skip("uv no está en el PATH")

    with tempfile.TemporaryDirectory() as tmp:
        raiz_tmp = Path(tmp)
        home = raiz_tmp / "home"
        tool_dir = raiz_tmp / "uv-tools"
        bin_dir = raiz_tmp / "uv-bin"
        for d in (home, tool_dir, bin_dir):
            d.mkdir()

        entorno = {
            **os.environ,
            "HOME": str(home),
            "UV_TOOL_DIR": str(tool_dir),
            "UV_TOOL_BIN_DIR": str(bin_dir),
        }
        # Que no herede un TUKU_HOME del entorno del autor: se prueba la
        # resolución a ~/.tuku (aquí, home/.tuku) desde la copia empaquetada.
        entorno.pop("TUKU_HOME", None)

        instalacion = subprocess.run(
            ["uv", "tool", "install", "--force", GIT_URL],
            env=entorno,
            capture_output=True,
            text=True,
            timeout=600,
        )
        assert instalacion.returncode == 0, (
            f"uv tool install falló ({instalacion.returncode}):\n{instalacion.stderr}"
        )

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
        siembra = subprocess.run(
            [str(tuku), "init", str(vault)],
            env=entorno,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert siembra.returncode == 0, f"`tuku init` falló: {siembra.stderr}"

        for archivo in ("AHORA.md", "PENDIENTES.md", "AGENTS.md", "LIBRO-DE-ESTILO.md"):
            assert (vault / archivo).is_file(), f"falta {archivo} en el vault sembrado"
        assert not placeholders_sin_sustituir(vault), "quedaron placeholders vivos"
        assert "DD de mes" not in (vault / "AHORA.md").read_text(encoding="utf-8")

        poblado = home / ".tuku" / "template" / "vanilla"
        assert poblado.is_dir(), (
            f"tuku init no pobló ~/.tuku desde la copia empaquetada: {poblado} no existe"
        )
        assert (poblado / "AHORA.md").is_file()


if __name__ == "__main__":
    test_001_001_uv_tool_install_deja_tuku_y_puebla_tuku_home()
    print("ok: uv tool install dejó tuku, tuku init sembró el vault y pobló ~/.tuku")
