"""Test del escenario 002-06-escribir-en-un-dia-fecha.

Escenario: 002-06-escribir-en-un-dia-fecha.md

Quinto paso de la cadena y punto 3 del epic: agendar es escribir donde
corresponde. Un `**pendiente**` escrito bajo un día futuro nace con fecha
exacta, sin pasar por la escalera de horizontes, y queda transcluido al inicio
de ese día.

`todo open` escribe el callout y `transclusion sync` la línea de transclusión,
que es el reparto de la regla 6 de `spec/pendientes.md`. Fechar mueve y nunca
copia: el pendiente está en exactamente un callout.

Ejecutable directo: python3 tests/escenarios/test_002_06_escribir_en_un_dia_fecha.py
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

from cadena import delta, instantanea, preparar_paso  # noqa: E402

from tuku import todo, transclusion  # noqa: E402
from tuku.entry import add  # noqa: E402

SLUG = "002-06-escribir-en-un-dia-fecha"
PREVIO = "002-05-cerrar-pendiente"
DESDE = date(2026, 8, 11)

MANANA = "## Miércoles 12 de agosto"
ANCLA = "2026-08-12"
CUERPO = "pagar la sesión con el psicólogo"
REGISTRO = f"- 09:00 - [[personal]] **pendiente**: {CUERPO}"
HORIZONTES = ["atrasados", "sin-fecha", "esta-semana", "proxima-semana", "fin-de-mes"]


def _agendar(vault: Path) -> None:
    """El flujo completo: escribir el registro, abrir con fecha, sincronizar."""
    ahora = vault / "AHORA.md"
    ahora.write_text(
        add(ahora.read_text(encoding="utf-8"), [REGISTRO], dia=MANANA), encoding="utf-8"
    )

    marca = todo.parsear(REGISTRO)
    assert marca is not None
    ruta = vault / "PENDIENTES.md"
    ruta.write_text(
        todo.abrir(ruta.read_text(encoding="utf-8"), marca, ancla=ANCLA), encoding="utf-8"
    )

    texto, _ = transclusion.sync(
        ahora.read_text(encoding="utf-8"), ruta.read_text(encoding="utf-8")
    )
    ahora.write_text(texto, encoding="utf-8")


def test_002_06_escribir_en_un_dia_futuro_fecha_el_pendiente() -> None:
    vault = preparar_paso(SLUG, previo=PREVIO, desde=DESDE)
    antes = instantanea(vault)
    _agendar(vault)

    pendientes = (vault / "PENDIENTES.md").read_text(encoding="utf-8")
    assert ANCLA in todo.anclas(pendientes), "no nació el callout de fecha"
    assert todo.cuerpos(pendientes, ANCLA) == [CUERPO]
    assert todo.cuerpos(pendientes, "sin-fecha") == [], "no debía pasar por la escalera"

    ahora = (vault / "AHORA.md").read_text(encoding="utf-8")
    lineas = ahora.splitlines()
    i = lineas.index(MANANA)
    assert lineas[i + 1] == transclusion.linea_de(ANCLA), lineas[i : i + 3]

    assert delta(antes, instantanea(vault)) == {
        "AHORA.md": "modificado",
        "PENDIENTES.md": "modificado",
    }


def test_002_06_fechar_mueve_nunca_copia() -> None:
    vault = preparar_paso(SLUG, previo=PREVIO, desde=DESDE)
    _agendar(vault)
    pendientes = (vault / "PENDIENTES.md").read_text(encoding="utf-8")

    apariciones = [a for a in todo.anclas(pendientes) if CUERPO in todo.cuerpos(pendientes, a)]
    assert apariciones == [ANCLA], f"el pendiente está en {apariciones}"
    assert todo.duplicados(pendientes) == [], "todo lint encontró una aparición duplicada"


def test_002_06_el_callout_de_fecha_nace_bajo_los_horizontes() -> None:
    vault = preparar_paso(SLUG, previo=PREVIO, desde=DESDE)
    _agendar(vault)
    anclas = todo.anclas((vault / "PENDIENTES.md").read_text(encoding="utf-8"))

    assert anclas == [*HORIZONTES, ANCLA], "el callout de fecha desplazó a los permanentes"


def test_002_06_el_movimiento_de_escalon_no_se_registra() -> None:
    vault = preparar_paso(SLUG, previo=PREVIO, desde=DESDE)
    antes = (vault / "AHORA.md").read_text(encoding="utf-8").splitlines()
    _agendar(vault)
    despues = (vault / "AHORA.md").read_text(encoding="utf-8").splitlines()

    nuevas = [linea for linea in despues if linea not in antes]
    esperadas = (
        [transclusion.linea_de(ANCLA), REGISTRO],
        [REGISTRO, transclusion.linea_de(ANCLA)],
        [MANANA, transclusion.linea_de(ANCLA), REGISTRO],
        [MANANA, REGISTRO, transclusion.linea_de(ANCLA)],
    )
    assert nuevas in esperadas, nuevas



def test_002_06_inyectar_dos_veces_no_duplica() -> None:
    vault = preparar_paso(SLUG, previo=PREVIO, desde=DESDE)
    _agendar(vault)
    despues = instantanea(vault)

    marca = todo.parsear(REGISTRO)
    assert marca is not None
    ruta = vault / "PENDIENTES.md"
    ruta.write_text(
        todo.abrir(ruta.read_text(encoding="utf-8"), marca, ancla=ANCLA), encoding="utf-8"
    )
    ahora = vault / "AHORA.md"
    texto, reparaciones = transclusion.sync(
        ahora.read_text(encoding="utf-8"), ruta.read_text(encoding="utf-8")
    )
    ahora.write_text(texto, encoding="utf-8")

    assert delta(despues, instantanea(vault)) == {}, "el segundo pase escribió"
    assert reparaciones == [], "sync reparó algo sobre un vault ya cuadrado"


if __name__ == "__main__":
    test_002_06_escribir_en_un_dia_futuro_fecha_el_pendiente()
    test_002_06_fechar_mueve_nunca_copia()
    test_002_06_el_callout_de_fecha_nace_bajo_los_horizontes()
    test_002_06_el_movimiento_de_escalon_no_se_registra()
    test_002_06_inyectar_dos_veces_no_duplica()
    print(f"ok: 5 afirmaciones (queda en playground/{SLUG}/)")
