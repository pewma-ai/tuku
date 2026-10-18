"""Decide first, write after: how a use case changes the vault.

A use case has two halves that do not mix. The **planner** is a pure function
`plan_*(state, ...)`: it receives what was read from the vault and the clock
(`now`) and returns a `Change`, or a `Resultado` when it refuses. It touches no
disk, so every rule of the command is tested with text, without a vault.

`apply` is the only executor. It writes the files of the `Change` that differ
from the disk, in order, and hands `regenerate.rehacer` what was touched. The
clock is read once, by `cli.main`, and travels down as `now`.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path

from tuku import archivo
from tuku.resultado import Resultado
from tuku.scope_tree import Tree


@dataclass(frozen=True)
class State:
    """What a planner reads from the vault, read once and before planning.

    `logbook` is `AHORA.md` and `todo` is `PENDIENTES.md`; a use case that does not
    read one leaves it empty. `horizons` are the author's steps (`### Horizontes`)
    and `default_scope` is the config's `scope_default`.
    """

    tree: Tree
    logbook: str = ""
    todo: str = ""
    horizons: tuple[str, ...] = ()
    default_scope: str | None = None


@dataclass(frozen=True)
class Change:
    """What a use case decided, with nothing written yet.

    `files` maps a path relative to the vault to its new text, in the order they
    are written. `regenerate` are the paths `regenerate.rehacer` receives to
    rebuild what depends on them; it runs even if no file changed. `pages` are the
    scopes whose page is rebuilt from `AHORA.md` once the files are written.
    """

    files: Mapping[str, str]
    message: str
    warnings: tuple[str, ...] = ()
    regenerate: tuple[str, ...] = ()
    pages: tuple[str, ...] = ()


def apply(vault: Path, plan: Change | Resultado, *, skip: Iterable[str] = ()) -> Resultado:
    """Carry out a plan: a rejection is returned as is, a `Change` is written.

    Only the files whose text differs from the disk are written, so repeating a
    command leaves no trace. `skip` leaves out a regeneration theme
    (`todo` with `--no-regenerate`).
    """
    from tuku import scope
    from tuku.regenerate import rehacer

    if isinstance(plan, Resultado):
        return plan
    for rel, text in plan.files.items():
        path = vault / rel
        if not path.is_file():
            path.parent.mkdir(parents=True, exist_ok=True)
            archivo.escribir(path, text)
        elif archivo.leer(path) != text:
            archivo.escribir(path, text)
    if plan.regenerate:
        rehacer(vault, plan.regenerate, salvo=skip)
    for name in plan.pages:
        scope.actualizar_pagina(vault, name)
    return Resultado.hecho(plan.message, avisos=plan.warnings)
