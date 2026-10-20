"""tuku process cycle: abre, repite o guarda un ciclo de `AHORA.md`.

El ciclo tiene un nombre (`cycle`) y un rango (`from` a `to`). `semana` se deduce
de un día cualquiera (de lunes a domingo); con otro nombre de la tabla de
`reglas/ciclo.user.md` el rango lo da `--to`. El ciclo siguiente empieza el día
después de que termina el anterior, sin hoyos ni solapes, y su nombre es el
siguiente de esa tabla.
Repetir el ciclo abierto solo lo verifica, o lo regenera si no tiene registros.
Un `--from` anterior al ciclo abierto guarda un ciclo pasado en `bitacoras/`,
sin verificarlo contra sus vecinos (`spec/ciclo.md`, "Abrir el siguiente ciclo").

Si hay una bitácora anterior en `bitacoras/`, el ciclo nuevo abre además el
pendiente `revisar la bitácora anterior`, con vencimiento el primer día.

**Qué lee y escribe:** lee `reglas/plantilla/AHORA.md`, `reglas/config.tuku.md`
y `bitacoras/`; lee y escribe `AHORA.md`; un ciclo pasado se escribe en
`bitacoras/`; y escribe `PENDIENTES.md` y sus vistas.
**A mano:** copiar `reglas/plantilla/AHORA.md` a `AHORA.md`, sustituir `cycle`,
`from` y `to` del frontmatter y dejar un encabezado de día por cada fecha del
rango; con una bitácora anterior, abrir `revisar la bitácora anterior` con
`tuku todo open --due <el primer día>`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

from tuku import archivo
from tuku.ahora import SEMANA, como_cerrar, nombre_del_ciclo, rango
from tuku.config import leer_config, resolver_plantilla_ahora
from tuku.init import DIAS, MESES
from tuku.resultado import Resultado

#: El pendiente con que abre todo ciclo que viene después de otro.
REVISAR_BITACORA = "revisar la bitácora anterior"

_ENCABEZADO_DE_PLANTILLA = re.compile(
    r"^## (" + "|".join(DIAS) + r") DD de mes[ \t]*$", re.MULTILINE
)


class CicloInvalido(Exception):
    """El ciclo pedido no se puede abrir; el mensaje dice el defecto y la corrección."""


@dataclass(frozen=True)
class Cycle:
    """A cycle already on disk: the open `AHORA.md` or an archived logbook."""

    start: date
    end: date
    name: str
    is_open: bool
    has_records: bool = False


def calcular_rango_semanal(fecha: date) -> tuple[date, date]:
    """Calcula el rango [lunes, domingo] de la semana que contiene `fecha`."""
    lunes = fecha - timedelta(days=fecha.weekday())
    domingo = lunes + timedelta(days=6)
    return lunes, domingo


def instantiate(
    template: str, start: date, end: date, name: str, *, status: str = "draft"
) -> str:
    """The template of `AHORA.md` for the cycle `name` that runs from `start` to `end`.

    It fills the frontmatter and writes one heading per date of the range. A day
    takes the block of the template that has its weekday (`## Martes DD de mes`),
    or the first block when the template has none for it, so a cycle of 8 or 14
    days has 8 or 14 headings.
    """
    text = template.replace("from: AAAA-MM-DD", f"from: {start.isoformat()}")
    text = text.replace("to: AAAA-MM-DD", f"to: {end.isoformat()}")
    if re.search(r"^cycle:", text, re.MULTILINE):
        text = re.sub(r"^cycle:.*$", f"cycle: {name}", text, count=1, flags=re.MULTILINE)
    else:
        has_status = re.search(r"^status:", text, re.MULTILINE)
        anchor = r"^(status:.*)$" if has_status else r"^(type:.*)$"
        text = re.sub(anchor, rf"\1\ncycle: {name}", text, count=1, flags=re.MULTILINE)
    text = re.sub(r"^status:.*$", f"status: {status}", text, count=1, flags=re.MULTILINE)

    headings = list(_ENCABEZADO_DE_PLANTILLA.finditer(text))
    if not headings:
        return text
    blocks: dict[str, str] = {}
    for i, m in enumerate(headings):
        stop = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        blocks[m.group(1)] = text[m.start() : stop].rstrip()
    first = next(iter(blocks.values()))
    trailing = text[len(text.rstrip()) :]
    days = []
    for i in range((end - start).days + 1):
        day = start + timedelta(days=i)
        block = blocks.get(DIAS[day.weekday()], first)
        heading = f"## {DIAS[day.weekday()]} {day.day} de {MESES[day.month - 1]}"
        days.append(_ENCABEZADO_DE_PLANTILLA.sub(heading, block, count=1))
    return text[: headings[0].start()] + "\n\n".join(days) + trailing


def resolver_plantilla(vault: Path) -> str:
    """Busca la plantilla de AHORA.md en el vault o en el fallback de TUKU."""
    return resolver_plantilla_ahora(vault)


def tiene_registros(ahora: str) -> bool:
    """Si el ciclo tiene algún registro escrito, con hora o sin ella."""
    from tuku.entry import registros

    return bool(registros(ahora))


def hay_bitacora_anterior(vault: Path) -> bool:
    """Si el autor ya cerró algún ciclo: `bitacoras/` tiene una bitácora."""
    return any((vault / "bitacoras").glob("bitacora-*.md"))


def _read(texto: str, *, is_open: bool) -> Cycle | None:
    limits = rango(texto)
    if limits is None:
        return None
    return Cycle(
        limits[0],
        limits[1],
        nombre_del_ciclo(texto),
        is_open,
        tiene_registros(texto) if is_open else False,
    )


def previous_cycle(vault: Path) -> Cycle | None:
    """The open cycle or, when none is open, the archived one that ends last."""
    ahora = vault / "AHORA.md"
    if ahora.is_file() and (open_cycle := _read(archivo.leer(ahora), is_open=True)):
        return open_cycle
    archived = [
        c
        for p in sorted((vault / "bitacoras").glob("bitacora-*.md"))
        if (c := _read(archivo.leer(p), is_open=False))
    ]
    return max(archived, key=lambda c: c.end, default=None)


def deduce_range(name: str, start: date, end: date | None) -> tuple[date, date]:
    """The range of a cycle: the week with `start` for `semana`, else `start` to `end`."""
    if name == SEMANA:
        monday, sunday = calcular_rango_semanal(start)
        if end is not None and end != sunday:
            raise CicloInvalido(
                f"`semana` va de lunes a domingo: el que contiene el {start.isoformat()} "
                f"termina el {sunday.isoformat()}. Quita --to o pasa --to {sunday.isoformat()}."
            )
        return monday, sunday
    if end is None:
        raise CicloInvalido(
            f"el ciclo «{name}» no tiene un rango que se deduzca. Pasa --to FECHA, "
            "el último día del ciclo (el autor lo dice)."
        )
    if end < start:
        raise CicloInvalido(
            f"--to {end.isoformat()} es anterior a --from {start.isoformat()}. "
            "El ciclo termina el mismo día que empieza o después."
        )
    return start, end


def next_name(names: tuple[str, ...], previous: str | None) -> str:
    """The cycle after `previous` in `reglas/ciclo.user.md`, wrapping around at the end."""
    if previous in names:
        return names[(names.index(previous) + 1) % len(names)]
    return names[0]


def _contiguity(previous: Cycle, start: date) -> str | None:
    expected = previous.end + timedelta(days=1)
    if start == expected:
        return None
    effect = (
        "dejaría días sin ciclo" if start > expected else "pisaría días que otro ciclo ya cubre"
    )
    return (
        f"el ciclo anterior termina el {previous.end.isoformat()}: el siguiente empieza el "
        f"{expected.isoformat()} y {start.isoformat()} {effect}. "
        f"Repite con --from {expected.isoformat()}."
    )


def _write_open(vault: Path, start: date, end: date, name: str) -> Path:
    path = vault / "AHORA.md"
    archivo.escribir(path, instantiate(resolver_plantilla(vault), start, end, name))
    return path


def _save_past(vault: Path, start: date, end: date | None, name: str | None) -> Resultado:
    """A cycle before the open one goes to `bitacoras/` unchecked: it is history."""
    if name is None:
        return Resultado.rechazo(
            f"el {start.isoformat()} es anterior al ciclo abierto: se guarda como ciclo "
            "pasado en bitacoras/, y sin ciclo anterior que haga avanzar el nombre hay que "
            "darlo. Repite con --name NOMBRE."
        )
    first, last = deduce_range(name, start, end)
    path = vault / "bitacoras" / f"bitacora-{first.isoformat()}-{last.isoformat()}-{name}.md"
    if path.exists():
        return Resultado.hecho(f"{path} ya existe: no se toca.")
    path.parent.mkdir(exist_ok=True)
    archivo.escribir(
        path, instantiate(resolver_plantilla(vault), first, last, name, status="stable")
    )
    return Resultado.hecho(
        f"ciclo pasado guardado en {path}. No se verificó contra los ciclos vecinos: "
        "`tuku doctor cycle` reporta los hoyos y solapes que queden."
    )


def abrir_en_vault(
    vault: Path,
    *,
    desde: date | None = None,
    hasta: date | None = None,
    nombre: str | None = None,
    force: bool = False,
    now: datetime,
) -> Resultado:
    """Opens the next cycle, repeats the open one, or saves a past one (`spec/ciclo.md`).

    Without `desde` the cycle starts the day after the previous one ends (the open
    `AHORA.md` or, once archived, the latest logbook) and, with no previous, today.
    """
    names = leer_config(vault).nombres_de_ciclo
    if nombre is not None and nombre not in names and not force:
        return Resultado.rechazo(
            f"«{nombre}» no está en la tabla de ciclos ({', '.join(names)}). Confírmalo con el "
            "autor y repite con --force, o agrégalo a la tabla de reglas/ciclo.user.md."
        )
    try:
        return _open(vault, names, desde, hasta, nombre, now)
    except CicloInvalido as e:
        return Resultado.rechazo(str(e))


def _open(
    vault: Path,
    names: tuple[str, ...],
    desde: date | None,
    hasta: date | None,
    nombre: str | None,
    now: datetime,
) -> Resultado:
    previous = previous_cycle(vault)
    asked = desde or (previous.end + timedelta(days=1) if previous else now.date())
    if previous is not None and desde is not None and desde < previous.start:
        return _save_past(vault, desde, hasta, nombre)

    repeat: tuple[date, date, str] | None = None
    if previous is not None and previous.is_open:
        name = nombre or previous.name
        if name == SEMANA:
            monday, _ = calcular_rango_semanal(asked)
            span = deduce_range(name, asked, hasta) if monday == previous.start else None
        elif asked == previous.start:
            span = deduce_range(name, asked, hasta or previous.end)
        else:
            span = None
        if span is not None and span[0] == previous.start:
            repeat = (span[0], span[1], name)

    if repeat is not None and previous is not None:
        start, end, name = repeat
        if (start, end, name) == (previous.start, previous.end, previous.name):
            return Resultado.hecho("AHORA.md ya cubre la fecha requerida.")
        if previous.has_records:
            return Resultado.rechazo(
                f"el ciclo abierto tiene registros y no se regenera con otro rango u otro "
                f"nombre. Ciérralo antes: {como_cerrar(previous.start, previous.end)}, "
                "y vuelve a correr esto."
            )
        path = _write_open(vault, start, end, name)
        return _opened(vault, path, start, asked, now)

    name = nombre or next_name(names, previous.name if previous else None)
    start, end = deduce_range(name, asked, hasta)
    if previous is not None:
        if problem := _contiguity(previous, start):
            return Resultado.rechazo(problem)
        if previous.is_open and previous.has_records:
            return Resultado.rechazo(
                f"hay un ciclo abierto con registros ({previous.start.isoformat()} a "
                f"{previous.end.isoformat()}) y el siguiente empieza el {start.isoformat()}. "
                f"Ciérralo antes: {como_cerrar(previous.start, previous.end)}, "
                "y vuelve a correr esto."
            )
    path = _write_open(vault, start, end, name)
    return _opened(vault, path, start, asked, now)


def _opened(vault: Path, path: Path, start: date, asked: date, now: datetime) -> Resultado:
    from tuku import todo

    message = f"ciclo abierto en {path}."
    if not hay_bitacora_anterior(vault):
        return Resultado.hecho(message)
    opening = todo.abrir_en_vault(
        vault, body=REVISAR_BITACORA, due=start.isoformat(), day=asked, now=now
    )
    if not opening.ok:
        return Resultado.hecho(
            message, avisos=(f"no se abrió «{REVISAR_BITACORA}»: {opening.mensaje}",)
        )
    return Resultado.hecho(f"{message}\n{opening.mensaje}", avisos=opening.avisos)
