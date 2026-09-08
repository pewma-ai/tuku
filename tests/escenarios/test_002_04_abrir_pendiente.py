"""Test del escenario 002-04-abrir-pendiente.

Escenario: 002-04-abrir-pendiente.md

Tercer paso de la cadena. Hereda el vault de 002-02 e inyecta un registro
`**pendiente**` bajo el día de hoy: la tabla gana una fila con horizonte
`sin fecha`, el detalle literal y `Cuándo` vacío, y abrir dos veces no duplica.

Escrito bajo el día de HOY va a `sin fecha` y no a `con fecha`:
`spec/pendientes.md` dice que solo fecha escribir bajo un día futuro.

Ejecutable directo: python3 tests/escenarios/test_002_04_abrir_pendiente.py
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

from cadena import correr_cli, delta, instantanea, preparar_paso  # noqa: E402

from tuku import todo  # noqa: E402
from tuku.cli import EXITO  # noqa: E402

SLUG = "002-04-abrir-pendiente"
PREVIO = "002-03-lint-de-registro"
DESDE = date(2026, 8, 11)
HOY = "## Martes 11 de agosto"

CUERPO = "avisar de los GGCC a la administradora"
REGISTRO = f"- 14:20 - [[personal]] **pendiente**: {CUERPO}"
FILA = f"| esta semana |  | [[personal]] | {CUERPO} |"


def _abrir(vault: Path) -> None:
    """Escribe el registro y aplica su consecuencia mediante el CLI."""
    cod_add, _, err_add = correr_cli(
        ["entry", "add", "--vault", str(vault), "--dia", HOY, REGISTRO]
    )
    assert cod_add == EXITO, err_add

    cod_open, _, err_open = correr_cli(
        ["todo", "open", "--vault", str(vault), REGISTRO]
    )
    assert cod_open == EXITO, err_open


def test_002_04_abrir_copia_el_cuerpo_literal_en_esta_semana() -> None:
    vault = preparar_paso(SLUG, previo=PREVIO, desde=DESDE)
    antes = instantanea(vault)
    _abrir(vault)

    pendientes = (vault / "PENDIENTES.md").read_text(encoding="utf-8")
    assert FILA in pendientes, pendientes
    assert todo.cuerpos(pendientes, "esta semana") == [CUERPO], "el cuerpo no llegó literal"
    assert CUERPO in (vault / "AHORA.md").read_text(encoding="utf-8")
    assert todo.filas(pendientes)[0].cuando == "", "la fila no debe llevar fecha"

    # tuku todo open abre y propaga las vistas, actualizando PENDIENTES-AMBITOS.md y personal.md
    assert delta(antes, instantanea(vault)) == {
        "AHORA.md": "modificado",
        "PENDIENTES.md": "modificado",
        "ambitos/PENDIENTES-AMBITOS.md": "modificado",
        "ambitos/personal/personal.md": "modificado",
    }

    pag_personal = vault / "ambitos" / "personal" / "personal.md"
    contenido_personal = pag_personal.read_text(encoding="utf-8")
    assert "## Esta semana" in contenido_personal
    assert "### Martes 11 de agosto" in contenido_personal
    assert f"- **pendiente**: {CUERPO}" in contenido_personal


def test_002_04_la_tabla_gana_una_fila_y_nada_mas() -> None:
    vault = preparar_paso(SLUG, previo=PREVIO, desde=DESDE)
    _abrir(vault)
    pendientes = (vault / "PENDIENTES.md").read_text(encoding="utf-8")

    assert todo.horizontes(pendientes) == ["esta semana"], "apareció un horizonte de más"
    assert len(todo.filas(pendientes)) == 1, "la tabla tiene más de una fila"
    assert todo.CABECERA in pendientes, "se perdió la cabecera de la tabla"


def test_002_04_abrir_dos_veces_no_duplica() -> None:
    vault = preparar_paso(SLUG, previo=PREVIO, desde=DESDE)
    _abrir(vault)
    despues_del_primero = instantanea(vault)

    cod_open, _, err_open = correr_cli(
        ["todo", "open", "--vault", str(vault), REGISTRO]
    )
    assert cod_open == EXITO, err_open

    assert delta(despues_del_primero, instantanea(vault)) == {}, "el segundo pase escribió"
    pendientes_segundo = (vault / "PENDIENTES.md").read_text(encoding="utf-8")
    assert todo.cuerpos(pendientes_segundo, "esta semana") == [CUERPO]


if __name__ == "__main__":
    test_002_04_abrir_copia_el_cuerpo_literal_en_esta_semana()
    test_002_04_la_tabla_gana_una_fila_y_nada_mas()
    test_002_04_abrir_dos_veces_no_duplica()
    print(f"ok: 3 afirmaciones (queda en playground/{SLUG}/)")
