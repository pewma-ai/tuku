"""El reloj de los escenarios: `TUKU_NOW` fija el `now` que recibe `cli.main`.

Lo usan el arnés (`gherkin.py`, para los comandos en proceso) y el shim del
agente (`agente.py`), de modo que el agente y el escenario viven en el mismo día.
El código de producción no lee `TUKU_NOW`: `main` recibe el instante.
"""

from __future__ import annotations

from datetime import datetime


def instante(tuku_now: str | None) -> datetime | None:
    """El instante de `TUKU_NOW` (`AAAA-MM-DD HH:MM` o `AAAA-MM-DD`), o `None` si no hay."""
    if not tuku_now:
        return None
    val = tuku_now.strip().replace(" ", "T")
    if "T" not in val:
        return datetime.fromisoformat(f"{val}T00:00:00")
    fecha, hora = val.split("T")
    if len(hora.split(":")) == 2:
        hora += ":00"
    return datetime.fromisoformat(f"{fecha}T{hora}")
