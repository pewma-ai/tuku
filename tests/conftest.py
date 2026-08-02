"""Fixtures compartidas de la suite de TUKU.

Reglas que esta suite hace cumplir por construcción:

- Ningún test toca datos reales. Todo perfil vive en `tmp_path` y se destruye.
- `TZ=UTC` en todo el proceso: medio sistema resuelve fechas relativas, y un test
  que pase en Chile y falle en CI por zona horaria es una tarde perdida.
- Los tests agénticos están excluidos por defecto (marcador `agentic`).

Ver `devel/plan-implementacion.md` §3 (estrategia) y §4 (Hermes).
"""

from __future__ import annotations

import os
import shutil
import subprocess
import time
from pathlib import Path

import pytest

# La zona horaria se fija antes de que nadie llame a time.localtime().
os.environ["TZ"] = "UTC"
if hasattr(time, "tzset"):
    time.tzset()

REPO_ROOT = Path(__file__).resolve().parent.parent
SPEC_DIR = REPO_ROOT / "spec"
SIMULACIONES_DIR = REPO_ROOT / "corpus" / "simulaciones"
DOCS_DIR = REPO_ROOT / "docs"


# ---------------------------------------------------------------------------
# Rutas del repositorio
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def spec_dir() -> Path:
    return SPEC_DIR


# ---------------------------------------------------------------------------
# Perfiles desechables
# ---------------------------------------------------------------------------


@pytest.fixture
def perfil_vacio(tmp_path: Path) -> Path:
    """Un directorio vacío con Git inicializado, listo para `tuku init`.

    Git importa incluso antes de que exista el motor: el criterio de varios
    tests de derivación es "el diff es exactamente cero", y eso se mide con Git.
    """
    perfil = tmp_path / "perfil"
    perfil.mkdir()
    _git(perfil, "init", "--quiet")
    _git(perfil, "config", "user.email", "test@tuku.invalid")
    _git(perfil, "config", "user.name", "TUKU Test")
    _git(perfil, "config", "commit.gpgsign", "false")
    return perfil


@pytest.fixture
def perfil_tmp(perfil_vacio: Path) -> Path:
    """Perfil sembrado por `tuku init`.

    Llama a `init_perfil()` en proceso en vez de invocar el binario `tuku` vía
    subprocess: mismo código que ejecuta `tuku init` (`cli.py` delega en esta
    función), sin pagar un arranque de intérprete por test. Con ~20 tests que
    consumen esta fixture, eso ahorra varios segundos por corrida.
    """
    from tuku.core.init import init_perfil

    init_perfil(perfil_vacio)
    return perfil_vacio


@pytest.fixture
def commit_inicial(perfil_tmp: Path):
    """Deja el perfil sembrado en un commit, para poder medir diffs después."""
    _git(perfil_tmp, "add", "-A")
    _git(perfil_tmp, "commit", "--quiet", "-m", "estado inicial")
    return perfil_tmp


# ---------------------------------------------------------------------------
# Utilidades de Git — el juez del "diff exactamente cero"
# ---------------------------------------------------------------------------


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    )


def git_diff(perfil: Path) -> str:
    """Diff del árbol de trabajo contra HEAD, incluyendo archivos nuevos."""
    _git(perfil, "add", "-A", "--intent-to-add")
    return subprocess.run(
        ["git", "diff", "HEAD"], cwd=perfil, capture_output=True, text=True
    ).stdout


def assert_diff_cero(perfil: Path, contexto: str = "") -> None:
    """El criterio del nivel 4 para lo producido por janitors.

    No es "parecido": es idéntico. Un diff no vacío aquí es un defecto de código,
    salvo que el artefacto lo haya producido un agente (ver plan §3, nivel 4).
    """
    diff = git_diff(perfil)
    if diff.strip():
        cabecera = f"Se esperaba diff cero{f' ({contexto})' if contexto else ''}."
        raise AssertionError(f"{cabecera}\n\n{diff}")


# ---------------------------------------------------------------------------
# Estado del motor: qué está implementado y qué no
# ---------------------------------------------------------------------------


def motor_implementa(subcomando: str | None = None) -> bool:
    """¿Existe el CLI y responde el subcomando?

    Durante F0 el `main()` levanta SystemExit('no implementado aún'). Esta
    función es lo que permite que la suite crezca antes que el código sin vivir
    en rojo permanente: los tests de lo no implementado se marcan `skip`, que es
    honesto, en vez de `xfail`, que esconde regresiones reales.
    """
    if shutil.which("tuku") is None:
        return False
    cmd = ["tuku", subcomando, "--help"] if subcomando else ["tuku", "--help"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return False
    return proc.returncode == 0


requiere_motor = pytest.mark.skipif(
    not motor_implementa(), reason="el CLI `tuku` aún no está implementado (F0)"
)


# ---------------------------------------------------------------------------
# Hermes — perfil efímero (ADR 0018)
# ---------------------------------------------------------------------------


@pytest.fixture
def hermes_efimero(perfil_tmp: Path) -> dict[str, str]:
    """Entorno con `HERMES_HOME` apuntando al directorio `.hermes/` del perfil.

    `tuku init` (llamado por `perfil_tmp`) ya provisiona `.hermes/` con
    symlinks a credenciales y config mínima (ADR 0018). Esta fixture solo
    expone el `env` resultante para que los tests lo pasen a `subprocess.run`.

    Si `~/.hermes` no existe (CI sin Hermes), el test que use esta fixture
    se marca skip automáticamente para no bloquear la suite determinista.
    """
    hermes_home = perfil_tmp / ".hermes"
    if not hermes_home.exists():
        pytest.skip("~/.hermes no encontrado — Hermes no instalado en este entorno")
    return {
        **os.environ,
        "HERMES_HOME": str(hermes_home),
        "TZ": "UTC",
        "NO_COLOR": "1",
    }


def hermes_oneshot(env: dict[str, str], prompt: str, timeout: int = 180) -> str:
    """Invoca Hermes en modo oneshot y devuelve solo la respuesta final.

    Usa `hermes -z <prompt> --continue` (ADR 0018): `-z`/`--continue` son
    flags globales de Hermes, no del subcomando `chat`. Sin --safe-mode:
    Hermes accede a la memoria del perfil y aprende. El aislamiento lo da
    HERMES_HOME apuntando al .hermes/ del perfil efímero.
    """
    if shutil.which("hermes") is None:
        pytest.skip("hermes no está instalado en este entorno")
    proc = subprocess.run(
        [
            "hermes",
            "-z",
            prompt,
            "--continue",
        ],
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if proc.returncode != 0:
        pytest.fail(f"hermes falló ({proc.returncode}):\n{proc.stderr}")
    return proc.stdout.strip()
