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


# --- componer y leer ----------------------------------------------------------


def test_componer_enlaces_con_ruta_relativa_ancla_y_ambitos_anidados() -> None:
    assert link.relativa("AHORA.md", "ambitos/x/x.md") == "ambitos/x/x.md"
    assert link.relativa("notas/a.md", "ambitos/x/x.md") == "../ambitos/x/x.md"
    assert link.relativa("ambitos/x/x.md", "PENDIENTES.md") == "../../PENDIENTES.md"
    assert link.relativa("ambitos/x/x.md", "ambitos/y/y.md") == "../y/y.md"

    assert link.enlace("n", "AHORA.md", "notas/a b.md", "^id") == "[n](notas/a%20b.md#^id)"

    assert link.enlace_ambito("x") == "[x](ambitos/x/x.md)"
    rutas = {"pewma": "ambitos/trabajo/pewma/pewma.md"}
    assert link.enlace_ambito("pewma", "AHORA.md", rutas) == (
        "[pewma](ambitos/trabajo/pewma/pewma.md)"
    )
    assert link.enlace_ambito("pewma", "notas/n.md", rutas) == (
        "[pewma](../ambitos/trabajo/pewma/pewma.md)"
    )


def test_nombre_de_lee_cualquier_formato() -> None:
    for enlace, nombre in [
        ("[[personal]]", "personal"),
        ("[[personal#ancla]]", "personal"),
        ("[[personal|mi texto]]", "personal"),
        ("[personal](ambitos/personal/personal.md)", "personal"),
        ("[x](ambitos/personal/personal.md#ancla)", "personal"),
        ("[cat](ambitos/cat)", "cat"),
        ("[cat](ambitos/cat/)", "cat"),
        ("[a](notas/a%20b.md)", "a b"),
        ("", None),
        ("texto suelto", None),
        ("[[", None),
    ]:
        assert link.nombre_de(enlace) == nombre, enlace

    linea = "- 09:00 - [a](ambitos/a/a.md) habló con [[b]] y con [c](notas/c.md)"
    assert link.nombres_enlazados(linea) == ["a", "b", "c"]


def test_wikilinks_reconoce_alias_y_ancla_e_ignora_transclusion_codigo_y_malformados() -> None:
    [w] = link.wikilinks("ver [[nota#sec|texto]] ahora")
    assert (w.destino, w.ancla, w.alias, w.linea) == ("nota", "sec", "texto", 1)
    assert w.original == "[[nota#sec|texto]]"

    assert link.wikilinks("![[archivo.md#^ancla]]") == []
    texto = "`[[a]]` y\n```\n[[b]]\n```\n~~~\n[[c]]\n~~~\ny [[d]]"
    assert [w.destino for w in link.wikilinks(texto)] == ["d"]
    assert [w.destino for w in link.wikilinks("[[a]]\n```\n[[b]]\n")] == ["a"]
    assert link.wikilinks("") == []
    assert link.wikilinks("[[]] y [[sin cerrar y [mal]]") == []


# --- convertir ---------------------------------------------------------------


def test_convertir_calcula_la_ruta_desde_donde_esta_el_archivo() -> None:
    r = link.convertir("- 09:00 - [[depto-centro]] **señal**: algo", "AHORA.md", IDX)
    assert r.texto == (
        "- 09:00 - [depto-centro](ambitos/depto-centro/depto-centro.md) **señal**: algo"
    )
    assert r.convertidos == 1

    r = link.convertir(
        "ver [[depto-centro]] y [[gastos-comunes]]", "ambitos/personal/personal.md", IDX
    )
    assert r.texto == (
        "ver [depto-centro](../depto-centro/depto-centro.md) y "
        "[gastos-comunes](../../notas/gastos-comunes.md)"
    )
    assert r.convertidos == 2 and r.decisiones == []

    assert (
        link.convertir("[[personal]]", "notas/otra.md", IDX).texto == "[personal](personal.md)"
    )
    assert link.convertir("[[depto-centro#Pendientes|el depto]]", "AHORA.md", IDX).texto == (
        "[el depto](ambitos/depto-centro/depto-centro.md#Pendientes)"
    )
    assert link.convertir("[[#Sección uno]]", "AHORA.md", IDX).texto == (
        "[Sección uno](#Sección%20uno)"
    )


