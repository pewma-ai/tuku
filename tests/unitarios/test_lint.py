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
- 10:00 - [[personal]] ~~(Hecho)~~: comprar pan
- 11:00 - [[personal]] **cadencia**: revisar el correo
- 12:00 - [[personal]] **reunión**: almuerzo con el equipo
"""


def test_lint_texto_valido_sin_hallazgos() -> None:
    hallazgos = lint.lint(AHORA_VALIDO, abiertos=["reunión"])
    assert hallazgos == []
    assert formatear(hallazgos) == "entry lint: sin hallazgos."


def test_lint_texto_vacio_sin_hallazgos() -> None:
    assert lint.lint("", abiertos=[]) == []


def test_lint_sin_registros_sin_hallazgos() -> None:
    texto = "# Solo comentarios\n\nTexto libre sin horas.\n"
    assert lint.lint(texto, abiertos=[]) == []


def test_ontologia_cerrada_reconoce_todas_las_marcas_canonicas() -> None:
    assert "**pendiente**" in CERRADA
    assert "~~(Hecho)~~" in CERRADA
    assert "**cadencia**" in CERRADA


def test_marca_cerrada_con_variacion_de_mayusculas_es_error() -> None:
    texto = """---
type: Logbook
status: draft
from: 2026-08-11
to: 2026-08-17
---

## Martes 11 de agosto
- 09:00 - **Pendiente**: comprar pan
- 10:00 - ~~(hecho)~~: comprar pan
- 11:00 - **Cadencia**: semanal
"""
    hallazgos = lint.lint(texto, abiertos=[])
    errores = [h for h in hallazgos if h.grado == ERROR]
    assert len(errores) == 3
    assert any("**Pendiente**" in e.defecto for e in errores)
    assert any("~~(hecho)~~" in e.defecto for e in errores)
    assert any("**Cadencia**" in e.defecto for e in errores)
    assert all("ontología cerrada" in e.defecto for e in errores)
    assert all("Escríbela exactamente" in e.correccion for e in errores)


def test_vocabulario_abierto_no_declarado_es_pregunta() -> None:
    texto = """---
type: Logbook
status: draft
from: 2026-08-11
to: 2026-08-17
---

## Martes 11 de agosto
- 09:00 - **llamada**: con don Rodolfo
"""
    hallazgos = lint.lint(texto, abiertos=["reunión"])
    assert len(hallazgos) == 1
    h = hallazgos[0]
    assert h.grado == PREGUNTA
    assert "**llamada**" in h.defecto
    assert "no está en el libro de estilo" in h.defecto
    assert "Se acepta igual" in h.correccion


def test_vocabulario_abierto_declarado_no_genera_hallazgo() -> None:
    texto = """---
type: Logbook
status: draft
from: 2026-08-11
to: 2026-08-17
---

## Martes 11 de agosto
- 09:00 - **Llamada**: con don Rodolfo
"""
    # case-insensitive
    hallazgos = lint.lint(texto, abiertos=["llamada"])
    assert hallazgos == []


def test_registro_fuera_del_ciclo_abierto_es_error() -> None:
    texto = """---
type: Logbook
status: draft
from: 2026-08-11
to: 2026-08-17
---

## Martes 25 de agosto
- 09:00 - registro fuera de ciclo
"""
    hallazgos = lint.lint(texto, abiertos=[])
    errores = [h for h in hallazgos if h.grado == ERROR]
    assert len(errores) == 1
    assert "fuera del ciclo abierto" in errores[0].defecto
    assert "Muévelo al ciclo que le corresponde" in errores[0].correccion


def test_formatear_con_errores_y_preguntas() -> None:
    hallazgos = [
        Hallazgo(10, ERROR, "defecto error", "corregir error"),
        Hallazgo(15, PREGUNTA, "defecto pregunta", "corregir pregunta"),
    ]
    reporte = formatear(hallazgos)
    assert "AHORA.md:10: error: defecto error. corregir error" in reporte
    assert "AHORA.md:15: pregunta: defecto pregunta. corregir pregunta" in reporte
    assert "entry lint: 1 error(es), 1 pregunta(s)." in reporte


def test_hallazgo_str() -> None:
    h = Hallazgo(5, ERROR, "defecto", "corrección")
    assert str(h) == "AHORA.md:5: error: defecto. corrección"

    h_preg = Hallazgo(6, PREGUNTA, "pregunta", "corrección")
    assert str(h_preg) == "AHORA.md:6: pregunta: pregunta. corrección"
