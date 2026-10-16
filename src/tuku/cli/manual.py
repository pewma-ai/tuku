"""`reglas/comandos.tuku.md`: qué hace cada comando y cómo hacerlo a mano.

El principio 5 pide que la especificación de cada automatismo acompañe al libro
del autor y que el código viva fuera. Sin `tuku` instalado no hay `-h`, así que
lo que el `-h` dice tiene que estar también en el vault: este archivo.

Sale del árbol de argparse y no de una lista escrita aparte, por la misma razón
que `comandos()`: una lista paralela se desincroniza en silencio. Lo escribe
`tuku init` al sembrar y lo reescribe `tuku rebuild`, porque es derivado: de la
versión de `tuku` instalada, no del conjunto canónico.

**A mano:** copiar, por cada comando, el párrafo y la línea "A mano" de su `-h`.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

#: Dónde vive el archivo dentro del vault.
ARCHIVO = "reglas/comandos.tuku.md"

_ENCABEZADO = (
    "---\ntype: Config\n---\n\n# Comandos de TUKU\n\n"
    "Qué hace cada comando de `tuku` y cómo hacerlo a mano. El código vive fuera de "
    "este vault, en el paquete `tuku`; este archivo es lo que queda si no está "
    "instalado. Lo escribe `tuku init` desde la ayuda de cada comando "
    "(`tuku <comando> -h`) y lo reescribe `tuku rebuild`: no se edita a mano.\n"
)


@dataclass(frozen=True)
class Entrada:
    """Un comando invocable y lo que su ayuda dice de él."""

    nombre: str
    que_hace: str
    a_mano: str


def entradas(parser: argparse.ArgumentParser, camino: str = "tuku") -> list[Entrada]:
    """Los comandos invocables del árbol, en el orden en que se registraron.

    Un sustantivo con verbos no se invoca solo: entran sus verbos. Un sustantivo
    sin verbos (`init`, `doctor`) entra él.
    """
    salida: list[Entrada] = []
    for accion in parser._actions:
        if not isinstance(accion, argparse._SubParsersAction):
            continue
        for nombre, sub in accion.choices.items():
            ruta = f"{camino} {nombre}"
            hijos = entradas(sub, ruta)
            if hijos:
                salida += hijos
                continue
            epilog = (sub.epilog or "").strip()
            salida.append(
                Entrada(
                    nombre=ruta,
                    que_hace=" ".join((sub.description or "").split()),
                    a_mano=" ".join(epilog.removeprefix("A mano:").split()),
                )
            )
    return salida


def documento(lista: list[Entrada]) -> str:
    """El archivo entero. Determinista: la misma lista da los mismos bytes."""
    bloques = [
        f"## {e.nombre}\n\n**Qué hace:** {e.que_hace or 'sin declarar.'}\n"
        f"**A mano:** {e.a_mano or 'sin declarar.'}\n"
        for e in lista
    ]
    return _ENCABEZADO + "".join(f"\n{b}" for b in bloques)


def del_cli() -> str:
    """El archivo que corresponde al `tuku` que está corriendo."""
    from tuku.cli import _construir_parser

    return documento(entradas(_construir_parser()))
