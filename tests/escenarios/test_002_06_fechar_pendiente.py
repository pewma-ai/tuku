"""Tests del escenario 002-06-fechar-pendiente.

Escenario: 002-06-fechar-pendiente.md

Punto 3 del epic: agendar es fechar mediante el comando `tuku todo open --when <fecha>`,
o escribiendo en día futuro por la vía bitácora (`tuku entry add`). El pendiente nace
con fecha exacta sin pasar por la escalera.
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

SLUG = "002-06-fechar-pendiente"
PERSONAL = "[personal](ambitos/personal/personal.md)"
FECHA = "2026-08-12"
CUERPO = "pagar la sesión con el psicólogo"
FILA = f"| con fecha | {FECHA} | {PERSONAL} | {CUERPO} |"
LINEA_PROPAGADA = f"> - {PERSONAL} - {CUERPO}"


def test_002_06_fechar_un_pendiente_en_dia_futuro() -> None:
    corrida = gherkin.correr(SLUG, "fechar un pendiente en dia futuro")
    assert corrida.codigo == EXITO, corrida.stderr
    vault = corrida.ruta("mi-vault")

    pendientes = (vault / "PENDIENTES.md").read_text(encoding="utf-8")
    assert FILA in pendientes, "no nació la fila con fecha"
    assert todo.cuerpos(pendientes, "con fecha") == [CUERPO]
    assert todo.cuerpos(pendientes, "esta semana") == [], "no debía pasar por la escalera"
    assert "^" not in pendientes, "no debe haber anclas en PENDIENTES.md"
    assert "> [!todo]" not in pendientes, "no debe haber callouts en PENDIENTES.md"

    ahora = (vault / "AHORA.md").read_text(encoding="utf-8")
    assert "> [!todo] Pendientes del día" in ahora
    assert LINEA_PROPAGADA in ahora, "no se propagó la línea a la región del día"

    assert corrida.delta_de("mi-vault") == {
        "AHORA.md": "modificado",
        "PENDIENTES.md": "modificado",
        "ambitos/PENDIENTES-AMBITOS.md": "modificado",
        "ambitos/personal/personal.md": "modificado",
    }


def test_002_06_fechar_dos_veces_no_duplica() -> None:
    corrida = gherkin.correr(SLUG, "fechar dos veces no duplica")
    assert corrida.codigo == EXITO, corrida.stderr
    assert corrida.delta_de("mi-vault") == {}, "el segundo pase escribió"


def test_002_06_bajo_un_dia_futuro_queda_con_esa_fecha() -> None:
    corrida = gherkin.correr(SLUG, "un pendiente escrito bajo un día futuro")
    assert corrida.codigo == EXITO, corrida.stderr
    vault = corrida.ruta("mi-vault")

    pendientes = (vault / "PENDIENTES.md").read_text(encoding="utf-8")
    assert f"| con fecha | 2026-08-13 | {PERSONAL} | comprar pasajes de tren |" in pendientes

    ahora = (vault / "AHORA.md").read_text(encoding="utf-8")
    assert f"> - {PERSONAL} - comprar pasajes de tren" in ahora

    faltan = todo.sin_consecuencia(ahora, pendientes)
    assert faltan == [], f"inconsistencia entre AHORA y PENDIENTES: {faltan}"


if __name__ == "__main__":
    test_002_06_fechar_un_pendiente_en_dia_futuro()
    test_002_06_fechar_dos_veces_no_duplica()
    test_002_06_bajo_un_dia_futuro_queda_con_esa_fecha()
    print(f"ok: 3 afirmaciones (queda en playground/{SLUG}/)")
