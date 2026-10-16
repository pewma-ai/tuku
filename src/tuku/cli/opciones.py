"""El vocabulario de opciones que comparten los comandos de `tuku`.

Un comando no declara una opción compartida por su cuenta: la pide a
`Opciones`, que fija su nombre, sus alias, su tipo y su ayuda. Así `--at`
significa lo mismo en `entry add` que en `scope create`.

`--at` es cuándo pasó algo y `--due`, para cuándo es. Los dos aceptan
`AAAA-MM-DD HH:MM`, `AAAA-MM-DD` o `HH:MM`. Una fecha sin año (`MM-DD`) no se
adivina: `08-11` en Chile se lee 8 de noviembre. El comando falla y ofrece la
invocación corregida con el año completo (`sin_anio`).
"""

from __future__ import annotations

import argparse
import re
import shlex
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

from tuku.ahora import encabezado_de
from tuku.cli.helpers import hora

_FECHA = re.compile(r"^(?:(?P<anio>\d{4})-)?(?P<mes>\d{1,2})-(?P<dia>\d{1,2})$")


@dataclass(frozen=True)
class Momento:
    """Un día, una hora, o los dos; lo que falte lo completa quien lo usa.

    `propuesto` es el día que se habría entendido de una fecha escrita sin año:
    no se usa, se ofrece.
    """

    dia: date | None = None
    hora: str | None = None
    texto: str = ""
    propuesto: date | None = None

    def celda(self) -> str:
        """Como se escribe en la columna `Vence`: `AAAA-MM-DD` o `AAAA-MM-DD HH:MM`."""
        if self.dia is None:
            return ""
        return f"{self.dia.isoformat()} {self.hora}" if self.hora else self.dia.isoformat()


def _leer(valor: str) -> tuple[re.Match[str] | None, str | None]:
    """La fecha y la hora de `valor`, en ese orden y cada una opcional."""
    partes = valor.split()
    if not partes or len(partes) > 2:
        raise argparse.ArgumentTypeError(_formato(valor))
    m = _FECHA.match(partes[0])
    if m is None and len(partes) == 2:
        raise argparse.ArgumentTypeError(_formato(valor))
    resto = partes[1:] if m else partes
    return m, (hora(resto[0]) if resto else None)


def _formato(valor: str) -> str:
    return f"{valor!r} no es AAAA-MM-DD HH:MM, AAAA-MM-DD ni HH:MM"


def _dia(anio: int, mes: int, dia: int, valor: str) -> date:
    try:
        return date(anio, mes, dia)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{valor!r} no es una fecha que exista") from None


def _momento(valor: str, *, hacia_adelante: bool) -> Momento:
    m, h = _leer(valor)
    if m is None:
        if not hacia_adelante:
            return Momento(hora=h, texto=valor)
        ahora = datetime.now()
        hoy = ahora.date()
        llega = hoy if str(h) > ahora.strftime("%H:%M") else hoy + timedelta(1)
        return Momento(llega, h, valor)
    mes, dia = int(m.group("mes")), int(m.group("dia"))
    if m.group("anio"):
        return Momento(_dia(int(m.group("anio")), mes, dia, valor), h, valor)
    return Momento(hora=h, texto=valor, propuesto=_con_anio(mes, dia, valor, hacia_adelante))


def _con_anio(mes: int, dia: int, valor: str, hacia_adelante: bool) -> date:
    """El `MM-DD` más cercano a hoy hacia adelante o hacia atrás, hoy incluido.

    Ocho años alcanzan para encontrar un 29 de febrero.
    """
    hoy = date.today()
    paso = 1 if hacia_adelante else -1
    for anio in range(hoy.year, hoy.year + 9 * paso, paso):
        try:
            candidato = date(anio, mes, dia)
        except ValueError:
            continue
        if (candidato >= hoy) if hacia_adelante else (candidato <= hoy):
            return candidato
    raise argparse.ArgumentTypeError(f"{valor!r} no es una fecha que exista")


def momento_pasado(valor: str) -> Momento:
    """`--at`: una fecha sin año se propone en el pasado más cercano."""
    return _momento(valor, hacia_adelante=False)


def momento_futuro(valor: str) -> Momento:
    """`--due`: una hora sola es la próxima vez que llega, y una fecha sin año, la próxima."""
    return _momento(valor, hacia_adelante=True)


def momento_con_hora(valor: str) -> Momento:
    """`--at` de un registro que ya existe: la hora lo ubica y no se completa."""
    m = momento_pasado(valor)
    if m.hora is None:
        raise argparse.ArgumentTypeError(f"{valor!r} no lleva la hora del registro (HH:MM)")
    return m


class Opciones:
    """Las opciones compartidas de un subcomando, cada una con su único vocabulario."""

    def __init__(self, parser: argparse.ArgumentParser) -> None:
        self.parser = parser

    def vault(self, ayuda: str = "vault a modificar") -> None:
        self.parser.add_argument("--vault", default=".", type=Path, help=ayuda)

    def body(self, ayuda: str, *, requerido: bool = True) -> None:
        self.parser.add_argument(
            "--body",
            "--cuerpo",
            dest="body",
            required=requerido,
            default=None,
            help=ayuda,
        )

    def scope(
        self, ayuda: str = "ámbito, sin corchetes; por defecto, `scope_default` de la config"
    ) -> None:
        self.parser.add_argument("--scope", "--ambito", dest="scope", default=None, help=ayuda)

    def at(
        self,
        ayuda: str = "cuándo: AAAA-MM-DD HH:MM, AAAA-MM-DD o HH:MM; lo que falte, hoy y ahora",
        *,
        con_hora: bool = False,
    ) -> None:
        self.parser.add_argument(
            "--at",
            "--cuando",
            dest="at",
            required=con_hora,
            default=Momento(),
            type=momento_con_hora if con_hora else momento_pasado,
            help=ayuda,
        )

    def due(self, grupo: argparse._MutuallyExclusiveGroup | None = None) -> None:
        (grupo or self.parser).add_argument(
            "--due",
            "--vence",
            dest="due",
            default=Momento(),
            type=momento_futuro,
            help=(
                "cuándo vence: AAAA-MM-DD HH:MM, AAAA-MM-DD o HH:MM (la próxima vez que "
                "llega); el horizonte pasa a `con fecha`"
            ),
        )


def sin_anio(args: argparse.Namespace, argv: list[str]) -> str | None:
    """El error de las fechas escritas sin año, con la invocación corregida; o `None`."""
    corregido = list(argv)
    lineas = []
    for opcion in ("at", "due"):
        m = getattr(args, opcion, None)
        if not isinstance(m, Momento) or m.propuesto is None:
            continue
        completo = f"{m.propuesto.isoformat()} {m.hora}" if m.hora else m.propuesto.isoformat()
        corregido[corregido.index(m.texto)] = completo
        dia = encabezado_de(m.propuesto).removeprefix("## ").lower()
        lineas.append(f"--{opcion} {m.texto!r} no lleva año: ¿el {dia} de {m.propuesto.year}?")
    if not lineas:
        return None
    return "\n".join([*lineas, f"  tuku {shlex.join(corregido)}"])
