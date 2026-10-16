"""Tests del escenario 002-04-abrir-pendiente.

`tuku todo open` copia el cuerpo literal a `PENDIENTES.md` y deja su huella en
`AHORA.md`; `tuku entry add` con `**pendiente**` hace lo mismo. `tuku todo lint`
encuentra lo que se editó a mano.

Ejecutable directo: `python3 tests/escenarios/test_002_04_abrir_pendiente.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import gherkin  # noqa: E402

from tuku import todo  # noqa: E402
from tuku.cli import EXITO, RECHAZO  # noqa: E402

SLUG = "002-04-abrir-pendiente"
PERSONAL = "[personal](ambitos/personal/personal.md)"
CUERPO = "avisar de los GGCC a la administradora"
FILA = f"| esta semana |  | {PERSONAL} | {CUERPO} |"

#: Lo que toca abrir un pendiente: la bitácora, la tabla y las dos vistas
#: derivadas que `tuku todo open` regenera al propagar la consecuencia.
DELTA_DE_ABRIR = {
    "AHORA.md": "modificado",
    "PENDIENTES.md": "modificado",
    "ambitos/PENDIENTES-AMBITOS.md": "modificado",
    "ambitos/personal/personal.md": "modificado",
}


def test_002_04_abrir_copia_el_cuerpo_literal_en_esta_semana() -> None:
    corrida = gherkin.correr(SLUG, "abrir el pendiente copia el cuerpo literal")
    assert corrida.codigo == EXITO, corrida.stderr
    vault = corrida.ruta("mi-vault")

    pendientes = (vault / "PENDIENTES.md").read_text(encoding="utf-8")
    assert FILA in pendientes, pendientes
    assert todo.cuerpos(pendientes, "esta semana") == [CUERPO], "el cuerpo no llegó literal"
    assert len(todo.filas(pendientes)) == 1, "la tabla tiene más de una fila"
    assert CUERPO in (vault / "AHORA.md").read_text(encoding="utf-8")
    assert todo.filas(pendientes)[0].cuando == "", "la fila no debe llevar fecha"

    assert corrida.delta_de("mi-vault") == DELTA_DE_ABRIR

    personal = (vault / "ambitos" / "personal" / "personal.md").read_text(encoding="utf-8")
    assert "## Esta semana" in personal
    assert "### Martes 11 de agosto" in personal
    assert f"- **pendiente**: {CUERPO}" in personal


def test_002_04_abrir_dos_veces_no_duplica() -> None:
    corrida = gherkin.correr(SLUG, "abrir dos veces no duplica")
    assert corrida.codigo == EXITO, corrida.stderr

    assert corrida.delta_de("mi-vault") == {}, "el segundo pase escribió"
    pendientes = corrida.ruta("mi-vault", "PENDIENTES.md").read_text(encoding="utf-8")
    assert todo.cuerpos(pendientes, "esta semana") == [CUERPO]


def test_002_04_todo_lint_encuentra_la_fila_borrada_a_mano() -> None:
    corrida = gherkin.correr(SLUG, "todo lint encuentra la fila que se borró a mano")

    lint = corrida.de("tuku todo lint")
    assert lint.codigo == RECHAZO, lint.stdout
    assert "tuku todo open" in lint.stdout, lint.stdout


def test_002_04_todo_lint_encuentra_una_vista_desactualizada() -> None:
    corrida = gherkin.correr(SLUG, "todo lint encuentra una vista desactualizada")

    primera, segunda = [r for r in corrida.resultados if "tuku todo lint" in r.comando]
    assert primera.codigo == RECHAZO, primera.stdout
    assert "PENDIENTES-AMBITOS.md" in primera.stdout, primera.stdout
    assert "tuku todo propagate" in primera.stdout, primera.stdout
    assert segunda.codigo == EXITO, segunda.stdout


if __name__ == "__main__":
    test_002_04_abrir_copia_el_cuerpo_literal_en_esta_semana()
    test_002_04_abrir_dos_veces_no_duplica()
    test_002_04_todo_lint_encuentra_la_fila_borrada_a_mano()
    test_002_04_todo_lint_encuentra_una_vista_desactualizada()
    print(f"ok: 4 afirmaciones (queda en playground/{SLUG}/)")
