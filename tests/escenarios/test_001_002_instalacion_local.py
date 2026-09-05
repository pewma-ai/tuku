"""Test byte a byte del escenario 001-002-instalacion-local.

Escenario: 001-002-instalacion-local.md

Este escenario no tiene fixture propio: su afirmación es que instalar
local (sin red ni curl) produce el mismo vault que 001-001-instalacion-minima
para la misma fecha. Por eso compara, igual que ese otro test, contra
`template/vanilla/` en vivo (todo salvo AHORA.md, que `instalar()` sustituye)
y contra el mismo fixture de AHORA.md, en vez de duplicar ninguno de los dos.
Si algún día divergen, el defecto está en `install.sh` (la parte que arma
el tarball y localiza `ORIGEN`), no en `instalar()`, que es lo que prueban
ambos escenarios.

Ejecutable directo: `python3 tests/escenarios/test_001_002_instalacion_local.py`.
"""

from __future__ import annotations

import filecmp
import sys
import tempfile
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from install_test_scenario import instalar  # noqa: E402

FECHA_FIJA = date(2026, 8, 11)
TEMPLATE_VANILLA = RAIZ / "template" / "vanilla"
AHORA_ESPERADO = Path(__file__).resolve().parent / "fixtures" / "001-001-instalacion-minima" / "esperado" / "AHORA.md"


def _diff_recursivo(a: Path, b: Path, *, ignorar: set[str] = frozenset()) -> list[str]:
    cmp = filecmp.dircmp(a, b, ignore=list(ignorar))
    diferencias = [*cmp.left_only, *cmp.right_only, *cmp.diff_files]
    for sub in cmp.common_dirs:
        diferencias += [f"{sub}/{d}" for d in _diff_recursivo(a / sub, b / sub)]
    return diferencias


def test_001_002_instalacion_local_coincide_con_001_001() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        destino = Path(tmp) / "vault"
        instalar("vanilla", destino, FECHA_FIJA)

        diferencias = _diff_recursivo(destino, TEMPLATE_VANILLA, ignorar={"AHORA.md"})
        assert not diferencias, f"difiere de template/vanilla/: {diferencias}"

        ahora_obtenido = (destino / "AHORA.md").read_text(encoding="utf-8")
        ahora_esperado = AHORA_ESPERADO.read_text(encoding="utf-8")
        assert ahora_obtenido == ahora_esperado, "AHORA.md no coincide con el fixture de fecha fija"


if __name__ == "__main__":
    test_001_002_instalacion_local_coincide_con_001_001()
    print("ok: instalación local idéntica a template/vanilla/, y AHORA.md idéntico al fixture de fecha fija")
