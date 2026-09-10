"""Tests del escenario 002-04-abrir-pendiente.

Escenario: 002-04-abrir-pendiente.md

Punto 2 del epic, primera mitad: un registro `**pendiente**` abre el pendiente
sin que el autor toque `PENDIENTES.md`. Abrir es copiar el cuerpo literal: el
comando no interpreta, y por eso este paso no necesita LLM.

Los comandos salen del `.md`, incluida la copia del estado que dejó `002-03`.

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
from tuku.cli import EXITO  # noqa: E402

SLUG = "002-04-abrir-pendiente"
CUERPO = "avisar de los GGCC a la administradora"
FILA = f"| esta semana |  | [[personal]] | {CUERPO} |"

#: Lo que toca abrir un pendiente: la bitácora, la tabla y las dos vistas
#: derivadas que `tuku entry add` regenera al propagar la consecuencia.
DELTA_DE_ABRIR = {
    "AHORA.md": "modificado",
    "PENDIENTES.md": "modificado",
    "ambitos/PENDIENTES-AMBITOS.md": "modificado",
    "ambitos/personal/personal.md": "modificado",
}


def test_002_04_abrir_copia_el_cuerpo_literal_en_esta_semana() -> None:
    corrida = gherkin.correr(SLUG, "abre el pendiente y copia el cuerpo literal")
    assert corrida.codigo == EXITO, corrida.stderr
    vault = corrida.ruta("mi-vault")

    pendientes = (vault / "PENDIENTES.md").read_text(encoding="utf-8")
    assert FILA in pendientes, pendientes
    assert todo.cuerpos(pendientes, "esta semana") == [CUERPO], "el cuerpo no llegó literal"
    assert CUERPO in (vault / "AHORA.md").read_text(encoding="utf-8")
    assert todo.filas(pendientes)[0].cuando == "", "la fila no debe llevar fecha"

    assert corrida.delta_de("mi-vault") == DELTA_DE_ABRIR

    personal = (vault / "ambitos" / "personal" / "personal.md").read_text(encoding="utf-8")
    assert "## Esta semana" in personal
    assert "### Martes 11 de agosto" in personal
    assert f"- **pendiente**: {CUERPO}" in personal


def test_002_04_la_tabla_gana_una_fila_y_nada_mas() -> None:
    corrida = gherkin.correr(SLUG, "abre el pendiente y copia el cuerpo literal")
    pendientes = corrida.ruta("mi-vault", "PENDIENTES.md").read_text(encoding="utf-8")

    assert todo.horizontes(pendientes) == ["esta semana"], "apareció un horizonte de más"
    assert len(todo.filas(pendientes)) == 1, "la tabla tiene más de una fila"
    assert todo.CABECERA in pendientes, "se perdió la cabecera de la tabla"


def test_002_04_abrir_dos_veces_no_duplica() -> None:
    corrida = gherkin.correr(SLUG, "abrir dos veces no duplica")
    assert corrida.codigo == EXITO, corrida.stderr

    assert corrida.delta_de("mi-vault") == {}, "el segundo pase escribió"
    pendientes = corrida.ruta("mi-vault", "PENDIENTES.md").read_text(encoding="utf-8")
    assert todo.cuerpos(pendientes, "esta semana") == [CUERPO]


if __name__ == "__main__":
    test_002_04_abrir_copia_el_cuerpo_literal_en_esta_semana()
    test_002_04_la_tabla_gana_una_fila_y_nada_mas()
    test_002_04_abrir_dos_veces_no_duplica()
    print(f"ok: 3 afirmaciones (queda en playground/{SLUG}/)")


def test_002_04_abrir_deja_la_marca_reflejada_en_la_tabla() -> None:
    """Verifica que la marca escrita tenga su fila correspondiente en PENDIENTES.md.

    `tuku entry add` aplica la consecuencia de forma atómica. Esta verificación
    asegura que `tuku doctor` valide la consistencia entre AHORA.md y PENDIENTES.md.
    """
    vault = gherkin.correr(SLUG, "abre el pendiente y copia el cuerpo literal").ruta("mi-vault")
    faltan = todo.sin_consecuencia(
        (vault / "AHORA.md").read_text(encoding="utf-8"),
        (vault / "PENDIENTES.md").read_text(encoding="utf-8"),
    )
    assert faltan == [], f"quedaron marcas sin su consecuencia: {faltan}"
