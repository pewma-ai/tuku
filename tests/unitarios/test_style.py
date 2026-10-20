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
AUTOR = "| Campo | Valor |\n| --- | --- |\n| Nombre | PEDIR AL AUTOR! |\n"
COMPLETO: dict[str, str | None] = {
    "LIBRO-DE-ESTILO.md": "# Libro\n\n## Registro\n\n![](reglas/clasificaciones.user.md)\n",
    "reglas/autor.user.md": AUTOR,
    "reglas/clasificaciones.user.md": TABLA,
    "reglas/pendientes.user.md": TABLA,
    "reglas/notas.user.md": TABLA,
    "reglas/ciclo.user.md": TABLA,
}


def _con(**cambios: str | None) -> dict[str, str | None]:
    """`COMPLETO` con los archivos cambiados (el guion bajo hace de `/` y de `.`)."""
    rutas = {ruta.replace("/", "_").replace(".", "_"): ruta for ruta in COMPLETO}
    return {**COMPLETO, **{rutas[nombre]: texto for nombre, texto in cambios.items()}}


def _errores(textos: dict[str, str | None]) -> list[style.HallazgoEstilo]:
    return [h for h in style.lint(textos) if h.grado == ERROR]


def test_lo_completo_no_tiene_errores_y_cada_contrato_que_falta_es_uno() -> None:
    assert _errores(COMPLETO) == []

    [error] = _errores(
        _con(reglas_autor_user_md="| Campo | Valor |\n| --- | --- |\n| Rol | x |\n")
    )
    assert "Nombre" in error.defecto
    assert "tuku init --author" in error.correccion

    for ruta in (
        "reglas/clasificaciones.user.md",
        "reglas/pendientes.user.md",
        "reglas/notas.user.md",
    ):
        sin_tabla = {**COMPLETO, ruta: "Solo prosa.\n"}
        [h] = _errores(sin_tabla)
        assert (h.archivo, "tabla" in h.defecto) == (ruta, True)
        sin_archivo = _errores({**COMPLETO, ruta: None})
        assert (ruta, "falta el archivo") in [(h.archivo, h.defecto) for h in sin_archivo]

    vacio: dict[str, str | None] = dict.fromkeys(COMPLETO)
    assert len(_errores(vacio)) == 5, "sin archivos, falta el autor y los cuatro de vocabulario"


def test_una_tabla_sin_terminos_es_pregunta_y_no_error() -> None:
    """Vocabulario del autor: el sistema pregunta qué significa, no rechaza."""
    sin_filas = TABLA.replace("| `progreso` | avance |\n", "")
    hallazgos = style.lint(_con(reglas_clasificaciones_user_md=sin_filas))

    assert any(h.grado == PREGUNTA and "ningún término" in h.defecto for h in hallazgos)
    assert [h for h in hallazgos if h.grado == ERROR] == []


def test_un_archivo_del_autor_lleva_una_tabla_y_una_transclusion_apunta_a_un_archivo() -> None:
    dos = f"{TABLA}\nOtra:\n\n{TABLA}"
    [h] = _errores(_con(reglas_clasificaciones_user_md=dos))
    assert (h.archivo, "2 tablas" in h.defecto) == ("reglas/clasificaciones.user.md", True)

    en_valla = f"{TABLA}\n```\n{TABLA}```\n"
    assert _errores(_con(reglas_clasificaciones_user_md=en_valla)) == [], (
        "un ejemplo en una valla no cuenta"
    )

    dos_en_el_libro = f"## Cadencia\n\n{TABLA}\nY otra:\n\n{TABLA}"
    [h] = _errores({**COMPLETO, "LIBRO-DE-ESTILO.md": dos_en_el_libro})
    assert "Cadencia" in h.defecto and "2 tablas" in h.defecto

    huerfana = "## Nota\n\n![Nota](reglas/notas-viejas.md)\n"
    [h] = _errores({**COMPLETO, "LIBRO-DE-ESTILO.md": huerfana})
    assert "reglas/notas-viejas.md" in h.defecto


def test_ningun_hallazgo_queda_sin_defecto_ni_correccion() -> None:
    """La regla de `spec/cli.md`, como barrido: decir qué pasó no basta."""
    casos = (
        dict.fromkeys(COMPLETO),
        _con(reglas_pendientes_user_md="Sin tabla\n"),
        _con(reglas_clasificaciones_user_md=f"{TABLA}\n{TABLA}"),
        {**COMPLETO, "LIBRO-DE-ESTILO.md": "## X\n\n![](reglas/falta.md)\n"},
    )
    for textos in casos:
        for h in style.lint(textos):
            assert h.defecto.strip(), f"hallazgo sin defecto en {h.archivo}"
            assert h.correccion.strip(), f"hallazgo sin corrección: {h.defecto}"
