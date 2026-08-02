"""Pruebas del parser de delimitadores HTML (F1.5)."""

from tuku.io.html_blocks import extract_html_blocks, replace_derived_block


def test_preservar_comentario_cadencias() -> None:
    doc = """
# Entidad

<!-- tuku:cadencias
- id: cad-1
  trigger: { type: calendar, rule: "weekly:MON" }
-->
    """.strip()

    blocks = extract_html_blocks(doc)
    assert len(blocks) == 1
    assert blocks[0].kind == "cadencias"
    assert "cad-1" in blocks[0].content


def test_reemplazar_zona_derivada_preserva_delimitadores() -> None:
    doc = (
        "# Índice\n"
        "<!-- tuku:derived id=indice hash=123 -->\n"
        "viejo contenido\n"
        "<!-- /tuku:derived -->"
    )

    nuevo_doc = replace_derived_block(doc, "indice", "\nnuevo contenido\n", "456")
    assert "hash=456" in nuevo_doc
    assert "nuevo contenido" in nuevo_doc
    assert "<!-- /tuku:derived -->" in nuevo_doc
