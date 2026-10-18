"""Los ejemplos de la ayuda: cada uno es una invocación válida y llega a `comandos.tuku.md`."""

from __future__ import annotations

import shlex

import pytest

from tuku import cli
from tuku.cli import manual
from tuku.cli.ejemplos import EJEMPLOS


@pytest.mark.parametrize(
    ("comando", "ejemplo"), [(c, e) for c, lista in EJEMPLOS.items() for e in lista]
)
def test_cada_ejemplo_es_una_invocacion_valida(comando: str, ejemplo: str) -> None:
    argv = shlex.split(ejemplo)
    assert argv[0] == "tuku" and " ".join(argv[1:]).startswith(comando)
    cli._construir_parser().parse_args(argv[1:])


def test_los_comandos_de_la_tabla_existen_en_el_cli() -> None:
    assert not [c for c in EJEMPLOS if c not in cli.comandos()]


def test_los_ejemplos_llegan_al_documento_derivado() -> None:
    documento = manual.del_cli()
    assert '```bash\ntuku todo close "pagar la patente"\n```' in documento
    assert "tuku context entry --since 7" in documento
