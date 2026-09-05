"""Test del escenario 001-003-destino-no-vacio.

Escenario: 001-003-destino-no-vacio.md

`install.sh` pregunta antes de sobrescribir un destino no vacío, y esa
pregunta corre antes de bajar nada de la red: se prueba sin `curl` ni
GitHub, con un subproceso.

El subproceso corre con `start_new_session=True` (setsid): sin terminal
de control, abrir `/dev/tty` falla y el script lee eso como respuesta
vacía, que cancela. Es el camino que toma cualquier invocación no
interactiva (un script, un cron, un agente), y es el que hay que
blindar: si algún día deja de preguntar ahí, sobrescribiría en silencio.

Ejecutable directo: `python3 tests/escenarios/test_001_003_destino_no_vacio.py`.
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
INSTALL_SH = RAIZ / "install.sh"


def test_001_003_destino_no_vacio_pregunta_y_no_sobrescribe() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        destino = Path(tmp) / "vault"
        destino.mkdir()
        centinela = destino / "algo-que-ya-estaba.txt"
        centinela.write_text("no tocar\n", encoding="utf-8")

        resultado = subprocess.run(
            ["sh", str(INSTALL_SH), str(destino)],
            start_new_session=True,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert resultado.returncode != 0, (
            f"debió cancelar, salió con {resultado.returncode}: {resultado.stderr}"
        )
        assert "Sobrescribir" in resultado.stderr, f"no preguntó: {resultado.stderr!r}"
        assert "cancelado" in resultado.stderr, f"no confirmó cancelar: {resultado.stderr!r}"
        assert list(destino.iterdir()) == [centinela], "el destino no quedó intacto"
        assert centinela.read_text(encoding="utf-8") == "no tocar\n"


if __name__ == "__main__":
    test_001_003_destino_no_vacio_pregunta_y_no_sobrescribe()
    print("ok: install.sh pregunta y no sobrescribe un destino no vacío")
