"""Tests del escenario 003-08-el-mismo-vault-otro-arnés.

Escenario: 003-08-el-mismo-vault-otro-arnes.md

La afirmación que le da sentido al resto del epic: el entregable no es que `agy`
opere un vault, sino que el `AGENTS.md` haga que **cualquier** agente lo opere
igual. Con un solo arnés eso no se puede sostener, porque todo lo verde es
compatible con que el documento no diga nada y ese arnés acierte por su cuenta.

Mismo dictado y mismos criterios que el `003-03`, cambiando solo quién lee.

Ejecutable directo: `python3 tests/escenarios/test_003_08_el_mismo_vault_otro_arnes.py`
"""

from __future__ import annotations

import os
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import agente  # noqa: E402
import gherkin  # noqa: E402

from tuku import todo  # noqa: E402

SLUG = "003-08-el-mismo-vault-otro-arnes"
TITULO = "otro agente, el mismo comando"
DIA = "## Martes 11 de agosto"

#: El arnés que este escenario ejerce. El resto del epic corre con el que diga
#: el entorno; este fija uno, porque cambiar de lector **es** lo que prueba.
ARNES = "hermes"

#: El delta del gemelo `002-02`: un registro sin consecuencia toca la bitácora y
#: la página de su ámbito. Copiado tal cual del `003-03`, sin relajar nada: si
#: hubiera que relajarlo para que pase otro arnés, el hallazgo sería que el
#: `AGENTS.md` depende de quién lo lee.
DELTA_SIN_CONSECUENCIA = {
    "AHORA.md": "modificado",
    "ambitos/personal/personal.md": "modificado",
}


@contextmanager
def _con_el_arnes(nombre: str) -> Iterator[None]:
    """Fija el arnés mientras dure el bloque, y devuelve el entorno como estaba."""
    previo = os.environ.get("TUKU_AGENTE")
    os.environ["TUKU_AGENTE"] = nombre
    try:
        yield
    finally:
        if previo is None:
            del os.environ["TUKU_AGENTE"]
        else:
            os.environ["TUKU_AGENTE"] = previo


def _disponible() -> str | None:
    with _con_el_arnes(ARNES):
        return agente.motivo_no_disponible()


sin_arnes = pytest.mark.skipif(_disponible() is not None, reason=_disponible() or "")


def _corrida() -> gherkin.Corrida:
    """La corrida del escenario, siempre con el otro arnés.

    `gherkin` cachea por escenario, así que el turno se paga una vez aunque
    todos los tests la pidan. El primero que entre es el que fija el arnés.
    """
    with _con_el_arnes(ARNES):
        return gherkin.correr(SLUG, TITULO)


def _registro(corrida: gherkin.Corrida) -> str:
    ahora = corrida.ruta("mi-vault", "AHORA.md").read_text(encoding="utf-8")
    dia = ahora.split(DIA, 1)[1].split("\n## ", 1)[0]
    puestos = [x for x in dia.splitlines() if x.startswith("- 09:12 ")]
    assert len(puestos) == 1, f"un registro a las 09:12, y hay {len(puestos)}:\n{dia}"
    return puestos[0]


@pytest.mark.agentic
@sin_arnes
def test_003_08_la_traduccion_es_la_misma_que_con_el_otro_arnes() -> None:
    turno = _corrida().turno
    assert turno.traduccion_sin_reintentos == ["entry add"], f"la traza dice: {turno.comandos}"
    if turno.reintentos:
        # Se reporta y no falla: una llamada idéntica repetida es idempotente y
        # deja el mismo vault. Dice algo del arnés, no de cómo leyó el vault.
        print(f"\n[reporte] {ARNES} repitió una llamada idéntica: {turno.reintentos}")


@pytest.mark.agentic
@sin_arnes
def test_003_08_el_registro_queda_igual_de_bien_puesto() -> None:
    """Hora y ámbito, que son lo cerrado. El cuerpo lo redacta él."""
    linea = _registro(_corrida())
    assert linea.startswith("- 09:12 - [[personal]]"), f"hora o ámbito distintos: {linea}"
    puestas = [m for m in (todo.ABRE, todo.CIERRA, "**cadencia**") if m in linea]
    assert not puestas, f"marcó {puestas} un hecho que no abrió ni cerró nada: {linea}"


@pytest.mark.agentic
@sin_arnes
def test_003_08_el_delta_es_el_del_gemelo_determinista() -> None:
    """Los criterios no se relajan porque cambie el arnés."""
    assert _corrida().delta_de("mi-vault") == DELTA_SIN_CONSECUENCIA


@pytest.mark.agentic
@sin_arnes
def test_003_08_el_turno_queda_escrito_para_leerlo_a_mano() -> None:
    """La evidencia de la corrida queda en disco, y con lo que hace falta leer.

    Un turno no repite resultado, así que el archivo es lo único que va a
    existir de esta corrida. Se afirma su estructura y no su contenido: lo que
    el agente diga se juzga leyéndolo, al lado del turno del `003-03`.

    La conversación intermedia sería mejor evidencia que la respuesta final, y
    el arnés la pide (`sesion` en `ARNESES`), pero `hermes` no persiste la
    sesión de un turno lanzado así y no se afirma sobre ella: una aserción que
    depende de que el arnés colabore verifica al arnés, no al vault.
    """
    corrida = _corrida()
    escritos = list(corrida.dir.parent.glob(f"{ARNES}.*.txt"))
    assert escritos, f"no quedó el archivo del turno en {corrida.dir.parent}"
    escrito = escritos[-1].read_text(encoding="utf-8")
    assert corrida.turno.prompt.strip() in escrito, "el archivo no trae lo que se dictó"
    for titulo in ("Lo que respondió el agente", "Lo que ejecutó"):
        assert titulo in escrito, f"al archivo del turno le falta «{titulo}»"


if __name__ == "__main__":
    motivo = _disponible()
    if motivo is not None:
        print(f"saltado: {motivo}")
        raise SystemExit(0)
    test_003_08_la_traduccion_es_la_misma_que_con_el_otro_arnes()
    test_003_08_el_registro_queda_igual_de_bien_puesto()
    test_003_08_el_delta_es_el_del_gemelo_determinista()
    test_003_08_el_turno_queda_escrito_para_leerlo_a_mano()
    print(f"ok: el vault manda igual sobre {ARNES}")
