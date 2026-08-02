"""Parser y gramática de expresiones temporales (F1.4).

Cumple `spec/tarea.md` §4.
Soporta:
- Precisa: `YYYY-MM-DD` o `YYYY-MM-DD HH:MM`
- Rango: `YYYY-MM-DD/YYYY-MM-DD`
- Difusa: `~YYYY-MM` o `~Ns` / `~Nm`
- Relativa a ciclo: `next:<tipo>` o `next`
"""

from __future__ import annotations

import re
from dataclasses import dataclass


class DateGrammarError(Exception):
    """Error al parsear una expresión temporal."""


@dataclass
class TemporalExpr:
    kind: str  # 'precise', 'range', 'fuzzy', 'next'
    start_date: str | None = None
    end_date: str | None = None
    time_str: str | None = None
    fuzzy_str: str | None = None
    cycle_type: str | None = None

    @classmethod
    def parse(cls, expr: str) -> TemporalExpr:
        raw = expr.strip()
        if raw.startswith("(") and raw.endswith(")"):
            raw = raw[1:-1].strip()

        if not raw:
            raise DateGrammarError("Expresión temporal vacía")

        # 1. Relativa a ciclo: next o next:<tipo>
        if raw == "next" or raw.startswith("next:"):
            cycle_type = raw.split(":", 1)[1] if ":" in raw else None
            return cls(kind="next", cycle_type=cycle_type)

        # 2. Difusa: ~YYYY-MM o ~Ns / ~Nm
        if raw.startswith("~"):
            return cls(kind="fuzzy", fuzzy_str=raw[1:])

        # 3. Rango: YYYY-MM-DD/YYYY-MM-DD
        if "/" in raw:
            parts = raw.split("/", 1)
            date_pat = r"^\d{4}-\d{2}-\d{2}$"
            if not (re.match(date_pat, parts[0]) and re.match(date_pat, parts[1])):
                raise DateGrammarError(f"Rango de fechas inválido: {expr!r}")
            return cls(kind="range", start_date=parts[0], end_date=parts[1])

        # 4. Precisa: YYYY-MM-DD o YYYY-MM-DD HH:MM
        time_part: str | None = None
        date_part = raw
        if " " in raw:
            date_part, time_part = raw.split(" ", 1)
            if not re.match(r"^(?:[01]\d|2[0-3]):[0-5]\d$", time_part):
                raise DateGrammarError(f"Hora inválida en fecha precisa: {expr!r}")

        date_match = re.match(r"^(\d{4})-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$", date_part)
        if not date_match:
            raise DateGrammarError(f"Fecha precisa inválida: {expr!r}")

        return cls(kind="precise", start_date=date_part, time_str=time_part)
