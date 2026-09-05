"""Test byte a byte del escenario 001-001-instalacion-minima.

Corpus: ../../corpus/escenarios/001-001-instalacion-minima.md

Fecha fija: 2026-08-11 (martes), el mismo día donde arranca el ground truth
de corpus/referencia/referencia-developer.md ("Turno Faena"). El usuario
real instala con la fecha de hoy (ver template/README.md); este test fija
la fecha para que el resultado sea comparable byte a byte, siempre, tal
como pide el principio 9.

Ejecutable directo (sin pytest instalado, que hoy no lo está en este
repo): `python3 tests/escenarios/test_001_001_instalacion_minima.py`. Cuando el
entorno tenga pytest, esta misma función se recolecta sola por su nombre.
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
ESPERADO = Path(__file__).resolve().parent / "fixtures" / "001-001-instalacion-minima" / "esperado"


def _diff_recursivo(a: Path, b: Path) -> list[str]:
    cmp = filecmp.dircmp(a, b)
    diferencias = [*cmp.left_only, *cmp.right_only, *cmp.diff_files]
    for sub in cmp.common_dirs:
        diferencias += [f"{sub}/{d}" for d in _diff_recursivo(a / sub, b / sub)]
    return diferencias


def test_001_001_instalacion_minima_byte_a_byte() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        destino = Path(tmp) / "vault"
        instalar("vanilla", destino, FECHA_FIJA)
        diferencias = _diff_recursivo(destino, ESPERADO)
        assert not diferencias, f"difiere de {ESPERADO}: {diferencias}"


if __name__ == "__main__":
    test_001_001_instalacion_minima_byte_a_byte()
    print("ok: instalación idéntica byte a byte al fixture esperado")
