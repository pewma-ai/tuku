"""Unitarios de `tuku.note`: el nombre del archivo, la constancia y el lint.

Todo en memoria. Lo que escribe archivos (`crear`, `crear_con_constancia`) lo
verifican los escenarios, que miran sus efectos completos sobre el vault.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from tuku import note  # noqa: E402

pytestmark = pytest.mark.unitario


def test_slug_convierte_el_titulo_en_nombre_de_archivo() -> None:
    assert note.slug("Cómo funciona el cobro de gastos comunes") == (
        "como-funciona-el-cobro-de-gastos-comunes"
    )


@pytest.mark.parametrize(
    ("titulo", "esperado"),
    [
        ("  espacios  alrededor  ", "espacios-alrededor"),
        ("signos: ¿y esto?", "signos-y-esto"),
        ("ÑANDÚ en mayúsculas", "nandu-en-mayusculas"),
        ("", ""),
    ],
)
def test_slug_ante_entradas_incomodas(titulo: str, esperado: str) -> None:
    assert note.slug(titulo) == esperado


def test_la_constancia_enlaza_a_la_nota_y_a_su_ambito() -> None:
    linea = note.registro_de_constancia(
        Path("notas/gastos-comunes.md"), time="21:15", scope="depto-centro"
    )
    assert linea == (
        "- 21:15 - [[depto-centro]] **nota**: escribí la nota [[gastos-comunes]]"
    )


def test_la_constancia_sin_ambito_no_deja_el_enlace_vacio() -> None:
    linea = note.registro_de_constancia(Path("notas/algo.md"), time="09:00")
    assert linea == "- 09:00 - **nota**: escribí la nota [[algo]]"


def test_una_nota_con_ver_ademas_y_motivos_no_tiene_hallazgos() -> None:
    nota = (
        "# Nota\n\ncuerpo\n\n## Ver además\n\n"
        "- [[depto-centro]] — el ámbito donde se aplica este cobro\n"
    )
    assert note.lint(nota) == []


def test_falta_la_seccion_ver_ademas() -> None:
    hallazgos = note.lint("# Nota\n\ncuerpo\n")
    assert len(hallazgos) == 1
    assert "falta la sección" in hallazgos[0]
    assert "cierra con sus enlaces" in hallazgos[0], "el error no dice la corrección"


def test_un_enlace_sin_motivo_se_reporta_con_su_linea() -> None:
    nota = "# Nota\n\ncuerpo\n\n## Ver además\n\n- [[depto-centro]]\n"
    hallazgos = note.lint(nota)
    assert len(hallazgos) == 1
    assert "para qué conecta" in hallazgos[0]
    assert "línea 7" in hallazgos[0]


def test_un_guion_de_adorno_no_cuenta_como_motivo() -> None:
    nota = "# Nota\n\ncuerpo\n\n## Ver además\n\n- [[depto-centro]] —\n"
    assert len(note.lint(nota)) == 1


def test_el_lint_solo_mira_dentro_de_ver_ademas() -> None:
    """Un enlace del cuerpo no necesita motivo: la regla es de la sección final."""
    nota = "# Nota\n\nhabla del [[depto-centro]] sin motivo\n\n## Ver además\n\n"
    assert note.lint(nota) == []


def test_una_nota_vacia_reporta_la_seccion_que_falta() -> None:
    assert len(note.lint("")) == 1
