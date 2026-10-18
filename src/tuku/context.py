"""tuku context: lo que el agente necesita para decidir, sin abrir archivos.

Solo lee. Cada tema es el nombre de la cosa (`spec/cli.md`) y sin tema van
todos, en este orden:

| Tema | Qué trae | De dónde |
| --- | --- | --- |
| `entry` | Los registros desde `--since`, bajo su día | `AHORA.md` y las bitácoras que cruza |
| `scope` | Cada ámbito con su ruta y sus keywords | `ambitos/` |
| `todo` | Los pendientes abiertos, atrasados marcados (`--late`: solo esos) | `PENDIENTES.md` |
| `style` | Clasificaciones, horizontes y tipos de nota | `LIBRO-DE-ESTILO.md` |
| `note` | Por cada tipo enlazable, sus últimas notas con nombres y aliases | `notas/` |

`--since` es un número de días o una fecha (`AAAA-MM-DD`), y vale 2 días.

**A mano:** leer los últimos días de `AHORA.md`, las `keywords` de cada página
de `ambitos/`, la tabla de `PENDIENTES.md` y las tablas del libro de estilo.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import date, timedelta
from pathlib import Path

from tuku import archivo
from tuku.resultado import Resultado

TEMAS = ("entry", "scope", "todo", "style", "note")

#: Días hacia atrás que lee `entry` y `note` sin `--since`.
DESDE_POR_DEFECTO = 2


def desde(valor: str | None, hoy: date, por_defecto: int = DESDE_POR_DEFECTO) -> date:
    """`--since`: un número de días hacia atrás desde `hoy`, o una fecha `AAAA-MM-DD`."""
    if valor is None:
        return hoy - timedelta(days=por_defecto)
    texto = valor.strip()
    if texto.isdigit():
        return hoy - timedelta(days=int(texto))
    try:
        return date.fromisoformat(texto)
    except ValueError:
        raise ValueError(
            f"--since {valor!r} no es un número de días ni una fecha AAAA-MM-DD: "
            "pasa --since 7 o --since 2026-08-01"
        ) from None


def _ciclos(vault: Path) -> list[Path]:
    """`AHORA.md` y las bitácoras cerradas, de la más antigua a la más reciente."""
    cerradas = (
        sorted((vault / "bitacoras").glob("*.md")) if (vault / "bitacoras").is_dir() else []
    )
    return [*cerradas, vault / "AHORA.md"]


def registros_desde(vault: Path, inicio: date) -> list[tuple[date, str, list[str]]]:
    """Los días desde `inicio` con sus líneas de registro, de los ciclos que cruza."""
    from tuku.ahora import fecha_del_dia, rango
    from tuku.entry import registros

    dias: list[tuple[date, str, list[str]]] = []
    for ruta in _ciclos(vault):
        if not ruta.is_file():
            continue
        texto = archivo.leer(ruta)
        limites = rango(texto)
        if limites is None or limites[1] < inicio:
            continue
        lineas = texto.splitlines()
        for r in registros(texto):
            fecha = fecha_del_dia(f"## {r.dia}", *limites)
            if fecha is None or fecha < inicio:
                continue
            if not dias or dias[-1][1] != r.dia:
                dias.append((fecha, r.dia, []))
            dias[-1][2].append(lineas[r.linea])
    return dias


def _entry(vault: Path, inicio: date) -> str:
    dias = registros_desde(vault, inicio)
    if not dias:
        return f"sin registros desde el {inicio.isoformat()}."
    return "\n\n".join(f"## {dia}\n" + "\n".join(lineas) for _, dia, lineas in dias)


def _scope(vault: Path) -> str:
    from tuku import scope

    lineas = []
    for a in scope.leer(vault):
        ruta = a.directorio.relative_to(vault / "ambitos").as_posix()
        palabras = f": {', '.join(a.keywords)}" if a.keywords else ""
        lineas.append(f"- {ruta}{palabras}")
    return "\n".join(lineas) or "sin ámbitos."


def _todo(vault: Path, hoy: date, late: bool = False) -> str:
    """Los pendientes abiertos; con `late`, solo los atrasados (`Vence` anterior a `hoy`)."""
    from tuku import todo

    ruta = vault / "PENDIENTES.md"
    if not ruta.is_file():
        return "sin PENDIENTES.md."
    lineas = []
    for f in todo.filas(archivo.leer(ruta)):
        vencido = f.dia is not None and f.dia < hoy
        if late and not vencido:
            continue
        vence = f", vence {f.vence}" if f.vence else ""
        atrasado = ", atrasado" if vencido else ""
        ambito = f" ({f.ambito})" if f.ambito else ""
        lineas.append(f"- {f.horizonte}{vence}{atrasado}: {f.cuerpo}{ambito}")
    return "\n".join(lineas) or (
        "sin pendientes atrasados." if late else "sin pendientes abiertos."
    )


def _style(vault: Path) -> str:
    from tuku import vocab

    return vocab.mostrar_del_vault(vault).mensaje


def _note(vault: Path) -> str:
    """Por cada tipo enlazable, sus últimas notas, de la modificada más recientemente.

    Enlazable es la columna del libro de estilo (`spec/notas.md`): las personas,
    no las ideas. Cada nota trae su título y sus `aliases`, que son los nombres con
    que el autor la menciona, para que el agente decida qué enlazar. El tope por
    tipo es `context_note_limit` de la config, para que el listado no crezca con el vault.
    """
    from tuku import note
    from tuku.config import leer_config, limite_de_notas

    tipos = leer_config(vault).tipos_enlazables
    if not tipos:
        return "sin tipos enlazables en `### Tipos de nota`."
    limite = limite_de_notas(vault)
    dir_notas = vault / "notas"
    rutas = sorted(dir_notas.glob("*.md")) if dir_notas.is_dir() else []
    por_tipo: dict[str, list[tuple[float, Path, str]]] = {t: [] for t in tipos}
    for ruta in rutas:
        texto = archivo.leer(ruta)
        if (tipo := note.subtype(texto)) in por_tipo:
            por_tipo[tipo].append((ruta.stat().st_mtime, ruta, texto))
    bloques = []
    for tipo in tipos:
        ultimas = sorted(por_tipo[tipo], key=lambda n: (-n[0], n[1].name))[:limite]
        lineas = []
        for _, ruta, texto in ultimas:
            otros = note.aliases(texto)
            alias = f"; aliases: {', '.join(otros)}" if otros else ""
            lineas.append(f"- notas/{ruta.name}: {note.titulo(texto, ruta)}{alias}")
        bloques.append(f"## {tipo}\n\n" + ("\n".join(lineas) or "sin notas."))
    return "\n\n".join(bloques)


def del_vault(
    vault: Path,
    tema: str | None = None,
    since: str | None = None,
    hoy: date | None = None,
    *,
    late: bool = False,
) -> Resultado:
    """El contexto del `tema`, o de todos, como texto para leer de una vez."""
    hoy = hoy or date.today()
    try:
        inicio = desde(since, hoy)
    except ValueError as e:
        return Resultado.rechazo(str(e))
    secciones: dict[str, tuple[str, Callable[[], str]]] = {
        "entry": (f"Registros desde el {inicio.isoformat()}", lambda: _entry(vault, inicio)),
        "scope": ("Ámbitos y sus keywords", lambda: _scope(vault)),
        "todo": (
            "Pendientes atrasados" if late else "Pendientes abiertos",
            lambda: _todo(vault, hoy, late),
        ),
        "style": ("Vocabulario del autor", lambda: _style(vault)),
        "note": ("Notas enlazables", lambda: _note(vault)),
    }
    temas = [tema] if tema else list(TEMAS)
    if len(temas) == 1:
        return Resultado.hecho(secciones[temas[0]][1]())
    return Resultado.hecho(
        "\n\n".join(
            f"# {titulo}\n\n{hacer()}" for titulo, hacer in (secciones[t] for t in temas)
        )
    )
