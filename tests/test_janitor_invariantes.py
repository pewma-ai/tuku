"""Pruebas de janitors de Invariantes (Fase 2).

Cada test viola una invariante a propósito y exige que el Janitor la detecte.
"""

from pathlib import Path

from tuku.core.init import init_perfil
from tuku.core.janitor import Janitor


def test_N1_frontmatter_entidad_invalido(tmp_path: Path) -> None:
    """N1: Violación deliberada del Front Matter en una entidad (sin id ni type)."""
    perfil_dir = init_perfil(tmp_path / "perfil")
    ent_file = perfil_dir / "entidades" / "personal" / "invalida.md"
    ent_file.write_text("# Entidad sin frontmatter\n", encoding="utf-8")

    janitor = Janitor(perfil_dir)
    report = janitor.run_all()
    assert not report.is_clean
    inv_ids = [v.invariant_id for v in report.violations]
    assert "N1" in inv_ids


def test_N2_id_entidad_duplicado(tmp_path: Path) -> None:
    """N2: Violación deliberada por id duplicado en dos entidades distintas."""
    perfil_dir = init_perfil(tmp_path / "perfil")
    ent1 = perfil_dir / "entidades" / "personal" / "e1.md"
    ent2 = perfil_dir / "entidades" / "personal" / "e2.md"

    doc = "---\nid: igual-id\ntype: proyecto\nalineamiento: test\n---\n# E1\n"
    ent1.write_text(doc, encoding="utf-8")
    ent2.write_text(doc, encoding="utf-8")

    janitor = Janitor(perfil_dir)
    report = janitor.run_all()
    inv_ids = [v.invariant_id for v in report.violations]
    assert "N2" in inv_ids


def test_N3_entidad_fuera_de_ambito(tmp_path: Path) -> None:
    """N3: Entidad colgado directamente de `entidades/` sin ámbito (violación)."""
    perfil_dir = init_perfil(tmp_path / "perfil")
    ent_suelta = perfil_dir / "entidades" / "suelta.md"
    ent_suelta.write_text(
        "---\nid: suelta\ntype: proyecto\nalineamiento: test\n---\n# Suelta\n",
        encoding="utf-8",
    )

    janitor = Janitor(perfil_dir)
    report = janitor.run_all()
    inv_ids = [v.invariant_id for v in report.violations]
    assert "N3" in inv_ids


def test_N7_entidad_vigente_sin_alineamiento(tmp_path: Path) -> None:
    """N7: Violación deliberada por entidad vigente sin el campo obligatorio `alineamiento`."""
    perfil_dir = init_perfil(tmp_path / "perfil")
    ent = perfil_dir / "entidades" / "personal" / "sin_alineamiento.md"
    ent.write_text(
        "---\nid: sin-alin\ntype: proyecto\nlifecycle: vigente\n---\n# Sin alineamiento\n",
        encoding="utf-8",
    )

    janitor = Janitor(perfil_dir)
    report = janitor.run_all()
    inv_ids = [v.invariant_id for v in report.violations]
    assert "N7" in inv_ids


def test_F2_notify_window_invalido(tmp_path: Path) -> None:
    """F2: Violación deliberada del formato de notify_window en estrategia/capacidad.md."""
    perfil_dir = init_perfil(tmp_path / "perfil")
    cap = perfil_dir / "estrategia" / "capacidad.md"
    cap_content = (
        "---\nid: capacidad\ntype: capacidad\n"
        "notify_window: 'formato-incorrecto'\n---\n# Capacidad\n"
    )
    cap.write_text(cap_content, encoding="utf-8")

    janitor = Janitor(perfil_dir)
    report = janitor.run_all()
    inv_ids = [v.invariant_id for v in report.violations]
    assert "F2" in inv_ids


def test_O1_O2_nota_sin_summary(tmp_path: Path) -> None:
    """O1/O2: Violación deliberada por nota sin el campo `summary` obligatorio."""
    perfil_dir = init_perfil(tmp_path / "perfil")
    nota = perfil_dir / "notas" / "nota_mala.md"
    nota.write_text(
        "---\nid: nota-mala\ntype: nota\n---\n# Nota sin summary\n",
        encoding="utf-8",
    )

    janitor = Janitor(perfil_dir)
    report = janitor.run_all()
    inv_ids = [v.invariant_id for v in report.violations]
    assert "O2" in inv_ids
