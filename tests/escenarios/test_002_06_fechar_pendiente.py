"""Tests del escenario 002-06-fechar-pendiente.

Escenario: 002-06-fechar-pendiente.md

Agendar es fechar con `tuku todo open --when <fecha>` o con un `--day` futuro: el
pendiente nace con fecha exacta, sin pasar por la escalera, y llega a su día y a su
ámbito.
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

#: Los cuatro pendientes del último escenario, en el orden en que se abren.
DOS_DIAS = (
    ("2026-08-13", "comprar pasajes de tren"),
    ("2026-08-12", "pagar la sesión con el psicólogo"),
    ("2026-08-13", "retirar el pase escolar"),
    ("2026-08-12", "llamar a la administradora"),
)


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


def test_002_06_pendientes_de_dos_dias_llegan_a_su_dia_y_a_su_ambito() -> None:
    corrida = gherkin.correr(SLUG, "pendientes de dos días futuros")
    assert corrida.codigo == EXITO, corrida.stderr
    vault = corrida.ruta("mi-vault")

    pendientes = (vault / "PENDIENTES.md").read_text(encoding="utf-8")
    for dia, cuerpo in DOS_DIAS:
        assert f"| con fecha | {dia} | {PERSONAL} | {cuerpo} |" in pendientes, cuerpo

    ahora = (vault / "AHORA.md").read_text(encoding="utf-8")
    dias = (
        ("## Miércoles 12 de agosto", "2026-08-12"),
        ("## Jueves 13 de agosto", "2026-08-13"),
    )
    for encabezado, dia in dias:
        region = ahora.split(encabezado, 1)[1].split("\n## ", 1)[0]
        esperados = [f"> - {PERSONAL} - {c}" for d, c in DOS_DIAS if d == dia]
        assert [x for x in region.splitlines() if x.startswith("> - ")] == esperados, region

    ambitos = (vault / "ambitos" / "PENDIENTES-AMBITOS.md").read_text(encoding="utf-8")
    callout = ambitos.split("^personal\n", 1)[1].splitlines()
    assert callout == [
        "> - Miércoles 12 de agosto - pagar la sesión con el psicólogo",
        "> - Miércoles 12 de agosto - llamar a la administradora",
        "> - Jueves 13 de agosto - comprar pasajes de tren",
        "> - Jueves 13 de agosto - retirar el pase escolar",
    ]

    assert corrida.de("tuku todo lint").codigo == EXITO


if __name__ == "__main__":
    test_002_06_fechar_un_pendiente_en_dia_futuro()
    test_002_06_fechar_dos_veces_no_duplica()
    test_002_06_pendientes_de_dos_dias_llegan_a_su_dia_y_a_su_ambito()
    print(f"ok: 3 afirmaciones (queda en playground/{SLUG}/)")
