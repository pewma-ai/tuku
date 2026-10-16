"""Tests unitarios de `reglas/comandos.tuku.md`, generado desde argparse."""

from __future__ import annotations

import argparse

from tuku import cli
from tuku.cli import manual


def _parser() -> argparse.ArgumentParser:
    raiz = argparse.ArgumentParser(prog="tuku")
    sub = raiz.add_subparsers(dest="noun")
    sub.add_parser("init", description="Siembra  un\nvault.")
    entry = sub.add_parser("entry", description="Registros.")
    verbos = entry.add_subparsers(dest="verb")
    verbos.add_parser("add", description="Escribe un registro.")
    verbos.add_parser("lint")
    return raiz


def test_entran_las_hojas_y_no_los_sustantivos_con_verbos() -> None:
    nombres = [e.nombre for e in manual.entradas(_parser())]
    assert nombres == ["tuku init", "tuku entry add", "tuku entry lint"]


def test_la_entrada_normaliza_espacios() -> None:
    assert manual.entradas(_parser())[0].que_hace == "Siembra un vault."


def test_lo_que_falta_se_dice_en_vez_de_omitirse() -> None:
    texto = manual.documento(manual.entradas(_parser()))
    assert "## tuku entry lint\n\nSin descripción.\n" in texto


def test_el_documento_es_determinista_y_lleva_type() -> None:
    lista = manual.entradas(_parser())
    texto = manual.documento(lista)
    assert texto == manual.documento(lista)
    assert texto.startswith("---\ntype: Config\n---\n")


def test_un_parser_vacio_deja_solo_el_encabezado() -> None:
    assert manual.documento([]).startswith("---\ntype: Config\n---\n")
    assert "## " not in manual.documento([])


def test_toda_ayuda_dice_que_archivos_del_vault_toca() -> None:
    """Principio 1: la ayuda alcanza para hacerlo sin `tuku`, y sin jerga de código."""
    archivos = (".md", "ambitos/", "notas/", "reglas/", "template/")
    jerga = ("def ", "import ", "module", "function", "class ")
    for e in manual.entradas(cli._construir_parser()):
        texto = e.que_hace
        assert texto, f"{e.nombre} no tiene descripción"
        assert any(a in texto for a in archivos), f"{e.nombre} no nombra archivos del vault"
        assert not any(j in texto for j in jerga), f"{e.nombre} usa jerga de código"
