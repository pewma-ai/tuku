"""Tests unitarios de la constancia que deja `tuku scope create` en la bitácora."""

from __future__ import annotations

from tuku import scope


def test_la_constancia_lleva_la_ruta_del_ambito_y_termina_en_el_cuerpo_fijo() -> None:
    assert scope.registro_de_constancia("depto-centro", hour="18:45") == (
        "- 18:45 - [depto-centro](ambitos/depto-centro/depto-centro.md) "
        "**nota**: abrí el ámbito"
    )
    rutas = {"pewma": "ambitos/trabajo/pewma/pewma.md"}
    assert scope.registro_de_constancia("pewma", hour="09:00", rutas=rutas) == (
        "- 09:00 - [pewma](ambitos/trabajo/pewma/pewma.md) **nota**: abrí el ámbito"
    )
    # los lectores la reconocen por el final, sin depender de la hora
    assert scope.registro_de_constancia("x", hour="").endswith(scope.CONSTANCIA)
