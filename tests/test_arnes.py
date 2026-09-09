"""Que el instrumento mida, comprobado antes de medir con él.

Un escenario agéntico cuesta tokens y minutos, y cuando falla no distingue solo
con mirarlo entre un agente que se equivocó y un arnés roto. Este archivo separa
esa pregunta y la contesta gratis: **sin invocar ningún modelo**, comprueba las
propiedades del arnés de las que depende cualquier afirmación del epic 003.

Las tres salieron de fallos reales, no de una lista escrita de antemano. Las dos
primeras están en el método del [`003-00`](escenarios/003-00-el-dia-uno-dictado.md).
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))

import agente
import vault

#: Sembrar el vault con el CLI del checkout, sin depender de que TUKU esté
#: instalado en la máquina que corre la suite. Es lo mismo que hace el shim.
_ARRANQUE = "import sys; from tuku.cli import main; sys.exit(main(sys.argv[1:]))"


def _sembrar(v: Path) -> None:
    subprocess.run(
        [sys.executable, "-c", _ARRANQUE, "init", str(v), "--date", "2026-08-11"],
        env={**os.environ, "TUKU_HOME": str(vault.RAIZ_REPO)},
        check=True,
        capture_output=True,
    )


def test_el_banco_esta_fuera_del_repo_y_sin_nada_heredable_encima() -> None:
    """Requisito 1 del método, comprobado en vez de supuesto.

    Un vault de prueba dentro del checkout hereda el árbol de arriba, y un agente
    que resuelve su proyecto por repositorio y no por `cwd` escribe en otra parte:
    `agy --sandbox` ejecutaba el comando correcto y el vault quedaba intacto.
    """
    assert vault.RAIZ_REPO not in vault.BANCO.resolve().parents
    vault.exigir_banco_limpio()


def test_el_shim_escribe_en_el_vault_con_el_entorno_que_recibe_el_agente() -> None:
    """Requisitos 2 y 3: el turno no hereda al runner, y no depende del `PATH`.

    Es la prueba barata de que un `tuku` invocado como lo invoca el agente (por
    nombre, con el entorno limpio, desde el vault) escribe **y persiste**. Cubre
    de una vez el filtrado de entorno, el intérprete escrito del shim y el vault
    fuera del repo; lo único que no cubre es el modelo, que es lo caro.
    """
    with tempfile.TemporaryDirectory(dir=vault.BANCO, prefix="arnes-") as caja:
        v = Path(caja) / "mi-vault"
        _sembrar(v)
        with tempfile.TemporaryDirectory(prefix="tuku-shim-") as tmp:
            bin = Path(tmp)
            traza = agente._sembrar_shim(bin)
            entorno = {
                **{k: x for k, x in os.environ.items() if k not in agente.DEL_RUNNER},
                "PATH": f"{bin}{os.pathsep}{agente._path_sin_venv()}",
                "TUKU_TRAZA": str(traza),
                "TUKU_HOME": str(vault.RAIZ_REPO),
            }
            p = subprocess.run(
                [
                    "tuku",
                    "entry",
                    "add",
                    "--day",
                    "2026-08-11",
                    "--hour",
                    "09:12",
                    "--scope",
                    "personal",
                    "--body",
                    "**señal**: el arnés mide",
                ],
                cwd=v,
                env=entorno,
                capture_output=True,
                text=True,
            )
            assert p.returncode == 0, p.stderr
            assert traza.is_file(), "el shim no anotó: el agente no pasaría por él"
        escrito = (v / "AHORA.md").read_text(encoding="utf-8")
        assert "el arnés mide" in escrito, "el comando salió 0 y no persistió"


def test_todo_arnes_declara_como_se_aisla() -> None:
    """Requisito 1, otra vez, del lado de la configuración.

    Un arnés con `aislar` vacío no está aislado, y el escenario que corra con él
    va a medir la máquina. Vale más que falte el arnés a que exista mintiendo.
    """
    sin_aislar = [n for n, c in agente.ARNESES.items() if not c.get("aislar")]
    assert not sin_aislar, f"arneses sin aislamiento declarado: {sin_aislar}"


@pytest.mark.agentic
def test_el_agente_configurado_escribe_de_verdad() -> None:
    """Un turno de una frase, para saber si el instrumento sirve hoy.

    Es agéntico y por eso no entra en la suite normal, pero es el turno más
    barato que existe: cuando la cadena del 003 falla entera, correr esto
    primero dice en medio minuto si el problema es el arnés o el `AGENTS.md`.
    """
    motivo = agente.motivo_no_disponible()
    if motivo is not None:
        pytest.skip(motivo)
    with tempfile.TemporaryDirectory(dir=vault.BANCO, prefix="arnes-") as caja:
        v = Path(caja) / "mi-vault"
        _sembrar(v)
        turno = agente.turno(v, "A las nueve y doce ordené los cables del escritorio.")
        assert turno.comandos, f"el agente no pasó por el shim. Dijo: {turno.stdout[:400]}"
        assert "09:12" in (v / "AHORA.md").read_text(encoding="utf-8"), (
            f"el agente ejecutó {turno.comandos} y el vault no cambió: el arnés no persiste"
        )
