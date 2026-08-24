"""Parser y serializador de Front Matter YAML (F1.1).

Cumple `spec/frontmatter.md` y preserva el orden exacto de claves en round-trip.
"""

from __future__ import annotations

from typing import Any

import yaml


class FrontMatterError(Exception):
    """Error al parsear o serializar el Front Matter."""


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Separa y parsea el Front Matter YAML de un documento Markdown.

    Retorna una tupla (frontmatter_dict, resto_del_cuerpo).
    Si el documento no abre con `---`, retorna ({}, content).
    """
    lines = content.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return {}, content

    end_index = -1
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_index = idx
            break

    if end_index == -1:
        raise FrontMatterError("El Front Matter no tiene delimitador de cierre '---'")

    yaml_block = "".join(lines[1:end_index])
    body = "".join(lines[end_index + 1:])

    try:
        data = yaml.safe_load(yaml_block) or {}
    except Exception as err:
        raise FrontMatterError(f"Error parseando YAML: {err}") from err

    if not isinstance(data, dict):
        raise FrontMatterError("El Front Matter debe ser un objeto YAML (diccionario)")

    return data, body


def serialize_frontmatter(data: dict[str, Any], body: str) -> str:
    """Serializa un diccionario a Front Matter YAML y lo antepone al cuerpo."""
    if not data:
        return body

    yaml_str = yaml.dump(data, sort_keys=False, allow_unicode=True).strip()
    return f"---\n{yaml_str}\n---\n{body}"
