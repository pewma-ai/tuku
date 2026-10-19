"""Tests unitarios de extracción y formateo de vocabularios de `reglas/`."""

from __future__ import annotations

import pytest

from tuku.vocab import VocabularioIncompleto, formatear, leer, terminos

TEXTOS: dict[str, str | None] = {
    "reglas/bitacora.md": (
        "# Registro\n\n## Clasificaciones\n\n"
        "| Clasificación | Descripción |\n|---|---|\n"
        "| `reunión` | Encuentro |\n| `foco` | Bloque concentrado |\n"
    ),
    "reglas/pendientes.md": (
        "## Horizontes\n\n| Horizonte | Alcance |\n|---|---|\n| `hoy` | Día en curso |\n"
    ),
    "reglas/notas.md": (
        "## Tipos de nota\n\n| Tipo | Propósito |\n|---|---|\n| `persona` | Ficha |\n"
    ),
}


def test_leer_extrae_los_terminos_falla_ruidoso_si_falta_uno_y_se_formatea() -> None:
    assert leer(TEXTOS) == {
        "clasificaciones": ["reunión", "foco"],
        "horizontes": ["hoy"],
        "tipos-de-nota": ["persona"],
    }

    sin_capitulo = {**TEXTOS, "reglas/pendientes.md": "# Sin capítulos\n"}
    with pytest.raises(VocabularioIncompleto, match=r"## Horizontes.*reglas/pendientes.md"):
        leer(sin_capitulo)
    with pytest.raises(VocabularioIncompleto, match=r"falta reglas/notas\.md"):
        leer({**TEXTOS, "reglas/notas.md": None})
    assert terminos(TEXTOS["reglas/bitacora.md"], "clasificaciones") == ["reunión", "foco"]

    salida = formatear({"clasificaciones": ["reunión", "foco"], "horizontes": []})
    assert "clasificaciones: reunión, foco" in salida
    assert "horizontes: (ninguno declarado)" in salida
