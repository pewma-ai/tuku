"""Pruebas del parser y serializador de Front Matter YAML (F1.1).

Verifica la separación de metadatos y reconstrucción exacta acorde a `spec/frontmatter.md`.
"""

import pytest

from tuku.io.frontmatter import FrontMatterError, parse_frontmatter, serialize_frontmatter


def test_roundtrip_frontmatter_exacto() -> None:
    """F1.1: Extracción de datos y reconstrucción exacta de Front Matter."""
    doc = (
        "---\n"
        "id: mi-entidad\n"
        "type: proyecto\n"
        "status: active\n"
        "---\n"
        "\n"
        "# Título del documento\n"
    )
    data, body = parse_frontmatter(doc)
    assert data == {"id": "mi-entidad", "type": "proyecto", "status": "active"}
    assert body == "\n# Título del documento\n"

    reser = serialize_frontmatter(data, body)
    assert reser == doc


def test_frontmatter_sin_delimitador_cierre_lanza_error() -> None:
    """M1: Front Matter sin '---' de cierre es rechazado con FrontMatterError."""
    doc = "---\nid: test\ntype: nota\n"
    with pytest.raises(FrontMatterError, match="cierre"):
        parse_frontmatter(doc)
