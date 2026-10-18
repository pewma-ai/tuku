"""Tests del escenario 002-14-casos-borde.

Sobre el vault del día uno editado con un editor: cada lint nombra su corrección,
`fix todo` y `regenerate` reparan, y un canónico roto no deja nada escrito.

Ejecutable directo: `python3 tests/escenarios/test_002_14_casos_borde.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import gherkin  # noqa: E402

from tuku.cli import EXITO, RECHAZO  # noqa: E402

SLUG = "002-14-casos-borde"
PERSONAL = "[personal](ambitos/personal/personal.md)"


def test_002_14_un_derivado_editado_se_detecta_y_se_regenera() -> None:
    corrida = gherkin.correr(SLUG, "un derivado editado a mano se detecta y se regenera")

    lint = corrida.de("doctor todo")
    assert lint.codigo == RECHAZO, lint.stdout
    assert "tuku regenerate todo" in lint.stdout, lint.stdout

    regenerado = corrida.de("tuku regenerate")
    assert regenerado.codigo == EXITO, regenerado.stderr
    for archivo in ("AHORA.md", "ambitos/PENDIENTES-AMBITOS.md"):
        assert archivo in regenerado.stdout, regenerado.stdout
    diff = corrida.de("diff -r")
    assert diff.codigo == 0, diff.stdout


def test_002_14_una_fila_borrada_la_nombra_todo_lint() -> None:
    corrida = gherkin.correr(SLUG, "una fila borrada a mano la nombra todo lint")
    assert corrida.codigo == RECHAZO, corrida.stdout
    assert "tuku todo open" in corrida.stdout, corrida.stdout


def test_002_14_abierto_y_cerrado_el_mismo_dia_lo_repara_fix() -> None:
    corrida = gherkin.correr(SLUG, "abierto y cerrado a mano el mismo día")

    antes, despues = [r for r in corrida.resultados if "tuku doctor todo" in r.comando]
    assert antes.codigo == RECHAZO, antes.stdout
    assert "tuku fix todo" in antes.stdout, antes.stdout
    assert corrida.de("tuku fix todo").codigo == EXITO
    assert despues.codigo == EXITO, despues.stdout

    for partes in (("AHORA.md",), ("ambitos", "personal", "personal.md")):
        texto = corrida.ruta("mi-vault", *partes).read_text(encoding="utf-8")
        assert "**pendiente**: renovar el carnet" not in texto, partes
        assert "(Hecho): ~~renovar el carnet~~" in texto, partes


def test_002_14_un_registro_a_una_categoria_lo_reporta_scope_lint() -> None:
    corrida = gherkin.correr(SLUG, "un registro a una categoría")

    lint = corrida.de("doctor scope")
    assert lint.codigo == RECHAZO, lint.stdout
    assert "gastos" in lint.stdout and "categoría" in lint.stdout, lint.stdout
    ahora = corrida.ruta("mi-vault", "AHORA.md").read_text(encoding="utf-8")
    assert "- 20:00 - [gastos](ambitos/depto-centro/gastos) **progreso**:" in ahora


def test_002_14_una_marca_cerrada_mal_escrita_la_reporta_entry_lint() -> None:
    corrida = gherkin.correr(SLUG, "una marca cerrada mal escrita")

    lint = corrida.de("doctor entry")
    assert lint.codigo == RECHAZO, lint.stdout
    assert "**Cadencia**" in lint.stdout and "**cadencia**" in lint.stdout, lint.stdout
    ahora = corrida.ruta("mi-vault", "AHORA.md").read_text(encoding="utf-8")
    assert f"- 13:30 - {PERSONAL} **Cadencia**: revisar la caldera" in ahora
    assert corrida.delta_de("mi-vault") == {
        "AHORA.md": "modificado",
        "ambitos/personal/personal.md": "modificado",
    }


def test_002_14_un_canonico_roto_hace_que_regenerate_no_escriba() -> None:
    corrida = gherkin.correr(SLUG, "un canónico roto")
    assert corrida.codigo == RECHAZO, corrida.stdout
    assert "PENDIENTES.md" in corrida.stderr, corrida.stderr
    assert corrida.delta_de("mi-vault") == {}, "el rechazo escribió"


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__, "-v"]))
