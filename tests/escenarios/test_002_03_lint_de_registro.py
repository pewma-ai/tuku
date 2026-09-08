"""Test del escenario 002-03-lint-de-registro.

Escenario: 002-03-lint-de-registro.md

Tercer paso de la cadena. Hereda el vault de 002-02 y ejerce `tuku entry lint`:
la ontología cerrada se valida estricta (`**Pendiente**` es error y no abre
nada), la abierta permisiva (un tipo desconocido es pregunta, no error), un
registro fuera del ciclo se reporta sin inventar el día, y el lint no escribe.

El caso fuera de rango se arma sobre el texto y no sobre el vault: `lint()` es
una función pura, y el arnés no escribe en el vault fuera del fixture inicial.

Ejecutable directo: python3 tests/escenarios/test_002_03_lint_de_registro.py
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

from cadena import delta, instantanea, preparar_paso  # noqa: E402

from tuku import vocab  # noqa: E402
from tuku.entry import add  # noqa: E402
from tuku.lint import ERROR, PREGUNTA, formatear, lint  # noqa: E402

SLUG = "002-03-lint-de-registro"
PREVIO = "002-02-registro-en-su-dia"
DESDE = date(2026, 8, 11)
HOY = "## Martes 11 de agosto"

DESCONOCIDO = "- 12:05 - [[personal]] **cachureo**: ordené los cables del escritorio"
MAL_ESCRITA = "- 13:00 - [[personal]] **Pendiente**: comprar una maleta"
FUERA_DE_RANGO = "- 08:00 - [[personal]] **progreso**: revisé la bodega"


def _vault() -> Path:
    return preparar_paso(SLUG, previo=PREVIO, desde=DESDE)


def _abiertos(vault: Path) -> list[str]:
    libro = (vault / "LIBRO-DE-ESTILO.md").read_text(encoding="utf-8")
    return [t for terminos in vocab.leer(libro).values() for t in terminos]


def test_002_03_cerrada_estricta_abierta_permisiva() -> None:
    vault = _vault()
    ruta = vault / "AHORA.md"
    ruta.write_text(
        add(ruta.read_text(encoding="utf-8"), [DESCONOCIDO, MAL_ESCRITA], dia=HOY),
        encoding="utf-8",
    )
    texto = ruta.read_text(encoding="utf-8")
    hallazgos = lint(texto, abiertos=_abiertos(vault))

    assert DESCONOCIDO in texto, "el tipo desconocido no quedó escrito"
    assert MAL_ESCRITA in texto, "la marca mal escrita no quedó escrita: el lint no rechaza"

    preguntas = [h for h in hallazgos if h.grado == PREGUNTA]
    assert len(preguntas) == 1, [str(h) for h in hallazgos]
    assert "cachureo" in preguntas[0].defecto

    errores = [h for h in hallazgos if h.grado == ERROR]
    assert len(errores) == 1, [str(h) for h in errores]
    assert "**Pendiente**" in errores[0].defecto
    assert "**pendiente**" in errores[0].correccion, "el error no dice cómo corregirse"


def test_002_03_la_marca_mal_escrita_no_abre_ningun_pendiente() -> None:
    vault = _vault()
    antes = instantanea(vault)
    ruta = vault / "AHORA.md"
    ruta.write_text(
        add(ruta.read_text(encoding="utf-8"), [MAL_ESCRITA], dia=HOY), encoding="utf-8"
    )
    lint(ruta.read_text(encoding="utf-8"), abiertos=_abiertos(vault))

    assert delta(antes, instantanea(vault)) == {"AHORA.md": "modificado"}


def test_002_03_un_registro_fuera_del_ciclo_se_reporta() -> None:
    vault = _vault()
    texto = (vault / "AHORA.md").read_text(encoding="utf-8")
    fuera = f"{texto}\n## Martes 25 de agosto\n\n{FUERA_DE_RANGO}\n"

    hallazgos = lint(fuera, abiertos=_abiertos(vault))
    fuera_de_rango = [h for h in hallazgos if "fuera del ciclo" in h.defecto]

    assert len(fuera_de_rango) == 1, [str(h) for h in hallazgos]
    assert "2026-08-25" in fuera_de_rango[0].defecto
    assert "## Miércoles 19 de agosto" not in fuera, "el lint no inventa los días que faltan"


def test_002_03_el_lint_no_escribe_y_es_idempotente() -> None:
    vault = _vault()
    abiertos = _abiertos(vault)
    antes = instantanea(vault)

    texto = (vault / "AHORA.md").read_text(encoding="utf-8")
    primero = formatear(lint(texto, abiertos=abiertos))
    segundo = formatear(lint(texto, abiertos=abiertos))

    assert delta(antes, instantanea(vault)) == {}, "el lint escribió en el vault"
    assert primero == segundo, "dos corridas del lint dan reportes distintos"


if __name__ == "__main__":
    test_002_03_cerrada_estricta_abierta_permisiva()
    test_002_03_la_marca_mal_escrita_no_abre_ningun_pendiente()
    test_002_03_un_registro_fuera_del_ciclo_se_reporta()
    test_002_03_el_lint_no_escribe_y_es_idempotente()
    print(f"ok: 4 afirmaciones (queda en playground/{SLUG}/)")
