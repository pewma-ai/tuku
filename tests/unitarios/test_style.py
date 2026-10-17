"""Unitarios de `tuku.style`: los contratos de `LIBRO-DE-ESTILO.md`.

Son los que otros comandos necesitan para funcionar: el marcador del autor, que
`tuku init --author` sustituye, y los tres encabezados de vocabulario, que
`tuku vocab show` lee. La regla transversal de `spec/cli.md` también se afirma
acá, en un barrido: ningún hallazgo puede quedar sin corrección.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from tuku import style  # noqa: E402
from tuku.lint import ERROR, PREGUNTA  # noqa: E402

pytestmark = pytest.mark.unitario

TABLA = "| Término | Qué significa |\n| --- | --- |\n| `progreso` | avance |\n"
COMPLETO = (
    "# Libro de estilo\n\n## El autor\n\n**Nombre del autor:** por declarar\n\n"
    f"### Clasificaciones\n\n{TABLA}\n"
    f"### Horizontes\n\n{TABLA}\n"
    f"### Tipos de nota\n\n{TABLA}\n"
)


def _errores(texto: str) -> list[style.HallazgoEstilo]:
    return [h for h in style.lint(texto) if h.grado == ERROR]


def test_el_libro_completo_no_tiene_errores_y_falta_el_marcador_del_autor() -> None:
    assert _errores(COMPLETO) == []

    [error] = _errores(COMPLETO.replace("**Nombre del autor:** por declarar", ""))
    assert "Nombre del autor" in error.defecto
    assert "tuku init --author" in error.correccion


def test_falta_un_encabezado_de_contrato() -> None:
    for encabezado in ("### Clasificaciones", "### Horizontes", "### Tipos de nota"):
        errores = _errores(COMPLETO.replace(f"{encabezado}\n", ""))
        assert any(encabezado in h.defecto for h in errores), encabezado

    assert len(_errores("# Libro de estilo\n")) >= 4, (
        "el libro vacío reporta el autor y los tres"
    )


def test_una_tabla_sin_terminos_es_pregunta_y_no_error() -> None:
    """Vocabulario del autor: el sistema pregunta qué significa, no rechaza."""
    hallazgos = style.lint(COMPLETO.replace("| `progreso` | avance |\n", "", 1))

    assert any(h.grado == PREGUNTA and "Clasificaciones" in h.defecto for h in hallazgos)
    assert [h for h in hallazgos if h.grado == ERROR] == []


def test_ningun_hallazgo_queda_sin_defecto_ni_correccion() -> None:
    """La regla de `spec/cli.md`, como barrido: decir qué pasó no basta."""
    for texto in ("# Libro de estilo\n", COMPLETO.replace("### Horizontes\n", ""), ""):
        for h in style.lint(texto):
            assert h.defecto.strip(), f"hallazgo sin defecto en {texto[:20]!r}"
            assert h.correccion.strip(), f"hallazgo sin corrección: {h.defecto}"
