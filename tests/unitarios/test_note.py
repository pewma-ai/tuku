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
    for titulo, esperado in [
        ("  espacios  alrededor  ", "espacios-alrededor"),
        ("signos: ¿y esto?", "signos-y-esto"),
        ("ÑANDÚ en mayúsculas", "nandu-en-mayusculas"),
        ("", ""),
    ]:
        assert note.slug(titulo) == esperado, titulo


def test_la_constancia_enlaza_a_la_nota_y_a_su_ambito_si_lo_hay() -> None:
    assert note.registro_de_constancia(
        Path("notas/gastos-comunes.md"), hour="21:15", scope="depto-centro"
    ) == (
        "- 21:15 - [depto-centro](ambitos/depto-centro/depto-centro.md) "
        "**nota**: escribí la nota [gastos-comunes](notas/gastos-comunes.md)"
    )
    assert note.registro_de_constancia(Path("notas/algo.md"), hour="09:00") == (
        "- 09:00 - **nota**: escribí la nota [algo](notas/algo.md)"
    )


def test_el_lint_pide_la_seccion_ver_ademas_y_un_motivo_por_enlace() -> None:
    sana = "# Nota\n\ncuerpo\n\n## Ver además\n\n- [[depto-centro]] — el ámbito del cobro\n"
    assert note.lint(sana) == []

    [sin_seccion] = note.lint("# Nota\n\ncuerpo\n")
    assert "falta la sección" in sin_seccion
    assert "cierra con sus enlaces" in sin_seccion, "el error no dice la corrección"
    assert len(note.lint("")) == 1

    [sin_motivo] = note.lint("# Nota\n\ncuerpo\n\n## Ver además\n\n- [[depto-centro]]\n")
    assert "para qué conecta" in sin_motivo and "línea 7" in sin_motivo

    adorno = "# Nota\n\ncuerpo\n\n## Ver además\n\n- [[depto-centro]] —\n"
    assert len(note.lint(adorno)) == 1, "un guion de adorno no cuenta como motivo"

    cuerpo = "# Nota\n\nhabla del [[depto-centro]] sin motivo\n\n## Ver además\n\n"
    assert note.lint(cuerpo) == [], "la regla es solo de la sección final"


def test_el_lint_nombra_el_enlace_del_cuerpo_que_ver_ademas_no_lista() -> None:
    cuerpo = "# Nota\n\nVer [Pagos](pagos.md) y [web](https://a.b) y `[x](no.md)`.\n\n"
    motivo = "* [Pagos](pagos.md) — cómo se cobra\n"

    [falta] = note.lint(
        f"{cuerpo}## Ver además\n\n* [negocio](../ambitos/n/n.md) — el ámbito\n"
    )
    assert "línea 3" in falta and "notas/pagos.md" in falta and "`## Ver además`" in falta
    assert "[Pagos](notas/pagos.md)" not in falta, (
        "la corrección repite el link tal cual está escrito"
    )

    assert note.lint(f"{cuerpo}## Ver además\n\n{motivo}") == []
    dos = "# Nota\n\n[Pagos](pagos.md) y otra vez [Pagos](pagos.md)\n\n## Ver además\n\n"
    assert len(note.lint(dos)) == 1, "un destino repetido se nombra una vez"


def test_aliases_en_linea_o_en_bloque() -> None:
    from tuku.note import aliases

    assert aliases('---\ntype: Note\naliases: [Rodolfo, "don Rodolfo"]\n---\n# R\n') == [
        "Rodolfo",
        "don Rodolfo",
    ]
    assert aliases("---\naliases:\n  - LR\n  - Los Robles\ntype: Note\n---\n") == [
        "LR",
        "Los Robles",
    ]
    assert aliases("# sin frontmatter\n") == []


def test_compose_escribe_los_aliases_que_context_ofrece_al_agente() -> None:
    from datetime import date

    texto = note.compose(
        title="Rodolfo Cifuentes",
        body="Administrador.",
        today=date(2026, 8, 11),
        subtype="persona",
        aliases=["don Rodolfo", "Rodolfo"],
    )
    assert "subtype: persona\naliases: [don Rodolfo, Rodolfo]\ncreated: 2026-08-11" in texto
    assert note.aliases(texto) == ["don Rodolfo", "Rodolfo"]
