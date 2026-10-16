"""Unitarios de `tuku.link`: componer, reconocer y convertir links.

Es el único módulo que arma y parsea links, así que acá se fija todo lo que
puede salir mal: un embed convertido en imagen, un `[[x]]` dentro de código
reescrito, una ruta mal calculada entre carpetas.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from tuku import link  # noqa: E402

pytestmark = pytest.mark.unitario

IDX = link.indice(
    [
        "AHORA.md",
        "ambitos/depto-centro/depto-centro.md",
        "ambitos/personal/personal.md",
        "notas/gastos-comunes.md",
        "notas/personal.md",
    ]
)


# --- componer ----------------------------------------------------------------


def test_relativa_desde_la_raiz_y_desde_otra_carpeta() -> None:
    assert link.relativa("AHORA.md", "ambitos/x/x.md") == "ambitos/x/x.md"
    assert link.relativa("notas/a.md", "ambitos/x/x.md") == "../ambitos/x/x.md"
    assert link.relativa("ambitos/x/x.md", "PENDIENTES.md") == "../../PENDIENTES.md"
    assert link.relativa("ambitos/x/x.md", "ambitos/y/y.md") == "../y/y.md"


def test_enlace_con_ancla_y_espacios() -> None:
    assert link.enlace("n", "AHORA.md", "notas/a b.md", "^id") == "[n](notas/a%20b.md#^id)"


def test_enlace_ambito_plano_y_anidado() -> None:
    assert link.enlace_ambito("x") == "[x](ambitos/x/x.md)"
    rutas = {"pewma": "ambitos/trabajo/pewma/pewma.md"}
    assert link.enlace_ambito("pewma", "AHORA.md", rutas) == (
        "[pewma](ambitos/trabajo/pewma/pewma.md)"
    )
    assert link.enlace_ambito("pewma", "notas/n.md", rutas) == (
        "[pewma](../ambitos/trabajo/pewma/pewma.md)"
    )


# --- leer el nombre en cualquier formato ---------------------------------------


@pytest.mark.parametrize(
    ("enlace", "nombre"),
    [
        ("[[personal]]", "personal"),
        ("[[personal#ancla]]", "personal"),
        ("[[personal|mi texto]]", "personal"),
        ("[personal](ambitos/personal/personal.md)", "personal"),
        ("[x](ambitos/personal/personal.md#ancla)", "personal"),
        ("[cat](ambitos/cat)", "cat"),
        ("[cat](ambitos/cat/)", "cat"),
        ("[a](notas/a%20b.md)", "a b"),
    ],
)
def test_nombre_de(enlace: str, nombre: str) -> None:
    assert link.nombre_de(enlace) == nombre


def test_nombre_de_algo_que_no_es_un_enlace() -> None:
    assert link.nombre_de("") is None
    assert link.nombre_de("texto suelto") is None
    assert link.nombre_de("[[") is None


def test_nombres_enlazados_de_una_linea_con_los_dos_formatos() -> None:
    linea = "- 09:00 - [a](ambitos/a/a.md) habló con [[b]] y con [c](notas/c.md)"
    assert link.nombres_enlazados(linea) == ["a", "b", "c"]


# --- wikilinks ---------------------------------------------------------------


def test_wikilinks_reconoce_alias_y_ancla() -> None:
    [w] = link.wikilinks("ver [[nota#sec|texto]] ahora")
    assert (w.destino, w.ancla, w.alias, w.linea) == ("nota", "sec", "texto", 1)
    assert w.original == "[[nota#sec|texto]]"


def test_wikilinks_ignora_la_transclusion() -> None:
    assert link.wikilinks("![[archivo.md#^ancla]]") == []


def test_wikilinks_ignora_el_codigo_inline_y_los_bloques() -> None:
    texto = "`[[a]]` y\n```\n[[b]]\n```\n~~~\n[[c]]\n~~~\ny [[d]]"
    assert [w.destino for w in link.wikilinks(texto)] == ["d"]


def test_wikilinks_con_un_bloque_sin_cerrar_ignora_el_resto() -> None:
    assert link.wikilinks("[[a]]\n```\n[[b]]\n") != []
    assert [w.destino for w in link.wikilinks("[[a]]\n```\n[[b]]\n")] == ["a"]


def test_wikilinks_vacio_y_malformado() -> None:
    assert link.wikilinks("") == []
    assert link.wikilinks("[[]] y [[sin cerrar y [mal]]") == []


# --- convertir ---------------------------------------------------------------


def test_convertir_un_wikilink_simple_desde_la_raiz() -> None:
    r = link.convertir("- 09:00 - [[depto-centro]] **señal**: algo", "AHORA.md", IDX)
    assert r.texto == (
        "- 09:00 - [depto-centro](ambitos/depto-centro/depto-centro.md) **señal**: algo"
    )
    assert r.convertidos == 1


def test_convertir_nombre_ambiguo_es_una_decision() -> None:
    r = link.convertir("[[personal]]", "AHORA.md", IDX)
    assert r.convertidos == 0
    assert r.texto == "[[personal]]"
    [d] = r.decisiones
    assert "ambiguo" in d.motivo and d.linea == 1 and d.archivo == "AHORA.md"


def test_convertir_resuelve_primero_el_archivo_junto_al_origen() -> None:
    r = link.convertir("[[personal]]", "notas/otra.md", IDX)
    assert r.texto == "[personal](personal.md)"


def test_convertir_calcula_la_ruta_desde_otra_carpeta() -> None:
    r = link.convertir(
        "ver [[depto-centro]] y [[gastos-comunes]]", "ambitos/personal/personal.md", IDX
    )
    assert r.texto == (
        "ver [depto-centro](../depto-centro/depto-centro.md) y "
        "[gastos-comunes](../../notas/gastos-comunes.md)"
    )
    assert r.convertidos == 2 and r.decisiones == []


def test_convertir_alias_y_ancla() -> None:
    r = link.convertir("[[depto-centro#Pendientes|el depto]]", "AHORA.md", IDX)
    assert r.texto == "[el depto](ambitos/depto-centro/depto-centro.md#Pendientes)"


def test_convertir_un_nombre_que_no_existe_se_deja_y_se_reporta() -> None:
    r = link.convertir("a [[fantasma]] b", "AHORA.md", IDX)
    assert r.texto == "a [[fantasma]] b"
    [d] = r.decisiones
    assert "no existe" in d.motivo


def test_convertir_respeta_la_transclusion_y_el_codigo() -> None:
    texto = (
        "![[ambitos/PENDIENTES-AMBITOS.md#^x]] `[[depto-centro]]`\n"
        "```\n[[depto-centro]]\n```\n"
    )
    r = link.convertir(texto, "AHORA.md", IDX)
    assert r.texto == texto and r.convertidos == 0 and r.decisiones == []


def test_convertir_es_idempotente() -> None:
    primero = link.convertir("[[depto-centro]] y [[fantasma]]", "AHORA.md", IDX)
    segundo = link.convertir(primero.texto, "AHORA.md", IDX)
    assert segundo.texto == primero.texto and segundo.convertidos == 0


def test_convertir_un_link_a_la_misma_pagina() -> None:
    r = link.convertir("[[#Sección uno]]", "AHORA.md", IDX)
    assert r.texto == "[Sección uno](#Sección%20uno)"


def test_convertir_texto_vacio() -> None:
    r = link.convertir("", "AHORA.md", IDX)
    assert (r.texto, r.convertidos, r.decisiones) == ("", 0, [])


# --- revisar y mover ---------------------------------------------------------


def test_rotos_reporta_solo_lo_que_no_existe() -> None:
    existentes = {"ambitos/x/x.md"}
    texto = (
        "[ok](ambitos/x/x.md) [mal](ambitos/y/y.md) [web](https://a.b/c) [aqui](#sec)\n"
        "`[codigo](no/existe.md)`"
    )
    [r] = link.rotos(texto, "AHORA.md", existentes.__contains__)
    assert (r.linea, r.destino) == (1, "ambitos/y/y.md")


def test_rotos_un_link_que_se_sale_del_vault() -> None:
    [r] = link.rotos("[x](../../fuera.md)", "AHORA.md", lambda _: True)
    assert r.destino == "../../fuera.md"


def test_rebasar_recalcula_las_rutas_al_mover_la_linea() -> None:
    linea = "habló con [a](ambitos/a/a.md#ancla) y [web](https://x.y)"
    salida = link.rebasar(linea, "AHORA.md", "ambitos/p/p.md")
    assert salida == "habló con [a](../a/a.md#ancla) y [web](https://x.y)"


def test_rebasar_en_la_misma_carpeta_no_cambia_nada() -> None:
    assert link.rebasar("[a](a.md)", "x/uno.md", "x/dos.md") == "[a](a.md)"


# --- enlazar hacia atrás -----------------------------------------------------


def test_enlaza_la_mencion_y_no_toca_el_resto_de_la_linea() -> None:
    linea = "- 18:40 - le mandé la boleta del depto centro a la administradora\n"
    texto, n = link.backfill(linea, scope="depto-centro", keywords=["depto centro"])
    assert n == 1
    assert texto == (
        "- 18:40 - le mandé la boleta del "
        "[depto-centro](ambitos/depto-centro/depto-centro.md) a la administradora\n"
    )


@pytest.mark.parametrize(
    "linea",
    [
        "- 18:40 - la boleta del [[depto-centro]] a la administradora\n",
        "- 18:40 - la boleta del [depto centro](ambitos/depto-centro/depto-centro.md) a\n",
        "- 18:40 - ![[ambitos/depto-centro/depto-centro.md]] a\n",
    ],
)
def test_no_enlaza_dos_veces_lo_que_ya_estaba_enlazado(linea: str) -> None:
    texto, n = link.backfill(
        linea, scope="depto-centro", keywords=["depto centro", "depto-centro"]
    )
    assert n == 0
    assert texto == linea


def test_varias_keywords_no_anidan_el_enlace_que_acaban_de_poner() -> None:
    texto, n = link.backfill(
        "- 09:00 - el depto centro\n", scope="depto-centro", keywords=["depto centro", "centro"]
    )
    assert n == 1
    assert texto.count("](") == 1


def test_sin_keywords_no_cambia_nada() -> None:
    linea = "- 18:40 - una línea cualquiera\n"
    assert link.backfill(linea, scope="depto-centro", keywords=[]) == (linea, 0)


def test_una_mencion_que_no_aparece_no_inventa_enlaces() -> None:
    linea = "- 18:40 - nada que ver acá\n"
    assert link.backfill(linea, scope="x", keywords=["depto centro"]) == (linea, 0)


def test_cuenta_todas_las_menciones_que_enlaza() -> None:
    texto = "- 09:00 - el depto centro\n- 10:00 - otra vez el depto centro\n"
    resultado, n = link.backfill(texto, scope="depto-centro", keywords=["depto centro"])
    assert n == 2
    assert resultado.count("](ambitos/depto-centro/depto-centro.md)") == 2


def test_un_texto_vacio_se_devuelve_igual() -> None:
    assert link.backfill("", scope="x", keywords=["y"]) == ("", 0)


def test_backfill_con_parametro_ambito() -> None:
    linea = "- 10:00 - reunión con el cliente\n"
    texto, n = link.backfill(linea, ambito="clientes", keywords=["cliente"])
    assert n == 1
    assert "[clientes](ambitos/clientes/clientes.md)" in texto


def test_keyword_vacia_o_espacios_no_enlaza_nada() -> None:
    linea = "- 10:00 - texto cualquiera\n"
    texto, n = link.backfill(linea, scope="algo", keywords=["", "   ", "--"])
    assert n == 0
    assert texto == linea


def test_patron_trata_guiones_y_espacios_como_equivalentes() -> None:
    destino = "[depto-centro](ambitos/depto-centro/depto-centro.md)"
    texto1, n1 = link.backfill(
        "- 10:00 - tema depto-centro importante\n",
        scope="depto-centro",
        keywords=["depto centro"],
    )
    assert n1 == 1 and destino in texto1
    texto2, n2 = link.backfill(
        "- 10:00 - tema depto centro importante\n",
        scope="depto-centro",
        keywords=["depto-centro"],
    )
    assert n2 == 1 and destino in texto2
