"""Tests del lint estructural de AHORA.md."""

from __future__ import annotations

from pathlib import Path

from tuku.cyclelint import (
    STATUS_ABIERTO,
    TYPE_DEL_CICLO,
    formatear,
    gaps_and_overlaps,
    lint,
)

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


def test_los_hoyos_y_solapes_entre_ciclos_se_reportan(tmp_path: Path) -> None:
    def ciclo(desde: str, hasta: str) -> str:
        return f"---\ntype: Logbook\nstatus: stable\nfrom: {desde}\nto: {hasta}\n---\n"

    (tmp_path / "bitacoras").mkdir()
    (tmp_path / "bitacoras" / "bitacora-2026-08-03-2026-08-09-semana.md").write_text(
        ciclo("2026-08-03", "2026-08-09"), encoding="utf-8"
    )
    (tmp_path / "bitacoras" / "bitacora-2026-08-12-2026-08-16-semana.md").write_text(
        ciclo("2026-08-12", "2026-08-16"), encoding="utf-8"
    )
    (tmp_path / "AHORA.md").write_text(ciclo("2026-08-15", "2026-08-21"), encoding="utf-8")

    solapes, huecos = gaps_and_overlaps(tmp_path)

    assert len(huecos) == 1 and "2026-08-10 y el 2026-08-11" in huecos[0]
    assert "--from 2026-08-10 --to 2026-08-11" in huecos[0]
    assert len(solapes) == 1 and solapes[0].startswith("AHORA.md: error:")
    assert "2026-08-16" in solapes[0]
