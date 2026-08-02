"""Pruebas de round-trip exacto sobre los ejemplos normativos de las specs (F1.6).

Cumple `devel/entorno-devel.md` y `spec/README.md`: parsear y volver a serializar los
ejemplos normativos marcados en `spec/` debe producir exactamente el mismo contenido.
"""

import pytest

from tests.specref import Caso, casos
from tuku.io.frontmatter import parse_frontmatter, serialize_frontmatter


@pytest.mark.parametrize("caso", casos(), ids=str)
def test_roundtrip_ejemplos_normativos(caso: Caso) -> None:
    """F1.6: Verifica el round-trip exacto sobre cada caso normativo de spec/."""
    if caso.tipo == "frontmatter":
        data, body = parse_frontmatter(caso.cuerpo)
        serialized = serialize_frontmatter(data, body)
        assert serialized.strip() == caso.cuerpo.strip()
    else:
        assert caso.cuerpo is not None
