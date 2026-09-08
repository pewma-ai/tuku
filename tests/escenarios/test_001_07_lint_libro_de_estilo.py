"""Test del escenario 001-07-lint-libro-de-estilo.

Escenario: 001-07-lint-libro-de-estilo.md

Verifica que el libro de estilo mantenga los contratos requeridos por los
comandos de TUKU:
- Marcador del autor (**Nombre del autor:**).
- Encabezados de contrato de las tablas de vocabulario (### Clasificaciones,
  ### Horizontes, ### Tipos de nota).
- Toda falla reporta defecto y corrección (spec/cli.md).

Ejecutable directo: python3 tests/escenarios/test_001_07_lint_libro_de_estilo.py
"""

from __future__ import annotations

import io
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

from vault import preparar_playground  # noqa: E402

from tuku import style  # noqa: E402
from tuku.cli import EXITO, RECHAZO, main  # noqa: E402
from tuku.init import MarcadorAutorFaltante, _sembrar_autor, init  # noqa: E402
from tuku.lint import ERROR, PREGUNTA  # noqa: E402

SLUG = "001-07-lint-libro-de-estilo"


def _correr(argv: list[str]) -> tuple[int | None, str, str]:
    out, err = io.StringIO(), io.StringIO()
    codigo: int | None = None
    with redirect_stdout(out), redirect_stderr(err):
        try:
            codigo = main(argv)
        except SystemExit as e:
            codigo = e.code if isinstance(e.code, int) else 1
    return codigo, out.getvalue(), err.getvalue()


def _vault() -> Path:
    destino = preparar_playground(SLUG)
    init(destino, variante="vanilla", home=RAIZ)
    return destino


def test_001_07_libro_de_estilo_vanilla_pasa_el_lint() -> None:
    vault = _vault()
    texto = (vault / "LIBRO-DE-ESTILO.md").read_text(encoding="utf-8")
    assert style.lint(texto) == [], "el libro de estilo vanilla no pasó el lint"

    codigo, salida, _ = _correr(["style", "lint", "--vault", str(vault)])
    assert codigo == EXITO
    assert "sin hallazgos" in salida


def test_001_07_falta_marcador_de_autor() -> None:
    vault = _vault()
    ruta = vault / "LIBRO-DE-ESTILO.md"
    lineas = [
        lin for lin in ruta.read_text(encoding="utf-8").splitlines()
        if "**Nombre del autor:**" not in lin
    ]
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")

    hallazgos = style.lint(ruta.read_text(encoding="utf-8"))
    assert any("Nombre del autor" in h.defecto and h.grado == ERROR for h in hallazgos)
    for h in hallazgos:
        assert h.correccion.strip()

    codigo, _, _ = _correr(["style", "lint", "--vault", str(vault)])
    assert codigo == RECHAZO

    try:
        _sembrar_autor(vault, "Pepe")
        raise AssertionError("debía fallar por falta de marcador")
    except MarcadorAutorFaltante as e:
        assert "Nombre del autor" in str(e)


def test_001_07_falta_encabezado_de_contrato() -> None:
    for encabezado in ("### Clasificaciones", "### Horizontes", "### Tipos de nota"):
        vault = _vault()
        ruta = vault / "LIBRO-DE-ESTILO.md"
        lineas = [
            lin for lin in ruta.read_text(encoding="utf-8").splitlines()
            if lin.strip() != encabezado
        ]
        ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")

        hallazgos = style.lint(ruta.read_text(encoding="utf-8"))
        assert any(encabezado in h.defecto and h.grado == ERROR for h in hallazgos)

        codigo, _, _ = _correr(["style", "lint", "--vault", str(vault)])
        assert codigo == RECHAZO

        codigo_v, _, err_v = _correr(["vocab", "show", "--vault", str(vault)])
        assert codigo_v == RECHAZO
        assert encabezado in err_v


def test_001_07_tabla_de_vocabulario_sin_terminos() -> None:
    vault = _vault()
    ruta = vault / "LIBRO-DE-ESTILO.md"
    texto = ruta.read_text(encoding="utf-8")
    # Vaciar las filas bajo Clasificaciones
    fila_progreso = "| `progreso` | Avance concreto en algo que estaba en curso. |\n"
    texto_vacio = texto.replace(fila_progreso, "")
    for term in ("decisión", "fricción", "señal", "nota"):
        texto_vacio = "\n".join(
            lin for lin in texto_vacio.splitlines() if f"`{term}`" not in lin
        )

    hallazgos = style.lint(texto_vacio)
    assert any("Clasificaciones" in h.defecto and h.grado == PREGUNTA for h in hallazgos)

    # Las preguntas no rechazan (salida 0)
    ruta.write_text(texto_vacio, encoding="utf-8")
    codigo, salida, _ = _correr(["style", "lint", "--vault", str(vault)])
    assert codigo == EXITO
    assert "pregunta(s)" in salida


def test_001_07_todo_hallazgo_del_lint_nombra_correccion() -> None:
    texto_roto = "# Libro de estilo\n\nSin nada mas.\n"
    hallazgos = style.lint(texto_roto)
    assert len(hallazgos) >= 4  # autor + 3 encabezados
    for h in hallazgos:
        assert h.defecto.strip()
        assert h.correccion.strip()


if __name__ == "__main__":
    test_001_07_libro_de_estilo_vanilla_pasa_el_lint()
    test_001_07_falta_marcador_de_autor()
    test_001_07_falta_encabezado_de_contrato()
    test_001_07_tabla_de_vocabulario_sin_terminos()
    test_001_07_todo_hallazgo_del_lint_nombra_correccion()
    print("ok: 5 afirmaciones (queda en playground/001-07-lint-libro-de-estilo/)")
