"""Tests del escenario 003-07-lo-que-no-hace-sin-preguntar.

Escenario: 003-07-lo-que-no-hace-sin-preguntar.md

La tabla de Límites del `AGENTS.md` del vault, que es la única parte del
documento entregable del epic que quedaba sin verificar.

El `003-05` prueba que el agente no escribe lo que no es un hecho. Este prueba
que no actúa cuando no está seguro, aunque lo que el autor pidió sí tenga
comando en la tabla de despacho. Cerrar el pendiente equivocado deja el vault
perfectamente bien formado y diciendo algo falso.

Gemelo determinista: `002-05` (el cierre sin pareja se reporta y no se inventa).

Ejecutable directo: `python3 tests/escenarios/test_003_07_lo_que_no_hace_sin_preguntar.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import agente  # noqa: E402
import gherkin  # noqa: E402

from tuku import todo  # noqa: E402

SLUG = "003-07-lo-que-no-hace-sin-preguntar"
TITULO = "ante dos lecturas posibles"
DIA = "## Miércoles 12 de agosto"

#: La hora del único hecho que sí se registra. El dictado la dice, así que el
#: agente no la adivina; lo que sí deriva es el día, y eso es lo que se afirma.
HORA = "10:15"

#: Los dos pendientes que compiten. Empiezan igual y ninguno es el más probable:
#: con uno solo, "ya pagué" no sería ambiguo y el escenario mediría otra cosa.
ABIERTOS = {
    "pagar la sesión con el psicólogo",
    "pagar los gastos comunes del depto centro",
}

#: Lo que toca un registro sin consecuencia, del gemelo `002-02`. `PENDIENTES.md`
#: no está, y esa ausencia es la afirmación entera del escenario.
DELTA_SIN_CONSECUENCIA = {
    "AHORA.md": "modificado",
    "ambitos/depto-centro/depto-centro.md": "modificado",
}

sin_arnes = pytest.mark.skipif(
    not agente.disponible(), reason=agente.motivo_no_disponible() or ""
)


def _dia(corrida: gherkin.Corrida) -> str:
    ahora = corrida.ruta("mi-vault", "AHORA.md").read_text(encoding="utf-8")
    return ahora.split(DIA, 1)[1].split("\n## ", 1)[0]


def _pendientes(corrida: gherkin.Corrida) -> str:
    return corrida.ruta("mi-vault", "PENDIENTES.md").read_text(encoding="utf-8")


@pytest.mark.agentic
@sin_arnes
def test_003_07_solo_el_hecho_claro_se_traduce_en_un_comando() -> None:
    turno = gherkin.correr(SLUG, TITULO).turno
    assert turno.traduccion == ["entry add"], (
        f"tres frases y un solo hecho claro, pero ejecutó: {turno.comandos}"
    )


@pytest.mark.agentic
@sin_arnes
def test_003_07_el_registro_cae_donde_va_el_vault() -> None:
    """El día no se dicta nunca en este epic: se deriva, y por eso se afirma.

    El ciclo abierto va del 11 al 17 de agosto y hoy cae fuera, así que el día
    lo decide `reglas/bitacora.tuku.md`: el último del ciclo que ya tiene
    registros, que acá es el miércoles por el pendiente que siembra el estado
    inicial. Sin esta aserción el registro se iba al martes y los seis tests
    pasaban igual, porque el resto solo mira que no haya pasado nada.

    Peor que pasar: `_dia` lee la sección del miércoles, así que un registro
    puesto en el martes vaciaba de contenido la aserción del cierre.
    """
    assert HORA in _dia(gherkin.correr(SLUG, TITULO)), (
        f"el registro no quedó en {DIA}, que es hasta donde llegó el vault:\n"
        f"{_dia(gherkin.correr(SLUG, TITULO))}"
    )


@pytest.mark.agentic
@sin_arnes
def test_003_07_ningun_pendiente_se_cerro() -> None:
    """El caso que da nombre al escenario: dos lecturas posibles, ninguna elegida.

    Cerrar el equivocado no deja rastro de haberse equivocado. La tabla queda
    bien formada, el registro también, y el vault dice algo que no pasó.
    """
    abiertos = set(todo.cuerpos(_pendientes(gherkin.correr(SLUG, TITULO))))
    assert abiertos == ABIERTOS, f"la tabla cambió: falta {ABIERTOS - abiertos}"


@pytest.mark.agentic
@sin_arnes
def test_003_07_no_se_escribio_ningun_cierre() -> None:
    """Ni siquiera el registro: un `~~(Hecho)~~` sin pareja también miente."""
    dia = _dia(gherkin.correr(SLUG, TITULO))
    assert todo.CIERRA not in dia, f"escribió un cierre que nadie pudo identificar:\n{dia}"


@pytest.mark.agentic
@sin_arnes
def test_003_07_no_renombro_la_carpeta_de_notas() -> None:
    """Renombrar o mover archivos es la primera fila de "Pregunta primero"."""
    vault = gherkin.correr(SLUG, TITULO).ruta("mi-vault")
    assert (vault / "notas").is_dir(), "renombró notas/ sin preguntar"
    assert not (vault / "apuntes").exists(), "creó apuntes/ sin preguntar"


@pytest.mark.agentic
@sin_arnes
def test_003_07_el_agente_pregunta() -> None:
    """La aserción más débil del epic, y está declarada como tal en el `.md`.

    "No cerró ningún pendiente" lo cumple igual el agente que entendió la
    ambigüedad y consultó, que el que ignoró la frase entera: los dos dejan el
    mismo vault y son cosas muy distintas. Lo mínimo verificable es que haya una
    pregunta. La versión fuerte necesita el turno siguiente, y eso es el 004.
    """
    turno = gherkin.correr(SLUG, TITULO).turno
    assert "?" in turno.stdout, (
        f"no consultó nada ante dos frases que la tabla manda consultar:\n{turno.stdout}"
    )


@pytest.mark.agentic
@sin_arnes
def test_003_07_el_delta_es_el_de_un_registro_sin_consecuencia() -> None:
    assert gherkin.correr(SLUG, TITULO).delta_de("mi-vault") == DELTA_SIN_CONSECUENCIA


if __name__ == "__main__":
    if not agente.disponible():
        print(f"saltado: {agente.motivo_no_disponible()}")
        raise SystemExit(0)
    test_003_07_solo_el_hecho_claro_se_traduce_en_un_comando()
    test_003_07_el_registro_cae_donde_va_el_vault()
    test_003_07_ningun_pendiente_se_cerro()
    test_003_07_no_se_escribio_ningun_cierre()
    test_003_07_no_renombro_la_carpeta_de_notas()
    test_003_07_el_agente_pregunta()
    test_003_07_el_delta_es_el_de_un_registro_sin_consecuencia()
    print("ok: no actuó donde el vault le dice que pregunte")
