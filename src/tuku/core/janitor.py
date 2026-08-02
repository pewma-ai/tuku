"""Implementación del Janitor e invariantes de TUKU (Fase 2).

Valida las invariantes del perfil y emite un reporte de violaciones.
"""

from __future__ import annotations

import re
from pathlib import Path

from pydantic import BaseModel, Field

from tuku.core.config import ProfileConfig
from tuku.io.frontmatter import parse_frontmatter


class Violation(BaseModel):
    invariant_id: str
    file_path: Path
    message: str


class JanitorReport(BaseModel):
    violations: list[Violation] = Field(default_factory=list)
    fixed_count: int = 0

    @property
    def is_clean(self) -> bool:
        return len(self.violations) == 0


class Janitor:
    def __init__(self, profile_dir: Path) -> None:
        self.profile_dir = profile_dir.resolve()
        self.config_path = self.profile_dir / ".tuku" / "config.yaml"

    def run_all(self, fix: bool = False) -> JanitorReport:
        report = JanitorReport()

        # F2.8: Perfil (F1, F2, F3, F4)
        report.violations.extend(self.check_perfil())

        # F2.1: Entidades (N1-N9)
        report.violations.extend(self.check_entidades())

        # F2.2: Entradas (E1-E7)
        report.violations.extend(self.check_entradas())

        # F2.3: Tareas (T1-T8)
        report.violations.extend(self.check_tareas())

        # F2.4: Cadencias (K1-K9)
        report.violations.extend(self.check_cadencias())

        # F2.5: Ciclos (C1-C7)
        report.violations.extend(self.check_ciclos())

        # F2.6: Procesos (R1-R6)
        report.violations.extend(self.check_procesos())

        # F2.7: Notas (O1-O8)
        report.violations.extend(self.check_notas())

        return report

    def check_perfil(self) -> list[Violation]:
        violations: list[Violation] = []

        if self.config_path.exists():
            try:
                cfg = ProfileConfig.from_yaml(self.config_path)
                # F4: Grafo acíclico
                for d in cfg.derivations:
                    if d.target in d.sources:
                        violations.append(
                            Violation(
                                invariant_id="F4",
                                file_path=self.config_path,
                                message=f"Ciclo directo detectado en {d.target}",
                            )
                        )
            except Exception as err:
                violations.append(
                    Violation(
                        invariant_id="F1",
                        file_path=self.config_path,
                        message=str(err),
                    )
                )

        capacidad_path = self.profile_dir / "estrategia" / "capacidad.md"
        if capacidad_path.exists():
            try:
                fm, _ = parse_frontmatter(capacidad_path.read_text(encoding="utf-8"))
                notify_window = fm.get("notify_window")
                if notify_window and not re.match(
                    r"^\d{2}:\d{2}-\d{2}:\d{2}$", str(notify_window)
                ):
                    violations.append(
                        Violation(
                            invariant_id="F2",
                            file_path=capacidad_path,
                            message=f"notify_window inválido: {notify_window!r}",
                        )
                    )
            except Exception as err:
                violations.append(
                    Violation(
                        invariant_id="F2",
                        file_path=capacidad_path,
                        message=f"Error parseando capacidad.md: {err}",
                    )
                )

        return violations

    def check_entidades(self) -> list[Violation]:
        violations: list[Violation] = []
        entidades_dir = self.profile_dir / "entidades"
        if not entidades_dir.exists():
            return violations

        seen_ids: dict[str, Path] = {}

        for md_file in sorted(entidades_dir.rglob("*.md")):
            try:
                fm, _ = parse_frontmatter(md_file.read_text(encoding="utf-8"))
            except Exception:
                violations.append(
                    Violation(
                        invariant_id="N1",
                        file_path=md_file,
                        message="Front matter inválido o ausente",
                    )
                )
                continue

            # N1: id y type requeridos
            ent_id = fm.get("id")
            ent_type = fm.get("type")
            if not ent_id or not ent_type:
                violations.append(
                    Violation(
                        invariant_id="N1",
                        file_path=md_file,
                        message="Entidad sin id o type obligatorio",
                    )
                )
                continue

            # N2: id único
            if ent_id in seen_ids:
                prev_path = seen_ids[ent_id].relative_to(self.profile_dir)
                violations.append(
                    Violation(
                        invariant_id="N2",
                        file_path=md_file,
                        message=f"id duplicado {ent_id!r} (visto en {prev_path})",
                    )
                )
            else:
                seen_ids[ent_id] = md_file

            # N3: dentro de un ámbito
            rel_parts = md_file.relative_to(entidades_dir).parts
            if len(rel_parts) < 2:
                violations.append(
                    Violation(
                        invariant_id="N3",
                        file_path=md_file,
                        message="La entidad debe colgar directamente de un ámbito",
                    )
                )

            # N7: alineamiento no vacío si vigente
            lifecycle = fm.get("lifecycle", "vigente")
            if lifecycle == "vigente" and not fm.get("alineamiento"):
                violations.append(
                    Violation(
                        invariant_id="N7",
                        file_path=md_file,
                        message="Entidad vigente sin campo alineamiento",
                    )
                )

        return violations

    def check_entradas(self) -> list[Violation]:
        violations: list[Violation] = []
        entradas_dir = self.profile_dir / "entradas"
        if not entradas_dir.exists():
            return violations

        for md_file in sorted(entradas_dir.rglob("*.md")):
            try:
                fm, _ = parse_frontmatter(md_file.read_text(encoding="utf-8"))
                rec_type = fm.get("type")
                if rec_type != "entradas":
                    violations.append(
                        Violation(
                            invariant_id="E1",
                            file_path=md_file,
                            message=f"type en entradas debe ser 'entradas', no {rec_type!r}",
                        )
                    )
            except Exception:
                violations.append(
                    Violation(
                        invariant_id="E1",
                        file_path=md_file,
                        message="Front matter de entradas inválido",
                    )
                )

        return violations

    def check_tareas(self) -> list[Violation]:
        violations: list[Violation] = []
        tareas_dir = self.profile_dir / "tareas"
        if not tareas_dir.exists():
            return violations

        for md_file in sorted(tareas_dir.rglob("*.md")):
            try:
                fm, _ = parse_frontmatter(md_file.read_text(encoding="utf-8"))
                rec_type = fm.get("type")
                if rec_type != "tareas":
                    violations.append(
                        Violation(
                            invariant_id="T1",
                            file_path=md_file,
                            message=f"type en tareas debe ser 'tareas', recibido {rec_type!r}",
                        )
                    )
            except Exception:
                violations.append(
                    Violation(
                        invariant_id="T1",
                        file_path=md_file,
                        message="Front matter de tareas inválido",
                    )
                )

        return violations

    def check_cadencias(self) -> list[Violation]:
        violations: list[Violation] = []
        # TODO: Implementar validación de invariantes K1-K9
        return violations

    def check_ciclos(self) -> list[Violation]:
        violations: list[Violation] = []
        # TODO: Implementar validación de invariantes C1-C7
        return violations

    def check_procesos(self) -> list[Violation]:
        violations: list[Violation] = []
        # TODO: Implementar validación de invariantes R1-R6
        return violations

    def check_notas(self) -> list[Violation]:
        violations: list[Violation] = []
        notas_dir = self.profile_dir / "notas"
        if not notas_dir.exists():
            return violations

        for md_file in sorted(notas_dir.rglob("*.md")):
            if md_file.name in {"notas.md", "AGENTS.md"}:
                continue
            try:
                fm, _ = parse_frontmatter(md_file.read_text(encoding="utf-8"))
                rec_type = fm.get("type")
                if rec_type != "nota":
                    violations.append(
                        Violation(
                            invariant_id="O1",
                            file_path=md_file,
                            message=f"type en nota debe ser 'nota', recibido {rec_type!r}",
                        )
                    )
                if "summary" not in fm:
                    violations.append(
                        Violation(
                            invariant_id="O2",
                            file_path=md_file,
                            message="Falta campo obligatorio summary en nota",
                        )
                    )
            except Exception:
                violations.append(
                    Violation(
                        invariant_id="O1",
                        file_path=md_file,
                        message="Front matter de nota inválido",
                    )
                )

        return violations
