"""El ayudante de la conversación a mano, sin invocar ningún modelo."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))

import agente
import conversar

from tuku.cli import EXITO, main


def _turno(traza: list[list[str]], stdout: str = "listo") -> agente.Turno:
    return agente.Turno(prompt="", codigo=0, stdout=stdout, stderr="", traza=traza)


def test_resumir_deja_los_comandos_que_escriben_y_no_la_ayuda() -> None:
    traza = [
        ["todo", "open", "--help"],
        ["doctor"],
        ["todo", "close", "--scope", "faena-ai", "--body", "presentar el marco"],
    ]
    r = conversar.resumir(_turno(traza), {"AHORA.md": "modificado"})
    assert r["escribe"] == ["tuku todo close --scope faena-ai --body 'presentar el marco'"]
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
    assert "**Damián:** ¿Qué me queda?" in texto
    assert "> Cuatro cosas." in texto
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
    assert "**Damián** (23:41:07): Pagué." in texto
    assert "**Agente** (23:41:44, 37 s):" in texto


def test_el_log_lista_comandos_y_delta_cuando_los_hay() -> None:
    estado = {
        "ahora": "2026-08-12 21:00",
        "modelo": "m",
        "turnos": [
            {
                "damian": "Pagué.",
                "agente": "Anotado.",
                "escribe": ["tuku entry add --body x"],
                "delta": {"AHORA.md": "modificado"},
            }
        ],
    }
    texto = conversar.renderizar(estado, "Conversación")
    assert "- `tuku entry add --body x`" in texto
    assert "- `AHORA.md`: modificado" in texto


def test_el_log_es_una_nota_que_el_doctor_acepta(tmp_path: Path) -> None:
    v = tmp_path / "mi-vault"
    assert main(["init", str(v), "--at", "2026-08-11"]) == EXITO
    estado = {"ahora": "2026-08-12 21:00", "modelo": "m", "turnos": []}
    (v / conversar.LOG).write_text(
        conversar.renderizar(estado, "Conversación"), encoding="utf-8"
    )
    assert main(["doctor", "--vault", str(v)]) == EXITO
