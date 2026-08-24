"""Parser y serializador de Entradas de Bitácora (F1.3).

Cumple `spec/entradas.md` §3 y ADR 0017 (Pydantic v2).
"""

from __future__ import annotations

import re

from pydantic import BaseModel, Field

VALORES_CLASIFICACION_DEFAULT = {"Hito", "Decisión", "Señal", "Msg"}


class EntryError(Exception):
    """Error al parsear o serializar una entrada de bitácora."""


class Entry(BaseModel):
    time: str | None = None
    entity_id: str | None = None
    entity_path: str | None = None
    classification: str | None = None
    text: str
    tags: list[str] = Field(default_factory=list)

    @classmethod
    def parse_line(
        cls,
        line: str,
        clasificaciones_validas: set[str] | None = None,
    ) -> Entry:
        raw = line.strip()
        if not raw.startswith("- "):
            raise EntryError(f"La línea de entrada debe comenzar con '- ': {line!r}")

        content = raw[2:].strip()

        # 1. Hora opcional (HH:MM)
        time_val: str | None = None
        time_match = re.match(r"^\((\d{2}:\d{2})\)\s*", content)
        if time_match:
            time_val = time_match.group(1)
            content = content[time_match.end():].strip()

        # 2. Referencia a entidad opcional [<id>](<ruta>)
        entity_id: str | None = None
        entity_path: str | None = None
        entity_match = re.match(r"^\[([\w-]+)\]\(([^)]+)\)\s*", content)
        if entity_match:
            entity_id = entity_match.group(1)
            entity_path = entity_match.group(2)
            content = content[entity_match.end():].strip()

        # 3. Clasificación opcional **Clasificación:**
        classification: str | None = None
        class_match = re.match(r"^\*\*([\wáéíóúÁÉÍÓÚñÑ]+):\*\*\s*", content)
        if class_match:
            class_cand = class_match.group(1)
            validas = clasificaciones_validas or VALORES_CLASIFICACION_DEFAULT
            if class_cand in validas:
                classification = class_cand
                content = content[class_match.end():].strip()

        # 4. Extraer #marcadores del final del texto
        tags: list[str] = []
        words = content.split()
        text_words: list[str] = []
        for word in words:
            if word.startswith("#") and len(word) > 1:
                tags.append(word[1:])
            else:
                text_words.append(word)

        text = " ".join(text_words)

        return cls(
            time=time_val,
            entity_id=entity_id,
            entity_path=entity_path,
            classification=classification,
            text=text,
            tags=tags,
        )

    def serialize(self) -> str:
        parts = ["-"]

        if self.time:
            parts.append(f"({self.time})")

        if self.entity_id and self.entity_path:
            parts.append(f"[{self.entity_id}]({self.entity_path})")

        if self.classification:
            parts.append(f"**{self.classification}:**")

        parts.append(self.text)

        if self.tags:
            for tag in self.tags:
                parts.append(f"#{tag}")

        return " ".join(parts)
