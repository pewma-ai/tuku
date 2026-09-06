"""Test del escenario 001-004-instalador-pregunta-el-nombre.

Escenario: 001-004-instalador-pregunta-el-nombre.md

Cierra la capa de identidad, y es la única cobertura del flag `--autor`:
prueba el camino completo desde que una persona teclea su nombre hasta que
queda en el archivo. `install.sh` lo pregunta por `/dev/tty`, lo
guarda en una variable, lo arma con `set --` y se lo pasa como `--autor`. Ese
texto atraviesa cuatro capas de citado y en cualquiera de ellas se puede
partir, por eso el nombre que se responde es `ARTURO PEREZ-REVERTE (Arturo)`,
con espacios, paréntesis y guion: un valor que un `$AUTOR` sin comillas
rompería de inmediato.

`pexpect` y no `subprocess` por lo mismo que en el 001-003: `read -r r <
/dev/tty` no lee la entrada estándar, así que hay que darle una pty real como
terminal de control.

Dos diferencias con los tests del 001-003, y las dos son a propósito:

- **Este deja que la instalación complete.** Espera el `EOF` y el estado de
  salida 0, en vez de matar el proceso apenas ve "bajando". Puede hacerlo
  porque no hay descarga: `TUKU_ORIGEN` apunta a la raíz del repositorio ya
  presente en disco y `install.sh` se salta el bloque de `curl | tar` entero.
  Y debe hacerlo porque el artefacto que queda en `playground/` es justamente
  lo que el escenario pide mirar a mano.
- **Instala en `playground/`**, no en un tempdir. Como `preparar_playground()`
  vacía la carpeta antes, el destino no existe cuando arranca `install.sh`, así
  que la pregunta de sobrescritura no se dispara y el único prompt es el del
  nombre. El test no da eso por supuesto: si aparece la otra pregunta, falla
  diciéndolo.

Fecha fija `--desde 2026-08-11`, la misma que fijan 001-001 y 001-002, para
que el vault resultante se pueda comparar con `diff -r` contra los de ellos.

Ejecutable directo:
`python3 tests/escenarios/test_001_004_instalador_pregunta_el_nombre.py`
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pexpect

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

from vault import placeholders_sin_sustituir, preparar_playground  # noqa: E402

INSTALL_SH = RAIZ / "install.sh"
SLUG = "001-004-instalador-pregunta-el-nombre"
DESDE = "2026-08-11"
AUTOR = "ARTURO PEREZ-REVERTE (Arturo)"


def test_001_004_instalador_pregunta_el_nombre_y_lo_escribe() -> None:
    destino = preparar_playground(SLUG)

    hijo = pexpect.spawn(
        "sh",
        [str(INSTALL_SH), str(destino), DESDE],
        env={**os.environ, "TUKU_ORIGEN": str(RAIZ)},
        timeout=10,
        encoding="utf-8",
    )
    try:
        # El destino acaba de ser vaciado, así que el único prompt esperado es
        # el del nombre. Si aparece el de sobrescritura, algo cambió en la
        # preparación del playground y el test lo dice en vez de responderlo.
        indice = hijo.expect(["Nombre del autor", "Sobrescribir"])
        assert indice == 0, (
            f"install.sh preguntó por sobrescribir un destino que debía estar vacío: {destino}"
        )
        hijo.sendline(AUTOR)
        hijo.expect(pexpect.EOF)
        salida = hijo.before or ""
    finally:
        hijo.close()

    assert hijo.exitstatus == 0, (
        f"install.sh no terminó bien (exitstatus={hijo.exitstatus}, "
        f"signalstatus={hijo.signalstatus}): {salida!r}"
    )
    assert "bajando" not in salida, f"bajó el tarball habiendo TUKU_ORIGEN: {salida!r}"

    libro = (destino / "LIBRO-DE-ESTILO.md").read_text(encoding="utf-8")
    assert f"**Nombre del autor:** {AUTOR}" in libro, (
        f"el nombre no llegó al libro de estilo: {libro[:400]!r}"
    )
    assert "por declarar" not in libro, "quedó el placeholder del nombre sin sustituir"

    # El vault quedó completo, no solo el archivo que este escenario toca.
    for archivo in ("AHORA.md", "PENDIENTES.md", "AGENTS.md"):
        assert (destino / archivo).is_file(), f"falta {archivo} en el vault instalado"

    vivos = placeholders_sin_sustituir(destino)
    assert not vivos, f"quedaron placeholders sin sustituir: {vivos}"


if __name__ == "__main__":
    test_001_004_instalador_pregunta_el_nombre_y_lo_escribe()
    print(
        "ok: install.sh preguntó el nombre, lo escribió en LIBRO-DE-ESTILO.md y no bajó nada "
        f"(queda en playground/{SLUG}/)"
    )
