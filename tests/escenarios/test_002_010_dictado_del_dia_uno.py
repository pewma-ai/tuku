"""Stub del escenario 002-010-dictado-del-dia-uno.

Escenario: 002-010-dictado-del-dia-uno.md

El único escenario del epic que gasta tokens, y el dueño del fixture que
consumen los otros nueve. Va último en la cadena aunque en la narración del
día uno ocurra primero: si el primer paso dependiera de una respuesta de
agente, los nueve deterministas colgarían de ella.

Corre sobre el fixture `vacio`, no sobre el estado heredado, porque el agente
tiene que trabajar contra el mismo vault que tenía el autor al dictar.

Lo que se afirma con `assert` es la ontología cerrada (marca, posición,
ámbito) y las consecuencias (mismos pendientes, mismo cuerpo, mismos
callouts). La clasificación abierta se mide aparte y no bloquea. Todo lo
demás está en el `## Qué se mira a mano` del escenario, y ahí se queda.

Falla a propósito. El escenario está escrito, el fixture no existe, y antes de
implementarlo hay que resolver la decisión 3 de `devel/epics.md`: qué arnés de
agente se usa y cómo se aísla para no gastar tokens por accidente.

Ese aislamiento es lo primero, no lo último: mientras no exista, este test no
se escribe.
"""

from __future__ import annotations

SLUG = "002-010-dictado-del-dia-uno"
PREVIO = None  # corre sobre el fixture `vacio`, no sobre el estado heredado
DESDE = "2026-08-11"
FIXTURE = "fixtures/002-010-dictado-del-dia-uno"

FALTA = (
    "la decisión 3 del epic (arnés de agente y su aislamiento); "
    f"el fixture {FIXTURE}/ (dictado.md y entradas.md); "
    "la marca de pytest que lo deja fuera de la corrida por defecto"
)


def test_002_010_el_agente_reproduce_las_entradas_congeladas() -> None:
    raise AssertionError(f"{SLUG}: sin implementar. Falta {FALTA}.")


if __name__ == "__main__":
    test_002_010_el_agente_reproduce_las_entradas_congeladas()
