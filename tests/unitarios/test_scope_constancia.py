"""Tests unitarios de la constancia que deja `tuku scope create` en la bitácora."""

from __future__ import annotations

from tuku import scope


def test_constancia_de_un_ambito_plano() -> None:
    assert scope.registro_de_constancia("depto-centro", hora="18:45") == (
        "- 18:45 - [depto-centro](ambitos/depto-centro/depto-centro.md) "
        "**nota**: abrí el ámbito"
    )


def test_constancia_de_un_ambito_anidado_lleva_su_ruta() -> None:
    rutas = {"pewma": "ambitos/trabajo/pewma/pewma.md"}
    linea = scope.registro_de_constancia("pewma", hora="09:00", rutas=rutas)
    assert linea == "- 09:00 - [pewma](ambitos/trabajo/pewma/pewma.md) **nota**: abrí el ámbito"


def test_constancia_termina_en_el_cuerpo_fijo() -> None:
    """Los lectores la reconocen por el final, sin depender de la hora."""
    assert scope.registro_de_constancia("x", hora="").endswith(scope.CONSTANCIA)
