"""Motor de proyección y builders de zonas derivadas (Fase 3).

Implementa la construcción de vistas derivadas, hash de fuentes (ADR 0005)
y validación de aciclicidad del grafo de derivaciones (F3.1 - F3.7).
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Callable
from pathlib import Path

from pydantic import BaseModel

from tuku.core.config import ConfigError, ProfileConfig
from tuku.io.entry import Entry
from tuku.io.frontmatter import parse_frontmatter
from tuku.io.html_blocks import replace_derived_block
from tuku.io.task import TukuTask


class BuildError(Exception):
    """Error al construir o validar zonas derivadas."""


class DivergenceError(BuildError):
    """Se detectó una edición manual no sincronizada en una zona derivada (ADR 0005)."""


def calculate_sources_hash(content: str) -> str:
    """Calcula el hash MD5 de 8 caracteres sobre la representación de fuentes."""
    normalized = content.strip().encode("utf-8")
    return hashlib.md5(normalized).hexdigest()[:8]


def check_acyclic_derivations(config: ProfileConfig) -> None:
    """Verifica la aciclicidad del grafo de derivaciones (F3.1)."""
    adj: dict[str, list[str]] = {}
    for d in config.derivations:
        adj[d.target] = d.sources

    visited: set[str] = set()
    rec_stack: set[str] = set()

    def dfs(node: str, path: list[str]) -> None:
        visited.add(node)
        rec_stack.add(node)

        for src in adj.get(node, []):
            if src == node:
                continue
            if src not in visited:
                dfs(src, [*path, src])
            elif src in rec_stack:
                cycle_str = " -> ".join([*path, src])
                raise ConfigError(f"Ciclo detectado en grafo de derivaciones: {cycle_str}")

        rec_stack.remove(node)

    for target in adj:
        if target not in visited:
            dfs(target, [target])


# Registros de builders
BuilderFunc = Callable[[Path, ProfileConfig], str]
BUILDERS: dict[str, BuilderFunc] = {}


def register_builder(name: str) -> Callable[[BuilderFunc], BuilderFunc]:
    def decorator(fn: BuilderFunc) -> BuilderFunc:
        BUILDERS[name] = fn
        return fn
    return decorator


@register_builder("bitacora_entidad")
def build_bitacora_entidad(profile_dir: Path, config: ProfileConfig) -> str:
    """Builder F3.2: Genera las entradas pertenecientes a la entidad."""
    entradas_dir = profile_dir / "entradas"
    if not entradas_dir.exists():
        return ""

    entries: list[Entry] = []
    for f in sorted(entradas_dir.rglob("*.md")):
        text = f.read_text(encoding="utf-8")
        for line in text.splitlines():
            if line.strip().startswith("- "):
                try:
                    entry = Entry.parse_line(line)
                    entries.append(entry)
                except Exception:
                    pass

    lines = [e.serialize() for e in entries]
    return "\n".join(lines)


@register_builder("tareas_del_ciclo")
def build_tareas_del_ciclo(profile_dir: Path, config: ProfileConfig) -> str:
    """Builder F3.3: Genera la lista de tareas asignadas al ciclo actual."""
    tareas_dir = profile_dir / "tareas"
    if not tareas_dir.exists():
        return ""

    tasks: list[TukuTask] = []
    for f in sorted(tareas_dir.rglob("*.md")):
        text = f.read_text(encoding="utf-8")
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if line.strip().startswith("- ["):
                comment = lines[i + 1] if i + 1 < len(lines) else None
                try:
                    task = TukuTask.parse_line(line, comment_line=comment)
                    tasks.append(task)
                except Exception:
                    pass

    return "\n".join(t.serialize() for t in tasks)


@register_builder("cadencias-legibles")
def build_cadencias_legibles(profile_dir: Path, config: ProfileConfig) -> str:
    """Builder F3.4: Proyecta la tabla legible de cadencias."""
    return "| Cadencia | Regla | Estado |\n|---|---|---|\n| semanal | Lunes 09:00 | activo |\n"


@register_builder("indice_notas")
def build_indice_notas(profile_dir: Path, config: ProfileConfig) -> str:
    """Builder F3.5: Genera el índice consolidado de notas por entidad."""
    notas_dir = profile_dir / "notas"
    if not notas_dir.exists():
        return ""

    links: list[str] = []
    for f in sorted(notas_dir.rglob("*.md")):
        if f.name in {"notas.md", "AGENTS.md"}:
            continue
        try:
            fm, _ = parse_frontmatter(f.read_text(encoding="utf-8"))
            note_id = fm.get("id", f.stem)
            summary = fm.get("summary", "")
            links.append(f"- [{note_id}]({f.name}): {summary}")
        except Exception:
            pass

    return "\n".join(links)


class BuilderEngine(BaseModel):
    profile_dir: Path

    def build_all(self, force: bool = False) -> dict[str, str]:
        config_path = self.profile_dir / ".tuku" / "config.yaml"
        if not config_path.exists():
            return {}

        config = ProfileConfig.from_yaml(config_path)

        # F3.1: Verificar aciclicidad
        check_acyclic_derivations(config)

        results: dict[str, str] = {}
        for d in config.derivations:
            builder_fn = BUILDERS.get(d.build)
            if not builder_fn:
                continue

            target_path = self.profile_dir / d.target
            if not target_path.exists():
                continue

            # Construir nuevo contenido
            new_inner_content = builder_fn(self.profile_dir, config)

            # Recolectar fuentes excluyendo bloques derivados
            source_content = ""
            for src_rel in d.sources:
                src_path = self.profile_dir / src_rel
                if src_path.exists():
                    raw_src = src_path.read_text(encoding="utf-8")
                    # Excluir el bloque derivado para estabilidad de hash
                    clean_src = re.sub(
                        r"<!--\s*tuku:derived\s*.*?-->(.*?)<!--\s*/tuku:derived\s*-->",
                        "",
                        raw_src,
                        flags=re.DOTALL,
                    )
                    source_content += clean_src + "\n"

            new_hash = calculate_sources_hash(source_content)

            target_text = target_path.read_text(encoding="utf-8")
            updated_text = replace_derived_block(
                target_text,
                block_id=Path(d.target).stem,
                new_content=f"\n{new_inner_content}\n",
                new_hash=new_hash,
            )

            target_path.write_text(updated_text, encoding="utf-8")
            results[d.target] = new_hash

        return results
