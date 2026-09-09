"""Tests del escenario 002-11-renombrar.

Escenario: 002-11-renombrar.md

Los tres `rename` del vault. Lo que se afirma no es que el archivo cambie de
nombre: es que **no quede nada apuntando al viejo**, que es la parte que un
renombrado a mano hace a medias sin que el vault avise.

Ejecutable directo: `python3 tests/escenarios/test_002_11_renombrar.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import gherkin  # noqa: E402

from tuku.cli import EXITO, RECHAZO  # noqa: E402

SLUG = "002-11-renombrar"
VIEJO = "depto-centro"
NUEVO = "depto-playa"


def _corrida_del_ambito() -> gherkin.Corrida:
    return gherkin.correr(SLUG, "renombrar un ámbito arrastra todo lo que lo nombraba")


def test_002_11_el_ambito_renombrado_lleva_el_nombre_nuevo_en_disco() -> None:
    corrida = _corrida_del_ambito()
    assert corrida.codigo == EXITO, corrida.stderr
    ambitos = corrida.ruta("mi-vault") / "ambitos"

    assert not (ambitos / VIEJO).exists(), "la carpeta vieja sigue ahí"
    assert (ambitos / NUEVO / f"{NUEVO}.md").is_file(), "falta la página con el nombre nuevo"
    for obligatorio in ("AGENTS.md", "CADENCIAS.md"):
        assert (ambitos / NUEVO / obligatorio).is_file(), f"falta {obligatorio}"


def test_002_11_no_queda_ningun_enlace_al_nombre_viejo() -> None:
    """La afirmación que da nombre al escenario, sobre el vault entero."""
    corrida = _corrida_del_ambito()
    vault = corrida.ruta("mi-vault")

    colgando = [
        f"{ruta.relative_to(vault)}:{i}"
        for ruta in sorted(vault.rglob("*.md"))
        for i, linea in enumerate(ruta.read_text(encoding="utf-8").splitlines(), 1)
        if f"[[{VIEJO}]]" in linea or f"^{VIEJO}" in linea
    ]
    assert not colgando, f"quedaron enlaces al nombre viejo: {colgando}"


def test_002_11_el_ancla_de_la_transclusion_apunta_a_un_bloque_que_existe() -> None:
    corrida = _corrida_del_ambito()
    vault = corrida.ruta("mi-vault")

    pagina = (vault / "ambitos" / NUEVO / f"{NUEVO}.md").read_text(encoding="utf-8")
    assert f"#^{NUEVO}" in pagina, "la página no transcluye el bloque del nombre nuevo"
    tabla = (vault / "ambitos" / "PENDIENTES-AMBITOS.md").read_text(encoding="utf-8")
    assert f"^{NUEVO}" in tabla, "el bloque que la página transcluye no existe"


def test_002_11_el_lint_de_ambitos_no_encuentra_nada_despues_de_renombrar() -> None:
    """La afirmación fuerte: es quien sabe ver un registro apuntando a lo que no está."""
    corrida = _corrida_del_ambito()
    assert corrida.codigo == EXITO, corrida.stderr
    assert "sin hallazgos" in corrida.stdout, corrida.stdout


def test_002_11_un_nombre_ocupado_se_rechaza_sin_tocar_nada() -> None:
    corrida = gherkin.correr(SLUG, "renombrar sobre un nombre ocupado no toca nada")
    assert corrida.codigo == RECHAZO, corrida.stdout
    assert "ya existe" in corrida.stderr, corrida.stderr

    ambitos = corrida.ruta("mi-vault") / "ambitos"
    assert (ambitos / VIEJO).is_dir() and (ambitos / "personal").is_dir(), (
        "un rechazo alcanzó a mover algo"
    )


def test_002_11_corregir_el_registro_corrige_tambien_su_fila() -> None:
    """Los dos textos tienen que decir lo mismo, o el pendiente no se puede cerrar."""
    corrida = gherkin.correr(SLUG, "corregir un registro corrige también su pendiente")
    assert corrida.codigo == EXITO, corrida.stderr
    vault = corrida.ruta("mi-vault")

    ahora = (vault / "AHORA.md").read_text(encoding="utf-8")
    linea = next(x for x in ahora.splitlines() if x.startswith("- 09:00 - "))
    assert "terapia" in linea, linea
    # El ámbito y la hora los fija `tuku entry add`; corregir el cuerpo no los toca.
    antes = corrida.antes["mi-vault/AHORA.md"].decode("utf-8")
    previa = next(x for x in antes.splitlines() if x.startswith("- 09:00 - "))
    assert linea.split("**pendiente**")[0] == previa.split("**pendiente**")[0], (
        f"cambió algo más que el cuerpo:\n{previa}\n{linea}"
    )

    pendientes = (vault / "PENDIENTES.md").read_text(encoding="utf-8")
    cuerpo = linea.split("**pendiente**:", 1)[1].strip()
    assert cuerpo in pendientes, f"la fila no dice lo mismo que el registro: {cuerpo!r}"


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__, "-v"]))