def test_convertir_deja_lo_ambiguo_y_lo_inexistente_como_decision() -> None:
    r = link.convertir("[[personal]]", "AHORA.md", IDX)
    assert (r.convertidos, r.texto) == (0, "[[personal]]")
    [d] = r.decisiones
    assert "ambiguo" in d.motivo and d.linea == 1 and d.archivo == "AHORA.md"

    r = link.convertir("a [[fantasma]] b", "AHORA.md", IDX)
    assert r.texto == "a [[fantasma]] b"
    [d] = r.decisiones
    assert "no existe" in d.motivo


def test_convertir_respeta_transclusion_y_codigo_y_es_idempotente() -> None:
    texto = (
        "![[ambitos/PENDIENTES-AMBITOS.md#^x]] `[[depto-centro]]`\n```\n[[depto-centro]]\n```\n"
    )
    r = link.convertir(texto, "AHORA.md", IDX)
    assert r.texto == texto and r.convertidos == 0 and r.decisiones == []

    r = link.convertir("", "AHORA.md", IDX)
    assert (r.texto, r.convertidos, r.decisiones) == ("", 0, [])

    primero = link.convertir("[[depto-centro]] y [[fantasma]]", "AHORA.md", IDX)
    segundo = link.convertir(primero.texto, "AHORA.md", IDX)
    assert segundo.texto == primero.texto and segundo.convertidos == 0


# --- revisar y mover ---------------------------------------------------------


def test_rotos_reporta_solo_lo_que_no_existe() -> None:
    texto = (
        "[ok](ambitos/x/x.md) [mal](ambitos/y/y.md) [web](https://a.b/c) [aqui](#sec)\n"
        "`[codigo](no/existe.md)`"
    )
    [r] = link.rotos(texto, "AHORA.md", {"ambitos/x/x.md"}.__contains__)
    assert (r.linea, r.destino) == (1, "ambitos/y/y.md")

    [r] = link.rotos("[x](../../fuera.md)", "AHORA.md", lambda _: True)
    assert r.destino == "../../fuera.md", "un link que se sale del vault"


def test_salientes_da_la_ruta_local_de_cada_link_y_salta_lo_externo() -> None:
    texto = (
        "[a](a.md) [web](https://a.b) [aqui](#sec)\n[b](../ambitos/b/b.md#ancla) `[c](c.md)`"
    )
    assert link.salientes(texto, "notas/n.md") == [
        (1, "a", "notas/a.md", "a.md"),
        (2, "b", "ambitos/b/b.md", "../ambitos/b/b.md#ancla"),
    ]


def test_rebasar_recalcula_las_rutas_al_mover_la_linea() -> None:
    linea = "habló con [a](ambitos/a/a.md#ancla) y [web](https://x.y)"
    assert link.rebasar(linea, "AHORA.md", "ambitos/p/p.md") == (
        "habló con [a](../a/a.md#ancla) y [web](https://x.y)"
    )
    assert link.rebasar("[a](a.md)", "x/uno.md", "x/dos.md") == "[a](a.md)"


MOVIDO = {"ambitos/a": "ambitos/g/a"}


def test_reubicar_recalcula_los_links_cuando_una_carpeta_cambia_de_lugar() -> None:
    assert link.reubicar("ver [a](ambitos/a/a.md#ancla)", "AHORA.md", "AHORA.md", MOVIDO) == (
        "ver [a](ambitos/g/a/a.md#ancla)"
    ), "el link de otro archivo a lo movido"
    assert link.reubicar(
        "ver [p](../p/p.md)", "ambitos/a/a.md", "ambitos/g/a/a.md", MOVIDO
    ) == ("ver [p](../../p/p.md)"), "los links de un archivo movido hacia afuera"
    assert link.reubicar(
        "ver [nota](nota.md)", "ambitos/a/a.md", "ambitos/g/a/a.md", MOVIDO
    ) == ("ver [nota](nota.md)"), "entre hermanos que se mueven juntos"
    assert (
        link.reubicar(
            "![[../PENDIENTES-AMBITOS.md#^a]]", "ambitos/a/a.md", "ambitos/g/a/a.md", MOVIDO
        )
        == "![[../../PENDIENTES-AMBITOS.md#^a]]"
    ), "la transclusión"


def test_reubicar_no_toca_externos_anclas_codigo_ni_lo_que_no_cambia() -> None:
    for texto in (
        "[web](https://x.y) [aca](#seccion) `[a](ambitos/a/a.md)`",
        "- 09:12 - [personal](ambitos/personal/personal.md) cuerpo",
    ):
        assert link.reubicar(texto, "AHORA.md", "AHORA.md", MOVIDO) == texto
