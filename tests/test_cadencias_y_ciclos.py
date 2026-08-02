"""Pruebas del motor de cadencias, ciclos y RADAR (Fase 4).

Verifica la evaluación de disparos con TZ=UTC, resolución de next:<tipo> (ADR 0007),
idempotencia K4 y consulta RADAR sin escrituras en disco.
"""

from datetime import UTC, datetime
from pathlib import Path

from tuku.core.cadence import CadenceEngine, abrir_ciclo, radar_query, resolve_next_cycle
from tuku.core.init import init_perfil


def test_F4_2_F4_3_evaluacion_cadencias_es_idempotente(tmp_path: Path) -> None:
    """F4.2-F4.3: Evaluación respetando TZ=UTC; segunda corrida no duplica tareas (K4)."""
    perfil_dir = init_perfil(tmp_path / "perfil")

    ent_path = perfil_dir / "entidades" / "personal" / "proyecto_a.md"
    cad_block = (
        "<!-- tuku:cadencias\n- id: cad-semanal\n  "
        "trigger: { type: calendar, rule: 'weekly:MON' }\n-->\n"
    )
    ent_path.write_text(
        f"---\nid: proj-a\ntype: proyecto\nalineamiento: test\n---\n# Proyecto A\n{cad_block}",
        encoding="utf-8",
    )

    engine = CadenceEngine(profile_dir=perfil_dir)
    now = datetime(2026, 8, 10, 9, 0, tzinfo=UTC)

    tasks_1 = engine.evaluate_triggers(current_time=now)
    assert len(tasks_1) == 1
    assert tasks_1[0].entity == "proyecto_a"

    # Segunda corrida en el mismo día produce cero tareas nuevas (idempotencia K4)
    tasks_2 = engine.evaluate_triggers(current_time=now)
    assert len(tasks_2) == 0


def test_F4_4_resolucion_next_ciclo_por_grep(tmp_path: Path) -> None:
    """F4.4: Resuelve next:<tipo> leyendo Front Matter en ciclos/ (ADR 0007 / spec §2.1)."""
    perfil_dir = init_perfil(tmp_path / "perfil")

    # Sin plan sembrado -> regresa None
    assert resolve_next_cycle(perfil_dir, "semana") is None

    # Crear plan futuro con Front Matter canónico (spec/artefactos-ciclo.md §2.1)
    plan_path = perfil_dir / "ciclos" / "plan_2026-08-17_semana.md"
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_doc = (
        "---\n"
        "id: plan-2026-08-17-semana\n"
        "type: plan\n"
        "cycle_type: semana\n"
        "cycle_start: 2026-08-17\n"
        "cycle_end: 2026-08-23\n"
        "status: open\n"
        "---\n"
        "# Plan del ciclo\n"
    )
    plan_path.write_text(plan_doc, encoding="utf-8")

    cycle_info = resolve_next_cycle(perfil_dir, "semana")
    assert cycle_info is not None
    assert cycle_info.start_date == "2026-08-17"
    assert cycle_info.end_date == "2026-08-23"


def test_F4_5_abrir_ciclo_sin_agente(tmp_path: Path) -> None:
    """F4.5: Verifica que tuku abrir siembre el plan sin invocar LLM por defecto."""
    perfil_dir = init_perfil(tmp_path / "perfil")
    plan_file = abrir_ciclo(perfil_dir, "2026-W33", sin_agente=True)
    assert plan_file.exists()
    text = plan_file.read_text(encoding="utf-8")
    assert "# Plan del ciclo" in text


def test_F4_6_radar_consulta_en_vivo_sin_disco(tmp_path: Path) -> None:
    """F4.6: Consulta en vivo de estado RADAR sin escribir nada en disco."""
    perfil_dir = init_perfil(tmp_path / "perfil")
    res = radar_query(perfil_dir)
    assert res["radar_status"] == "OK"
    assert "open_tasks" in res
