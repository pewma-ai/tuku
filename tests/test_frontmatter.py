"""Pruebas del parser/serializador de Front Matter (F1.1)."""

import pytest

from tuku.io.frontmatter import FrontMatterError, parse_frontmatter, serialize_frontmatter


def test_roundtrip_frontmatter_exacto() -> None:
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
    doc = "---\nid: test\ntype: nota\n"
    with pytest.raises(FrontMatterError, match="cierre"):
        parse_frontmatter(doc)
