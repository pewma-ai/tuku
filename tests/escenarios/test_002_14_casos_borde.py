"""Tests del escenario 002-14-casos-borde.

Sobre el vault de las dos semanas editado con un editor: `regenerate` rehace lo
derivado hasta dejar el vault idéntico, y `fix todo` repara un pendiente abierto
y cerrado a mano el mismo día.

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
CARNET = "renovar el carnet"


def test_002_14_un_derivado_editado_se_detecta_y_se_regenera() -> None:
    corrida = gherkin.correr(SLUG, "un derivado editado a mano se detecta y se regenera")

    lint = corrida.de("doctor todo")
    assert lint.codigo == RECHAZO, lint.stdout
    assert "tuku regenerate todo" in lint.stdout, lint.stdout

    regenerado = corrida.de("tuku regenerate")
    assert regenerado.codigo == EXITO, regenerado.stderr
    for archivo in ("AHORA.md", "ambitos/PENDIENTES-AMBITOS.md"):
        assert archivo in regenerado.stdout, regenerado.stdout
    assert corrida.de("diff -r").codigo == 0


def test_002_14_abierto_y_cerrado_el_mismo_dia_lo_repara_fix() -> None:
    corrida = gherkin.correr(SLUG, "abierto y cerrado a mano el mismo día")

    antes, despues = [r for r in corrida.resultados if "tuku doctor todo" in r.comando]
    assert antes.codigo == RECHAZO, antes.stdout
    assert "tuku fix todo" in antes.stdout, antes.stdout
    assert corrida.de("tuku fix todo").codigo == EXITO
    assert despues.codigo == EXITO, despues.stdout

    for partes in (("AHORA.md",), ("ambitos", "personal", "personal.md")):
        texto = corrida.ruta("mi-vault", *partes).read_text(encoding="utf-8")
        assert f"**pendiente**: {CARNET}" not in texto, partes
        assert f"(Hecho): ~~{CARNET}~~" in texto, partes


if __name__ == "__main__":
    test_002_14_un_derivado_editado_se_detecta_y_se_regenera()
    test_002_14_abierto_y_cerrado_el_mismo_dia_lo_repara_fix()
    print(f"ok: regenerate rehace lo derivado y fix repara (playground/{SLUG}/)")
