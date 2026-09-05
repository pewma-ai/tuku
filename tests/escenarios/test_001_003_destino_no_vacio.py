"""Tests del escenario 001-003-destino-no-vacio.

Escenario: 001-003-destino-no-vacio.md

`install.sh` pregunta antes de sobrescribir un destino no vacío, y esa
pregunta corre antes de bajar nada de la red: los dos casos se prueban
sin `curl` ni GitHub.

El primer test simula que nadie respondió: el subproceso corre con
`start_new_session=True` (setsid), sin terminal de control, así que
abrir `/dev/tty` falla y el script lee eso como respuesta vacía, que
cancela. Es el camino que toma cualquier invocación no interactiva (un
script, un cron, un agente), y es el que hay que blindar: si algún día
deja de preguntar ahí, sobrescribiría en silencio.

El segundo simula que sí se confirma ("s"), que sí necesita una tty de
verdad: `read -r r < /dev/tty` no lee de la entrada estándar, así que un
`subprocess` con pipes no sirve para escribirle una respuesta. `pexpect`
abre una pty y la deja como terminal de control del hijo, que es lo que
el script necesita. No se espera a que la descarga real termine (no hay
por qué depender de que la red funcione): basta con ver que imprime
"bajando..." en vez de "cancelado" para saber que pasó la pregunta, y
ahí se mata el proceso.

Ejecutable directo: `python3 tests/escenarios/test_001_003_destino_no_vacio.py`.
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

import pexpect

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


def test_001_003_destino_no_vacio_confirma_y_continua() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        destino = Path(tmp) / "vault"
        destino.mkdir()
        (destino / "algo-que-ya-estaba.txt").write_text("no tocar\n", encoding="utf-8")

        hijo = pexpect.spawn(
            "sh", [str(INSTALL_SH), str(destino)], timeout=10, encoding="utf-8"
        )
        try:
            hijo.expect(r"Sobrescribir\? \[s/N\]")
            hijo.sendline("s")
            indice = hijo.expect(["bajando", "cancelado"])
            assert indice == 0, f"no continuó tras confirmar: {hijo.before!r}"
        finally:
            hijo.close(force=True)


if __name__ == "__main__":
    test_001_003_destino_no_vacio_pregunta_y_no_sobrescribe()
    test_001_003_destino_no_vacio_confirma_y_continua()
    print("ok: install.sh pregunta, no sobrescribe sin confirmar, y continúa si se confirma")
