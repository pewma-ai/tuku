"""Tests del escenario 002-06-escribir-en-un-dia-fecha.

Escenario: 002-06-escribir-en-un-dia-fecha.md

Punto 3 del epic y su razón de ser: agendar es escribir donde corresponde, sin
un comando aparte para fechar. El pendiente nace con fecha exacta sin pasar por
la escalera, que describe cómo se concreta lo que nació difuso y no es un camino
obligatorio.

Los comandos salen del `.md`, incluida la copia del estado que dejó `002-05`.

Ejecutable directo: `python3 tests/escenarios/test_002_06_escribir_en_un_dia_fecha.py`
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

SLUG = "002-06-escribir-en-un-dia-fecha"
FECHA = "2026-08-12"
CUERPO = "pagar la sesión con el psicólogo"
REGISTRO = f"- 09:00 - [[personal]] **pendiente**: {CUERPO}"
FILA = f"| con fecha | {FECHA} | [[personal]] | {CUERPO} |"
LINEA_PROPAGADA = f"> - [[personal]] - {CUERPO}"


def test_002_06_escribir_en_un_dia_futuro_fecha_el_pendiente() -> None:
    corrida = gherkin.correr(SLUG, "escribir un pendiente en un día futuro lo fecha")
    assert corrida.codigo == EXITO, corrida.stderr
    vault = corrida.ruta("mi-vault")

    pendientes = (vault / "PENDIENTES.md").read_text(encoding="utf-8")
    assert FILA in pendientes, "no nació la fila con fecha"
    assert todo.cuerpos(pendientes, "con fecha") == [CUERPO]
    assert todo.cuerpos(pendientes, "esta semana") == [], "no debía pasar por la escalera"

    ahora = (vault / "AHORA.md").read_text(encoding="utf-8")
    assert "> [!todo] Pendientes del día" in ahora
    assert LINEA_PROPAGADA in ahora, "no se propagó la línea a la región del día"

    assert corrida.delta_de("mi-vault") == {
        "AHORA.md": "modificado",
        "PENDIENTES.md": "modificado",
        "ambitos/PENDIENTES-AMBITOS.md": "modificado",
        "ambitos/personal/personal.md": "modificado",
    }


def test_002_06_fechar_mueve_nunca_copia() -> None:
    corrida = gherkin.correr(SLUG, "fechar mueve, nunca copia")
    pendientes = corrida.ruta("mi-vault", "PENDIENTES.md").read_text(encoding="utf-8")

    filas = [f for f in todo.filas(pendientes) if f.cuerpo == CUERPO]
    assert len(filas) == 1, f"el pendiente está en más de una fila: {filas}"
    assert filas[0].cuando == FECHA
    assert filas[0].horizonte == todo.CON_FECHA
    assert todo.duplicados(pendientes) == [], "todo lint encontró una aparición duplicada"


def test_002_06_la_fecha_vive_en_columna_cuando() -> None:
    corrida = gherkin.correr(SLUG, "la fecha vive en la columna Cuándo")
    pendientes = corrida.ruta("mi-vault", "PENDIENTES.md").read_text(encoding="utf-8")

    assert "^" not in pendientes, "no debe haber anclas en PENDIENTES.md"
    assert "> [!todo]" not in pendientes, "no debe haber callouts en PENDIENTES.md"


def test_002_06_el_movimiento_de_escalon_no_se_registra() -> None:
    """Mover un pendiente es un hecho del sistema, no de la vida del autor."""
    corrida = gherkin.correr(SLUG, "el movimiento de escalón no se registra")

    antes = corrida.antes["mi-vault/AHORA.md"].decode("utf-8").splitlines()
    despues = corrida.despues["mi-vault/AHORA.md"].decode("utf-8").splitlines()
    nuevas = [linea for linea in despues if linea not in antes]

    assert REGISTRO in nuevas, nuevas
    assert LINEA_PROPAGADA in nuevas, nuevas
    assert not any("cambió" in linea or "movido" in linea for linea in nuevas)


def test_002_06_inyectar_dos_veces_no_duplica() -> None:
    corrida = gherkin.correr(SLUG, "inyectar dos veces no duplica")
    assert corrida.codigo == EXITO, corrida.stderr
    assert corrida.delta_de("mi-vault") == {}, "el segundo pase escribió"


if __name__ == "__main__":
    test_002_06_escribir_en_un_dia_futuro_fecha_el_pendiente()
    test_002_06_fechar_mueve_nunca_copia()
    test_002_06_la_fecha_vive_en_columna_cuando()
    test_002_06_el_movimiento_de_escalon_no_se_registra()
    test_002_06_inyectar_dos_veces_no_duplica()
    print(f"ok: 5 afirmaciones (queda en playground/{SLUG}/)")
