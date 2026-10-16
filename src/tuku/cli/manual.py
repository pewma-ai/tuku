"""`reglas/comandos.tuku.md`: qué hace cada comando sobre los archivos del vault.

El principio 5 pide que la especificación de cada automatismo acompañe al libro
del autor y que el código viva fuera. Sin `tuku` instalado no hay `-h`, así que
lo que el `-h` dice tiene que estar también en el vault: este archivo.

Sale del árbol de argparse y no de una lista escrita aparte, por la misma razón
que `comandos()`: una lista paralela se desincroniza en silencio. Lo escribe
`tuku init` al sembrar y lo reescribe `tuku rebuild`, porque es derivado: de la
versión de `tuku` instalada, no del conjunto canónico.

Cada descripción dice qué archivos toca y cómo, con precisión para hacerlo sin
`tuku` (principio 1).
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

#: Dónde vive el archivo dentro del vault.
ARCHIVO = "reglas/comandos.tuku.md"

_ENCABEZADO = (
    "---\ntype: Config\n---\n\n# Comandos de TUKU\n\n"
    "Qué hace cada comando de `tuku` sobre los archivos del vault. El código vive fuera de "
    "este vault, en el paquete `tuku`; este archivo es lo que queda si no está "
    "instalado. Lo escribe `tuku init` desde la ayuda de cada comando "
    "(`tuku <comando> -h`) y lo reescribe `tuku rebuild`, así que no se edita.\n"
)


@dataclass(frozen=True)
class Entrada:
    """Un sustantivo o un comando, con lo que su ayuda dice de él.

    `nivel` es la profundidad en el árbol: 1 para `tuku scope`, 2 para
    `tuku scope rename`. `invocable` es falso en un sustantivo con verbos.
    """

    nombre: str
    que_hace: str
    nivel: int = 1
    invocable: bool = True


def entradas(
    parser: argparse.ArgumentParser, camino: str = "tuku", nivel: int = 1
) -> list[Entrada]:
    """El árbol de la ayuda, en el orden en que se registró.

    Cada sustantivo entra con su descripción, seguido de sus verbos un nivel
    más adentro. Un sustantivo sin verbos (`init`, `doctor`) es él mismo el
    comando.
    """
    salida: list[Entrada] = []
    for accion in parser._actions:
        if not isinstance(accion, argparse._SubParsersAction):
            continue
        for nombre, sub in accion.choices.items():
            ruta = f"{camino} {nombre}"
            hijos = entradas(sub, ruta, nivel + 1)
            texto = " ".join((sub.description or "").split())
            salida.append(Entrada(ruta, texto, nivel, invocable=not hijos))
            salida += hijos
    return salida


def documento(lista: list[Entrada]) -> str:
    """El archivo entero. Determinista: la misma lista da los mismos bytes."""
    bloques = [
        f"{'#' * (e.nivel + 1)} {e.nombre}\n\n{e.que_hace or 'Sin descripción.'}\n"
        for e in lista
    ]
    return _ENCABEZADO + "".join(f"\n{b}" for b in bloques)


def del_cli() -> str:
    """El archivo que corresponde al `tuku` que está corriendo."""
    from tuku.cli import _construir_parser

    return documento(entradas(_construir_parser()))
