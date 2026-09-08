"""Tests del escenario 001-03-destino-no-vacio.

Escenario: 001-03-destino-no-vacio.md

`init()` se niega a sembrar en un directorio que ya tiene contenido y lanza
`DestinoNoVacio`, sin tocar nada. Con `force=True` lo reemplaza entero. Ya no
hay prompt ni `/dev/tty`: la decisión 8 del epic 001 lo cambió por un flag,
porque la lógica es importable y no depende de una tty.

Tres afirmaciones:

1. Sobre un destino no vacío y sin `force`, `init()` lanza y el destino queda
   exactamente igual a como estaba (el centinela intacto, nada más).
2. `force=True` sobre ese mismo destino lo reemplaza: el centinela desaparece y
   queda un vault operable.
3. Sobre un destino vacío, `init()` siembra sin más: la negativa es
   específicamente por contenido, no por que el directorio exista.

Los tres comparten `playground/001-03-destino-no-vacio/`, cada uno lo vacía al
empezar; la corrida completa lo deja con el vault que siembra el caso 3.

Ejecutable directo: `python3 tests/escenarios/test_001_03_destino_no_vacio.py`.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

from vault import preparar_playground  # noqa: E402

from tuku.init import DestinoNoVacio, init  # noqa: E402

SLUG = "001-03-destino-no-vacio"
FECHA_FIJA = date(2026, 8, 11)


def _con_centinela() -> tuple[Path, Path]:
    destino = preparar_playground(SLUG)
    destino.mkdir()
    centinela = destino / "algo-que-ya-estaba.txt"
    centinela.write_text("no tocar\n", encoding="utf-8")
    return destino, centinela


def test_001_03_destino_no_vacio_se_niega_y_no_toca_nada() -> None:
    destino, centinela = _con_centinela()

    with pytest.raises(DestinoNoVacio):
        init(destino, variante="vanilla", desde=FECHA_FIJA, home=RAIZ)

    assert list(destino.iterdir()) == [centinela], "el destino no quedó intacto"
    assert centinela.read_text(encoding="utf-8") == "no tocar\n"


def test_001_03_force_reemplaza_el_destino_no_vacio() -> None:
    destino, centinela = _con_centinela()

    init(destino, variante="vanilla", desde=FECHA_FIJA, home=RAIZ, force=True)

    assert not centinela.exists(), "force no reemplazó el contenido previo"
    assert (destino / "AHORA.md").is_file(), "force no dejó un vault operable"
    assert "DD de mes" not in (destino / "AHORA.md").read_text(encoding="utf-8")


def test_001_03_destino_vacio_se_siembra_sin_force() -> None:
    destino = preparar_playground(SLUG)  # ni existe: preparar_playground lo vació

    init(destino, variante="vanilla", desde=FECHA_FIJA, home=RAIZ)

    assert (destino / "AHORA.md").is_file()


if __name__ == "__main__":
    test_001_03_destino_no_vacio_se_niega_y_no_toca_nada()
    test_001_03_force_reemplaza_el_destino_no_vacio()
    test_001_03_destino_vacio_se_siembra_sin_force()
    print(f"ok: se niega sin force, force reemplaza, vacío siembra (playground/{SLUG}/)")
