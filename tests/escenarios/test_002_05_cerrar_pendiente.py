"""Tests del escenario 002-05-cerrar-pendiente.

Escenario: 002-05-cerrar-pendiente.md

Punto 2 del epic, segunda mitad: un registro `~~(Hecho)~~` cierra el pendiente,
y el cierre sin pareja se reporta sin inventar nada. Ese es el caso negativo más
importante del epic: con `PENDIENTES.md` como fuente de verdad, un cierre
inventado deja el archivo mintiendo.

Los comandos salen del `.md`, incluida la copia del estado que dejó `002-04`.

Ejecutable directo: `python3 tests/escenarios/test_002_05_cerrar_pendiente.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import gherkin  # noqa: E402

from tuku import todo  # noqa: E402
from tuku.cli import EXITO  # noqa: E402

SLUG = "002-05-cerrar-pendiente"
CUERPO = "avisar de los GGCC a la administradora"
APERTURA = f"- 14:20 - [[personal]] **pendiente**: {CUERPO}"
HUERFANO = "comprar una maleta"
CIERRE_HUERFANO = f"- 19:10 - [[personal]] ~~(Hecho)~~: {HUERFANO}"

SIN_PAREJA = "no había ningún pendiente abierto"


def test_002_05_cerrar_borra_el_item_y_deja_la_tabla_vacia() -> None:
    corrida = gherkin.correr(SLUG, "el cierre repite el texto y borra el ítem")
    assert corrida.codigo == EXITO, corrida.stderr
    assert "pendiente cerrado" in corrida.stdout, corrida.stdout
    vault = corrida.ruta("mi-vault")

    pendientes = (vault / "PENDIENTES.md").read_text(encoding="utf-8")
    assert todo.cuerpos(pendientes) == [], "el ítem no se borró"
    assert len(todo.filas(pendientes)) == 0, "la tabla no quedó vacía"
    assert todo.CABECERA in pendientes, "se perdió la cabecera de la tabla"
    assert APERTURA in (vault / "AHORA.md").read_text(encoding="utf-8"), "se tocó la apertura"

    assert corrida.delta_de("mi-vault") == {
        "AHORA.md": "modificado",
        "PENDIENTES.md": "modificado",
        "ambitos/PENDIENTES-AMBITOS.md": "modificado",
        "ambitos/personal/personal.md": "modificado",
    }


def test_002_05_un_cierre_sin_pareja_no_inventa_nada() -> None:
    corrida = gherkin.correr(SLUG, "un cierre sin pendiente abierto se reporta")
    assert corrida.codigo == EXITO, "un error del autor se reporta, nunca se rechaza"
    assert SIN_PAREJA in corrida.stdout, corrida.stdout
    vault = corrida.ruta("mi-vault")

    pendientes = (vault / "PENDIENTES.md").read_text(encoding="utf-8")
    assert HUERFANO not in pendientes, "se inventó el pendiente que faltaba"
    assert CIERRE_HUERFANO in (vault / "AHORA.md").read_text(encoding="utf-8"), (
        "la línea no quedó escrita: un error del autor se reporta, nunca se rechaza"
    )

    # `PENDIENTES.md` no aparece en el delta: el cierre huérfano no lo tocó.
    assert corrida.delta_de("mi-vault") == {
        "AHORA.md": "modificado",
        "ambitos/personal/personal.md": "modificado",
    }


def test_002_05_cerrar_dos_veces_no_vuelve_a_mover() -> None:
    corrida = gherkin.correr(SLUG, "cerrar dos veces no vuelve a mover")
    assert corrida.codigo == EXITO, corrida.stderr

    # El segundo pase de un cierre correcto es, por construcción, un cierre sin
    # pareja: eso hace idempotente al comando sin que lleve estado.
    assert SIN_PAREJA in corrida.stdout, corrida.stdout
    assert corrida.delta_de("mi-vault") == {}, "el segundo pase escribió"


if __name__ == "__main__":
    test_002_05_cerrar_borra_el_item_y_deja_la_tabla_vacia()
    test_002_05_un_cierre_sin_pareja_no_inventa_nada()
    test_002_05_cerrar_dos_veces_no_vuelve_a_mover()
    print(f"ok: 3 afirmaciones (queda en playground/{SLUG}/)")


def test_002_05_cerrar_deja_la_tabla_al_dia_con_la_bitacora() -> None:
    """El gemelo del cierre: un `~~(Hecho)~~` cuyo cuerpo sigue en la tabla es un
    cierre que se escribió y nunca se aplicó, y por separado los dos archivos se
    ven bien. Lo revisa `tuku doctor` desde el 2026-09-09.
    """
    vault = gherkin.correr(SLUG, "el cierre repite el texto").ruta("mi-vault")
    faltan = todo.sin_consecuencia(
        (vault / "AHORA.md").read_text(encoding="utf-8"),
        (vault / "PENDIENTES.md").read_text(encoding="utf-8"),
    )
    assert faltan == [], f"quedaron marcas sin su consecuencia: {faltan}"


def test_002_05_comando_directo_close_elimina_y_estampa_huella() -> None:
    corrida = gherkin.correr(SLUG, "comando directo tuku todo close elimina el ítem")
    assert corrida.codigo == EXITO, corrida.stderr
    vault = corrida.ruta("mi-vault")

    pendientes = (vault / "PENDIENTES.md").read_text(encoding="utf-8")
    assert "avisar de los GGCC a la administradora" not in pendientes
    assert todo.cuerpos(pendientes) == []

    ahora = (vault / "AHORA.md").read_text(encoding="utf-8")
    assert "- 19:30 - [[personal]] ~~(Hecho)~~: avisar de los GGCC a la administradora" in ahora

    faltan = todo.sin_consecuencia(ahora, pendientes)
    assert faltan == [], f"inconsistencia entre AHORA y PENDIENTES: {faltan}"
