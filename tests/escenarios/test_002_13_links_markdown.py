"""Tests del escenario 002-13-links-markdown.

Escenario: 002-13-links-markdown.md

El flujo del autor que enlaza a mano en Obsidian: `tuku doctor link` reporta el
wikilink, `tuku fix link` lo convierte sin cambiar la fecha de modificación, y
lo que requiere una decisión se devuelve sin escribir. La lógica está en los
unitarios de `tuku.link` y `tuku.fix`; esto fija lo que ve quien invoca.

Fuera de la cadena: siembra su propio vault.

Ejecutable directo: `python3 tests/escenarios/test_002_13_links_markdown.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import gherkin  # noqa: E402

from tuku.cli import EXITO, RECHAZO  # noqa: E402

SLUG = "002-13-links-markdown"
ANTIGUA = 1577836800  # 2020-01-01 00:00 UTC, con holgura de zona horaria


def test_002_13_doctor_link_reporta_y_fix_link_convierte() -> None:
    corrida = gherkin.correr(SLUG, "doctor link reporta el wikilink y fix link lo convierte")

    primera, reparacion, segunda = (
        r for r in corrida.resultados if "doctor link" in r.comando or "fix link" in r.comando
    )
    assert primera.codigo == RECHAZO, primera.stdout
    assert "tuku fix link" in primera.stdout, primera.stdout
    assert reparacion.codigo == EXITO, reparacion.stdout + reparacion.stderr
    assert segunda.codigo == EXITO, segunda.stdout

    nota = corrida.ruta("mi-vault", "notas", "prueba.md")
    assert "[personal](../ambitos/personal/personal.md)" in nota.read_text(encoding="utf-8")
    cambio = nota.stat().st_mtime
    assert cambio < ANTIGUA + 86_400 * 2, "la reparación cambió la fecha del archivo"


def test_002_13_una_segunda_reparacion_no_cambia_nada() -> None:
    corrida = gherkin.correr(SLUG, "una segunda reparación no cambia nada")
    assert corrida.codigo == EXITO, corrida.stdout + corrida.stderr
    assert corrida.delta_de("mi-vault") == {}, "la segunda reparación escribió"


def test_002_13_un_wikilink_ambiguo_se_devuelve_como_decision() -> None:
    corrida = gherkin.correr(SLUG, "un wikilink ambiguo se devuelve como decisión sin escribir")
    assert corrida.codigo == RECHAZO, corrida.stdout + corrida.stderr
    assert "[[doble]]" in corrida.stdout and "ambiguo" in corrida.stdout, corrida.stdout
    assert "a/doble.md" in corrida.stdout and "b/doble.md" in corrida.stdout, corrida.stdout
    assert corrida.delta_de("mi-vault") == {}, "se escribió algo ante una decisión"
    nota = corrida.ruta("mi-vault", "notas", "ambigua.md").read_text(encoding="utf-8")
    assert "[[doble]]" in nota


if __name__ == "__main__":
    test_002_13_doctor_link_reporta_y_fix_link_convierte()
    test_002_13_una_segunda_reparacion_no_cambia_nada()
    test_002_13_un_wikilink_ambiguo_se_devuelve_como_decision()
    print("002-13: ok")
