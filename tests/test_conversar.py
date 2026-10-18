"""El ayudante de la conversación a mano, sin invocar ningún modelo."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))

import agente
import conversar
import gherkin

from tuku import init
from tuku.cli import EXITO, main

RAIZ_REPO = Path(__file__).resolve().parent.parent


def _turno_falso(traza: list[list[str]], stdout: str) -> agente.Turno:
    return agente.Turno(prompt="", codigo=0, stdout=stdout, stderr="", traza=traza)


def _turno(traza: list[list[str]], stdout: str = "listo") -> agente.Turno:
    return agente.Turno(prompt="", codigo=0, stdout=stdout, stderr="", traza=traza)


def test_resumir_deja_los_comandos_que_escriben_y_no_la_ayuda() -> None:
    traza = [
        ["todo", "open", "--help"],
        ["doctor"],
        ["todo", "close", "--scope", "faena-ai", "presentar el marco"],
    ]
    r = conversar.resumir(_turno(traza), {"AHORA.md": "modificado"})
    assert r["escribe"] == ["tuku todo close --scope faena-ai 'presentar el marco'"]
    assert r["delta"] == {"AHORA.md": "modificado"}


def test_un_turno_sin_cambios_se_lee_vacio() -> None:
    estado = {
        "ahora": "2026-08-12 21:00",
        "modelo": "m",
        "turnos": [
            {"damian": "¿Qué me queda?", "agente": "Cuatro cosas.", "escribe": [], "delta": {}}
        ],
    }
    texto = conversar.renderizar(estado, "Conversación")
    assert "> [!question] Damián\n> ¿Qué me queda?" in texto
    assert "> [!info] Agente\n> Cuatro cosas." in texto
    assert "**Comandos que escriben:** ninguno" in texto
    assert "**Delta del vault:** vacío" in texto


def test_el_log_muestra_la_hora_de_cada_turno_y_cuanto_demoro() -> None:
    estado = {
        "ahora": "2026-08-12 21:00",
        "modelo": "m",
        "turnos": [
            {
                "damian": "Pagué.",
                "enviado": "2026-10-16T23:41:07",
                "respondido": "2026-10-16T23:41:44",
                "segundos": 37,
                "agente": "Anotado.",
                "escribe": [],
                "delta": {},
            }
        ],
    }
    texto = conversar.renderizar(estado, "Conversación")
    assert (
        "> [!question] Damián (23:41:07)\n> Pagué.\n\n> [!info] Agente (23:41:44, 37 s)\n"
        in texto
    )


def test_el_log_lista_comandos_y_delta_cuando_los_hay() -> None:
    estado = {
        "ahora": "2026-08-12 21:00",
        "modelo": "m",
        "turnos": [
            {
                "damian": "Pagué.",
                "agente": "Anotado.",
                "escribe": ["tuku entry create --body x"],
                "delta": {"AHORA.md": "modificado"},
            }
        ],
    }
    texto = conversar.renderizar(estado, "Conversación")
    assert "- `tuku entry create --body x`" in texto
    assert "- `AHORA.md`: modificado" in texto


def test_el_log_es_una_nota_que_el_doctor_acepta(tmp_path: Path) -> None:
    v = init.init(tmp_path / "mi-vault", home=RAIZ_REPO, desde=date(2026, 8, 10))
    estado = {"ahora": "2026-08-12 21:00", "modelo": "m", "turnos": []}
    (v / conversar.LOG).write_text(
        conversar.renderizar(estado, "Conversación"), encoding="utf-8"
    )
    assert main(["doctor", "--vault", str(v)]) == EXITO


def test_un_escenario_agentico_deja_su_conversacion_en_el_vault(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    v = init.init(tmp_path / "mi-vault", home=RAIZ_REPO, desde=date(2026, 8, 10))

    def _turno(vault: Path, prompt: str, **_: object) -> agente.Turno:
        (vault / "borrador.txt").write_text("x\n", encoding="utf-8")
        return _turno_falso([["entry", "create", "--body", "x"]], "Anotado.")

    monkeypatch.setattr(agente, "turno", _turno)
    monkeypatch.setattr(
        agente, "configurado", lambda: agente.Arnes(nombre="agy", ejecutable="agy", modelo="m")
    )
    conversacion: dict[str, Any] = {
        "ahora": None,
        "turnos": [],
        "autor": "Autor",
        "presenta": "El autor es el texto del escenario.",
    }
    paso = gherkin.Paso("Cuando", "dicta", agente=["Pagué."], ahora="2026-08-12 21:00")
    gherkin._correr_agente(paso, tmp_path, conversacion)
    gherkin._dejar_la_conversacion(tmp_path, conversacion, "dicta")

    texto = (v / conversar.LOG).read_text(encoding="utf-8")
    assert "El autor es el texto del escenario." in texto
    assert "> [!question] Autor (" in texto
    assert "- `tuku entry create --body x`" in texto
    assert "- `borrador.txt`: nuevo" in texto
    assert main(["doctor", "--vault", str(v)]) == EXITO


def test_sin_turnos_el_escenario_no_deja_log(tmp_path: Path) -> None:
    v = init.init(tmp_path / "mi-vault", home=RAIZ_REPO, desde=date(2026, 8, 10))
    gherkin._dejar_la_conversacion(tmp_path, {"ahora": None, "turnos": []}, "dicta")
    assert not (v / conversar.LOG).exists()


def test_el_log_no_deja_links_de_la_respuesta_que_el_doctor_lea(tmp_path: Path) -> None:
    v = init.init(tmp_path / "mi-vault", home=RAIZ_REPO, desde=date(2026, 8, 10))
    respuesta = (
        "Quedó en [tesis](ambitos/no-existe/no-existe.md) y en [[otra-nota-que-no-existe]].\n"
        "```markdown\n- [x](ambitos/no-existe/no-existe.md)\n```"
    )
    estado = {
        "ahora": "2026-08-12 21:00",
        "modelo": "m",
        "turnos": [{"damian": "Pagué.", "agente": respuesta, "escribe": [], "delta": {}}],
    }
    conversar.escribir_log(v, estado, "Conversación")
    assert main(["doctor", "--vault", str(v)]) == EXITO


def test_cada_turno_deja_junto_al_vault_lo_que_devolvio_el_arnes_sin_filtrar(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    v = init.init(tmp_path / "esc" / "mi-vault", home=RAIZ_REPO, desde=date(2026, 8, 10))

    def _turno(vault: Path, prompt: str, **_: object) -> agente.Turno:
        return agente.Turno(
            prompt=prompt,
            codigo=0,
            stdout="Listo.",
            stderr="",
            conversacion="  1    2.0 s  modelo (10 tokens de entrada, 5 de salida)",
            crudo='{"event":"result"}\n',
        )

    monkeypatch.setattr(agente, "turno", _turno)
    monkeypatch.setattr(
        agente, "configurado", lambda: agente.Arnes(nombre="agy", ejecutable="agy", modelo="m")
    )
    conversar.turno(v, "Hola", "2026-08-12 21:00")
    conversar.turno(v, "Otra vez", "2026-08-12 21:00")

    trazas = v.parent / conversar.TRAZAS
    assert sorted(p.name for p in trazas.iterdir()) == [
        "turno-01.jsonl",
        "turno-01.txt",
        "turno-02.jsonl",
        "turno-02.txt",
    ]
    assert (trazas / "turno-01.jsonl").read_text(encoding="utf-8") == '{"event":"result"}\n'
    assert "modelo (10 tokens" in (trazas / "turno-02.txt").read_text(encoding="utf-8")
