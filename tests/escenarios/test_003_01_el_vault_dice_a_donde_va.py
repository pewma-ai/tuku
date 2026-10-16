"""Tests del escenario 003-01-el-vault-dice-a-donde-va.

El `AGENTS.md` sembrado no nombra comandos que no existen en el CLI.

Ejecutable directo: `python3 tests/escenarios/test_003_01_el_vault_dice_a_donde_va.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import gherkin  # noqa: E402

from tuku import doctor  # noqa: E402
from tuku.cli import EXITO, RECHAZO, comandos  # noqa: E402

SLUG = "003-01-el-vault-dice-a-donde-va"


def test_003_01_el_vault_nace_con_su_tabla_y_el_doctor_la_aprueba() -> None:
    revision = gherkin.correr(SLUG, "el vault nace con su tabla").de("tuku doctor")
    assert revision.codigo == EXITO, revision.stdout + revision.stderr
    assert "el vault está sano" in revision.stdout
    assert "dispatch:" in revision.stdout, "el doctor no corrió la revisión de despacho"
    assert "todos existen" in revision.stdout


def test_003_01_la_tabla_sembrada_nombra_comandos_reales() -> None:
    """Lo mismo, sobre `template/vanilla/AGENTS.md` en vivo y sin pasar por el CLI."""
    agents = (RAIZ / "template" / "vanilla" / "AGENTS.md").read_text(encoding="utf-8")
    nombrados = doctor.comandos_de_despacho(agents)
    assert nombrados, "el AGENTS.md del template no nombra ningún comando"
    assert not [c for c in nombrados if c not in comandos()], (
        f"el template nombra comandos que no existen: "
        f"{[c for c in nombrados if c not in comandos()]}"
    )


def test_003_01_un_comando_inventado_es_un_error() -> None:
    corrida = gherkin.correr(SLUG, "un comando que no existe")
    revision = corrida.de("tuku doctor")
    assert revision.codigo == RECHAZO, "un comando inventado tiene que ser rechazo"
    assert "tuku scope crear" in revision.stdout, revision.stdout
    assert "Corrige la tabla" in revision.stdout, "no dice cómo corregirlo"

    agents = corrida.ruta("mi-vault", "AGENTS.md").read_text(encoding="utf-8")
    assert "`tuku scope crear`" in agents, "el doctor no debe reparar lo que encuentra"


def test_003_01_sin_agents_md_no_hay_despacho() -> None:
    corrida = gherkin.correr(SLUG, "sin AGENTS.md")
    revision = corrida.de("tuku doctor")
    assert revision.codigo == RECHAZO
    assert "AGENTS.md" in revision.stdout
    assert corrida.ruta("mi-vault", "AGENTS.md").is_file(), "el escenario tiene que reponerlo"


if __name__ == "__main__":
    test_003_01_el_vault_nace_con_su_tabla_y_el_doctor_la_aprueba()
    test_003_01_la_tabla_sembrada_nombra_comandos_reales()
    test_003_01_un_comando_inventado_es_un_error()
    test_003_01_sin_agents_md_no_hay_despacho()
    print(f"ok: 4 afirmaciones (queda en playground/{SLUG}/)")
