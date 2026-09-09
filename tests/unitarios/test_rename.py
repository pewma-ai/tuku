"""Tests del núcleo puro de renombrado.

Lo que se prueba acá es que renombrar alcance todo lo que apunta al nombre y
**nada más que eso**: el modo de falla de un renombrado no es que no haga nada,
es que además cambie algo que el autor no pidió.
"""

from __future__ import annotations

from tuku.rename import renombrar_ancla, renombrar_enlaces, renombrar_titulo


def test_renombra_el_enlace_simple() -> None:
    texto = "- 09:12 - [[personal]] **señal**: algo"
    assert renombrar_enlaces(texto, "personal", "propio") == (
        "- 09:12 - [[propio]] **señal**: algo",
        1,
    )


def test_conserva_el_ancla_y_el_alias() -> None:
    """Lo que va tras el nombre apunta a una parte del destino, no al destino."""
    texto = "![[PENDIENTES-AMBITOS.md#^personal]] y [[personal|lo mío]]"
    salida, n = renombrar_enlaces(texto, "personal", "propio")
    assert salida == "![[PENDIENTES-AMBITOS.md#^personal]] y [[propio|lo mío]]"
    assert n == 1


def test_el_nombre_se_compara_entero() -> None:
    """`[[depto-centro]]` no es una mención de `[[depto]]`."""
    texto = "[[depto]] y [[depto-centro]] y [[mi-depto]]"
    assert renombrar_enlaces(texto, "depto", "casa") == (
        "[[casa]] y [[depto-centro]] y [[mi-depto]]",
        1,
    )


def test_la_mencion_en_prosa_no_se_toca() -> None:
    """El autor escribió esa frase; renombrar no la reescribe."""
    texto = "hablé con personal sobre [[personal]]"
    assert renombrar_enlaces(texto, "personal", "propio") == (
        "hablé con personal sobre [[propio]]",
        1,
    )


def test_renombrar_al_mismo_nombre_no_cambia_nada() -> None:
    assert renombrar_enlaces("[[a]]", "a", "a") == ("[[a]]", 0)


def test_texto_vacio_y_nombre_vacio() -> None:
    assert renombrar_enlaces("", "a", "b") == ("", 0)
    assert renombrar_enlaces("[[a]]", "", "b") == ("[[a]]", 0)


def test_sin_enlaces_devuelve_cero() -> None:
    assert renombrar_enlaces("nada que ver", "a", "b") == ("nada que ver", 0)


def test_renombra_el_ancla_de_la_transclusion() -> None:
    texto = "![[ambitos/PENDIENTES-AMBITOS.md#^personal]]"
    assert renombrar_ancla(texto, "personal", "propio") == (
        "![[ambitos/PENDIENTES-AMBITOS.md#^propio]]",
        1,
    )


def test_el_ancla_se_compara_entera() -> None:
    assert renombrar_ancla("^personal ^personal-2", "personal", "propio")[1] == 1


def test_renombra_solo_el_primer_titulo() -> None:
    texto = "---\ntype: Note\n---\n\n# viejo\n\ncuerpo\n\n# no soy el título\n"
    assert renombrar_titulo(texto, "nuevo") == (
        "---\ntype: Note\n---\n\n# nuevo\n\ncuerpo\n\n# no soy el título\n"
    )


def test_sin_encabezado_no_inventa_uno() -> None:
    """Un documento sin título es defecto del lint, no algo que esto tape."""
    assert renombrar_titulo("solo cuerpo\n", "nuevo") == "solo cuerpo\n"
