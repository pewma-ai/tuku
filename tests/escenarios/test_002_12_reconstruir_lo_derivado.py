"""Tests del escenario 002-12-reconstruir-lo-derivado.

Escenario: 002-12-reconstruir-lo-derivado.md

El principio 9 de TUKU: lo derivado no es fuente de verdad, se regenera desde
el conjunto canónico y borrarlo debe devolver exactamente el mismo resultado
byte a byte.

Ejecutable directo: `python3 tests/escenarios/test_002_12_reconstruir_lo_derivado.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import gherkin  # noqa: E402

from tuku.cli import EXITO, RECHAZO  # noqa: E402
from tuku.rebuild import archivos_derivados  # noqa: E402

SLUG = "002-12-reconstruir-lo-derivado"


def test_002_12_borrar_lo_derivado_y_regenerarlo_devuelve_lo_mismo() -> None:
    corrida = gherkin.correr(SLUG, "borrar lo derivado y regenerarlo devuelve lo mismo")
    assert corrida.codigo == EXITO, corrida.stderr
    vault = corrida.ruta("mi-vault")

    # El diff entre referencia y mi-vault tiene que ser exactamente cero
    diff = corrida.de("diff -r referencia mi-vault")
    assert diff.codigo == 0, f"diff encontró diferencias:\n{diff.stdout}\n{diff.stderr}"

    # Ningún archivo canónico cambió: rebuild solo escribe lo derivado
    derivados_rel = {
        d.relative_to(vault).as_posix()
        for d in archivos_derivados(vault)
    }
    # Además de los derivados puros, las secciones propagadas de páginas de ámbito
    for ruta_modificada in corrida.delta:
        es_derivado = (
            ruta_modificada in derivados_rel
            or (ruta_modificada.startswith("ambitos/") and ruta_modificada.endswith(".md"))
        )
        assert es_derivado, f"rebuild modificó un archivo canónico: {ruta_modificada}"

    # El vault queda sano según scope lint
    lint = corrida.de("tuku scope lint")
    assert lint.codigo == EXITO, lint.stderr


def test_002_12_reconstruir_dos_veces_seguidas_no_mueve_nada() -> None:
    corrida = gherkin.correr(SLUG, "reconstruir dos veces seguidas no mueve nada")
    assert corrida.codigo == EXITO, corrida.stderr

    # Idempotencia: la segunda reconstrucción no mueve ningún archivo
    assert not corrida.delta, f"la segunda reconstrucción modificó archivos: {corrida.delta}"


def test_002_12_un_derivado_editado_a_mano_se_corrige_al_reconstruir() -> None:
    corrida = gherkin.correr(SLUG, "un derivado editado a mano se corrige al reconstruir")
    assert corrida.codigo == EXITO, corrida.stderr
    vault = corrida.ruta("mi-vault")

    contenido = (vault / "ambitos" / "PENDIENTES-AMBITOS.md").read_text(encoding="utf-8")
    assert "- una fila que nadie escribió" not in contenido, (
        "la edición manual no se limpió al reconstruir"
    )


def test_002_12_reconstruir_sobre_canonico_roto_informa_y_no_escribe() -> None:
    corrida = gherkin.correr(SLUG, "reconstruir sobre un canónico roto informa y no escribe")
    assert corrida.codigo == RECHAZO, corrida.stdout
    assert "error" in corrida.stderr.lower(), corrida.stderr
    assert "PENDIENTES.md" in corrida.stderr, corrida.stderr

    # No se borró el derivado existente
    vault = corrida.ruta("mi-vault")
    assert (vault / "ambitos" / "PENDIENTES-AMBITOS.md").is_file(), (
        "el rechazo borró derivados antes de abortar"
    )


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__, "-v"]))
