"""La pantalla de `test-tui.py`: lo que se muestra y cómo se lee el escenario.

Nada de esto llama a un modelo. Lo caro (Damián según Claude, el agente del
arnés) se probó a mano antes de escribir el módulo.
"""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))

import tui


def _vista(**kw: object) -> tuple[tui.Vista, io.StringIO]:
    salida = io.StringIO()
    return tui.Vista(salida=salida, color=False, **kw), salida  # type: ignore[arg-type]


def _paso(**campos: object) -> str:
    return json.dumps({"event": "step_update", "step_update": campos})


def test_la_respuesta_se_escribe_a_medida_que_llega() -> None:
    v, salida = _vista()
    v.evento(_paso(step_index=4, step_type="agent_response", state="ACTIVE", text_delta="Hola"))
    assert salida.getvalue() == "Agente\n  Hola"
    v.evento(
        _paso(step_index=4, step_type="agent_response", state="ACTIVE", text_delta=", Damián")
    )
    assert salida.getvalue() == "Agente\n  Hola, Damián"
    v.evento(
        _paso(
            step_index=4,
            step_type="agent_response",
            state="DONE",
            text_delta="\n",
            duration_seconds=3.39,
            usage={"input_tokens": 16019, "output_tokens": 256},
        )
    )
    assert "3.4 s · 16019 → 256 tokens" in salida.getvalue()


def test_un_comando_se_muestra_al_empezar_y_su_salida_al_terminar() -> None:
    v, salida = _vista()
    info = {"name": "run_command", "parameters": {"CommandLine": "tuku todo open --body x"}}
    v.evento(_paso(step_index=7, step_type="tool", state="ACTIVE", tool_info=info))
    assert salida.getvalue() == "  $ tuku todo open --body x\n"
    v.evento(
        _paso(
            step_index=7,
            step_type="tool",
            state="DONE",
            duration_seconds=0.4,
            tool_info={**info, "output": "pendiente abierto\r\nnota: simulada\r\n"},
        )
    )
    final = salida.getvalue()
    assert final.count("$ tuku todo open") == 1, "el comando se anunció dos veces"
    assert "    pendiente abierto\n    nota: simulada\n  0.4 s\n" in final


def test_una_salida_larga_se_recorta_y_dice_cuanto_falta() -> None:
    v, salida = _vista(max_lineas=3)
    info = {"name": "run_command", "parameters": {"CommandLine": "ls"}}
    largo = "\n".join(f"a{i}" for i in range(10))
    v.evento(
        _paso(step_index=1, step_type="tool", state="DONE", tool_info={**info, "output": largo})
    )
    assert "    a2\n" in salida.getvalue()
    assert "a3" not in salida.getvalue()
    assert "… 7 líneas más" in salida.getvalue()


def test_raw_imprime_la_linea_sin_darle_formato() -> None:
    v, salida = _vista(raw=True)
    linea = '{"event":"init","init":{"model":"m"}}'
    v.evento(linea)
    assert salida.getvalue() == linea + "\n"


def test_una_linea_que_no_es_json_no_rompe_la_pantalla() -> None:
    v, salida = _vista()
    v.evento("warning: algo")
    assert salida.getvalue() == "warning: algo\n"


def test_el_plan_sale_del_md_del_escenario() -> None:
    plan = tui.leer_plan("004-03")
    assert plan.ahora == "2026-08-12 21:00"
    assert len(plan.pasos) == 4
    assert plan.pasos[3].startswith("Ratificas:")
    assert plan.base == ("004-00-la-conversacion", "el-vault-de-partida")


def test_un_id_que_no_existe_se_dice() -> None:
    with pytest.raises(tui.EscenarioNoEncontrado):
        tui.leer_plan("999-99")


def test_damian_recibe_solo_el_paso_que_toca() -> None:
    plan = tui.leer_plan("004-03")
    prompt = tui.prompt_de_damian(
        plan, [("hola", "¿qué tal?")], 2, persona="Damián Ulloa, 47 años"
    )
    assert plan.pasos[1] in prompt
    assert plan.pasos[3] not in prompt, "el modelo se adelantaría a ratificar"
    assert "Agente: ¿qué tal?" in prompt


