"""Unitarios de `tuku.lint`: revisión de registros de AHORA.md en memoria.

Verifica la ontología cerrada (estricta) y abierta (permisiva), rangos de ciclo,
entradas vacías y formateo de hallazgos. Todo sin tocar disco.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from tuku import lint  # noqa: E402
from tuku.lint import CERRADA, ERROR, PREGUNTA, Hallazgo, formatear  # noqa: E402

pytestmark = pytest.mark.unitario

AHORA_VALIDO = """---
type: Logbook
status: draft
from: 2026-08-11
to: 2026-08-17
---

# Actividad diaria

## Martes 11 de agosto
- 09:00 - [[personal]] **pendiente**: comprar pan
- 10:00 - [[personal]] (Hecho): ~~comprar pan~~
- 11:00 - [[personal]] **cadencia**: revisar el correo
- 12:00 - [[personal]] **reunión**: almuerzo con el equipo
"""


CABECERA = "---\ntype: Logbook\nstatus: draft\nfrom: 2026-08-11\nto: 2026-08-17\n---\n\n"


def test_lint_de_lo_valido_o_sin_registros_no_tiene_hallazgos() -> None:
    hallazgos = lint.lint(AHORA_VALIDO, abiertos=["reunión"])
    assert hallazgos == []
    assert formatear(hallazgos) == "entry lint: sin hallazgos."
    assert lint.lint("", abiertos=[]) == []
    assert lint.lint("# Solo comentarios\n\nTexto libre sin horas.\n", abiertos=[]) == []
    assert {"**pendiente**", "(Hecho)", "**cadencia**"} <= set(CERRADA)


def test_una_marca_cerrada_mal_escrita_es_error_y_dice_como_escribirla() -> None:
    texto = (
        CABECERA + "## Martes 11 de agosto\n"
        "- 09:00 - **Pendiente**: comprar pan\n"
        "- 10:00 - (hecho): ~~comprar pan~~\n"
        "- 10:30 - ~~(hecho)~~: comprar pan\n"
        "- 11:00 - **Cadencia**: semanal\n"
    )
    errores = [h for h in lint.lint(texto, abiertos=[]) if h.grado == ERROR]
    assert len(errores) == 4
    for marca in ("**Pendiente**", "(hecho)", "~~(hecho)~~", "**Cadencia**"):
        assert any(marca in e.defecto for e in errores), marca
    assert all("ontología cerrada" in e.defecto for e in errores)
    assert all("Escríbela exactamente" in e.correccion for e in errores)

    tachada = (
        f"{CABECERA}## Martes 11 de agosto\n- 10:00 - [[personal]] ~~(Hecho)~~: comprar pan\n"
    )
    [h] = lint.lint(tachada, abiertos=[])
    assert h.grado == ERROR and "Escríbela exactamente (Hecho)" in h.correccion


def test_un_vocabulario_abierto_no_declarado_es_pregunta_y_declarado_no_dice_nada() -> None:
    [h] = lint.lint(
        f"{CABECERA}## Martes 11 de agosto\n- 09:00 - **llamada**: con don Rodolfo\n",
        abiertos=["reunión"],
    )
    assert h.grado == PREGUNTA
    assert "**llamada**" in h.defecto
    assert "no está en el libro de estilo" in h.defecto
    assert "Se acepta igual" in h.correccion

    declarado = f"{CABECERA}## Martes 11 de agosto\n- 09:00 - **Llamada**: con don Rodolfo\n"
    assert lint.lint(declarado, abiertos=["llamada"]) == [], "sin distinguir mayúsculas"


def test_un_registro_fuera_del_ciclo_abierto_es_error() -> None:
    texto = f"{CABECERA}## Martes 25 de agosto\n- 09:00 - registro fuera de ciclo\n"
    [error] = [h for h in lint.lint(texto, abiertos=[]) if h.grado == ERROR]
    assert "fuera del ciclo abierto" in error.defecto
    assert "Muévelo al ciclo que le corresponde" in error.correccion


def test_formatear_y_str_de_los_hallazgos() -> None:
    reporte = formatear(
        [
            Hallazgo(10, ERROR, "defecto error", "corregir error"),
            Hallazgo(15, PREGUNTA, "defecto pregunta", "corregir pregunta"),
        ]
    )
    assert "AHORA.md:10: error: defecto error. corregir error" in reporte
    assert "AHORA.md:15: pregunta: defecto pregunta. corregir pregunta" in reporte
    assert "entry lint: 1 error(es), 1 pregunta(s)." in reporte
    assert str(Hallazgo(5, ERROR, "defecto", "corrección")) == (
        "AHORA.md:5: error: defecto. corrección"
    )
