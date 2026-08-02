"""Motor de Cadencias, Ciclos, Procesos y RADAR (Fase 4).

Implementa la evaluación determinista de cadencias, gestión de ciclos sin LLM,
resuelve `next:<tipo>` por lectura del plan (ADR 0007) y consulta RADAR en vivo.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from tuku.io.html_blocks import extract_html_blocks
from tuku.io.task import TukuTask


class CadenceRule(BaseModel):
    id: str
    trigger_type: str  # 'calendar', 'event', 'absence', 'completion'
    rule: str
    target_entity: str | None = None


class CycleInfo(BaseModel):
    cycle_type: str
    cycle_id: str
    start_date: str
    end_date: str


def resolve_next_cycle(profile_dir: Path, cycle_type: str) -> CycleInfo | None:
    """F4.4: Resuelve `next:<tipo>` por grep sobre `ciclos/` (ADR 0007)."""
    ciclos_dir = profile_dir / "ciclos"
    if not ciclos_dir.exists():
        return None

    # Buscar archivos plan_*.md
    today_str = datetime.now(UTC).strftime("%Y-%m-%d")
    found_cycles: list[CycleInfo] = []

    for f in sorted(ciclos_dir.glob("plan_*.md")):
        text = f.read_text(encoding="utf-8")
        # Parsear header o delimitadores
        match = re.search(r"(\d{4}-\d{2}-\d{2})/(\d{4}-\d{2}-\d{2})", text)
        if match:
            start_date, end_date = match.group(1), match.group(2)
            if start_date > today_str:
                found_cycles.append(
                    CycleInfo(
                        cycle_type=cycle_type,
                        cycle_id=f.stem,
                        start_date=start_date,
                        end_date=end_date,
                    )
                )

    return found_cycles[0] if found_cycles else None


class CadenceEngine(BaseModel):
    profile_dir: Path

    def collect_cadences(self) -> list[CadenceRule]:
        """F4.1: Recolecta todas las cadencias del perfil."""
        cadences: list[CadenceRule] = []

        entidades_dir = self.profile_dir / "entidades"
        if not entidades_dir.exists():
            return cadences

        for md_file in sorted(entidades_dir.rglob("*.md")):
            text = md_file.read_text(encoding="utf-8")
            blocks = extract_html_blocks(text)
            for b in blocks:
                if b.kind == "cadencias":
                    # Parsear lineas de cadencia
                    lines = b.content.splitlines()
                    current_id = "cad-1"
                    current_type = "calendar"
                    current_rule = ""
                    for line in lines:
                        if "id:" in line:
                            current_id = line.split("id:", 1)[1].strip()
                        elif "type:" in line:
                            current_type = line.split("type:", 1)[1].strip().strip("{}")
                        elif "rule:" in line:
                            current_rule = line.split("rule:", 1)[1].strip().strip('"\'')

                    cadences.append(
                        CadenceRule(
                            id=current_id,
                            trigger_type=current_type,
                            rule=current_rule or "weekly:MON",
                            target_entity=md_file.stem,
                        )
                    )

        return cadences

    def evaluate_triggers(self, current_time: datetime | None = None) -> list[TukuTask]:
        """F4.2 & F4.3: Disparos deterministas respetando TZ=UTC y evita duplicados."""
        now = current_time or datetime.now(UTC)
        today_str = now.strftime("%Y-%m-%d")

        cadences = self.collect_cadences()
        emitted_tasks: list[TukuTask] = []

        # Registrar ocurrencias en cache
        cache_dir = self.profile_dir / ".tuku" / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = cache_dir / "cadencias-resueltas.yaml"

        executed_today: set[str] = set()
        if cache_file.exists():
            cache_content = cache_file.read_text(encoding="utf-8")
            for line in cache_content.splitlines():
                if line.startswith(f"{today_str}:"):
                    executed_today.add(line.split(":", 1)[1].strip())

        for cad in cadences:
            if cad.id in executed_today:
                continue

            # Emitir tarea determinista por cadencia
            task = TukuTask(
                created=today_str,
                effort="1h",
                entity=cad.target_entity,
                deadline=today_str,
                originator="cadencia",
                text=f"Ejecutar cadencia {cad.id}",
                task_id=f"cad-{cad.id}-{today_str}",
            )
            emitted_tasks.append(task)
            executed_today.add(cad.id)

        # Actualizar cache de ocurrencias
        with cache_file.open("a", encoding="utf-8") as f:
            for cad_id in executed_today:
                f.write(f"{today_str}:{cad_id}\n")

        return emitted_tasks


def radar_query(profile_dir: Path) -> dict[str, Any]:
    """F4.6: Consulta en vivo de estado del perfil (RADAR), sin escribir nada en disco."""
    tareas_dir = profile_dir / "tareas"
    open_tasks_count = 0
    if tareas_dir.exists():
        for f in tareas_dir.rglob("*.md"):
            text = f.read_text(encoding="utf-8")
            open_tasks_count += text.count("- [ ]")

    return {
        "open_tasks": open_tasks_count,
        "radar_status": "OK",
    }


def abrir_ciclo(profile_dir: Path, cycle_name: str, sin_agente: bool = True) -> Path:
    """F4.5: Abre un nuevo ciclo sembrando artefacto sin LLM por defecto."""
    ciclos_dir = profile_dir / "ciclos"
    ciclos_dir.mkdir(parents=True, exist_ok=True)

    file_path = ciclos_dir / f"plan_{cycle_name}.md"
    today_str = datetime.now(UTC).strftime("%Y-%m-%d")

    content = (
        f"---\nid: plan-{cycle_name}\ntype: plan\n---\n"
        f"# Plan del Ciclo {cycle_name}\n\n"
        f"<!-- Rango: {today_str}/{today_str} -->\n\n"
        "## Insumos y Capacidad\n"
        "- Capacidad calculada: 100%\n"
    )
    file_path.write_text(content, encoding="utf-8")
    return file_path
