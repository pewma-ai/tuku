"""`DEVEL.md`: lo que nombra existe (archivos, enlaces y comandos)."""

from __future__ import annotations

import re
from pathlib import Path

from tuku.cli import manual

RAIZ = Path(__file__).resolve().parents[2]
DEVEL = (RAIZ / "DEVEL.md").read_text(encoding="utf-8")


def test_lo_que_devel_nombra_existe() -> None:
    enlaces = re.findall(r"\]\(([^)#]+)[^)]*\)", DEVEL)
    comandos = set(re.findall(r"`(tuku [a-z]+(?: [a-z]+)?)`", DEVEL))
    cli = manual.del_cli()
    faltan = [e for e in enlaces if "://" not in e and not (RAIZ / e).exists()]
    faltan += [c for c in sorted(comandos) if c not in cli]
    assert any(f.startswith("| `PENDIENTES.md`") for f in DEVEL.splitlines())
    assert not faltan, faltan
