"""Parser y serializador posicional de tareas Markdown (F1.2).

Cumple ADR 0014 y `spec/tarea.md` §3.
Formato posicional:
- [ ] <created> <effort> <entity|-> <deadline|-> <followup|-> <blockuntil|->
      <originator> <texto> ^t-<id>
      <!-- tuku: cycles=N outcome=... completed=... deps=... process=... -->
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


class TaskError(Exception):
    """Error al parsear o serializar una tarea posicional."""


@dataclass
class TukuTask:
    created: str
    effort: str
    entity: str | None
    deadline: str | None
    followup: str | None
    blockuntil: str | None
    originator: str
    text: str
    task_id: str
    status: str = "open"  # 'open' ([ ]), 'completed' ([x]), 'cancelled' ([-])
    metadata: dict[str, Any] = field(default_factory=dict)
    quote: str | None = None

    @classmethod
    def parse_line(
        cls,
        line: str,
        comment_line: str | None = None,
        quote_lines: list[str] | None = None,
    ) -> TukuTask:
        raw = line.strip()
        if raw.startswith("- [ ] "):
            status = "open"
            raw = raw[6:].strip()
        elif raw.startswith("- [x] ") or raw.startswith("- [X] "):
            status = "completed"
            raw = raw[6:].strip()
        elif raw.startswith("- [-] "):
            status = "cancelled"
            raw = raw[6:].strip()
        else:
            raise TaskError(f"Línea de tarea no comienza con formato válido: {line!r}")

        # Extraer ^t-id del final
        id_match = re.search(r"\^t-([\w-]+)$", raw)
        if not id_match:
            raise TaskError(f"Línea de tarea no contiene id ^t-id al final: {line!r}")

        task_id = id_match.group(1)
        content_part = raw[: id_match.start()].strip()

        # Partes separadas por espacio
        parts = content_part.split(maxsplit=7)
        if len(parts) < 8:
            raise TaskError(f"Línea posicional incompleta: {line!r}")

        (
            created,
            effort,
            entity_raw,
            deadline_raw,
            followup_raw,
            blockuntil_raw,
            originator,
            text,
        ) = parts

        metadata: dict[str, Any] = {}
        if comment_line and "<!-- tuku:" in comment_line:
            match = re.search(r"<!-- tuku:\s*(.*?)\s*-->", comment_line)
            if match:
                pairs = match.group(1).split()
                for pair in pairs:
                    if "=" in pair:
                        k, v = pair.split("=", 1)
                        metadata[k] = v

        quote = "".join(quote_lines) if quote_lines else None

        return cls(
            created=created,
            effort=effort,
            entity=None if entity_raw == "-" else entity_raw,
            deadline=None if deadline_raw == "-" else deadline_raw,
            followup=None if followup_raw == "-" else followup_raw,
            blockuntil=None if blockuntil_raw == "-" else blockuntil_raw,
            originator=originator,
            text=text,
            task_id=task_id,
            status=status,
            metadata=metadata,
            quote=quote,
        )

    def serialize(self) -> str:
        if self.status == "open":
            check = "[ ]"
        elif self.status == "completed":
            check = "[x]"
        else:
            check = "[-]"

        ent = self.entity if self.entity else "-"
        dl = self.deadline if self.deadline else "-"
        fl = self.followup if self.followup else "-"
        bu = self.blockuntil if self.blockuntil else "-"

        line = (
            f"- {check} {self.created} {self.effort} {ent} {dl} {fl} {bu} "
            f"{self.originator} {self.text} ^t-{self.task_id}"
        )

        res = [line]
        if self.metadata:
            meta_str = " ".join(f"{k}={v}" for k, v in sorted(self.metadata.items()))
            res.append(f"      <!-- tuku: {meta_str} -->")
        if self.quote:
            res.append(self.quote)

        return "\n".join(res)