def test_la_frase_de_damian_sale_de_las_etiquetas() -> None:
    sucio = "Ojo, lo que me pides es otra cosa:\n<damian>Mejor el viernes.</damian>"
    assert tui.extraer_frase(sucio) == "Mejor el viernes."
    assert tui.extraer_frase("Mejor el viernes.\n") == "Mejor el viernes."


def test_el_cierre_de_la_respuesta_no_deja_una_linea_en_blanco() -> None:
    v, salida = _vista()
    v.evento(
        _paso(step_index=4, step_type="agent_response", state="ACTIVE", text_delta="Listo.")
    )
    v.evento(
        _paso(
            step_index=4,
            step_type="agent_response",
            state="DONE",
            text_delta="\n",
            duration_seconds=1.0,
            usage={"input_tokens": 1, "output_tokens": 2},
        )
    )
    assert salida.getvalue().startswith("Agente\n  Listo.\n  1.0 s")


def test_el_resultado_muestra_los_tokens_del_turno() -> None:
    v, salida = _vista()
    usage = {
        "input_tokens": 68467,
        "output_tokens": 4140,
        "thinking_tokens": 3429,
        "cache_read_tokens": 129946,
        "total_tokens": 72607,
    }
    resultado = {"status": "SUCCESS", "duration_seconds": 69.6, "num_turns": 4, "usage": usage}
    v.evento(json.dumps({"event": "result", "result": resultado}))
    texto = salida.getvalue()
    assert "fin del turno · SUCCESS · 69.6 s" in texto
    assert "4 llamadas" in texto
    assert (
        "entrada 68467 · salida 4140 · razonamiento 3429 · caché 129946 · total 72607" in texto
    )


def test_el_stderr_sale_en_rojo_y_solo_si_lo_hay() -> None:
    salida = io.StringIO()
    v = tui.Vista(salida=salida, color=True)
    v.error("aviso del arnés")
    assert salida.getvalue() == "\033[31magy stderr: aviso del arnés\033[0m\n"


def _turno(delta: dict[str, str], escribe: list[str], codigo: int = 0) -> dict[str, object]:
    return {"agente": "ok", "delta": delta, "escribe": escribe, "codigo": codigo}


def test_la_tabla_del_escenario_dice_que_turnos_cambian_el_vault() -> None:
    plan = tui.leer_plan("004-03")
    assert {n: e.cambia for n, e in plan.esperado.items()} == {
        1: False,
        2: False,
        3: False,
        4: True,
    }
    assert plan.esperado[4].comandos == ["todo open"]
    assert plan.a_mano[0].startswith("En los turnos 1 a 3")
    uno = tui.leer_plan("004-01")
    assert uno.esperado[10].comandos == ["scope create", "scope move"]
    assert uno.esperado[3].comandos == ["todo close", "entry add"]


def test_la_conclusion_dice_que_funciono_cuando_todo_coincide() -> None:
    plan = tui.leer_plan("004-03")
    turnos = [
        _turno({}, []),
        _turno({}, []),
        _turno({}, []),
        _turno({"AHORA.md": "modificado"}, ["tuku todo open --body x"]),
    ]
    c = tui.evaluar(plan, turnos, (0, "doctor: el vault está sano."))
    assert c.ok
    assert all(ok for ok, _ in c.chequeos)


def test_la_conclusion_dice_por_que_no_funciono() -> None:
    plan = tui.leer_plan("004-03")
    turnos = [
        _turno({"AHORA.md": "modificado"}, ["tuku entry add --body x"]),
        _turno({}, []),
        _turno({"AHORA.md": "modificado"}, []),
        _turno({}, [], codigo=124),
    ]
    c = tui.evaluar(plan, turnos, (1, "doctor: 2 hallazgos"))
    assert not c.ok
    motivos = "\n".join(t for ok, t in c.chequeos if not ok)
    assert "Turno 1" in motivos and "tabla dice vacío" in motivos
    assert "Turno 3" in motivos and "sin un comando" in motivos
    assert "Turno 4" in motivos and "esperaba" in motivos and "todo open" in motivos
    assert "Turno 4" in motivos and "salió 124" in motivos
    assert "doctor" in motivos
