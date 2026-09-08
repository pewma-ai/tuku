"""Tests del escenario 001-07-lint-libro-de-estilo.

Escenario: 001-07-lint-libro-de-estilo.md

Los contratos que `LIBRO-DE-ESTILO.md` tiene que cumplir para que los comandos
de TUKU funcionen: el marcador de autor y los tres encabezados de vocabulario.
Todo rechazo nombra el defecto y la corrección, que es la regla de
`spec/cli.md`.

Los comandos salen del `.md`, que es la fuente ejecutable. Este arnés afirma
sobre lo que dejaron, pidiendo el resultado de cada comando por un trozo de su
texto (`corrida.de`), porque los escenarios corren el mismo comando sobre varios
vaults.

La única ruta que no pasa por un comando es la del `_sembrar_autor`, y el `.md`
dice por qué: `tuku init --author` sobre un vault existente exige `--force`, que
recopia el template y borra el defecto antes de poder probarlo.

Ejecutable directo: `python3 tests/escenarios/test_001_07_lint_libro_de_estilo.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import gherkin  # noqa: E402

from tuku import style  # noqa: E402
from tuku.cli import EXITO, RECHAZO  # noqa: E402
from tuku.init import MarcadorAutorFaltante, _sembrar_autor  # noqa: E402
from tuku.lint import ERROR, PREGUNTA  # noqa: E402

SLUG = "001-07-lint-libro-de-estilo"
MARCADOR = "**Nombre del autor:**"
ENCABEZADOS = {
    "sin-clasificaciones": "### Clasificaciones",
    "sin-horizontes": "### Horizontes",
    "sin-tipos-de-nota": "### Tipos de nota",
}


def test_001_07_libro_de_estilo_vanilla_pasa_el_lint() -> None:
    corrida = gherkin.correr(SLUG, "pasa el lint sin hallazgos")

    assert corrida.codigo == EXITO, corrida.stderr
    assert "sin hallazgos" in corrida.stdout


def test_001_07_falta_marcador_de_autor() -> None:
    corrida = gherkin.correr(SLUG, "falta el marcador de autor")
    vault = corrida.ruta("mi-vault")

    assert corrida.codigo == RECHAZO, "el lint no rechazó un libro sin marcador de autor"
    hallazgos = style.lint((vault / "LIBRO-DE-ESTILO.md").read_text(encoding="utf-8"))
    assert any("Nombre del autor" in h.defecto and h.grado == ERROR for h in hallazgos)
    for h in hallazgos:
        assert h.correccion.strip(), f"un hallazgo no nombra la corrección: {h.defecto}"

    try:
        _sembrar_autor(vault, "Pepe")
        raise AssertionError("sembrar el autor debía fallar por falta de marcador")
    except MarcadorAutorFaltante as e:
        assert "Nombre del autor" in str(e)


def test_001_07_falta_encabezado_de_contrato() -> None:
    corrida = gherkin.correr(SLUG, "falta un encabezado de contrato")

    for vault, encabezado in ENCABEZADOS.items():
        lint = corrida.de(f"style lint --vault {vault}")
        assert lint.codigo == RECHAZO, f"el lint no rechazó {vault}"

        texto = corrida.ruta(vault, "LIBRO-DE-ESTILO.md").read_text(encoding="utf-8")
        hallazgos = style.lint(texto)
        assert any(encabezado in h.defecto and h.grado == ERROR for h in hallazgos)

        vocab = corrida.de(f"vocab show --vault {vault}")
        assert vocab.codigo == RECHAZO, f"`vocab show` no se negó sobre {vault}"
        assert encabezado in vocab.stderr, f"el rechazo no nombra {encabezado}"


def test_001_07_tabla_de_vocabulario_sin_terminos() -> None:
    corrida = gherkin.correr(SLUG, "tabla de vocabulario vacía")

    texto = corrida.ruta("mi-vault", "LIBRO-DE-ESTILO.md").read_text(encoding="utf-8")
    hallazgos = style.lint(texto)
    assert any("Clasificaciones" in h.defecto and h.grado == PREGUNTA for h in hallazgos)

    assert corrida.codigo == EXITO, "una pregunta no rechaza"
    assert "pregunta(s)" in corrida.stdout


def test_001_07_todo_hallazgo_del_lint_nombra_correccion() -> None:
    """Barrido sobre la función pura: ningún hallazgo puede quedar sin corrección."""
    hallazgos = style.lint("# Libro de estilo\n\nSin nada mas.\n")
    assert len(hallazgos) >= 4, "faltan hallazgos: autor más los tres encabezados"
    for h in hallazgos:
        assert h.defecto.strip()
        assert h.correccion.strip()


if __name__ == "__main__":
    test_001_07_libro_de_estilo_vanilla_pasa_el_lint()
    test_001_07_falta_marcador_de_autor()
    test_001_07_falta_encabezado_de_contrato()
    test_001_07_tabla_de_vocabulario_sin_terminos()
    test_001_07_todo_hallazgo_del_lint_nombra_correccion()
    print(f"ok: 5 afirmaciones (queda en playground/{SLUG}/)")
