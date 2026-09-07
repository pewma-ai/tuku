"""Test del escenario 001-005-init-no-toca-la-red.

Escenario: 001-005-init-no-toca-la-red.md

Aísla la afirmación "offline" que `001-002` da por supuesta. Con el módulo
`socket` parchado para que cualquier intento de abrir un socket falle, `init()`
completa la siembra igual: es copia de archivos y nada más.

No basta con no ver tráfico; el test lo fuerza. Si algún día `init()` (o algo
que importe) intenta resolver un nombre, abrir una conexión o consultar la red,
`RedBloqueada` sube y el test falla señalando exactamente eso.

Ejecutable directo: `python3 tests/escenarios/test_001_005_init_no_toca_la_red.py`
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

from vault import placeholders_sin_sustituir, preparar_playground  # noqa: E402

from tuku.init import init  # noqa: E402

SLUG = "001-005-init-no-toca-la-red"
FECHA_FIJA = date(2026, 8, 11)


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


def test_001_005_init_completa_con_la_red_bloqueada() -> None:
    destino = preparar_playground(SLUG)

    with _sin_red():
        init(destino, variante="vanilla", desde=FECHA_FIJA, home=RAIZ)

    assert (destino / "AHORA.md").is_file(), "init no sembró el vault con la red bloqueada"
    assert "DD de mes" not in (destino / "AHORA.md").read_text(encoding="utf-8")
    assert not placeholders_sin_sustituir(destino), "quedaron placeholders vivos"


if __name__ == "__main__":
    test_001_005_init_completa_con_la_red_bloqueada()
    print(f"ok: init() completó la siembra con socket bloqueado (queda en playground/{SLUG}/)")
