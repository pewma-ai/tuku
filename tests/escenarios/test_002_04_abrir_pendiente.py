"""Test del escenario 002-04-abrir-pendiente.

Escenario: 002-04-abrir-pendiente.md

Tercer paso de la cadena. Hereda el vault de 002-02 e inyecta un registro
`**pendiente**` bajo el día de hoy: el ítem aparece en `^sin-fecha` con el
cuerpo literal, sin fecha, los cinco horizontes permanentes siguen ahí, y
abrir dos veces no duplica.

Escrito bajo el día de HOY va a `^sin-fecha` y no a un callout de fecha:
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

from cadena import delta, instantanea, preparar_paso  # noqa: E402

from tuku import todo  # noqa: E402
from tuku.entry import add  # noqa: E402

SLUG = "002-04-abrir-pendiente"
PREVIO = "002-03-lint-de-registro"
DESDE = date(2026, 8, 11)
HOY = "## Martes 11 de agosto"

CUERPO = "avisar de los GGCC a la administradora"
REGISTRO = f"- 14:20 - [[personal]] **pendiente**: {CUERPO}"
ITEM = f"> - [[personal]] - {CUERPO}"
HORIZONTES = ["atrasados", "sin-fecha", "esta-semana", "proxima-semana", "fin-de-mes"]


def _abrir(vault: Path) -> None:
    """Escribe el registro y aplica su consecuencia, que es lo que hace el flujo."""
    ahora = vault / "AHORA.md"
    ahora.write_text(
        add(ahora.read_text(encoding="utf-8"), [REGISTRO], dia=HOY), encoding="utf-8"
    )

    marca = todo.parsear(REGISTRO)
    assert marca is not None and marca.marca == todo.ABRE
    ruta = vault / "PENDIENTES.md"
    ruta.write_text(todo.abrir(ruta.read_text(encoding="utf-8"), marca), encoding="utf-8")


def test_002_04_abrir_copia_el_cuerpo_literal_en_sin_fecha() -> None:
    vault = preparar_paso(SLUG, previo=PREVIO, desde=DESDE)
    antes = instantanea(vault)
    _abrir(vault)

    pendientes = (vault / "PENDIENTES.md").read_text(encoding="utf-8")
    assert ITEM in pendientes, pendientes
    assert todo.cuerpos(pendientes, "sin-fecha") == [CUERPO], "el cuerpo no llegó literal"
    assert CUERPO in (vault / "AHORA.md").read_text(encoding="utf-8")
    assert "2026-08-11" not in ITEM, "el ítem no debe llevar fecha"

    assert delta(antes, instantanea(vault)) == {
        "AHORA.md": "modificado",
        "PENDIENTES.md": "modificado",
    }


def test_002_04_los_cinco_horizontes_permanentes_siguen_existiendo() -> None:
    vault = preparar_paso(SLUG, previo=PREVIO, desde=DESDE)
    _abrir(vault)
    pendientes = (vault / "PENDIENTES.md").read_text(encoding="utf-8")

    assert todo.anclas(pendientes) == HORIZONTES, "cambió la escalera de horizontes"
    for ancla in HORIZONTES:
        if ancla != "sin-fecha":
            assert todo.cuerpos(pendientes, ancla) == [], f"^{ancla} dejó de estar vacío"


def test_002_04_abrir_dos_veces_no_duplica() -> None:
    vault = preparar_paso(SLUG, previo=PREVIO, desde=DESDE)
    _abrir(vault)
    despues_del_primero = instantanea(vault)

    marca = todo.parsear(REGISTRO)
    assert marca is not None
    ruta = vault / "PENDIENTES.md"
    ruta.write_text(todo.abrir(ruta.read_text(encoding="utf-8"), marca), encoding="utf-8")

    assert delta(despues_del_primero, instantanea(vault)) == {}, "el segundo pase escribió"
    assert todo.cuerpos(ruta.read_text(encoding="utf-8"), "sin-fecha") == [CUERPO]


if __name__ == "__main__":
    test_002_04_abrir_copia_el_cuerpo_literal_en_sin_fecha()
    test_002_04_los_cinco_horizontes_permanentes_siguen_existiendo()
    test_002_04_abrir_dos_veces_no_duplica()
    print(f"ok: 3 afirmaciones (queda en playground/{SLUG}/)")
