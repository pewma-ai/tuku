"""Tests unitarios de extracción y formateo de vocabularios del libro de estilo."""

from __future__ import annotations

import pytest

from tuku.vocab import VocabularioIncompleto, formatear, leer


def test_leer_vocabularios_extrae_terminos_correctamente() -> None:
    libro = (
        "# Libro de estilo\n\n"
        "### Clasificaciones\n\n"
        "| Clasificación | Descripción |\n"
        "|---|---|\n"
        "| `reunión` | Encuentro |\n"
        "| `foco` | Bloque concentrado |\n\n"
        "### Horizontes\n\n"
        "| Horizonte | Alcance |\n"
        "|---|---|\n"
        "| `hoy` | Día en curso |\n\n"
        "### Tipos de nota\n\n"
        "| Tipo | Propósito |\n"
        "|---|---|\n"
        "| `persona` | Ficha |\n"
    )
    res = leer(libro)
    assert res == {
        "clasificaciones": ["reunión", "foco"],
        "horizontes": ["hoy"],
        "tipos-de-nota": ["persona"],
    }


def test_leer_vocabulario_incompleto_lanza_excepcion() -> None:
    libro = "# Libro de estilo incompleto\n\n### Clasificaciones\n| `reunión` | Descripción |\n"
    with pytest.raises(VocabularioIncompleto, match="Horizontes"):
        leer(libro)


def test_formatear_con_terminos_declarados() -> None:
    datos = {
        "clasificaciones": ["reunión", "foco"],
        "horizontes": ["hoy"],
    }
    salida = formatear(datos)
    assert "clasificaciones: reunión, foco" in salida
    assert "horizontes: hoy" in salida


def test_formatear_sin_terminos_muestra_ninguno_declarado() -> None:
    datos: dict[str, list[str]] = {
        "clasificaciones": [],
        "tipos-de-nota": [],
    }
    salida = formatear(datos)
    assert "clasificaciones: (ninguno declarado)" in salida
    assert "tipos-de-nota: (ninguno declarado)" in salida
