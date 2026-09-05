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

El tercero prueba que `TUKU_FORCE=1` salta la pregunta entera: ni
siquiera necesita una tty, porque el `if` que la dispara no se ejecuta.
Mismo criterio que el segundo: se lee la primera línea de `stderr` y se
mata el proceso apenas se confirma que fue "bajando...", sin esperar la
descarga real.

En el segundo y el tercero, "matar el proceso" tiene que matar el grupo
entero (`os.killpg`), no solo el pid del shell: para cuando se los mata
ya lanzaron `curl | tar` como su propia tubería, y una señal al shell no
siempre alcanza a esos hijos ni llega a tiempo, lo que dejaba el test
colgado esperando a que una descarga real terminara.

Ejecutable directo: `python3 tests/escenarios/test_001_003_destino_no_vacio.py`.
"""

from __future__ import annotations

import contextlib
import os
import signal
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
            # SIGKILL solo a hijo.pid no basta: pexpect crea una sesión nueva
            # (hijo.pid es el líder de grupo), pero install.sh ya lanzó a esa
            # altura la tubería curl | tar como procesos propios. Matar el
            # grupo entero evita dejarlos corriendo en segundo plano o, peor,
            # que este `finally` se quede esperando a que el shell reaccione
            # a una señal que a veces solo procesa al terminar el comando en
            # curso.
            with contextlib.suppress(ProcessLookupError):
                os.killpg(hijo.pid, signal.SIGKILL)
            hijo.close(force=True)


def test_001_003_destino_no_vacio_tuku_force_salta_la_pregunta() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        destino = Path(tmp) / "vault"
        destino.mkdir()
        (destino / "algo-que-ya-estaba.txt").write_text("no tocar\n", encoding="utf-8")

        proceso = subprocess.Popen(
            ["sh", str(INSTALL_SH), str(destino)],
            env={**os.environ, "TUKU_FORCE": "1"},
            stdin=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )
        try:
            primera_linea = proceso.stderr.readline()
        finally:
            # Matar solo proceso.pid no basta: es el shell, y para esa altura
            # ya lanzó curl | tar como su propia tubería. SIGTERM al shell no
            # siempre corta esos hijos, y algunos shells difieren la señal
            # hasta que el comando en curso termina, lo que deja el `wait()`
            # colgado esperando una descarga real. Con start_new_session=True
            # el pid del proceso es también el del grupo: matar el grupo se
            # lleva puesto todo.
            with contextlib.suppress(ProcessLookupError):
                os.killpg(proceso.pid, signal.SIGKILL)
            proceso.wait(timeout=5)
            proceso.stderr.close()

        assert "Sobrescribir" not in primera_linea, f"preguntó igual: {primera_linea!r}"
        assert "bajando" in primera_linea, f"no continuó: {primera_linea!r}"


if __name__ == "__main__":
    test_001_003_destino_no_vacio_pregunta_y_no_sobrescribe()
    test_001_003_destino_no_vacio_confirma_y_continua()
    test_001_003_destino_no_vacio_tuku_force_salta_la_pregunta()
    print("ok: install.sh pregunta, respeta la respuesta, y TUKU_FORCE=1 la salta")
