"""Tests del escenario 002-08-crear-ambito.

Escenario: 002-08-crear-ambito.md

Punto 4 del epic en su versión mínima: crear el ámbito `depto-centro` deja el
árbol correcto (los dos obligatorios más la página propia, que es lo que lo hace
ámbito y no categoría) y el enlazado retroactivo convierte la mención suelta del
martes 11 en enlace.

`scope lint` cubre la única regla de los tres roles verificable sin un árbol
profundo: un registro no puede apuntar a una categoría.

Los comandos salen del `.md`, incluida la copia del estado que dejó `002-06`.

Ejecutable directo: `python3 tests/escenarios/test_002_08_crear_ambito.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import gherkin  # noqa: E402

from tuku import scope  # noqa: E402
from tuku.cli import EXITO, RECHAZO  # noqa: E402

SLUG = "002-08-crear-ambito"
AMBITO = "depto-centro"
MENCION = "del depto centro"
ENLAZADO = f"del [[{AMBITO}]]"
REGISTRO_A_CATEGORIA = "- 20:00 - [[gastos]] **progreso**: revisé el detalle del mes"


def test_002_08_crear_ambito_deja_el_arbol_correcto_y_enlaza_hacia_atras() -> None:
    corrida = gherkin.correr(SLUG, "crear un ámbito deja el árbol correcto")
    assert corrida.codigo == EXITO, corrida.stderr
    vault = corrida.ruta("mi-vault")

    directorio = vault / "ambitos" / AMBITO
    assert directorio.is_dir()
    for archivo in (*scope.OBLIGATORIOS, f"{AMBITO}.md"):
        assert (directorio / archivo).is_file(), f"falta {archivo}"
    assert not (directorio / "CAPACIDAD.md").exists(), "CAPACIDAD.md es opcional"

    pagina = (directorio / f"{AMBITO}.md").read_text(encoding="utf-8")
    assert "![[../PENDIENTES-AMBITOS.md#^depto-centro]]" in pagina, (
        "falta transclusión de pendientes en página de ámbito"
    )

    # El barrido retroactivo llega a AHORA.md y no más: el delta dice qué se tocó.
    esperados = {
        "AHORA.md",
        "ambitos/PENDIENTES-AMBITOS.md",
        f"ambitos/{AMBITO}/{AMBITO}.md",
        *(f"ambitos/{AMBITO}/{a}" for a in scope.OBLIGATORIOS),
    }
    tocados = set(corrida.delta_de("mi-vault"))
    assert tocados == esperados, tocados
    assert not any(r.startswith("ambitos/personal/") for r in tocados), "cambió personal/"

    ahora = (vault / "AHORA.md").read_text(encoding="utf-8")
    assert ENLAZADO in ahora, "la mención suelta no quedó enlazada"
    assert MENCION not in ahora.replace(ENLAZADO, ""), "quedó una mención sin enlazar"

    pendientes_ambitos = (vault / "ambitos" / "PENDIENTES-AMBITOS.md").read_text(
        encoding="utf-8"
    )
    assert f"> [!todo] Pendientes en **Depto Centro** ^{AMBITO}" in pendientes_ambitos
    assert "> SIN PENDIENTES" in pendientes_ambitos
    assert not scope.lint_transclusiones(vault)
    assert not scope.lint_callouts(vault)

    assert "## Esta semana" in pagina
    assert "### Martes 11 de agosto" in pagina
    assert (
        "- le mandé la boleta de gastos comunes del depto-centro a la "
        "administradora por WhatsApp" in pagina
    )
    assert "- 18:40 - " not in pagina
    assert "## Actividad reciente" in pagina
    assert "### Agosto 2026" in pagina

    cadencias = (directorio / "CADENCIAS.md").read_text(encoding="utf-8")
    sembrado = (vault / "ambitos" / "personal" / "CADENCIAS.md").read_text(encoding="utf-8")
    assert cadencias == sembrado.replace("personal", AMBITO), (
        "el ámbito creado por comando no es equivalente al que siembra `tuku init`"
    )


def test_002_08_el_resto_de_la_linea_no_se_reescribe() -> None:
    corrida = gherkin.correr(SLUG, "las menciones sueltas del ciclo en curso pasan a enlace")

    antes = corrida.antes["mi-vault/AHORA.md"].decode("utf-8").splitlines()
    despues = corrida.despues["mi-vault/AHORA.md"].decode("utf-8").splitlines()
    cambiadas = [(a, d) for a, d in zip(antes, despues, strict=True) if a != d]

    assert len(cambiadas) == 1, cambiadas
    a, d = cambiadas[0]
    assert d == a.replace(MENCION, ENLAZADO), "se reescribió algo más de la línea"


def test_002_08_un_registro_no_puede_apuntar_a_una_categoria() -> None:
    corrida = gherkin.correr(SLUG, "un registro no puede apuntar a una categoría")

    lint = corrida.de("scope lint")
    assert lint.codigo == RECHAZO, lint.stdout
    assert "gastos" in lint.stdout and "categoría" in lint.stdout, lint.stdout

    ahora = corrida.ruta("mi-vault", "AHORA.md").read_text(encoding="utf-8")
    assert REGISTRO_A_CATEGORIA in ahora, (
        "el registro no quedó escrito: se reporta, nunca se rechaza"
    )


def test_002_08_el_ambito_recien_creado_deja_el_vault_sano() -> None:
    """El doctor sobre lo que TUKU acaba de escribir.

    Un `CADENCIAS.md` sin `type` hacía que el doctor reportara un archivo que el
    propio comando había escrito, y ninguna afirmación del escenario lo notaba.
    Va sobre un vault recién sembrado porque el de la cadena arrastra, a
    propósito desde el `002-03`, un registro que el doctor reporta con razón.
    """
    corrida = gherkin.correr(SLUG, "el ámbito recién creado deja el vault sano")

    doctor = corrida.de("tuku doctor")
    assert doctor.codigo == EXITO, doctor.stdout
    assert "el vault está sano" in doctor.stdout, doctor.stdout


def test_002_08_crear_dos_veces_no_hace_nada() -> None:
    corrida = gherkin.correr(SLUG, "crear dos veces el mismo ámbito no hace nada")
    assert corrida.codigo == EXITO, corrida.stderr

    assert corrida.delta_de("mi-vault") == {}, "el segundo pase escribió"
    ahora = corrida.ruta("mi-vault", "AHORA.md").read_text(encoding="utf-8")
    assert f"[[[[{AMBITO}]]]]" not in ahora, "se enlazó dos veces"


if __name__ == "__main__":
    test_002_08_crear_ambito_deja_el_arbol_correcto_y_enlaza_hacia_atras()
    test_002_08_el_resto_de_la_linea_no_se_reescribe()
    test_002_08_un_registro_no_puede_apuntar_a_una_categoria()
    test_002_08_el_ambito_recien_creado_deja_el_vault_sano()
    test_002_08_crear_dos_veces_no_hace_nada()
    print(f"ok: 5 afirmaciones (queda en playground/{SLUG}/)")
