"""Tests del escenario 003-09-el-mismo-vault-tercer-arnés.

Escenario: 003-09-el-mismo-vault-tercer-arnes.md

El [`003-08`](003-08-el-mismo-vault-otro-arnes.md) sostiene la portabilidad en
dos arneses; este agrega el tercero. Lo que hace distinto a `claude` es que no
descubre solo el documento del vault (busca `CLAUDE.md`, no `AGENTS.md`), así
que el arnés le antepone un preámbulo que dice **dónde mirar, no qué dice**: si
el `AGENTS.md` no alcanzara, el turno fallaría igual.

Mismo dictado y mismos criterios que el `003-03`, cambiando solo quién lee.

Ejecutable directo: `python3 tests/escenarios/test_003_09_el_mismo_vault_tercer_arnes.py`
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

SLUG = "003-09-el-mismo-vault-tercer-arnes"
TITULO = "un tercer agente, el mismo comando"
DIA = "## Martes 11 de agosto"

#: El arnés que este escenario ejerce, con lo que lo hace reproducible.
#:
#: **El modelo y el esfuerzo van fijos y son baratos**, por lo mismo que el
#: resto del epic corre así: el comportamiento que el `AGENTS.md` describe es
#: leer una tabla de despacho y ejecutar la fila que corresponde. Un documento
#: que solo funcionara con el modelo más caro pensando al máximo no cumpliría
#: lo que promete, porque lo que estaría resolviendo el turno es el modelo.
ARNES = "claude"
MODELO = "sonnet"
ESFUERZO = "low"

#: Lo que se fija en el entorno para que la corrida no dependa de la máquina.
ENTORNO = {
    "TUKU_AGENTE": ARNES,
    "TUKU_AGENTE_MODELO": MODELO,
    "TUKU_AGENTE_ESFUERZO": ESFUERZO,
}

#: El delta del gemelo `002-02`: un registro sin consecuencia toca la bitácora y
#: la página de su ámbito. Copiado tal cual del `003-03`, sin relajar nada: si
#: hubiera que relajarlo para que pase otro arnés, el hallazgo sería que el
#: `AGENTS.md` depende de quién lo lee.
DELTA_SIN_CONSECUENCIA = {
    "AHORA.md": "modificado",
    "ambitos/personal/personal.md": "modificado",
}


@contextmanager
def _con_el_arnes() -> Iterator[None]:
    """Fija arnés, modelo y esfuerzo mientras dure el bloque, y los devuelve."""
    previo = {k: os.environ.get(k) for k in ENTORNO}
    os.environ.update(ENTORNO)
    try:
        yield
    finally:
        for k, v in previo.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def _disponible() -> str | None:
    with _con_el_arnes():
        return agente.motivo_no_disponible()


sin_arnes = pytest.mark.skipif(_disponible() is not None, reason=_disponible() or "")


def _corrida() -> gherkin.Corrida:
    """La corrida del escenario, siempre con el tercer arnés.

    `gherkin` cachea por escenario, así que el turno se paga una vez aunque
    todos los tests la pidan. El primero que entre es el que fija el arnés.
    """
    with _con_el_arnes():
        return gherkin.correr(SLUG, TITULO)


def _registro(corrida: gherkin.Corrida) -> str:
    ahora = corrida.ruta("mi-vault", "AHORA.md").read_text(encoding="utf-8")
    dia = ahora.split(DIA, 1)[1].split("\n## ", 1)[0]
    puestos = [x for x in dia.splitlines() if x.startswith("- 09:12 ")]
    assert len(puestos) == 1, f"un registro a las 09:12, y hay {len(puestos)}:\n{dia}"
    return puestos[0]


@pytest.mark.agentic
@sin_arnes
def test_003_09_la_traduccion_es_la_misma_que_con_los_otros_arneses() -> None:
    turno = _corrida().turno
    assert turno.traduccion_sin_reintentos == ["entry add"], f"la traza dice: {turno.comandos}"
    if turno.reintentos:
        # Se reporta y no falla: una llamada idéntica repetida es idempotente y
        # deja el mismo vault. Dice algo del arnés, no de cómo leyó el vault.
        print(f"\n[reporte] {ARNES} repitió una llamada idéntica: {turno.reintentos}")


@pytest.mark.agentic
@sin_arnes
def test_003_09_el_registro_queda_igual_de_bien_puesto() -> None:
    """Hora y ámbito, que son lo cerrado. El cuerpo lo redacta él."""
    linea = _registro(_corrida())
    assert linea.startswith("- 09:12 - [[personal]]"), f"hora o ámbito distintos: {linea}"
    puestas = [m for m in (todo.ABRE, todo.CIERRA, "**cadencia**") if m in linea]
    assert not puestas, f"marcó {puestas} un hecho que no abrió ni cerró nada: {linea}"


@pytest.mark.agentic
@sin_arnes
def test_003_09_el_delta_es_el_del_gemelo_determinista() -> None:
    """Los criterios no se relajan porque cambie el arnés."""
    assert _corrida().delta_de("mi-vault") == DELTA_SIN_CONSECUENCIA


@pytest.mark.agentic
@sin_arnes
def test_003_09_el_turno_queda_escrito_para_leerlo_a_mano() -> None:
    """La evidencia de la corrida queda en disco, y con lo que hace falta leer.

    Un turno no repite resultado, así que el archivo es lo único que va a
    existir de esta corrida. Se afirma su estructura y no su contenido: lo que
    el agente diga se juzga leyéndolo, al lado de los turnos del `003-03` y el
    `003-08`.
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
    test_003_09_la_traduccion_es_la_misma_que_con_los_otros_arneses()
    test_003_09_el_registro_queda_igual_de_bien_puesto()
    test_003_09_el_delta_es_el_del_gemelo_determinista()
    test_003_09_el_turno_queda_escrito_para_leerlo_a_mano()
    print(f"ok: el vault manda igual sobre {ARNES}")
