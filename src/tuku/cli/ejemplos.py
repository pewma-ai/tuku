"""Los ejemplos de cada comando: el `epilog` de su ayuda y de `reglas/comandos.tuku.md`.

Viven juntos y no junto a cada parser para que se lean de corrido y con los
mismos nombres (la pyme de Andrea). `tests/unitarios/test_ejemplos.py` parsea
cada uno, así que un ejemplo que deja de ser válido rompe la suite.

**Qué lee y escribe:** nada; solo fija el texto de la ayuda.
"""

from __future__ import annotations

import argparse

#: Cada comando (`sustantivo` o `sustantivo verbo`) con sus ejemplos, uno por línea.
EJEMPLOS: dict[str, tuple[str, ...]] = {
    "init": ('tuku init mi-vault --author "Andrea Rojas" --at 2026-08-11',),
    "process": ("tuku process",),
    "process cycle": ("tuku process cycle --at 2026-08-17",),
    "entry create": (
        'tuku entry create --body "entregué 40 cuadernos" --scope colegio-los-robles',
        'tuku entry create --body "llamé al contador" --at "2026-08-11 09:12"',
    ),
    "entry update": (
        'tuku entry update --match cuadernos --body "entregué 45 cuadernos"',
        'tuku entry update 2026-08-11 --match contador --body "llamé al contador por el F29"',
    ),
    "entry move": (
        "tuku entry move --match cuadernos --scope colegio-los-robles",
        "tuku entry move 2026-08-11 --match contador --scope negocio",
    ),
    "todo open": (
        'tuku todo open --body "pagar la patente" --due 2026-08-20',
        'tuku todo open --body "renovar el seguro del local" --horizon "próxima semana"',
    ),
    "todo close": ('tuku todo close "pagar la patente"',),
    "scope create": (
        "tuku scope create colegio-los-robles --keyword don-rodolfo,lr",
        "tuku scope create clientes-nuevos --parent negocio --since 30",
    ),
    "scope update": ("tuku scope update colegio-los-robles --keyword cuadernos",),
    "scope move": ("tuku scope move colegio-los-robles --parent negocio/clientes",),
    "scope rename": ("tuku scope rename colegio-los-robles colegio-robles",),
    "note create": (
        'tuku note create "Reunión con Viana" --body "Quedamos en revisar la cotización." '
        "--scope negocio",
        'tuku note create "Patricia Lillo" --subtype persona --body-file patricia.md '
        "--scope liceo-tecnico-andes",
    ),
    "note rename": ('tuku note rename "Reunión con Viana" "Reunión con Viana, marzo"',),
    "context": (
        "tuku context",
        "tuku context todo",
        "tuku context todo --late",
        "tuku context entry --since 7",
    ),
    "doctor": ("tuku doctor", "tuku doctor todo"),
    "fix": ("tuku fix link",),
    "regenerate": ("tuku regenerate", "tuku regenerate scope"),
}


def aplicar(parser: argparse.ArgumentParser, camino: str = "") -> None:
    """Pone a cada parser de `EJEMPLOS` su epílogo, con los saltos de línea como están."""
    for accion in parser._actions:
        if not isinstance(accion, argparse._SubParsersAction):
            continue
        for nombre, sub in accion.choices.items():
            ruta = f"{camino} {nombre}".strip()
            if ejemplos := EJEMPLOS.get(ruta):
                sub.epilog = "Ejemplos:\n" + "\n".join(f"  {e}" for e in ejemplos)
                sub.formatter_class = argparse.RawDescriptionHelpFormatter
            aplicar(sub, ruta)
