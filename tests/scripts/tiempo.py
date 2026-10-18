"""El reloj falso de los escenarios: `TUKU_NOW` congela `date` y `datetime` de `tuku`.

Lo usan el arnés (`gherkin.py`, para los comandos en proceso) y el shim del
agente (`agente.py`), de modo que el agente y el escenario viven en el mismo día.
El código de producción no lee `TUKU_NOW`.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import ExitStack, contextmanager, suppress
from datetime import date, datetime
from typing import Any
from unittest.mock import patch


@contextmanager
def congelar(tuku_now: str | None) -> Iterator[None]:
    """Congela deterministamente date.today() y datetime.now() en tuku para tests."""
    if not tuku_now:
        yield
        return

    val = tuku_now.strip().replace(" ", "T")
    if "T" in val:
        partes = val.split("T")
        fecha_parte = partes[0]
        hora_parte = partes[1]
        if len(hora_parte.split(":")) == 2:
            hora_parte += ":00"
        dt = datetime.fromisoformat(f"{fecha_parte}T{hora_parte}")
    else:
        dt = datetime.fromisoformat(f"{val}T00:00:00")
    d = dt.date()

    class FakeDate(date):
        @classmethod
        def today(cls) -> Any:
            return d

    class FakeDatetime(datetime):
        @classmethod
        def now(cls, tz: Any = None) -> Any:
            if tz is not None:
                return dt.astimezone(tz) if dt.tzinfo else dt.replace(tzinfo=tz)
            return dt

    modulos = [
        "tuku.entry",
        "tuku.todo",
        "tuku.note",
        "tuku.cycle",
        "tuku.context",
        "tuku.init",
        "tuku.scope",
        "tuku.cli.opciones",
    ]
    with ExitStack() as stack:
        for mod in modulos:
            with suppress(AttributeError, ModuleNotFoundError):
                stack.enter_context(patch(f"{mod}.date", FakeDate))
            with suppress(AttributeError, ModuleNotFoundError):
                stack.enter_context(patch(f"{mod}.datetime", FakeDatetime))
        yield
