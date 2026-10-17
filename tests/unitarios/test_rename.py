"""Tests del núcleo puro de renombrado: alcanza todo lo que apunta al nombre y nada más."""

from __future__ import annotations

from tuku.rename import renombrar_ancla, renombrar_enlaces, renombrar_titulo


def test_renombrar_enlaces_cambia_solo_el_nombre_entero() -> None:
    assert renombrar_enlaces(
        "- 09:12 - [[personal]] **señal**: algo", "personal", "propio"
    ) == (
        "- 09:12 - [[propio]] **señal**: algo",
        1,
    )
    # lo que va tras el nombre apunta a una parte del destino, no al destino
    assert renombrar_enlaces(
        "![[PENDIENTES-AMBITOS.md#^personal]] y [[personal|lo mío]]", "personal", "propio"
    ) == ("![[PENDIENTES-AMBITOS.md#^personal]] y [[propio|lo mío]]", 1)
    assert renombrar_enlaces(
        "[[depto]] y [[depto-centro]] y [[mi-depto]]", "depto", "casa"
    ) == (
        "[[casa]] y [[depto-centro]] y [[mi-depto]]",
        1,
    )
    # la frase del autor no se reescribe
    assert renombrar_enlaces("hablé con personal sobre [[personal]]", "personal", "propio") == (
        "hablé con personal sobre [[propio]]",
        1,
    )


def test_renombrar_enlaces_sin_nada_que_cambiar() -> None:
    assert renombrar_enlaces("[[a]]", "a", "a") == ("[[a]]", 0)
    assert renombrar_enlaces("", "a", "b") == ("", 0)
    assert renombrar_enlaces("[[a]]", "", "b") == ("[[a]]", 0)
    assert renombrar_enlaces("nada que ver", "a", "b") == ("nada que ver", 0)


def test_renombrar_ancla_y_titulo() -> None:
    assert renombrar_ancla(
        "![[ambitos/PENDIENTES-AMBITOS.md#^personal]]", "personal", "propio"
    ) == (
        "![[ambitos/PENDIENTES-AMBITOS.md#^propio]]",
        1,
    )
    assert renombrar_ancla("^personal ^personal-2", "personal", "propio")[1] == 1

    texto = "---\ntype: Note\n---\n\n# viejo\n\ncuerpo\n\n# no soy el título\n"
    assert renombrar_titulo(texto, "nuevo") == (
        "---\ntype: Note\n---\n\n# nuevo\n\ncuerpo\n\n# no soy el título\n"
    )
    assert renombrar_titulo("solo cuerpo\n", "nuevo") == "solo cuerpo\n"
