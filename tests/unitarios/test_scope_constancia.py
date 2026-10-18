"""Tests unitarios de la constancia que deja `tuku scope create` en la bitácora."""

from __future__ import annotations

from tuku import scope


def test_la_constancia_lleva_la_ruta_del_ambito_y_dice_donde_quedo() -> None:
    assert scope.registro_de_constancia("depto-centro", hour="18:45") == (
        "- 18:45 - [depto-centro](ambitos/depto-centro/depto-centro.md) "
        "**nota**: abrí el ámbito"
    )
    rutas = {"pewma": "ambitos/trabajo/pewma/pewma.md"}
    assert scope.registro_de_constancia("pewma", hour="09:00", rutas=rutas) == (
        "- 09:00 - [pewma](ambitos/trabajo/pewma/pewma.md) **nota**: abrí el ámbito"
    )
    # los lectores la reconocen por el cuerpo fijo, sin depender de la hora
    assert scope.CONSTANCIA in scope.registro_de_constancia("x", hour="")

    rutas = {"bodega": "ambitos/negocio/bodega/bodega.md"}
    enlace = "[negocio](ambitos/negocio/negocio.md)"
    assert scope.registro_de_constancia("bodega", hour="07:48", rutas=rutas, bajo=enlace) == (
        "- 07:48 - [bodega](ambitos/negocio/bodega/bodega.md) "
        f"**nota**: abrí el ámbito bajo {enlace}"
    )
    assert scope.registro_de_constancia("x", hour="07:48", bajo="clientes").endswith(
        "abrí el ámbito bajo clientes"
    )
