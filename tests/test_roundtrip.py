import pytest

from tests.specref import Caso, casos
from tuku.io.frontmatter import parse_frontmatter, serialize_frontmatter


@pytest.mark.parametrize("caso", casos(), ids=str)
def test_roundtrip_ejemplos_normativos(caso: Caso) -> None:
    """Verifica el round-trip exacto sobre los ejemplos normativos de las specs."""
    if caso.tipo == "frontmatter":
        data, body = parse_frontmatter(caso.cuerpo)
        serialized = serialize_frontmatter(data, body)
        assert serialized.strip() == caso.cuerpo.strip()
    else:
        assert caso.cuerpo is not None
