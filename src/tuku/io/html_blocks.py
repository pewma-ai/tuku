"""Parser y serializador de delimitadores HTML en Markdown (F1.5).

Cumple ADR 0013 y preserva íntegramente comentarios especiales:
- `<!-- tuku:editable --> ... <!-- /tuku:editable -->`
- `<!-- tuku:derived id=... hash=... --> ... <!-- /tuku:derived -->`
- `<!-- tuku:cadencias ... -->`
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class HTMLBlock:
    kind: str  # 'editable', 'derived', 'cadencias'
    attrs: dict[str, str] = field(default_factory=dict)
    content: str = ""
    raw: str = ""


def extract_html_blocks(text: str) -> list[HTMLBlock]:
    """Extrae bloques de delimitadores HTML de TUKU preservando su contenido exacto."""
    blocks: list[HTMLBlock] = []

    # 1. tuku:cadencias
    for match in re.finditer(r"<!--\s*tuku:cadencias\s*(.*?)\s*-->", text, re.DOTALL):
        blocks.append(
            HTMLBlock(
                kind="cadencias",
                content=match.group(1).strip(),
                raw=match.group(0),
            )
        )

    # 2. tuku:derived
    for match in re.finditer(
        r"<!--\s*tuku:derived\s*(.*?)\s*-->(.*?)<!--\s*/tuku:derived\s*-->",
        text,
        re.DOTALL,
    ):
        attr_str = match.group(1).strip()
        attrs: dict[str, str] = {}
        for pair in attr_str.split():
            if "=" in pair:
                k, v = pair.split("=", 1)
                attrs[k] = v.strip('"')

        blocks.append(
            HTMLBlock(
                kind="derived",
                attrs=attrs,
                content=match.group(2),
                raw=match.group(0),
            )
        )

    # 3. tuku:editable
    for match in re.finditer(
        r"<!--\s*tuku:editable\s*(.*?)\s*-->(.*?)<!--\s*/tuku:editable\s*-->",
        text,
        re.DOTALL,
    ):
        blocks.append(
            HTMLBlock(
                kind="editable",
                content=match.group(2),
                raw=match.group(0),
            )
        )

    return blocks


def replace_derived_block(text: str, block_id: str, new_content: str, new_hash: str) -> str:
    """Reemplaza el contenido de una zona derivada preservando los delimitadores HTML."""
    pattern = (
        rf"(<!--\s*tuku:derived\s+id={re.escape(block_id)}\s+hash=)(\w+)"
        rf"(\s*-->)(.*?)(<!--\s*/tuku:derived\s*-->)"
    )

    def repl(m: re.Match[str]) -> str:
        return f"{m.group(1)}{new_hash}{m.group(3)}{new_content}{m.group(5)}"

    return re.sub(pattern, repl, text, flags=re.DOTALL)
