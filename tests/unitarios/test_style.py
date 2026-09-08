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


def test_el_libro_completo_no_tiene_errores() -> None:
    assert [h for h in style.lint(COMPLETO) if h.grado == ERROR] == []


def test_falta_el_marcador_del_autor() -> None:
    sin_marcador = COMPLETO.replace("**Nombre del autor:** por declarar", "")

    errores = [h for h in style.lint(sin_marcador) if h.grado == ERROR]

    assert len(errores) == 1
    assert "Nombre del autor" in errores[0].defecto
    assert "tuku init --author" in errores[0].correccion


@pytest.mark.parametrize(
    "encabezado", ["### Clasificaciones", "### Horizontes", "### Tipos de nota"]
)
def test_falta_un_encabezado_de_contrato(encabezado: str) -> None:
    sin_encabezado = COMPLETO.replace(f"{encabezado}\n", "")

    errores = [h for h in style.lint(sin_encabezado) if h.grado == ERROR]

    assert any(encabezado in h.defecto for h in errores), [h.defecto for h in errores]


def test_una_tabla_sin_terminos_es_pregunta_y_no_error() -> None:
    """Vocabulario del autor: el sistema pregunta qué significa, no rechaza."""
    vacia = COMPLETO.replace("| `progreso` | avance |\n", "", 1)

    hallazgos = style.lint(vacia)

    assert any(h.grado == PREGUNTA and "Clasificaciones" in h.defecto for h in hallazgos)
    assert [h for h in hallazgos if h.grado == ERROR] == []


def test_un_libro_vacio_reporta_el_autor_y_los_tres_encabezados() -> None:
    errores = [h for h in style.lint("# Libro de estilo\n") if h.grado == ERROR]
    assert len(errores) >= 4


def test_ningun_hallazgo_queda_sin_defecto_ni_correccion() -> None:
    """La regla de `spec/cli.md`, como barrido: decir qué pasó no basta."""
    for texto in ("# Libro de estilo\n", COMPLETO.replace("### Horizontes\n", ""), ""):
        for h in style.lint(texto):
            assert h.defecto.strip(), f"hallazgo sin defecto en {texto[:20]!r}"
            assert h.correccion.strip(), f"hallazgo sin corrección: {h.defecto}"
