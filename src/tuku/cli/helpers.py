"""Constantes y funciones auxiliares compartidas por la capa CLI."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from datetime import date, time
from typing import Any

from tuku.resultado import Resultado

#: Códigos de salida. Son contrato con quien invoca, persona o agente, y están
#: fijados en `spec/cli.md`. El 2 queda reservado a argparse, que lo emite ante
#: una invocación mal formada: ningún comando puede devolverlo por otra causa,
#: o quien invoca no puede distinguir "me equivoqué al escribir el comando" de
#: "el comando se negó".
EXITO = 0
RECHAZO = 1  # el comando entendió y se negó por el estado del vault
USO = 2  # reservado a argparse
ENTORNO = 3  # la instalación de TUKU no está donde debería

Handler = Callable[[argparse.Namespace], int]
Subparsers = Any


def fecha(valor: str) -> date:
    """AAAA-MM-DD, o un error de uso que dice qué se esperaba."""
    try:
        return date.fromisoformat(valor)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{valor!r} no es una fecha AAAA-MM-DD") from None


def hora(valor: str) -> str:
    """HH:MM, normalizada a dos dígitos: `9:05` es `09:05`."""
    try:
        h, m = valor.split(":")
        if len(m) == 2:
            return time(int(h), int(m)).strftime("%H:%M")
    except ValueError:
        pass
    raise argparse.ArgumentTypeError(f"{valor!r} no es una hora HH:MM")


def traducir(r: Resultado, prefijo: str) -> int:
    """Escribe lo que dejó una operación y devuelve su código de salida.

    Es toda la lógica que le queda al CLI después de despachar: un rechazo por el
    estado del vault va a `stderr` con el nombre del comando delante, y todo lo
    demás a `stdout`. Los lint son el caso intermedio, y por eso `Resultado`
    lleva `error` aparte de `ok`: reportan hallazgos por `stdout` y aun así
    salen con `RECHAZO`.
    """
    if r.error:
        print(f"{prefijo}: {r.mensaje}", file=sys.stderr)
    else:
        print(r.mensaje)
    for aviso in r.avisos:
        print(f"{prefijo}: warning: {aviso}", file=sys.stderr)
    return EXITO if r.ok else RECHAZO


def sin_implementar(prefijo: str, mientras: str) -> int:
    """Un verbo que ya tiene lugar en el CLI y todavía no tiene implementación.

    Avisa por `stderr` y sale con éxito sin escribir nada. Existe para que la
    superficie y la ayuda del comando se revisen antes que su lógica; `mientras`
    dice qué hacer hasta que exista.
    """
    return traducir(
        Resultado.hecho(
            "no escribí nada.", avisos=(f"todavía no está implementado. {mientras}",)
        ),
        prefijo,
    )


def cuerpo_de_la_nota(args: argparse.Namespace) -> str | None:
    """De dónde sale el cuerpo: la línea de comandos, o un archivo (`-` es `stdin`).

    Se queda en el CLI porque es una decisión sobre cómo llegó el texto, no
    sobre qué hace TUKU con él.

    `stdin` se lee solo cuando lo piden: `isatty()` en falso no dice que haya
    datos, dice que no es una terminal. Contra un pipe vacío el comando se
    colgaba esperando para siempre.
    """
    if args.body_file is not None:
        crudo = (
            sys.stdin.read()
            if str(args.body_file) == "-"
            else str(args.body_file.read_text(encoding="utf-8"))
        )
    elif args.body is not None:
        crudo = str(args.body)
    else:
        return None
    return crudo if crudo.strip() else None
