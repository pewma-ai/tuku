"""Test del escenario 001-02-init-siembra-el-estado-cero.

Con la red bloqueada, `tuku init` deja un árbol idéntico a `template/vanilla/`
salvo lo que resuelve, un `AHORA.md` con su foco y ningún placeholder vivo, y el
vault sembrado pasa `tuku doctor`. Compara contra el template en vivo.

Ejecutable directo: `python3 tests/escenarios/test_001_02_init_siembra_el_estado_cero.py`
"""

from __future__ import annotations

import socket
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import gherkin  # noqa: E402
from vault import diff_recursivo, placeholders_sin_sustituir  # noqa: E402

from tuku.cli import EXITO, manual  # noqa: E402

SLUG = "001-02-init-siembra-el-estado-cero"

TEMPLATE_VANILLA = RAIZ / "template" / "vanilla"


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

    # Lo que la instalación resuelve: `AHORA.md`, la configuración y el manual de
    # comandos, que sale de la ayuda del `tuku` instalado y no del template.
    resueltos = frozenset({"AHORA.md", "config.tuku.md", "comandos.tuku.md"})
    diferencias = diff_recursivo(destino, TEMPLATE_VANILLA, ignorar=resueltos)
    assert not diferencias, f"difiere de template/vanilla/: {diferencias}"

    manual_escrito = (destino / "reglas" / "comandos.tuku.md").read_text(encoding="utf-8")
    assert manual_escrito == manual.del_cli(), "reglas/comandos.tuku.md no es el del CLI"

    plantilla = (TEMPLATE_VANILLA / "reglas" / "plantilla" / "AHORA.md").read_text(
        encoding="utf-8"
    )
    ahora = (destino / "AHORA.md").read_text(encoding="utf-8")
    assert ahora == plantilla, "AHORA.md no es la plantilla"
    assert "> [!abstract] Foco" in ahora and "\n## " not in ahora

    pendientes = (destino / "PENDIENTES.md").read_text(encoding="utf-8")
    assert "| Horizonte | Vence | Creado | Ámbito | Detalle |" in pendientes
    filas = [ln for ln in pendientes.splitlines() if ln.startswith("|") and "---" not in ln]
    assert len(filas) == 1, f"PENDIENTES.md no está vacío: {filas}"

    vivos = placeholders_sin_sustituir(destino)
    assert not vivos, f"quedaron placeholders sin sustituir: {vivos}"


def test_001_02_el_vault_sembrado_esta_sano() -> None:
    corrida = gherkin.correr(SLUG, "el vault sembrado está sano")
    assert corrida.codigo == EXITO, corrida.stdout + corrida.stderr
    assert "el vault está sano" in corrida.stdout, corrida.stdout


if __name__ == "__main__":
    test_001_02_init_siembra_el_estado_cero_byte_a_byte()
    test_001_02_el_vault_sembrado_esta_sano()
    print(f"ok: estado cero idéntico al template, sin red y sano (playground/{SLUG}/)")
