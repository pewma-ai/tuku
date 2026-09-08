"""Test del escenario 001-06-cli-ayuda.

Escenario: 001-06-cli-ayuda.md

Fija la superficie de `tuku -h` y `tuku init -h` con lo que el epic 001 puso en
el CLI, y los códigos de salida que `spec/cli.md` declara contrato.

Los comandos no se escriben acá: salen del `.md`, que es la fuente ejecutable
(`tests/scripts/gherkin.py`). El runner los corre en proceso sobre
`tuku.cli.main`, así que argparse imprime la ayuda y sale antes de sembrar nada:
sin red, y dentro de la corrida por defecto.

No compara el texto palabra por palabra (eso se lee a mano): comprueba que cada
comando y cada opción que el epic 001 agregó está nombrada, y que `-h` sale con
código 0.

Ejecutable directo: `python3 tests/escenarios/test_001_06_cli_ayuda.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import gherkin  # noqa: E402

from tuku.cli import ENTORNO, EXITO, RECHAZO, USO  # noqa: E402

SLUG = "001-06-cli-ayuda"


def test_tuku_menos_h_nombra_init_y_el_proposito() -> None:
    corrida = gherkin.correr(SLUG, "nombra lo que el epic 001 puso en el CLI")
    assert corrida.codigo == EXITO, "`tuku -h` no salió con código 0"
    assert "init" in corrida.stdout, "`tuku -h` no nombra el comando init"
    assert "TUKU" in corrida.stdout, "`tuku -h` no dice qué es TUKU"


def test_tuku_init_menos_h_lista_lo_que_anade_el_epic_001() -> None:
    corrida = gherkin.correr(SLUG, "lista las opciones que añade el epic 001")
    assert corrida.codigo == EXITO, "`tuku init -h` no salió con código 0"
    for pieza in ("dir", "--variante", "--author", "--force"):
        assert pieza in corrida.stdout, f"`tuku init -h` no nombra {pieza}"


def test_tuku_sin_comando_es_error_de_uso() -> None:
    corrida = gherkin.correr(SLUG, "`tuku` sin comando es error de uso")
    assert corrida.codigo == USO, "`tuku` sin comando debería salir con el código de uso"
    assert "init" in corrida.stderr, "el error no lista los comandos válidos"


def test_author_sin_valor_es_error_de_uso() -> None:
    corrida = gherkin.correr(SLUG, "`--author` sin valor es error de uso")
    assert corrida.codigo == USO, "`--author` sin nombre debería salir con el código de uso"


def test_entorno_roto_no_se_confunde_con_error_de_uso() -> None:
    """El choque que `spec/cli.md` prohíbe: `TukuHomeInvalido` devolvía 2, igual
    que argparse ante una invocación mal escrita. Quien invoca no podía saber si
    corregir el comando o la instalación."""
    corrida = gherkin.correr(SLUG, "un entorno roto no se confunde con un error de uso")

    assert corrida.codigo == ENTORNO, (
        "una instalación rota debería salir con el código de entorno"
    )
    assert corrida.codigo != USO, "el entorno roto no puede confundirse con un error de uso"
    assert "template" in corrida.stderr, "el error no dice qué le falta al árbol"


def test_los_cuatro_codigos_son_distintos() -> None:
    codigos = [EXITO, RECHAZO, USO, ENTORNO]
    assert len(set(codigos)) == len(codigos), "dos causas comparten código de salida"


if __name__ == "__main__":
    test_tuku_menos_h_nombra_init_y_el_proposito()
    test_tuku_init_menos_h_lista_lo_que_anade_el_epic_001()
    test_tuku_sin_comando_es_error_de_uso()
    test_author_sin_valor_es_error_de_uso()
    test_entorno_roto_no_se_confunde_con_error_de_uso()
    test_los_cuatro_codigos_son_distintos()
    print("ok: la ayuda nombra lo del epic 001 y los cuatro códigos de salida son distintos")
