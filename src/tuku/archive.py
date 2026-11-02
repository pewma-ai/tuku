"""Self-archiving of `AHORA.md` into weekly logbooks.

`AHORA.md` keeps the last `archive_weeks` full weeks counted from Monday: with 2,
from the Monday of the previous week up to today (a Monday has 8 days, a Sunday
14). Every day before that window leaves for `bitacoras/bitacora-AAAAMMDD-AAAAMMDD.md`
(Monday to Sunday), and only its records travel: the focus and the pending
callouts are derived or the author's, and are dropped.

`plan_archive` is a pure planner over text: it receives `AHORA.md`, the logbooks
already in `bitacoras/` and the day of the command's `now`, and returns the
`Change` that moves what fell out of the window. Running it on its own result
yields an empty `Change`. `archivar_en_vault` is the use case every command that
writes calls first; one that only reads (`context`, `doctor`) never does.

`AHORA.md` declares no range: its day headings take the year nearest to `today`. A vault
sown with cycles still carries `cycle`, `from` and `to` there; the first plan that writes
drops them.

`stamp` is the other half: a record dated before the window goes straight to the
logbook of its week, created if missing, instead of `AHORA.md`.

**Qué lee y escribe:** lee `AHORA.md`, `bitacoras/` y `reglas/config.tuku.md`;
escribe `AHORA.md` y las bitácoras semanales que reciben días.
**A mano:** mover cada `## <día>` anterior a la ventana a la bitácora de su semana
(`bitacoras/bitacora-AAAAMMDD-AAAAMMDD.md`, con `type: Logbook`, `status: stable`,
`from` y `to`), dejar solo sus registros con los días del más nuevo al más viejo y
recalcular las rutas de sus links desde `bitacoras/`.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from tuku import archivo, link
from tuku.ahora import dias, encabezado_de, insertar_dia, rango
from tuku.config import SEMANAS_POR_DEFECTO, semanas_de_archivo
from tuku.plan import Change, apply
from tuku.resultado import Resultado

#: The name of a weekly logbook, relative to the vault.
_NOMBRE = re.compile(r"^bitacoras/bitacora-(\d{8})-(\d{8})\.md$")
#: The frontmatter fields of an `AHORA.md` sown with cycles, which no longer exist.
_CAMPOS_DEL_CICLO = re.compile(r"^(cycle|from|to):")
#: A line of the old derived region (`- [ambito](ruta) - detalle`): not a record.
_REGION = re.compile(rf"^- {link.ENLACE} - ")


def week_of(day: date) -> tuple[date, date]:
    """The Monday and the Sunday of the week that contains `day`."""
    monday = day - timedelta(days=day.weekday())
    return monday, monday + timedelta(days=6)


def window_start(today: date, weeks: int = SEMANAS_POR_DEFECTO) -> date:
    """The first day `AHORA.md` keeps: the Monday `weeks - 1` weeks before this one."""
    return week_of(today)[0] - timedelta(weeks=weeks - 1)


def logbook_path(monday: date, sunday: date) -> str:
    """`bitacoras/bitacora-20261019-20261025.md`, relative to the vault."""
    return f"bitacoras/bitacora-{monday:%Y%m%d}-{sunday:%Y%m%d}.md"


def new_logbook(monday: date, sunday: date) -> str:
    """The text of an empty weekly logbook."""
    return (
        "---\n"
        "type: Logbook\n"
        "status: stable\n"
        f"from: {monday.isoformat()}\n"
        f"to: {sunday.isoformat()}\n"
        "---\n"
        "# Actividad diaria\n"
    )


def read_history(vault: Path) -> dict[str, str]:
    """Every logbook of `bitacoras/` (both name styles), by path relative to the vault."""
    carpeta = vault / "bitacoras"
    if not carpeta.is_dir():
        return {}
    return {
        p.relative_to(vault).as_posix(): archivo.leer(p) for p in sorted(carpeta.glob("*.md"))
    }


def covering(history: Mapping[str, str], day: date) -> str | None:
    """The path of the logbook whose `from`-`to` contains `day`, whatever its name."""
    for path in sorted(history):
        limits = rango(history[path])
        if limits is not None and limits[0] <= day <= limits[1]:
            return path
    return None


def destination(history: Mapping[str, str], day: date) -> tuple[str, str]:
    """Where the records of `day` live: the logbook that covers it, or the weekly one.

    Returns the path and its text, which is a new empty logbook if the file does not exist.
    """
    path = covering(history, day)
    if path is not None:
        return path, history[path]
    monday, sunday = week_of(day)
    path = logbook_path(monday, sunday)
    return path, history.get(path) or new_logbook(monday, sunday)


def _fin_de_seccion(lineas: list[str], ini: int) -> int:
    return next(
        (
            i
            for i in range(ini + 1, len(lineas))
            if lineas[i].startswith("## ") or lineas[i].strip() == "---"
        ),
        len(lineas),
    )


def _sin_blancos_dobles(lineas: list[str]) -> list[str]:
    """`lineas` without two blank lines in a row."""
    salida: list[str] = []
    for x in lineas:
        if x.strip() or (salida and salida[-1].strip()):
            salida.append(x)
    return salida


def _registros_de(lineas: list[str]) -> list[str]:
    """The record lines of a day section: from the first record on, trailing blanks out."""
    corte = next(
        (i for i, x in enumerate(lineas) if x.startswith("- ") and not _REGION.match(x)),
        len(lineas),
    )
    registros = lineas[corte:]
    while registros and not registros[-1].strip():
        registros.pop()
    return registros


def _fusionar_dia(texto: str, fecha: date, registros: list[str]) -> str:
    """`texto` (a logbook) with `registros` under the day `fecha`, none repeated.

    A day the logbook does not have is written as it comes, keeping the order of its
    records; one it already has gets the missing records by hour (`entry.add`).
    """
    from tuku import entry

    encabezado = encabezado_de(fecha)
    lineas = texto.splitlines()
    if any(x.strip() == encabezado for x in lineas):
        return entry.add(texto, registros, day=encabezado, fecha=fecha)
    limites = rango(texto)
    if limites is None:
        raise ValueError("la bitácora no tiene `from` y `to` resueltos")
    lineas, ini = insertar_dia(lineas, fecha, limites)
    lineas[ini + 2 : ini + 2] = [*registros, ""]
    salida = "\n".join(lineas)
    return salida if salida.endswith("\n") else salida + "\n"


def without_cycle(ahora: str) -> str:
    """`ahora` without `cycle`, `from` and `to` in its frontmatter."""
    lineas = ahora.splitlines(keepends=True)
    if not lineas or lineas[0].strip() != "---":
        return ahora
    fin = next((i for i in range(1, len(lineas)) if lineas[i].strip() == "---"), None)
    if fin is None:
        return ahora
    return "".join(
        x for i, x in enumerate(lineas) if not (0 < i < fin and _CAMPOS_DEL_CICLO.match(x))
    )


def plan_archive(
    logbook: str,
    history: Mapping[str, str],
    *,
    today: date,
    weeks: int = SEMANAS_POR_DEFECTO,
) -> Change:
    """The change that moves the days of `logbook` before the window to their logbooks.

    `history` holds the logbooks already in `bitacoras/`. A day whose week has a
    logbook is added to it; otherwise the weekly logbook is created. The links of each
    record are recalculated for the new folder. The `Change` is empty when nothing
    falls out and `AHORA.md` carries no leftover of the cycles.
    """
    vacio = Change({}, "")
    original = logbook
    logbook = without_cycle(logbook)
    inicio = window_start(today, weeks)
    lineas = logbook.splitlines()
    work = dict(history)
    files: dict[str, str] = {}
    n = 0
    antiguos = [
        (ini, fecha) for ini, _, fecha in dias(logbook, today) if fecha and fecha < inicio
    ]
    for ini, fecha in reversed(antiguos):
        fin = _fin_de_seccion(lineas, ini)
        registros = _registros_de(lineas[ini + 1 : fin])
        if registros:
            path, texto = destination(work, fecha)
            movidos = [link.rebasar(x, "AHORA.md", path) for x in registros]
            work[path] = files[path] = _fusionar_dia(texto, fecha, movidos)
            n += len(registros)
        del lineas[ini:fin]
    if antiguos:
        lineas = _sin_blancos_dobles(lineas)
    if not antiguos and logbook == original:
        return vacio
    texto = "\n".join(lineas)
    if logbook.endswith("\n") and not texto.endswith("\n"):
        texto += "\n"
    if texto == original:
        return vacio
    ordenados = {"AHORA.md": texto, **dict(sorted(files.items()))}
    return Change(
        ordenados,
        f"archivados {n} registro(s) de AHORA.md en bitacoras/." if n else "",
        regenerate=("AHORA.md", "bitacoras/"),
    )


def archivar_en_vault(vault: Path, today: date) -> None:
    """Archives what fell out of the window; every command that writes calls it first.

    Idempotent: with nothing out of the window it writes nothing.
    """
    ruta = vault / "AHORA.md"
    if not ruta.is_file():
        return
    plan = plan_archive(
        archivo.leer(ruta), read_history(vault), today=today, weeks=semanas_de_archivo(vault)
    )
    if plan.files:
        apply(vault, plan, today=today)


@dataclass(frozen=True)
class Placement:
    """Where `stamp` put the records: the text of `AHORA.md` and any logbook that changed."""

    logbook: str
    extra: Mapping[str, str]


def stamp(
    logbook: str,
    history: Mapping[str, str],
    lines: list[str],
    *,
    day: date,
    today: date,
    weeks: int = SEMANAS_POR_DEFECTO,
) -> Placement | Resultado:
    """`lines` under `day`: in `AHORA.md`, or in the logbook of its week if before the window.

    A day after `today` is rejected. The lines come composed for `AHORA.md`; going to
    a logbook their links are recalculated.
    """
    from tuku import entry

    if day > today:
        return Resultado.rechazo(
            f"el {day.isoformat()} todavía no llega: un registro cuenta lo que ya pasó. "
            "Corrige la fecha de --at."
        )
    if day >= window_start(today, weeks):
        stamped = entry.stamp(logbook, lines, day=day)
        if isinstance(stamped, Resultado):
            return stamped
        return Placement(stamped, {})
    if not lines:
        return Placement(logbook, {})
    path, texto = destination(history, day)
    try:
        nuevo = entry.add(
            texto,
            [link.rebasar(x, "AHORA.md", path) for x in lines],
            day=encabezado_de(day),
            fecha=day,
        )
    except ValueError as e:
        return Resultado.rechazo(f"{path}: {e}")
    return Placement(logbook, {path: nuevo})


def text_for(
    logbook: str, history: Mapping[str, str], *, day: date, today: date, weeks: int
) -> str:
    """The text where a record of `day` would be written: `AHORA.md` or its logbook."""
    if day >= window_start(today, weeks):
        return logbook
    return destination(history, day)[1]


def lint_history(history: Mapping[str, str]) -> list[str]:
    """Findings of the weekly logbooks whose `from` and `to` disagree with their name."""
    hallazgos: list[str] = []
    for path in sorted(history):
        m = _NOMBRE.match(path)
        if m is None:
            continue
        esperado = (
            date.fromisoformat(f"{m.group(1)[:4]}-{m.group(1)[4:6]}-{m.group(1)[6:]}"),
            date.fromisoformat(f"{m.group(2)[:4]}-{m.group(2)[4:6]}-{m.group(2)[6:]}"),
        )
        limites = rango(history[path])
        if limites != esperado:
            dice = (
                f"dice {limites[0].isoformat()} a {limites[1].isoformat()}"
                if limites
                else "no tiene `from` y `to` resueltos"
            )
            hallazgos.append(
                f"{path}: error: el nombre pide {esperado[0].isoformat()} a "
                f"{esperado[1].isoformat()} y el frontmatter {dice}. Corrige `from` y `to`, "
                "o renombra el archivo."
            )
    return hallazgos


def lint_window(ahora: str, *, today: date, weeks: int) -> list[str]:
    """Warnings for days of `AHORA.md` before the window; a writing command archives them."""
    inicio = window_start(today, weeks)
    fechas = (fecha for _, _, fecha in dias(ahora, today))
    fuera = [fecha for fecha in fechas if fecha is not None and fecha < inicio]
    return [
        f"AHORA.md: aviso: el día {fecha.isoformat()} es anterior a la ventana de "
        f"{weeks} semana(s) (desde el {inicio.isoformat()}). Cualquier comando que escribe "
        "lo archiva en bitacoras/."
        for fecha in fuera
    ]


def lint_legacy(ahora: str, *, ciclo_user_md: bool) -> list[str]:
    """Warnings for what a vault sown with cycles still carries; commands ignore it."""
    hallazgos: list[str] = []
    if without_cycle(ahora) != ahora:
        hallazgos.append(
            "AHORA.md: aviso: el frontmatter trae `cycle`, `from` o `to` de los ciclos, que "
            "ya no existen y se ignoran. El primer comando que escribe los quita."
        )
    if ciclo_user_md:
        hallazgos.append(
            "reglas/ciclo.user.md: aviso: los ciclos ya no existen y ningún comando lo lee. "
            "Puedes borrarlo."
        )
    return hallazgos
