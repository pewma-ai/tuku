"""Los ejemplos de la ayuda: cada uno es una invocación válida y llega a `comandos.tuku.md`."""

from __future__ import annotations

import shlex

from tuku import cli
from tuku.cli import manual
from tuku.cli.ejemplos import EJEMPLOS


def test_cada_ejemplo_es_una_invocacion_valida() -> None:
    parser = cli._construir_parser()
    for comando, lista in EJEMPLOS.items():
        for ejemplo in lista:
            argv = shlex.split(ejemplo)
            assert argv[0] == "tuku" and " ".join(argv[1:]).startswith(comando), ejemplo
            try:
                parser.parse_args(argv[1:])
            except SystemExit as e:
                raise AssertionError(
                    f"el ejemplo no es una invocación válida: {ejemplo}"
                ) from e


def test_los_comandos_de_la_tabla_existen_en_el_cli() -> None:
    assert not [c for c in EJEMPLOS if c not in cli.comandos()]


def test_los_ejemplos_llegan_al_documento_derivado() -> None:
    documento = manual.del_cli()
    assert '```bash\ntuku todo close "pagar la patente"\n```' in documento
    assert "tuku context entry --since 7" in documento
