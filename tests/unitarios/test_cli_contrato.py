"""El contrato del CLI que no necesita un vault: códigos, uso, correcciones y propuestas."""

from __future__ import annotations

from pathlib import Path

import pytest

from tuku import cli
from tuku.cli import ENTORNO, EXITO, RECHAZO, USO, manual
from tuku.lint import lint

RAIZ = Path(__file__).resolve().parent.parent.parent
PERSONAL = "[personal](ambitos/personal/personal.md)"


def test_los_cuatro_codigos_son_distintos() -> None:
    codigos = [EXITO, RECHAZO, USO, ENTORNO]
    assert len(set(codigos)) == len(codigos), "dos causas comparten código de salida"


def test_un_sustantivo_sin_verbo_es_error_de_uso() -> None:
    for noun in ("entry", "todo", "scope", "note", "cycle", "vocab", "style"):
        with pytest.raises(SystemExit) as salida:
            cli.main([noun])
        assert salida.value.code == USO, noun


def test_todo_hallazgo_del_lint_nombra_la_correccion() -> None:
    ahora = (
        "## Martes 11 de agosto\n\n"
        f"- 12:05 - {PERSONAL} **cachureo**: ordené los cables\n"
        f"- 13:00 - {PERSONAL} **Cadencia**: comprar una maleta\n"
    )
    hallazgos = lint(ahora, abiertos=["progreso"])
    assert len(hallazgos) >= 2, hallazgos
    for h in hallazgos:
        assert h.correccion.strip(), f"hallazgo sin corrección: {h.defecto}"


def test_ningun_comando_escribe_una_propuesta() -> None:
    """La propuesta no tiene comando a propósito: se muestra y espera."""
    nombres = [e.nombre for e in manual.entradas(cli._construir_parser())]
    assert not any("propose" in n for n in nombres), nombres
    for fuente in (RAIZ / "src" / "tuku").rglob("*.py"):
        assert "propuestas/" not in fuente.read_text(encoding="utf-8"), fuente.name
