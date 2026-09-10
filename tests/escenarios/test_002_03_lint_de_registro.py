"""Tests del escenario 002-03-lint-de-registro.

Escenario: 002-03-lint-de-registro.md

Criterio de salida de la fase 1: `tuku entry lint` valida estricta la ontología
cerrada y permisiva la abierta. La misma zona de la línea, dos tratamientos.

Los comandos salen del `.md`, incluida la copia del estado que dejó `002-02`.
Todo pasa por el CLI, también el caso del día fuera del ciclo: antes se armaba
el texto en memoria y se llamaba a `lint()` directo, lo que dejaba sin probar
que el comando lo reporte igual.

Ejecutable directo: `python3 tests/escenarios/test_002_03_lint_de_registro.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import gherkin  # noqa: E402

from tuku.cli import EXITO, RECHAZO  # noqa: E402

SLUG = "002-03-lint-de-registro"
DESCONOCIDO = "- 12:05 - [[personal]] **cachureo**: ordené los cables del escritorio"
MAL_ESCRITA = "- 13:00 - [[personal]] **Cadencia**: comprar una maleta"


def test_002_03_cerrada_estricta_abierta_permisiva() -> None:
    corrida = gherkin.correr(SLUG, "un tipo abierto desconocido se reporta y se acepta")

    texto = corrida.ruta("mi-vault", "AHORA.md").read_text(encoding="utf-8")
    assert DESCONOCIDO in texto, "el tipo desconocido no quedó escrito"

    lint = corrida.de("entry lint")
    assert lint.codigo == EXITO, "el tipo abierto desconocido debía dar éxito"
    assert "cachureo" in lint.stdout, "la pregunta de vocabulario no salió en el reporte"


def test_002_03_la_marca_mal_escrita_no_abre_ningun_pendiente() -> None:
    corrida = gherkin.correr(SLUG, "la ontología cerrada se valida estricta")

    texto = corrida.ruta("mi-vault", "AHORA.md").read_text(encoding="utf-8")
    assert MAL_ESCRITA in texto, "la marca mal escrita no quedó escrita"
    assert corrida.de("entry add").codigo == EXITO, "la línea debía quedar escrita igual"

    lint = corrida.de("entry lint")
    assert lint.codigo == RECHAZO, "la ontología cerrada mal escrita debía dar rechazo"
    assert "**Cadencia**" in lint.stdout, "el error de ontología cerrada no salió"
    assert "**cadencia**" in lint.stdout, "el error no dice cómo corregirse"

    assert corrida.delta_de("mi-vault") == {
        "AHORA.md": "modificado",
        "ambitos/personal/personal.md": "modificado",
    }, "`**Cadencia**` no es `**cadencia**`: no se abre ninguna consecuencia"


def test_002_03_un_registro_fuera_del_ciclo_se_reporta() -> None:
    corrida = gherkin.correr(SLUG, "un registro fuera del rango del ciclo se reporta")

    assert "2026-08-25" in corrida.stdout, (
        f"no reportó el día fuera del ciclo: {corrida.stdout}"
    )
    ahora = corrida.ruta("mi-vault", "AHORA.md").read_text(encoding="utf-8")
    assert "## Miércoles 19 de agosto" not in ahora, "el lint inventó los días que faltan"


def test_002_03_el_lint_no_escribe_y_es_idempotente() -> None:
    corrida = gherkin.correr(SLUG, "el lint no escribe en el vault")

    assert corrida.delta_de("mi-vault") == {}, "el lint escribió en el vault"
    primero, segundo = corrida.resultados[-2], corrida.resultados[-1]
    assert primero.stdout == segundo.stdout, "dos corridas del lint dan reportes distintos"


if __name__ == "__main__":
    test_002_03_cerrada_estricta_abierta_permisiva()
    test_002_03_la_marca_mal_escrita_no_abre_ningun_pendiente()
    test_002_03_un_registro_fuera_del_ciclo_se_reporta()
    test_002_03_el_lint_no_escribe_y_es_idempotente()
    print(f"ok: 4 afirmaciones (queda en playground/{SLUG}/)")
