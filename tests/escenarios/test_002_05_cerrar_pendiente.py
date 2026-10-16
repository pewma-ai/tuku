"""Tests del escenario 002-05-cerrar-pendiente.

`tuku todo close` borra la fila y deja su huella en `AHORA.md`; un cierre sin
pareja se reporta sin inventar nada. `tuku entry add` con `(Hecho)` hace lo
mismo.

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
from tuku.cli import EXITO, RECHAZO  # noqa: E402

SLUG = "002-05-cerrar-pendiente"
PERSONAL = "[personal](ambitos/personal/personal.md)"
CUERPO = "avisar de los GGCC a la administradora"
APERTURA = f"- 14:20 - {PERSONAL} **pendiente**: {CUERPO}"
CIERRE = f"- 19:05 - {PERSONAL} (Hecho): ~~{CUERPO}~~"
HUERFANO = "comprar una maleta"
CIERRE_HUERFANO = f"- 19:10 - {PERSONAL} (Hecho): ~~{HUERFANO}~~"

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
    ahora = (vault / "AHORA.md").read_text(encoding="utf-8")
    assert APERTURA not in ahora, "abierto y cerrado el mismo día: sobra la apertura"
    assert CIERRE in ahora, "no se estampó la huella de cierre"
    pagina = (vault / "ambitos" / "personal" / "personal.md").read_text(encoding="utf-8")
    assert f"**pendiente**: {CUERPO}" not in pagina, "la página del ámbito conserva la apertura"
    assert f"(Hecho): ~~{CUERPO}~~" in pagina

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


def test_002_05_abierto_y_cerrado_a_mano_el_mismo_dia_fix_deja_el_cierre() -> None:
    corrida = gherkin.correr(SLUG, "abierto y cerrado a mano el mismo día")
    vault = corrida.ruta("mi-vault")

    antes, despues = [r for r in corrida.resultados if "tuku todo lint" in r.comando]
    assert antes.codigo == RECHAZO, antes.stdout
    assert "tuku fix todo" in antes.stdout, antes.stdout
    assert corrida.de("tuku fix todo").codigo == EXITO
    assert despues.codigo == EXITO, despues.stdout

    ahora = (vault / "AHORA.md").read_text(encoding="utf-8")
    pagina = (vault / "ambitos" / "personal" / "personal.md").read_text(encoding="utf-8")
    for texto in (ahora, pagina):
        assert "**pendiente**: renovar el carnet" not in texto
        assert "(Hecho): ~~renovar el carnet~~" in texto


if __name__ == "__main__":
    test_002_05_cerrar_borra_el_item_y_deja_la_tabla_vacia()
    test_002_05_un_cierre_sin_pareja_no_inventa_nada()
    test_002_05_cerrar_dos_veces_no_vuelve_a_mover()
    test_002_05_abierto_y_cerrado_a_mano_el_mismo_dia_fix_deja_el_cierre()
    print(f"ok: 3 afirmaciones (queda en playground/{SLUG}/)")
