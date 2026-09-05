"""Test byte a byte del escenario 001-001-instalacion-minima.

Escenario: 001-001-instalacion-minima.md

`instalar()` hace dos cosas: copia `template/vanilla/` tal cual, y sustituye
las fechas de `AHORA.md`. Solo lo segundo necesita un fixture congelado
(fixtures/001-001-instalacion-minima/AHORA.md, para la fecha fija
de abajo); todo lo demás se compara en vivo contra `template/vanilla/`, para
que un cambio en el template no exija acordarse de regenerar una copia
paralela que nunca debería haber divergido. Si el árbol de destino agrega
o quita un archivo respecto a `template/vanilla/`, el test también lo dice.

Fecha fija: 2026-08-11 (martes), el mismo día donde arranca el ground truth
de corpus/referencia/referencia-faena.md ("Turno Faena"). El usuario
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
TEMPLATE_VANILLA = RAIZ / "template" / "vanilla"
AHORA_ESPERADO = Path(__file__).resolve().parent / "fixtures" / "001-001-instalacion-minima" / "AHORA.md"


def _diff_recursivo(a: Path, b: Path, *, ignorar: set[str] = frozenset()) -> list[str]:
    cmp = filecmp.dircmp(a, b, ignore=list(ignorar))
    diferencias = [*cmp.left_only, *cmp.right_only, *cmp.diff_files]
    for sub in cmp.common_dirs:
        diferencias += [f"{sub}/{d}" for d in _diff_recursivo(a / sub, b / sub)]
    return diferencias


def test_001_001_instalacion_minima_byte_a_byte() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        destino = Path(tmp) / "vault"
        instalar("vanilla", destino, FECHA_FIJA)

        diferencias = _diff_recursivo(destino, TEMPLATE_VANILLA, ignorar={"AHORA.md"})
        assert not diferencias, f"difiere de template/vanilla/: {diferencias}"

        ahora_obtenido = (destino / "AHORA.md").read_text(encoding="utf-8")
        ahora_esperado = AHORA_ESPERADO.read_text(encoding="utf-8")
        assert ahora_obtenido == ahora_esperado, "AHORA.md no coincide con el fixture de fecha fija"


if __name__ == "__main__":
    test_001_001_instalacion_minima_byte_a_byte()
    print("ok: instalación idéntica a template/vanilla/, y AHORA.md idéntico al fixture de fecha fija")
