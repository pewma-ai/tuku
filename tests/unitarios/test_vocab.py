"""Tests unitarios de extracción y formateo de vocabularios de `reglas/`."""

from __future__ import annotations

import pytest

from tuku.vocab import VocabularioIncompleto, formatear, leer, terminos

TEXTOS: dict[str, str | None] = {
    "reglas/clasificaciones.user.md": (
        "---\ntype: Style Guide\n---\n\n"
        "| Clasificación | Descripción |\n|---|---|\n"
        "| `reunión` | Encuentro |\n| `foco` | Bloque concentrado |\n"
    ),
    "reglas/pendientes.user.md": (
        "| Horizonte | Alcance |\n|---|---|\n| `hoy` | Día en curso |\n"
    ),
    "reglas/notas.user.md": ("| Tipo | Propósito |\n|---|---|\n| `persona` | Ficha |\n"),
    "reglas/ciclo.user.md": "| Ciclo | Días |\n|---|---|\n| `semana` | 7 |\n",
}


def test_leer_extrae_los_terminos_falla_ruidoso_si_falta_uno_y_se_formatea() -> None:
    assert leer(TEXTOS) == {
        "clasificaciones": ["reunión", "foco"],
        "horizontes": ["hoy"],
        "tipos-de-nota": ["persona"],
        "ciclos": ["semana"],
    }

    sin_tabla = {**TEXTOS, "reglas/pendientes.user.md": "Solo prosa.\n"}
    with pytest.raises(
        VocabularioIncompleto, match=r"falta la tabla.*reglas/pendientes\.user\.md"
    ):
        leer(sin_tabla)
    with pytest.raises(VocabularioIncompleto, match=r"falta reglas/notas\.user\.md"):
        leer({**TEXTOS, "reglas/notas.user.md": None})
    assert terminos(TEXTOS["reglas/clasificaciones.user.md"], "clasificaciones") == [
        "reunión",
        "foco",
    ]

    salida = formatear({"clasificaciones": ["reunión", "foco"], "horizontes": []})
    assert "clasificaciones: reunión, foco" in salida
    assert "horizontes: (ninguno declarado)" in salida
