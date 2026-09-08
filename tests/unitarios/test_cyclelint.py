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


def test_frontmatter_sin_resolver_es_error() -> None:
    sin_fechas = SANO.replace("2026-09-07", "AAAA-MM-DD").replace("2026-09-13", "AAAA-MM-DD")

    assert any("frontmatter" in h.defecto for h in lint(sin_fechas))


def test_dia_fuera_del_ciclo_es_error() -> None:
    hallazgos = lint(SANO.replace("## Lunes 7 de septiembre", "## Lunes 21 de septiembre"))

    assert len(hallazgos) == 1
    assert "fuera del ciclo abierto" in hallazgos[0].defecto


def test_falta_el_type() -> None:
    hallazgos = lint(SANO.replace(f"type: {TYPE_DEL_CICLO}\n", ""))

    assert len(hallazgos) == 1
    assert "no declara `type`" in hallazgos[0].defecto
    assert TYPE_DEL_CICLO in hallazgos[0].correccion


def test_un_ciclo_archivado_no_es_el_ciclo_abierto() -> None:
    hallazgos = lint(SANO.replace(f"status: {STATUS_ABIERTO}", "status: stable"))

    assert len(hallazgos) == 1
    assert "status: stable" in hallazgos[0].defecto


def test_sin_frontmatter_reporta_todo_lo_que_falta() -> None:
    hallazgos = lint("# Actividad diaria\n\n## Lunes 7 de septiembre\n")

    defectos = " ".join(h.defecto for h in hallazgos)
    assert "frontmatter" in defectos
    assert "`type`" in defectos
    assert "`status`" in defectos
