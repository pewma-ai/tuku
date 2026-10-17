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
import uuid
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))

import agente
import gherkin
import vault

#: Sembrar el vault con el CLI del checkout, sin depender de que TUKU esté
#: instalado en la máquina que corre la suite. Es lo mismo que hace el shim.
_ARRANQUE = "import sys; from tuku.cli import main; sys.exit(main(sys.argv[1:]))"


def _sembrar(v: Path) -> None:
    subprocess.run(
        [sys.executable, "-c", _ARRANQUE, "init", str(v), "--at", "2026-08-11"],
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
            with agente.Puente(bin, {**entorno, "PATH": os.environ["PATH"]}):
                p = subprocess.run(
                    [
                        "tuku",
                        "entry",
                        "add",
                        "--at",
                        "2026-08-11 09:12",
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


def test_el_modelo_barato_de_agy_es_flash_en_esfuerzo_bajo(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    lista = (
        "Fetching available models...\n"
        "gemini-4-argon-medium\tGemini 4 Argon (Medium)\n"
        "gemini-4-argon-low\tGemini 4 Argon (Low)\n"
        "gemini-3.8-flash-high\tGemini 3.8 Flash (High)\n"
        "gemini-3.8-flash-low\tGemini 3.8 Flash (Low)\n"
        "claude-opus-5-5-low\tClaude Opus 5.5 (Low)\n"
        "gpt-oss-120b-medium\tGPT-OSS 120B (Medium)\n"
    )
    monkeypatch.setattr(agente, "_MODELOS", {})
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *a, **k: subprocess.CompletedProcess(a, 0, stdout=lista, stderr=""),
    )
    assert agente.modelo_barato("agy", "agy") == "gemini-3.8-flash-low"


@pytest.mark.parametrize(
    ("titulo", "prepara"),
    [("preparar el ambiente del epic", True), ("el vault de partida", False)],
)
def test_el_00_solo_prepara_el_epic_si_su_escenario_lo_dice(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, titulo: str, prepara: bool
) -> None:
    (tmp_path / "999-00-prueba.md").write_text(
        f"# Epic 999\n\n## Escenario: {titulo}\n\nCuando se corre\n```bash\ntrue\n```\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(gherkin, "ESCENARIOS", tmp_path)
    assert (gherkin._escenario_de_preparacion("999") is not None) is prepara


def _agy() -> agente.Arnes:
    return agente.Arnes(nombre="agy", ejecutable="agy", modelo="m")


def test_un_turno_sin_sesion_no_pide_json_ni_conversacion() -> None:
    argv = _agy().argv("hola")
    assert "--output-format" not in argv
    assert "--conversation" not in argv


def test_el_primer_turno_de_una_sesion_pide_json() -> None:
    argv = _agy().argv("hola", agente.Sesion())
    assert argv[argv.index("--output-format") + 1] == "stream-json"
    assert "--conversation" not in argv


def test_los_turnos_siguientes_retoman_la_conversacion_por_id() -> None:
    argv = _agy().argv("hola", agente.Sesion("abc"))
    assert argv[argv.index("--conversation") + 1] == "abc"


def test_un_arnes_que_no_sabe_continuar_lo_dice() -> None:
    hermes = agente.Arnes(nombre="hermes", ejecutable="hermes", modelo="m")
    with pytest.raises(agente.ArnesNoDisponible, match="hermes"):
        hermes.argv("hola", agente.Sesion())


def test_la_respuesta_json_deja_el_id_en_la_sesion() -> None:
    sesion = agente.Sesion()
    texto = agente.leer_sesion('{"conversation_id": "abc", "response": "ok\\n"}', sesion)
    assert (texto, sesion.id) == ("ok\n", "abc")


STREAM = "\n".join(
    [
        '{"event":"init","conversation_id":"abc"}',
        '{"event":"step_update","step_update":{"step_index":1,"state":"DONE","step_type":"agent_response",'
        '"duration_seconds":3.5,"usage":{"input_tokens":14526,"output_tokens":57}}}',
        '{"event":"step_update","step_update":{"step_index":2,"state":"ACTIVE","step_type":"tool","tool_name":"view_file"}}',
        '{"event":"step_update","step_update":{"step_index":2,"state":"DONE","step_type":"tool","tool_name":"view_file",'
        '"duration_seconds":0.5,"tool_info":{"parameters":{"AbsolutePath":"/v/AHORA.md"}}}}',
        '{"event":"result","result":{"conversation_id":"abc","response":"Listo.","duration_seconds":4.2}}',
    ]
)


def test_el_turno_lleva_la_fecha_simulada_delante() -> None:
    assert (
        agente.con_reloj("Pagué.", "2026-08-12 21:00") == "(Hoy es 2026-08-12 21:00.)\nPagué."
    )
    assert agente.con_reloj("Pagué.", None) == "Pagué."


def test_el_stream_deja_la_respuesta_y_el_id_de_la_sesion() -> None:
    sesion = agente.Sesion()
    assert agente.leer_sesion(STREAM, sesion) == "Listo."
    assert sesion.id == "abc"


def test_los_pasos_cuentan_cada_llamada_con_lo_que_tardo() -> None:
    pasos = agente.pasos_de(STREAM).splitlines()
    assert pasos[0].endswith("3.5 s  modelo (14526 tokens de entrada, 57 de salida)")
    assert pasos[1].endswith("0.5 s  view_file /v/AHORA.md")
    assert pasos[2] == "total 4.2 s, 2 pasos"
    assert agente.pasos_de("texto plano") == ""


def test_una_salida_que_no_es_json_se_devuelve_tal_cual() -> None:
    sesion = agente.Sesion()
    assert agente.leer_sesion("hola", sesion) == "hola"
    assert sesion.id is None


@pytest.mark.agentic
def test_la_sesion_continua_entre_turnos() -> None:
    """El segundo turno retoma la conversación del primero, con el mismo id."""
    motivo = agente.motivo_no_disponible()
    if motivo is not None:
        pytest.skip(motivo)
    palabra = uuid.uuid4().hex[:8]
    with tempfile.TemporaryDirectory(dir=vault.BANCO, prefix="arnes-") as caja:
        v = Path(caja) / "mi-vault"
        _sembrar(v)
        sesion = agente.Sesion()
        agente.turno(v, f"La palabra clave es {palabra}. Responde solo: ok", sesion=sesion)
        primero = sesion.id
        assert primero, "el primer turno no devolvió el id de la conversación"
        segundo = agente.turno(
            v, "¿Cuál era la palabra clave? Responde solo la palabra.", sesion=sesion
        )
        assert sesion.id == primero, "el segundo turno abrió otra conversación"
        assert palabra in segundo.stdout


def test_la_ayuda_abreviada_no_cuenta_como_traduccion() -> None:
    traza = [["note", "create", "--h"], ["note", "create", "x"], ["todo", "open", "--help"]]
    turno = agente.Turno(prompt="", codigo=0, stdout="", stderr="", traza=traza)
    assert turno.traduccion == ["note create"]


def test_la_traduccion_cuenta_todo_lo_que_no_es_lectura() -> None:
    traza = [
        ["doctor"],
        ["scope", "lint"],
        ["vocab", "show"],
        ["scope", "create", "faena"],
        ["scope", "move", "faena-ai", "--parent", "faena"],
        ["entry", "rename", "--body", "x"],
        ["regenerate", "todo"],
    ]
    turno = agente.Turno(prompt="", codigo=0, stdout="", stderr="", traza=traza)
    assert turno.traduccion == [
        "scope create",
        "scope move",
        "entry rename",
        "regenerate",
    ]
