"""Test del escenario 002-06-escribir-en-un-dia-fecha.

Escenario: 002-06-escribir-en-un-dia-fecha.md

Quinto paso de la cadena y punto 3 del epic: agendar es escribir donde
corresponde. Un `**pendiente**` escrito bajo un día futuro nace con fecha
exacta, sin pasar por la escalera de horizontes, y queda propagado al inicio
de ese día.

`todo open` escribe la fila y propaga a las vistas derivadas (`AHORA.md` y
`ambitos/PENDIENTES-AMBITOS.md`). Fechar mueve y nunca copia: el pendiente está
en exactamente una fila.

Ejecutable directo: python3 tests/escenarios/test_002_06_escribir_en_un_dia_fecha.py
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

SLUG = "002-06-escribir-en-un-dia-fecha"
PREVIO = "002-05-cerrar-pendiente"
DESDE = date(2026, 8, 11)

MANANA = "## Miércoles 12 de agosto"
FECHA = "2026-08-12"
CUERPO = "pagar la sesión con el psicólogo"
REGISTRO = f"- 09:00 - [[personal]] **pendiente**: {CUERPO}"
FILA = f"| con fecha | {FECHA} | [[personal]] | {CUERPO} |"
LINEA_PROPAGADA = f"> - [[personal]] - {CUERPO}"


def _agendar(vault: Path) -> None:
    """El flujo completo mediante CLI: escribir el registro y abrir con fecha (propaga solo)."""
    cod_add, _, err_add = correr_cli(
        ["entry", "add", "--vault", str(vault), "--dia", MANANA, REGISTRO]
    )
    assert cod_add == EXITO, err_add

    cod_open, _, err_open = correr_cli(
        [
            "todo",
            "open",
            "--vault",
            str(vault),
            "--horizonte",
            todo.CON_FECHA,
            "--when",
            FECHA,
            REGISTRO,
        ]
    )
    assert cod_open == EXITO, err_open


def test_002_06_escribir_en_un_dia_futuro_fecha_el_pendiente() -> None:
    vault = preparar_paso(SLUG, previo=PREVIO, desde=DESDE)
    antes = instantanea(vault)
    _agendar(vault)

    pendientes = (vault / "PENDIENTES.md").read_text(encoding="utf-8")
    assert FILA in pendientes, "no nació la fila con fecha"
    assert todo.cuerpos(pendientes, "con fecha") == [CUERPO]
    assert todo.cuerpos(pendientes, "esta semana") == [], "no debía pasar por la escalera"

    ahora = (vault / "AHORA.md").read_text(encoding="utf-8")
    assert "> [!todo] Pendientes del día" in ahora
    assert LINEA_PROPAGADA in ahora, "no se propagó la línea a la región del día"

    # Propagó en AHORA.md y actualizó ambitos/PENDIENTES-AMBITOS.md y personal.md
    assert delta(antes, instantanea(vault)) == {
        "AHORA.md": "modificado",
        "PENDIENTES.md": "modificado",
        "ambitos/PENDIENTES-AMBITOS.md": "modificado",
        "ambitos/personal/personal.md": "modificado",
    }


def test_002_06_fechar_mueve_nunca_copia() -> None:
    vault = preparar_paso(SLUG, previo=PREVIO, desde=DESDE)
    _agendar(vault)
    pendientes = (vault / "PENDIENTES.md").read_text(encoding="utf-8")

    filas = [f for f in todo.filas(pendientes) if f.cuerpo == CUERPO]
    assert len(filas) == 1, f"el pendiente está en más de una fila: {filas}"
    assert filas[0].cuando == FECHA
    assert filas[0].horizonte == todo.CON_FECHA
    assert todo.duplicados(pendientes) == [], "todo lint encontró una aparición duplicada"


def test_002_06_la_fecha_vive_en_columna_cuando() -> None:
    vault = preparar_paso(SLUG, previo=PREVIO, desde=DESDE)
    _agendar(vault)
    pendientes = (vault / "PENDIENTES.md").read_text(encoding="utf-8")

    # No hay encabezados ni anclas de bloque
    assert "^" not in pendientes, "no debe haber anclas en PENDIENTES.md"
    assert "> [!todo]" not in pendientes, "no debe haber callouts en PENDIENTES.md"


def test_002_06_el_movimiento_de_escalon_no_se_registra() -> None:
    vault = preparar_paso(SLUG, previo=PREVIO, desde=DESDE)
    antes = (vault / "AHORA.md").read_text(encoding="utf-8").splitlines()
    _agendar(vault)
    despues = (vault / "AHORA.md").read_text(encoding="utf-8").splitlines()

    nuevas = [linea for linea in despues if linea not in antes]
    # En AHORA.md se agregó el registro y la línea propagada
    assert REGISTRO in nuevas, nuevas
    assert LINEA_PROPAGADA in nuevas, nuevas
    # No hay registros artificiales de cambio de estado
    assert not any("cambió" in linea or "movido" in linea for linea in nuevas)


def test_002_06_inyectar_dos_veces_no_duplica() -> None:
    vault = preparar_paso(SLUG, previo=PREVIO, desde=DESDE)
    _agendar(vault)
    despues = instantanea(vault)

    cod_open, _, err_open = correr_cli(
        [
            "todo",
            "open",
            "--vault",
            str(vault),
            "--horizonte",
            todo.CON_FECHA,
            "--when",
            FECHA,
            REGISTRO,
        ]
    )
    assert cod_open == EXITO, err_open
    assert delta(despues, instantanea(vault)) == {}, "el segundo pase escribió"


if __name__ == "__main__":
    test_002_06_escribir_en_un_dia_futuro_fecha_el_pendiente()
    test_002_06_fechar_mueve_nunca_copia()
    test_002_06_la_fecha_vive_en_columna_cuando()
    test_002_06_el_movimiento_de_escalon_no_se_registra()
    test_002_06_inyectar_dos_veces_no_duplica()
    print(f"ok: 5 afirmaciones (queda en playground/{SLUG}/)")

