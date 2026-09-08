"""Test del escenario 002-08-crear-ambito.

Escenario: 002-08-crear-ambito.md

Octavo paso de la cadena, punto 4 del epic en su versión mínima. Crear el
ámbito `depto-centro` deja el árbol correcto (los dos obligatorios más la
página propia, que es lo que lo hace ámbito y no categoría) y `link backfill`
convierte la mención suelta del martes 11 en enlace.

`scope lint` cubre la única regla de los tres roles verificable sin un árbol
profundo: un registro no puede apuntar a una categoría.

Ejecutable directo: python3 tests/escenarios/test_002_08_crear_ambito.py
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

from cadena import correr_cli, delta, instantanea, preparar_paso  # noqa: E402

from tuku import scope  # noqa: E402
from tuku.cli import EXITO, RECHAZO  # noqa: E402

SLUG = "002-08-crear-ambito"
PREVIO = "002-06-escribir-en-un-dia-fecha"
DESDE = date(2026, 8, 11)
HOY = "## Martes 11 de agosto"

AMBITO = "depto-centro"
MENCION = "del depto centro"
ENLAZADO = f"del [[{AMBITO}]]"


def _crear(vault: Path) -> None:
    """Crea el ámbito y enlaza hacia atrás, que es lo que hace el punto 4."""
    codigo, _, err = correr_cli(["scope", "create", AMBITO, "--vault", str(vault)])
    assert codigo == EXITO, err


def test_002_08_crear_ambito_deja_el_arbol_correcto_y_enlaza_hacia_atras() -> None:
    vault = preparar_paso(SLUG, previo=PREVIO, desde=DESDE)
    antes = instantanea(vault)
    personal_antes = instantanea(vault / "ambitos" / "personal")
    _crear(vault)

    directorio = vault / "ambitos" / AMBITO
    assert directorio.is_dir()
    for archivo in (*scope.OBLIGATORIOS, f"{AMBITO}.md"):
        assert (directorio / archivo).is_file(), f"falta {archivo}"
    assert not (directorio / "CAPACIDAD.md").exists(), "CAPACIDAD.md es opcional"
    assert "![[../PENDIENTES-AMBITOS.md#^depto-centro]]" in (
        directorio / f"{AMBITO}.md"
    ).read_text(encoding="utf-8"), "falta transclusión de pendientes en página de ámbito"

    assert instantanea(vault / "ambitos" / "personal") == personal_antes, "cambió personal/"

    ahora = (vault / "AHORA.md").read_text(encoding="utf-8")
    assert ENLAZADO in ahora, "la mención suelta no quedó enlazada"
    assert MENCION not in ahora.replace(ENLAZADO, ""), "quedó una mención sin enlazar"

    tocados = set(delta(antes, instantanea(vault)))
    esperados = {"AHORA.md", *(f"ambitos/{AMBITO}/{a}" for a in scope.OBLIGATORIOS)}
    esperados.add(f"ambitos/{AMBITO}/{AMBITO}.md")
    esperados.add("ambitos/PENDIENTES-AMBITOS.md")
    assert tocados == esperados, tocados

    p_ambitos = vault / "ambitos" / "PENDIENTES-AMBITOS.md"
    pendientes_ambitos = p_ambitos.read_text(encoding="utf-8")
    assert f"> [!todo] Pendientes en **Depto Centro** ^{AMBITO}" in pendientes_ambitos
    assert "> SIN PENDIENTES" in pendientes_ambitos
    assert not scope.lint_transclusiones(vault)
    assert not scope.lint_callouts(vault)

    contenido_depto = (directorio / f"{AMBITO}.md").read_text(encoding="utf-8")
    assert "## Esta semana" in contenido_depto
    assert "### Martes 11 de agosto" in contenido_depto
    linea_esperada = (
        "- le mandé la boleta de gastos comunes del depto-centro a la "
        "administradora por WhatsApp"
    )
    assert linea_esperada in contenido_depto
    assert "- 18:40 - " not in contenido_depto
    assert "## Actividad reciente" in contenido_depto
    assert "### Agosto 2026" in contenido_depto



def test_002_08_el_resto_de_la_linea_no_se_reescribe() -> None:
    vault = preparar_paso(SLUG, previo=PREVIO, desde=DESDE)
    antes = (vault / "AHORA.md").read_text(encoding="utf-8").splitlines()
    _crear(vault)
    despues = (vault / "AHORA.md").read_text(encoding="utf-8").splitlines()

    cambiadas = [(a, d) for a, d in zip(antes, despues, strict=True) if a != d]
    assert len(cambiadas) == 1, cambiadas
    a, d = cambiadas[0]
    assert d == a.replace(MENCION, ENLAZADO), "se reescribió algo más de la línea"


def test_002_08_un_registro_no_puede_apuntar_a_una_categoria() -> None:
    vault = preparar_paso(SLUG, previo=PREVIO, desde=DESDE)
    _crear(vault)

    # Una categoría es un directorio con los obligatorios y sin página propia.
    categoria = vault / "ambitos" / AMBITO / "gastos"
    categoria.mkdir()
    for archivo in scope.OBLIGATORIOS:
        (categoria / archivo).write_text("", encoding="utf-8")

    registro = "- 20:00 - [[gastos]] **progreso**: revisé el detalle del mes"
    codigo, _, err = correr_cli(
        ["entry", "add", "--vault", str(vault), "--day", HOY, registro]
    )
    assert codigo == EXITO, err

    texto = (vault / "AHORA.md").read_text(encoding="utf-8")
    codigo, salida, err = correr_cli(["scope", "lint", "--vault", str(vault)])
    assert codigo == RECHAZO, salida
    assert "gastos" in salida and "categoría" in salida, salida
    assert registro in texto, "el registro no quedó escrito: se reporta, nunca se rechaza"


def test_002_08_crear_dos_veces_no_hace_nada() -> None:
    vault = preparar_paso(SLUG, previo=PREVIO, desde=DESDE)
    _crear(vault)
    despues = instantanea(vault)

    _crear(vault)

    assert delta(despues, instantanea(vault)) == {}, "el segundo pase escribió"
    ahora = (vault / "AHORA.md").read_text(encoding="utf-8")
    assert f"[[[[{AMBITO}]]]]" not in ahora, "se enlazó dos veces"


if __name__ == "__main__":
    test_002_08_crear_ambito_deja_el_arbol_correcto_y_enlaza_hacia_atras()
    test_002_08_el_resto_de_la_linea_no_se_reescribe()
    test_002_08_un_registro_no_puede_apuntar_a_una_categoria()
    test_002_08_crear_dos_veces_no_hace_nada()
    print(f"ok: 4 afirmaciones (queda en playground/{SLUG}/)")
