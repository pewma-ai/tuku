"""Tests del escenario 002-10-cli-superficie.

`tuku -h` nombra los sustantivos, cada sustantivo lista sus verbos y uno sin
verbo es error de uso.

Ejecutable directo: `python3 tests/escenarios/test_002_10_cli_superficie.py`
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import gherkin  # noqa: E402

from tuku.cli import EXITO, USO  # noqa: E402

SLUG = "002-10-cli-superficie"

#: Cada noun del CLI con los verbs que su ayuda tiene que nombrar.
VERBS = {
    "entry": ("add", "rename", "lint"),
    "vocab": ("show",),
    "cycle": ("open", "lint"),
    "style": ("lint",),
    "todo": ("open", "close", "lint"),
    "scope": ("create", "rename", "lint"),
    "note": ("create", "rename", "lint"),
}


def test_002_10_tuku_h_nombra_los_nouns_del_epic() -> None:
    corrida = gherkin.correr(SLUG, "nombra los nouns del epic")
    assert corrida.codigo == EXITO, corrida.stderr
    for noun in ("init", "doctor", "fix", "rebuild", *VERBS):
        assert noun in corrida.stdout, f"`tuku -h` no nombra {noun}"


def test_002_10_cada_noun_lista_sus_verbs() -> None:
    corrida = gherkin.correr(SLUG, "cada noun lista sus verbs")

    for noun, verbs in VERBS.items():
        ayuda = corrida.de(f"tuku {noun} -h")
        assert ayuda.codigo == EXITO, ayuda.stderr
        for verb in verbs:
            assert verb in ayuda.stdout, f"`tuku {noun} -h` no nombra {verb}"

    add = corrida.de("entry add -h")
    for pieza in ("--body", "--scope", "--day", "--hour"):
        assert pieza in add.stdout, f"`tuku entry add -h` no nombra {pieza}"

    rename = corrida.de("entry rename -h")
    for pieza in ("--body", "--day", "--hour"):
        assert pieza in rename.stdout, f"`tuku entry rename -h` no nombra {pieza}"


def test_002_10_un_noun_sin_verb_es_error_de_uso() -> None:
    corrida = gherkin.correr(SLUG, "un noun sin verb es error de uso")
    assert corrida.codigo == USO, "un noun sin verb debería ser error de uso, no rechazo"


if __name__ == "__main__":
    test_002_10_tuku_h_nombra_los_nouns_del_epic()
    test_002_10_cada_noun_lista_sus_verbs()
    test_002_10_un_noun_sin_verb_es_error_de_uso()
    print("ok: la superficie del CLI del epic 002 está fijada")
