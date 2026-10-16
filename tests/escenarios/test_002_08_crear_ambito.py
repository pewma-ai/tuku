"""Tests del escenario 002-08-crear-ambito.

`tuku scope create` deja el árbol del ámbito, su constancia en la bitácora y las
menciones previas enlazadas; `scope lint` reporta un registro que apunta a una
categoría.

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
ENLAZADO = f"del [{AMBITO}](ambitos/{AMBITO}/{AMBITO}.md)"
CONSTANCIA = f"- 18:45 - [{AMBITO}](ambitos/{AMBITO}/{AMBITO}.md) **nota**: abrí el ámbito"
REGISTRO_A_CATEGORIA = (
    "- 20:00 - [gastos](ambitos/depto-centro/gastos) **progreso**: revisé el detalle del mes"
)


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
    martes = ahora.split("## Martes 11 de agosto", 1)[1].split("\n## ", 1)[0]
    assert CONSTANCIA in martes, "crear el ámbito no dejó su constancia en el martes 11"

    # La constancia es la única línea nueva, y en la de la mención solo cambia la mención.
    antes = corrida.antes["mi-vault/AHORA.md"].decode("utf-8").splitlines()
    despues = ahora.splitlines()
    despues.remove(CONSTANCIA)
    cambiadas = [(a, d) for a, d in zip(antes, despues, strict=True) if a != d]
    assert len(cambiadas) == 1, cambiadas
    a, d = cambiadas[0]
    assert d == a.replace(MENCION, ENLAZADO), "se reescribió algo más de la línea"

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


def test_002_08_un_registro_no_puede_apuntar_a_una_categoria() -> None:
    corrida = gherkin.correr(SLUG, "un registro no puede apuntar a una categoría")

    lint = corrida.de("scope lint")
    assert lint.codigo == RECHAZO, lint.stdout
    assert "gastos" in lint.stdout and "categoría" in lint.stdout, lint.stdout

    ahora = corrida.ruta("mi-vault", "AHORA.md").read_text(encoding="utf-8")
    assert REGISTRO_A_CATEGORIA in ahora, (
        "el registro no quedó escrito: se reporta, nunca se rechaza"
    )


def test_002_08_crear_dos_veces_no_hace_nada() -> None:
    corrida = gherkin.correr(SLUG, "crear dos veces el mismo ámbito no hace nada")
    assert corrida.codigo == EXITO, corrida.stderr

    assert corrida.delta_de("mi-vault") == {}, "el segundo pase escribió"
    ahora = corrida.ruta("mi-vault", "AHORA.md").read_text(encoding="utf-8")
    assert ahora.count(ENLAZADO) == 1, "se enlazó dos veces"
    assert ahora.count(CONSTANCIA) == 1, "la constancia se escribió dos veces"


def test_002_08_el_nombre_con_espacios_se_escribe_con_guion() -> None:
    """El autor dicta "depto centro"; el ámbito es uno solo y se llama `depto-centro`."""
    corrida = gherkin.correr(SLUG, "el nombre dictado con espacios se escribe con guion")
    assert corrida.codigo == EXITO, corrida.stderr

    ambitos = corrida.ruta("vault-nombres", "ambitos")
    assert (ambitos / AMBITO / f"{AMBITO}.md").is_file(), "no quedó como depto-centro"
    assert not (ambitos / "depto centro").exists(), "quedó con el espacio"


def test_002_08_un_ambito_que_no_existe_se_rechaza() -> None:
    corrida = gherkin.correr(SLUG, "un registro a un ámbito que no existe se rechaza")

    assert corrida.codigo == RECHAZO, corrida.stdout
    assert f"tuku scope create {AMBITO}" in corrida.stderr, corrida.stderr
    assert corrida.delta_de("vault-sin-ambito") == {}, "escribió pese al rechazo"


def test_002_08_un_ambito_rechazado_no_queda_a_medias() -> None:
    corrida = gherkin.correr(SLUG, "un ámbito rechazado no queda a medias")

    assert corrida.codigo == RECHAZO, corrida.stdout
    assert "tabla" in corrida.stderr, corrida.stderr
    assert not corrida.ruta("vault-roto", "ambitos", AMBITO).exists(), (
        "el rechazo dejó la carpeta creada"
    )


def test_002_08_un_dia_fuera_del_ciclo_no_crea_el_ambito() -> None:
    """La constancia se prueba antes de crear la carpeta: un rechazo no deja nada."""
    corrida = gherkin.correr(SLUG, "un día fuera del ciclo se rechaza sin crear nada")

    assert corrida.codigo == RECHAZO, corrida.stdout
    assert "fuera del ciclo" in corrida.stderr, corrida.stderr
    assert not corrida.ruta("vault-fuera", "ambitos", AMBITO).exists(), (
        "el rechazo dejó la carpeta creada"
    )


if __name__ == "__main__":
    test_002_08_crear_ambito_deja_el_arbol_correcto_y_enlaza_hacia_atras()
    test_002_08_un_registro_no_puede_apuntar_a_una_categoria()
    test_002_08_crear_dos_veces_no_hace_nada()
    test_002_08_el_nombre_con_espacios_se_escribe_con_guion()
    test_002_08_un_ambito_que_no_existe_se_rechaza()
    test_002_08_un_ambito_rechazado_no_queda_a_medias()
    test_002_08_un_dia_fuera_del_ciclo_no_crea_el_ambito()
    print(f"ok: 7 afirmaciones (queda en playground/{SLUG}/)")
