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
    assert len(act_personal["## Martes 11 de agosto"]) == 2
    assert act_personal["## Miércoles 12 de agosto"] == ["- **pendiente**: pagar sesión"]

    assert scope.extraer_actividad_ambito(AHORA_EJEMPLO, "no-existe") == {}


def test_actualizar_contenido_pagina_crea_secciones_es_idempotente_y_preserva_el_resumen() -> (
    None
):
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
    assert scope.actualizar_contenido_pagina(res1, AHORA_EJEMPLO, "depto-centro") == res1

    con_resumen = (
        "---\ntype: Scope\nkeywords: [depto-centro]\n---\n# depto-centro\n\n"
        "![[../PENDIENTES-AMBITOS.md#^depto-centro]]\n\n"
        "## Esta semana\n\n"
        "## Actividad reciente\n"
        "### Julio 2026\n"
        "- Resumen generado por LLM que debe conservarse intacto.\n"
    )
    res = scope.actualizar_contenido_pagina(con_resumen, AHORA_EJEMPLO, "depto-centro")
    assert "### Julio 2026" in res
    assert "- Resumen generado por LLM que debe conservarse intacto." in res
    assert "### Martes 11 de agosto" in res


def test_keywords_se_leen_del_frontmatter() -> None:
    pagina = (
        "---\ntype: Scope\nkeywords: [depto-centro, depto centro, departamento]\n"
        "---\n# Titulo\n"
    )
    assert scope.keywords(pagina) == ["depto-centro", "depto centro", "departamento"]
    assert scope.keywords("---\ntype: Scope\nkeywords: []\n---\n") == []
    assert scope.keywords("---\ntype: Scope\n---\n") == []
    assert scope.keywords("") == []


def test_esta_semana_vacia_y_categorias_en_memoria() -> None:
    assert scope.formatear_esta_semana({}) == "## Esta semana"

    texto = "- 10:00 - [[clientes]] reunión con cliente\n- 11:00 - [[personal]] compras\n"
    [hallazgo] = scope.lint_categorias(texto, categorias=["clientes"])
    assert "clientes es una categoría" in hallazgo
    assert "no puede apuntar a una" in hallazgo
    assert scope.lint_categorias(texto, categorias=[]) == []
