"""Tests del escenario 001-03-destino-no-vacio.

Escenario: 001-03-destino-no-vacio.md

`tuku init` se niega a sembrar en un directorio que ya tiene contenido, sin
tocar nada. Con `--force` lo reemplaza entero. Ya no hay prompt ni `/dev/tty`:
la decisión 8 del epic 001 lo cambió por un flag.

Los comandos no se escriben acá. Los tres casos viven en el `.md` y este arnés
solo afirma sobre lo que dejaron, cada uno buscando su `## Escenario:` por el
título. Las tres afirmaciones van por la superficie CLI, que es donde el usuario
ve la negativa:

1. Sobre un destino no vacío y sin `--force`, el comando sale con `RECHAZO` (1),
   el mensaje nombra el defecto y la corrección, y el destino queda exactamente
   igual a como estaba (el centinela intacto, nada más).
2. `--force` sobre ese mismo destino lo reemplaza: el centinela desaparece y
   queda un vault operable.
3. Sobre un destino que no existe, siembra sin más: la negativa es
   específicamente por contenido, no por que el directorio exista.

Cada caso deja su resultado en su propia carpeta bajo
`playground/001-03-destino-no-vacio/`, para poder mirar los tres y no solo el
último.

Ejecutable directo: `python3 tests/escenarios/test_001_03_destino_no_vacio.py`.
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import gherkin  # noqa: E402

from tuku.cli import EXITO, RECHAZO  # noqa: E402

SLUG = "001-03-destino-no-vacio"
CENTINELA = "algo-que-ya-estaba.txt"


def test_001_03_destino_no_vacio_se_niega_y_no_toca_nada() -> None:
    corrida = gherkin.correr(SLUG, "no sembrar sobre un directorio que ya tiene algo")

    assert corrida.codigo == RECHAZO, f"el comando no se negó: código {corrida.codigo}"
    assert "--force" in corrida.stderr, (
        f"el rechazo no nombra la corrección: {corrida.stderr!r}"
    )

    destino = corrida.ruta("mi-vault")
    assert [p.name for p in destino.iterdir()] == [CENTINELA], "el destino no quedó intacto"
    assert (destino / CENTINELA).read_text(encoding="utf-8") == "no tocar\n"


def test_001_03_force_reemplaza_el_destino_no_vacio() -> None:
    corrida = gherkin.correr(SLUG, "`--force` siembra igual")

    assert corrida.codigo == EXITO, corrida.stderr
    destino = corrida.ruta("mi-vault")
    assert not (destino / CENTINELA).exists(), "force no reemplazó el contenido previo"
    assert (destino / "AHORA.md").is_file(), "force no dejó un vault operable"
    assert "DD de mes" not in (destino / "AHORA.md").read_text(encoding="utf-8")


def test_001_03_destino_vacio_se_siembra_sin_force() -> None:
    corrida = gherkin.correr(SLUG, "un destino vacío se siembra sin `force`")

    assert corrida.codigo == EXITO, corrida.stderr
    assert corrida.ruta("mi-vault", "AHORA.md").is_file()


if __name__ == "__main__":
    test_001_03_destino_no_vacio_se_niega_y_no_toca_nada()
    test_001_03_force_reemplaza_el_destino_no_vacio()
    test_001_03_destino_vacio_se_siembra_sin_force()
    print(f"ok: se niega sin force, force reemplaza, vacío siembra (playground/{SLUG}/)")
