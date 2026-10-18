"""Leer y escribir archivos del vault sin pisar lo que otro programa cambió entretanto.

El autor edita en Obsidian mientras un agente o un cron corre `tuku` (`spec/cli.md`,
"Escribir con el vault abierto en otro editor"). Dentro de un intento, `leer` recuerda
el texto que había y `escribir` reemplaza el archivo de una vez (un temporal y
`os.replace`), solo si en disco sigue ese texto. Si cambió, levanta `Conflicto`, y
`con_reintentos` vuelve a correr el comando entero: todo mutador es idempotente, así
que repetirlo completa lo que quedó a medias.

Fuera de un intento (un test que llama directo a un caso de uso) la escritura sigue
siendo atómica, pero no compara nada.
"""

from __future__ import annotations

import contextvars
import os
import tempfile
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

#: Las esperas entre un intento y el siguiente: tres reintentos.
ESPERAS = (0.1, 0.3, 1.0)


class Conflicto(Exception):
    """Otro programa cambió el archivo entre que `tuku` lo leyó y lo iba a escribir."""

    def __init__(self, ruta: Path) -> None:
        super().__init__(f"otro programa cambió {ruta} mientras tuku escribía")
        self.ruta = ruta


@dataclass(frozen=True)
class SinReintentos(Exception):
    """El último intento también chocó: qué alcanzó a escribir y qué archivo faltó."""

    ruta: Path
    escritos: tuple[Path, ...]

    def mensaje(self, base: Path) -> str:
        def nombre(r: Path) -> str:
            try:
                return r.resolve().relative_to(base.resolve()).as_posix()
            except ValueError:
                return str(r)

        falta = nombre(self.ruta)
        if not self.escritos:
            return (
                f"no escribí nada: otro programa estaba editando {falta}. "
                "Corre el mismo comando de nuevo."
            )
        hechos = ", ".join(dict.fromkeys(nombre(r) for r in self.escritos))
        return (
            f"escribí {hechos}. Faltó {falta}, y lo que venía después de él: otro programa "
            "lo estaba editando. Corre el mismo comando de nuevo."
        )


@dataclass
class _Intento:
    leidos: dict[Path, str] = field(default_factory=dict)
    escritos: list[Path] = field(default_factory=list)


_INTENTO: contextvars.ContextVar[_Intento | None] = contextvars.ContextVar(
    "tuku_intento", default=None
)


def _modo_por_defecto() -> int:
    mascara = os.umask(0)
    os.umask(mascara)
    return 0o666 & ~mascara


_MODO = _modo_por_defecto()


def leer(ruta: Path) -> str:
    """El texto del archivo. Dentro de un intento, recuerda el primero que se leyó."""
    texto = ruta.read_text(encoding="utf-8")
    if (intento := _INTENTO.get()) is not None:
        intento.leidos.setdefault(ruta.resolve(), texto)
    return texto


def escribir(ruta: Path, texto: str, *, conservar_fecha: bool = False) -> None:
    """Reemplaza el archivo de una vez, si sigue como se leyó en este intento.

    `conservar_fecha` deja la fecha de modificación como estaba: un cambio solo de
    forma no es una edición del autor (`spec/cli.md`, la pareja `doctor` / `fix`).
    """
    clave = ruta.resolve()
    intento = _INTENTO.get()
    if intento is not None and clave in intento.leidos:
        try:
            actual: str | None = ruta.read_text(encoding="utf-8")
        except FileNotFoundError:
            actual = None
        if actual != intento.leidos[clave]:
            raise Conflicto(ruta)

    antes = ruta.stat() if ruta.exists() else None
    fd, temporal = tempfile.mkstemp(dir=ruta.parent, prefix=f".{ruta.name}.", suffix=".tuku")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(texto)
        os.chmod(temporal, (antes.st_mode & 0o777) if antes else _MODO)
        os.replace(temporal, ruta)
    except BaseException:
        Path(temporal).unlink(missing_ok=True)
        raise
    if conservar_fecha and antes is not None:
        os.utime(ruta, ns=(antes.st_atime_ns, antes.st_mtime_ns))

    if intento is not None:
        intento.leidos[clave] = texto
        intento.escritos.append(ruta)


def con_reintentos[T](
    correr: Callable[[], T], esperar: Callable[[float], None] = time.sleep
) -> T:
    """Corre `correr`; ante un `Conflicto`, espera y lo corre de nuevo, hasta tres veces."""
    for espera in (*ESPERAS, None):
        intento = _Intento()
        token = _INTENTO.set(intento)
        try:
            return correr()
        except Conflicto as c:
            if espera is None:
                raise SinReintentos(c.ruta, tuple(intento.escritos)) from c
        finally:
            _INTENTO.reset(token)
        esperar(espera)
    raise AssertionError("inalcanzable")
