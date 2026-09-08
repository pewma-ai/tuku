"""tuku link backfill: convierte menciones sueltas en enlaces, hacia atrás.

Punto 4 del epic 002. Cuando nace un ámbito, lo que ya estaba escrito sobre él
en el ciclo en curso queda enlazado, para que la página del ámbito recoja su
historia en vez de empezar en blanco.

**Empareja contra las `keywords` declaradas** en el frontmatter de la página del
ámbito, sin distinguir mayúsculas y tratando guiones y espacios como
equivalentes (`depto-centro` captura "depto centro"). Nada se adivina: lo que se
enlaza está escrito en un archivo que el autor lee y edita, y ampliar la
cobertura es agregar una keyword. Variantes morfológicas y sinónimos quedan
fuera a propósito: eso es juicio, y el juicio no es del comando.

Nunca toca texto que ya está dentro de `[[...]]`, así que correrlo dos veces no
anida enlaces.

**Qué lee y escribe:** `AHORA.md`. Los ciclos cerrados de `bitacoras/` son
inmutables y no se tocan.
**A mano:** buscar la mención en el texto y rodearla de dobles corchetes.
"""

from __future__ import annotations

import re

#: Un enlace ya escrito. El texto se parte por acá para no enlazar dentro.
_ENLACE = re.compile(r"\[\[[^\]]*\]\]")


def _patron(keyword: str) -> re.Pattern[str]:
    """Empareja la keyword con guiones y espacios como equivalentes."""
    partes = [re.escape(p) for p in re.split(r"[-\s]+", keyword) if p]
    if not partes:
        return re.compile(r"(?!x)x")  # nunca empareja
    cuerpo = r"[-\s]+".join(partes)
    return re.compile(rf"(?<![\w-]){cuerpo}(?![\w-])", re.IGNORECASE)


def backfill(
    texto: str,
    *,
    scope: str = "",
    ambito: str = "",
    keywords: list[str],
) -> tuple[str, int]:
    """Enlaza las menciones de `keywords` a `[[scope]]`. Devuelve texto y cuántas.

    Idempotente: lo que ya está enlazado no se vuelve a enlazar, porque los
    tramos dentro de `[[...]]` no se tocan.
    """
    valor_scope = scope or ambito
    patrones = [_patron(k) for k in keywords if k.strip()]
    if not patrones:
        return texto, 0

    enlace = f"[[{valor_scope}]]"
    cambios = 0

    # El texto se parte en tramos libres separados por los enlaces que ya están.
    # Solo se transforman los tramos libres, y después se vuelve a intercalar.
    libres = _ENLACE.split(texto)
    existentes = _ENLACE.findall(texto)

    transformados = []
    for tramo in libres:
        tramo, n = _enlazar(tramo, patrones, enlace)
        cambios += n
        transformados.append(tramo)

    salida = [transformados[0]]
    for existente, tramo in zip(existentes, transformados[1:], strict=True):
        salida.append(existente)
        salida.append(tramo)
    return "".join(salida), cambios


def _enlazar(tramo: str, patrones: list[re.Pattern[str]], enlace: str) -> tuple[str, int]:
    cambios = 0
    for patron in patrones:
        tramo, n = patron.subn(enlace, tramo)
        cambios += n
    return tramo, cambios
