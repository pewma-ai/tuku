"""Pruebas del parser/serializador posicional de tareas (F1.2)."""

from tuku.io.task import TukuTask


def test_roundtrip_tarea_posicional_exacto() -> None:
    line = (
        "- [ ] 2026-08-01 2h nucleo-datos 2026-08-10 - - manual Diseñar interfaz ^t-2026-0001"
    )
    comment = "      <!-- tuku: cycles=1 process=cot-0042 step=2 -->"

    task = TukuTask.parse_line(line, comment_line=comment)
    assert task.created == "2026-08-01"
    assert task.effort == "2h"
    assert task.entity == "nucleo-datos"
    assert task.deadline == "2026-08-10"
    assert task.followup is None
    assert task.blockuntil is None
    assert task.originator == "manual"
    assert task.text == "Diseñar interfaz"
    assert task.task_id == "2026-0001"
    assert task.metadata["process"] == "cot-0042"

    serialized = task.serialize()
    assert line in serialized
    assert "process=cot-0042" in serialized
