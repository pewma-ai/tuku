"""Test del escenario 001-02-init-siembra-el-estado-cero.

Con la red bloqueada, `tuku init` deja un árbol idéntico a `template/vanilla/`
salvo lo que resuelve, un `AHORA.md` con las siete fechas y ningún placeholder
vivo. Compara contra el template en vivo, nunca contra una copia congelada.

Ejecutable directo: `python3 tests/escenarios/test_001_02_init_siembra_el_estado_cero.py`
"""

from __future__ import annotations

import socket
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import gherkin  # noqa: E402
from vault import (  # noqa: E402
    ahora_sembrado,
    diff_recursivo,
    placeholders_sin_sustituir,
)

from tuku.cli import EXITO, manual  # noqa: E402

SLUG = "001-02-init-siembra-el-estado-cero"

FECHA_FIJA = date(2026, 8, 11)
TEMPLATE_VANILLA = RAIZ / "template" / "vanilla"

#: Los siete días que corresponden a FECHA_FIJA, escritos a mano: es lo único que
#: el test no deriva del template.
DESDE, HASTA = "2026-08-10", "2026-08-16"
DIAS = [
    "## Lunes 10 de agosto",
    "## Martes 11 de agosto",
    "## Miércoles 12 de agosto",
    "## Jueves 13 de agosto",
    "## Viernes 14 de agosto",
    "## Sábado 15 de agosto",
    "## Domingo 16 de agosto",
]


class RedBloqueada(RuntimeError):
    """Algo intentó tocar la red durante `tuku init`."""


@contextmanager
def _sin_red() -> Iterator[None]:
    def _prohibido(*_args: object, **_kwargs: object) -> object:
        raise RedBloqueada("init intentó abrir un socket")

    originales = {
        "socket": socket.socket,
        "create_connection": socket.create_connection,
        "getaddrinfo": socket.getaddrinfo,
    }
    socket.socket = _prohibido  # type: ignore[assignment,misc]
    socket.create_connection = _prohibido  # type: ignore[assignment]
    socket.getaddrinfo = _prohibido  # type: ignore[assignment]
    try:
        yield
    finally:
        for nombre, valor in originales.items():
            setattr(socket, nombre, valor)


def test_001_02_init_siembra_el_estado_cero_byte_a_byte() -> None:
    with _sin_red():
        corrida = gherkin.correr(SLUG, "produce el estado cero")
    assert corrida.codigo == EXITO, corrida.stderr
    destino = corrida.ruta("mi-vault")

    # Lo que la instalación resuelve: el ciclo, la zona horaria y el manual de
    # comandos, que sale de la ayuda del `tuku` instalado y no del template.
    # El resto tiene que ser idéntico al template, byte a byte.
    resueltos = frozenset({"AHORA.md", "config.tuku.md", "comandos.tuku.md"})
    diferencias = diff_recursivo(destino, TEMPLATE_VANILLA, ignorar=resueltos)
    assert not diferencias, f"difiere de template/vanilla/: {diferencias}"

    manual_escrito = (destino / "reglas" / "comandos.tuku.md").read_text(encoding="utf-8")
    assert manual_escrito == manual.del_cli(), "reglas/comandos.tuku.md no es el del CLI"

    obtenido = (destino / "AHORA.md").read_text(encoding="utf-8")
    esperado = ahora_sembrado(TEMPLATE_VANILLA, desde=DESDE, hasta=HASTA, dias=DIAS)
    assert obtenido == esperado, "AHORA.md no quedó como el template con las fechas resueltas"

    vivos = placeholders_sin_sustituir(destino)
    assert not vivos, f"quedaron placeholders sin sustituir: {vivos}"


if __name__ == "__main__":
    test_001_02_init_siembra_el_estado_cero_byte_a_byte()
    print(
        "ok: árbol idéntico a template/vanilla/, AHORA.md sembrado, sin placeholders vivos, "
        "sin red "
        "(queda en playground/001-02-init-siembra-el-estado-cero/)"
    )
