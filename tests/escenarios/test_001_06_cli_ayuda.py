"""Test del escenario 001-06-cli-ayuda.

Escenario: 001-06-cli-ayuda.md

Fija la superficie de `tuku -h` y `tuku init -h` con lo que el epic 001 puso en
el CLI. Corre en proceso sobre `tuku.cli.main`: argparse imprime la ayuda y sale
antes de tocar `init()`, así que no hay red ni disco y entra en la corrida por
defecto.

No compara el texto palabra por palabra (eso se lee a mano): comprueba que cada
comando y cada opción que el epic 001 agregó está nombrada, y que `-h` sale con
código 0.

Ejecutable directo: `python3 tests/escenarios/test_001_06_cli_ayuda.py`
"""

from __future__ import annotations

import io
import os
import sys
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from tuku.cli import ENTORNO, EXITO, RECHAZO, USO, main  # noqa: E402


def _correr(argv: list[str]) -> tuple[int | None, str, str]:
    """Llama a `main(argv)` capturando salida, error y el código con que sale."""
    out, err = io.StringIO(), io.StringIO()
    codigo: int | None = None
    with redirect_stdout(out), redirect_stderr(err):
        try:
            codigo = main(argv)
        except SystemExit as e:  # argparse sale así con -h y con error de uso
            codigo = e.code if isinstance(e.code, int) else 1
    return codigo, out.getvalue(), err.getvalue()


@contextmanager
def _tuku_home(valor: str) -> Iterator[None]:
    """Fija `TUKU_HOME` durante el bloque y restaura lo que hubiera."""
    previo = os.environ.get("TUKU_HOME")
    os.environ["TUKU_HOME"] = valor
    try:
        yield
    finally:
        if previo is None:
            os.environ.pop("TUKU_HOME", None)
        else:
            os.environ["TUKU_HOME"] = previo


def test_tuku_menos_h_nombra_init_y_el_proposito() -> None:
    codigo, salida, _ = _correr(["-h"])
    assert codigo == 0, "`tuku -h` no salió con código 0"
    assert "init" in salida, "`tuku -h` no nombra el comando init"
    assert "TUKU" in salida, "`tuku -h` no dice qué es TUKU"


def test_tuku_init_menos_h_lista_lo_que_anade_el_epic_001() -> None:
    codigo, salida, _ = _correr(["init", "-h"])
    assert codigo == 0, "`tuku init -h` no salió con código 0"
    for pieza in ("dir", "--variante", "--author", "--force"):
        assert pieza in salida, f"`tuku init -h` no nombra {pieza}"


def test_tuku_sin_comando_es_error_de_uso() -> None:
    codigo, _, error = _correr([])
    assert codigo == USO, "`tuku` sin comando debería salir con el código de uso"
    assert "init" in error, "el error no lista los comandos válidos"


def test_author_sin_valor_es_error_de_uso() -> None:
    codigo, _, _ = _correr(["init", "--author"])
    assert codigo == USO, "`--author` sin nombre debería salir con el código de uso"


def test_entorno_roto_no_se_confunde_con_error_de_uso() -> None:
    """El choque que `spec/cli.md` prohíbe: `TukuHomeInvalido` devolvía 2, igual
    que argparse ante una invocación mal escrita. Quien invoca no podía saber si
    corregir el comando o la instalación."""
    # El tempdir existe pero no tiene `template/`: la cascada de `resolver_home` falla.
    with tempfile.TemporaryDirectory() as tmp, _tuku_home(tmp):
        codigo, _, error = _correr(["init", str(Path(tmp) / "vault")])

    assert codigo == ENTORNO, "una instalación rota debería salir con el código de entorno"
    assert codigo != USO, "el entorno roto no puede confundirse con un error de uso"
    assert "template" in error, "el error no dice qué le falta al árbol"


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
    print("ok: la ayuda y los códigos de salida del epic 001 están fijados")
