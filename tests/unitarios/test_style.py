"""Unitarios de `tuku.style`: los contratos del libro de estilo y de `reglas/`.

Son los que otros comandos necesitan para funcionar: el marcador del autor, que
`tuku init --author` sustituye, los capítulos de vocabulario, que `tuku context
style` lee, una sola tabla por capítulo y transclusiones que apunten a un archivo.
La regla transversal de `spec/cli.md` también se afirma acá, en un barrido:
ningún hallazgo puede quedar sin corrección.
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
COMPLETO: dict[str, str | None] = {
    "LIBRO-DE-ESTILO.md": "# Libro\n\n## Registro\n\n![Registro](reglas/bitacora.md)\n",
    "reglas/autor.md": "## Autor\n\n**Nombre del autor:** por declarar\n",
    "reglas/bitacora.md": f"## Clasificaciones\n\n{TABLA}",
    "reglas/pendientes.md": f"## Horizontes\n\n{TABLA}",
    "reglas/notas.md": f"## Tipos de nota\n\n{TABLA}",
}


def _con(**cambios: str | None) -> dict[str, str | None]:
    """`COMPLETO` con los archivos cambiados (el guion bajo hace de `/` y de `.`)."""
    rutas = {ruta.replace("/", "_").replace(".", "_"): ruta for ruta in COMPLETO}
    return {**COMPLETO, **{rutas[nombre]: texto for nombre, texto in cambios.items()}}


def _errores(textos: dict[str, str | None]) -> list[style.HallazgoEstilo]:
    return [h for h in style.lint(textos) if h.grado == ERROR]


def test_lo_completo_no_tiene_errores_y_cada_contrato_que_falta_es_uno() -> None:
    assert _errores(COMPLETO) == []

    [error] = _errores(_con(reglas_autor_md="## Autor\n"))
    assert "Nombre del autor" in error.defecto
    assert "tuku init --author" in error.correccion

    for ruta, capitulo in (
        ("reglas/bitacora.md", "Clasificaciones"),
        ("reglas/pendientes.md", "Horizontes"),
        ("reglas/notas.md", "Tipos de nota"),
    ):
        sin_capitulo = {**COMPLETO, ruta: "# Sin capítulos\n"}
        [h] = _errores(sin_capitulo)
        assert (h.archivo, capitulo in h.defecto) == (ruta, True)
        sin_archivo = _errores({**COMPLETO, ruta: None})
        assert (ruta, "falta el archivo") in [(h.archivo, h.defecto) for h in sin_archivo]

    vacio: dict[str, str | None] = dict.fromkeys(COMPLETO)
    assert len(_errores(vacio)) == 4, "sin archivos, falta el autor y los tres de vocabulario"


def test_una_tabla_sin_terminos_es_pregunta_y_no_error() -> None:
    """Vocabulario del autor: el sistema pregunta qué significa, no rechaza."""
    sin_filas = f"## Clasificaciones\n\n{TABLA.replace('| `progreso` | avance |', '')}"
    hallazgos = style.lint(_con(reglas_bitacora_md=sin_filas))

    assert any(h.grado == PREGUNTA and "Clasificaciones" in h.defecto for h in hallazgos)
    assert [h for h in hallazgos if h.grado == ERROR] == []


def test_un_capitulo_lleva_una_tabla_y_una_transclusion_apunta_a_un_archivo() -> None:
    dos = f"## Clasificaciones\n\n{TABLA}\nOtra:\n\n{TABLA}"
    [h] = _errores(_con(reglas_bitacora_md=dos))
    assert (h.archivo, "2 tablas" in h.defecto) == ("reglas/bitacora.md", True)

    en_valla = f"## Clasificaciones\n\n{TABLA}\n```\n{TABLA}```\n"
    assert _errores(_con(reglas_bitacora_md=en_valla)) == [], (
        "un ejemplo en una valla no cuenta"
    )

    huerfana = "## Nota\n\n![Nota](reglas/notas-viejas.md)\n"
    [h] = _errores({**COMPLETO, "LIBRO-DE-ESTILO.md": huerfana})
    assert "reglas/notas-viejas.md" in h.defecto


def test_ningun_hallazgo_queda_sin_defecto_ni_correccion() -> None:
    """La regla de `spec/cli.md`, como barrido: decir qué pasó no basta."""
    casos = (
        dict.fromkeys(COMPLETO),
        _con(reglas_pendientes_md="# Sin capítulos\n"),
        _con(reglas_bitacora_md=f"## Clasificaciones\n\n{TABLA}\n{TABLA}"),
        {**COMPLETO, "LIBRO-DE-ESTILO.md": "## X\n\n![](reglas/falta.md)\n"},
    )
    for textos in casos:
        for h in style.lint(textos):
            assert h.defecto.strip(), f"hallazgo sin defecto en {h.archivo}"
            assert h.correccion.strip(), f"hallazgo sin corrección: {h.defecto}"
