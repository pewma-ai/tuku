"""Tests del escenario 001-07-lint-libro-de-estilo.

Con qué código salen `tuku doctor style` y `tuku context style` ante un libro de
estilo o unos archivos del autor rotos. Los hallazgos del lint los prueban los
unitarios de `tuku.style`.

Ejecutable directo: `python3 tests/escenarios/test_001_07_lint_libro_de_estilo.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import gherkin  # noqa: E402

from tuku.cli import EXITO, RECHAZO  # noqa: E402

SLUG = "001-07-lint-libro-de-estilo"
CAPITULO = "## Horizontes"


def test_001_07_falta_capitulo_de_contrato() -> None:
    corrida = gherkin.correr(SLUG, "falta un capítulo de contrato")

    lint = corrida.de("doctor style")
    assert lint.codigo == RECHAZO, lint.stdout
    assert CAPITULO in lint.stdout and "reglas/pendientes.md" in lint.stdout, lint.stdout

    vocab = corrida.de("context style")
    assert vocab.codigo == RECHAZO, vocab.stdout
    assert CAPITULO in vocab.stderr, vocab.stderr


def test_001_07_tabla_de_vocabulario_sin_terminos() -> None:
    corrida = gherkin.correr(SLUG, "tabla de vocabulario vacía")

    assert corrida.codigo == EXITO, "una pregunta no rechaza"
    assert "pregunta(s)" in corrida.stdout, corrida.stdout


def test_001_07_un_capitulo_con_dos_tablas() -> None:
    corrida = gherkin.correr(SLUG, "un capítulo con dos tablas")

    assert corrida.codigo == RECHAZO, corrida.stdout
    assert "2 tablas" in corrida.stdout and "Horizontes" in corrida.stdout, corrida.stdout


if __name__ == "__main__":
    test_001_07_falta_capitulo_de_contrato()
    test_001_07_tabla_de_vocabulario_sin_terminos()
    test_001_07_un_capitulo_con_dos_tablas()
    print(f"ok: 3 afirmaciones (queda en playground/{SLUG}/)")
