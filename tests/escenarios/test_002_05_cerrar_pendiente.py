"""Test del escenario 002-05-cerrar-pendiente.

Escenario: 002-05-cerrar-pendiente.md

Cuarto paso de la cadena. Hereda el ítem abierto en `^sin-fecha` y lo cierra:
el emparejamiento es literal, el callout sobrevive vacío, y el registro de
apertura sigue escrito.

El caso negativo más importante del epic: un cierre sin pendiente abierto deja
`PENDIENTES.md` byte a byte igual y se reporta. Con el archivo como fuente de
verdad, un cierre inventado lo dejaría mintiendo. Es el caso normal del día uno
y no el borde: el corpus trae 52 cierres contra 15 pendientes.

Ejecutable directo: python3 tests/escenarios/test_002_05_cerrar_pendiente.py
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

SLUG = "002-05-cerrar-pendiente"
PREVIO = "002-04-abrir-pendiente"
DESDE = date(2026, 8, 11)
HOY = "## Martes 11 de agosto"

CUERPO = "avisar de los GGCC a la administradora"
APERTURA = f"- 14:20 - [[personal]] **pendiente**: {CUERPO}"
CIERRE = f"- 19:05 - [[personal]] ~~(Hecho)~~: {CUERPO}"

HUERFANO = "comprar una maleta"
CIERRE_HUERFANO = f"- 19:10 - [[personal]] ~~(Hecho)~~: {HUERFANO}"


def _escribir(vault: Path, linea: str) -> None:
    cod, _, err = correr_cli(["entry", "add", "--vault", str(vault), "--dia", HOY, linea])
    assert cod == EXITO, err


def _cerrar(vault: Path, linea: str) -> tuple[int, str]:
    """Aplica el cierre mediante CLI."""
    cod, out, err = correr_cli(["todo", "close", "--vault", str(vault), linea])
    return cod, out or err


def test_002_05_cerrar_borra_el_item_y_el_cierre_sin_pareja_se_reporta() -> None:
    vault = preparar_paso(SLUG, previo=PREVIO, desde=DESDE)
    antes = instantanea(vault)

    _escribir(vault, CIERRE)
    cod, out = _cerrar(vault, CIERRE)
    assert cod == EXITO
    assert "pendiente cerrado" in out, out

    pendientes = (vault / "PENDIENTES.md").read_text(encoding="utf-8")
    assert todo.cuerpos(pendientes) == [], "el ítem no se borró"
    assert len(todo.filas(pendientes)) == 0, "la tabla no quedó vacía"
    assert todo.CABECERA in pendientes, "se perdió la cabecera de la tabla"
    assert APERTURA in (vault / "AHORA.md").read_text(encoding="utf-8"), "se tocó la apertura"

    # Al cerrar con el CLI, se propaga y PENDIENTES-AMBITOS.md pasa a SIN PENDIENTES
    assert delta(antes, instantanea(vault)) == {
        "AHORA.md": "modificado",
        "PENDIENTES.md": "modificado",
        "ambitos/PENDIENTES-AMBITOS.md": "modificado",
    }


def test_002_05_un_cierre_sin_pareja_no_inventa_nada() -> None:
    vault = preparar_paso(SLUG, previo=PREVIO, desde=DESDE)
    _escribir(vault, CIERRE)
    _cerrar(vault, CIERRE)
    antes = instantanea(vault)
    pendientes_antes = (vault / "PENDIENTES.md").read_bytes()

    _escribir(vault, CIERRE_HUERFANO)
    cod, out = _cerrar(vault, CIERRE_HUERFANO)
    assert cod == EXITO
    assert "no había ningún pendiente abierto" in out, out

    assert (vault / "PENDIENTES.md").read_bytes() == pendientes_antes, "PENDIENTES.md cambió"
    assert HUERFANO not in (vault / "PENDIENTES.md").read_text(encoding="utf-8")
    assert CIERRE_HUERFANO in (vault / "AHORA.md").read_text(encoding="utf-8"), (
        "la línea no quedó escrita: un error del autor se reporta, nunca se rechaza"
    )
    assert delta(antes, instantanea(vault)) == {"AHORA.md": "modificado"}


def test_002_05_cerrar_dos_veces_no_vuelve_a_mover() -> None:
    vault = preparar_paso(SLUG, previo=PREVIO, desde=DESDE)
    _escribir(vault, CIERRE)
    cod, out = _cerrar(vault, CIERRE)
    assert cod == EXITO and "pendiente cerrado" in out
    despues = instantanea(vault)

    # El segundo pase de un cierre correcto es, por construcción, un cierre sin
    # pareja: eso hace idempotente al comando sin que lleve estado.
    cod2, out2 = _cerrar(vault, CIERRE)
    assert cod2 == EXITO
    assert "no había ningún pendiente abierto" in out2
    assert delta(despues, instantanea(vault)) == {}, "el segundo pase escribió"


if __name__ == "__main__":
    test_002_05_cerrar_borra_el_item_y_el_cierre_sin_pareja_se_reporta()
    test_002_05_un_cierre_sin_pareja_no_inventa_nada()
    test_002_05_cerrar_dos_veces_no_vuelve_a_mover()
    print(f"ok: 3 afirmaciones (queda en playground/{SLUG}/)")
