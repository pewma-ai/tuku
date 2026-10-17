"""Tests del lint estructural de AHORA.md."""

from __future__ import annotations

from tuku.cyclelint import STATUS_ABIERTO, TYPE_DEL_CICLO, formatear, lint

CABECERA = (
    "---\n"
    f"type: {TYPE_DEL_CICLO}\n"
    f"status: {STATUS_ABIERTO}\n"
    "from: 2026-09-07\n"
    "to: 2026-09-13\n"
    "---\n\n"
    "# Actividad diaria\n\n"
)
SANO = CABECERA + "## Lunes 7 de septiembre\n"


def test_ahora_sano_no_tiene_hallazgos() -> None:
    assert lint(SANO) == []
    assert formatear([]) == "cycle lint: sin hallazgos."


def test_un_defecto_del_frontmatter_o_del_dia_es_un_hallazgo_que_lo_nombra() -> None:
    sin_fechas = SANO.replace("2026-09-07", "AAAA-MM-DD").replace("2026-09-13", "AAAA-MM-DD")
    assert any("frontmatter" in h.defecto for h in lint(sin_fechas))

    [fuera] = lint(SANO.replace("## Lunes 7 de septiembre", "## Lunes 21 de septiembre"))
    assert "fuera del ciclo abierto" in fuera.defecto

    [sin_type] = lint(SANO.replace(f"type: {TYPE_DEL_CICLO}\n", ""))
    assert "no declara `type`" in sin_type.defecto
    assert TYPE_DEL_CICLO in sin_type.correccion

    [archivado] = lint(SANO.replace(f"status: {STATUS_ABIERTO}", "status: stable"))
    assert "status: stable" in archivado.defecto


def test_sin_frontmatter_reporta_todo_lo_que_falta() -> None:
    defectos = " ".join(
        h.defecto for h in lint("# Actividad diaria\n\n## Lunes 7 de septiembre\n")
    )
    assert "frontmatter" in defectos and "`type`" in defectos and "`status`" in defectos
