"""Test byte a byte del escenario 001-002-instalacion-local.

Escenario: 001-002-instalacion-local.md

Su afirmación es que instalar local (sin red ni curl) produce el mismo vault
que 001-001-instalacion-minima para la misma fecha. Por eso comparte los tres
pasos con ese escenario (`tests/scripts/vault.py`) en vez de duplicarlos, y
como aquel, no compara contra ninguna copia congelada del template: el árbol
va en vivo contra `template/vanilla/` y el `AHORA.md` esperado se deriva del
template real.

Si algún día divergen, el defecto está en `install.sh` (la parte que arma el
tarball y localiza `ORIGEN`), no en `instalar()`, que es lo que prueban ambos
escenarios.

Ejecutable directo: `python3 tests/escenarios/test_001_002_instalacion_local.py`.
"""

from __future__ import annotations

import sys
import tempfile
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

from install_test_scenario import instalar  # noqa: E402
from vault import ahora_sembrado, diff_recursivo, placeholders_sin_sustituir  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_001_001_instalacion_minima import DESDE, DIAS, FECHA_FIJA, HASTA  # noqa: E402

TEMPLATE_VANILLA = RAIZ / "template" / "vanilla"


def test_001_002_instalacion_local_coincide_con_001_001() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        destino = Path(tmp) / "vault"
        instalar("vanilla", destino, FECHA_FIJA)

        diferencias = diff_recursivo(destino, TEMPLATE_VANILLA, ignorar=frozenset({"AHORA.md"}))
        assert not diferencias, f"difiere de template/vanilla/: {diferencias}"

        obtenido = (destino / "AHORA.md").read_text(encoding="utf-8")
        esperado = ahora_sembrado(TEMPLATE_VANILLA, desde=DESDE, hasta=HASTA, dias=DIAS)
        assert obtenido == esperado, "AHORA.md no quedó como el template con las fechas resueltas"

        vivos = placeholders_sin_sustituir(destino)
        assert not vivos, f"quedaron placeholders sin sustituir: {vivos}"


if __name__ == "__main__":
    test_001_002_instalacion_local_coincide_con_001_001()
    print("ok: instalación local idéntica a la de 001-001, sin placeholders vivos")
