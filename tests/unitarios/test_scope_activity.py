"""Tests unitarios para funciones puras de ámbitos (actividad, keywords, categorías)."""

from __future__ import annotations

from tuku import scope

AHORA_EJEMPLO = """---
type: Logbook
status: draft
from: 2026-08-11
to: 2026-08-17
---

# Ciclo

## Martes 11 de agosto
- 09:12 - [[personal]] **señal**: la administradora responde con retraso
- 11:30 - hice la consulta presencial por el standing desk
- 14:20 - [[personal]] **pendiente**: avisar de los GGCC
- 18:40 - le mandé la boleta de gastos comunes del [[depto-centro]] a la administradora
- 21:15 - [[depto-centro]] **nota**: escribí la nota [[como-funciona-el-cobro]]

## Miércoles 12 de agosto
- 09:00 - [[personal]] **pendiente**: pagar sesión
- 16:00 - [[trabajo]] reunión de equipo

---
"""


def test_extraer_actividad_ambito_omite_hora_y_agrupa_por_dia() -> None:
    act_depto = scope.extraer_actividad_ambito(AHORA_EJEMPLO, "depto-centro")
    assert list(act_depto.keys()) == ["## Martes 11 de agosto"]
    assert act_depto["## Martes 11 de agosto"] == [
        "- le mandé la boleta de gastos comunes del depto-centro a la administradora",
        "- **nota**: escribí la nota [[como-funciona-el-cobro]]",
    ]

    act_personal = scope.extraer_actividad_ambito(AHORA_EJEMPLO, "personal")
    assert "## Martes 11 de agosto" in act_personal
    assert "## Miércoles 12 de agosto" in act_personal
    assert len(act_personal["## Martes 11 de agosto"]) == 2
    assert act_personal["## Miércoles 12 de agosto"] == [
        "- **pendiente**: pagar sesión"
    ]


def test_extraer_actividad_ambito_sin_menciones_retorna_vacio() -> None:
    act = scope.extraer_actividad_ambito(AHORA_EJEMPLO, "no-existe")
    assert act == {}


def test_actualizar_contenido_pagina_crea_secciones_e_idempotente() -> None:
    base = (
        "---\ntype: Scope\nkeywords: [depto-centro]\n---\n"
        "# depto-centro\n\n![[../PENDIENTES-AMBITOS.md#^depto-centro]]"
    )
    res1 = scope.actualizar_contenido_pagina(base, AHORA_EJEMPLO, "depto-centro")

    assert "## Esta semana" in res1
    assert "### Martes 11 de agosto" in res1
    assert "- le mandé la boleta de gastos comunes del depto-centro" in res1
    assert "- 18:40 - " not in res1
    assert "## Actividad reciente" in res1
    assert "### Agosto 2026" in res1

    # Idempotencia: correr sobre el resultado da el mismo texto
    res2 = scope.actualizar_contenido_pagina(res1, AHORA_EJEMPLO, "depto-centro")
    assert res2 == res1


def test_actualizar_contenido_pagina_preserva_resumen_previo() -> None:
    pagina_con_resumen = (
        "---\ntype: Scope\nkeywords: [depto-centro]\n---\n# depto-centro\n\n"
        "![[../PENDIENTES-AMBITOS.md#^depto-centro]]\n\n"
        "## Esta semana\n\n"
        "## Actividad reciente\n"
        "### Julio 2026\n"
        "- Resumen generado por LLM que debe conservarse intacto.\n"
    )
    res = scope.actualizar_contenido_pagina(pagina_con_resumen, AHORA_EJEMPLO, "depto-centro")
    assert "### Julio 2026" in res
    assert "- Resumen generado por LLM que debe conservarse intacto." in res
    assert "### Martes 11 de agosto" in res


def test_keywords_extrae_lista_correctamente() -> None:
    pagina = (
        "---\ntype: Scope\nkeywords: [depto-centro, depto centro, departamento]\n"
        "---\n# Titulo\n"
    )
    assert scope.keywords(pagina) == ["depto-centro", "depto centro", "departamento"]


def test_keywords_vacia_o_sin_declarar() -> None:
    assert scope.keywords("---\ntype: Scope\nkeywords: []\n---\n") == []
    assert scope.keywords("---\ntype: Scope\n---\n") == []
    assert scope.keywords("") == []


def test_formatear_esta_semana_vacia_devuelve_solo_encabezado() -> None:
    assert scope.formatear_esta_semana({}) == "## Esta semana"


def test_lint_categorias_en_memoria() -> None:
    texto = "- 10:00 - [[clientes]] reunión con cliente\n- 11:00 - [[personal]] compras\n"
    hallazgos = scope.lint_categorias(texto, categorias=["clientes"])
    assert len(hallazgos) == 1
    assert "[[clientes]] es una categoría" in hallazgos[0]
    assert "no puede apuntar a una" in hallazgos[0]

    sin_categorias = scope.lint_categorias(texto, categorias=[])
    assert sin_categorias == []
