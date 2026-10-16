"""Tests unitarios de `reglas/comandos.tuku.md`, generado desde argparse."""

from __future__ import annotations

import argparse

from tuku import cli
from tuku.cli import manual


def _parser() -> argparse.ArgumentParser:
    raiz = argparse.ArgumentParser(prog="tuku")
    sub = raiz.add_subparsers(dest="noun")
    sub.add_parser("init", description="Siembra  un\nvault.", epilog="A mano: copiar.")
    entry = sub.add_parser("entry", description="Registros.")
    verbos = entry.add_subparsers(dest="verb")
    verbos.add_parser("add", description="Escribe un registro.", epilog="A mano: escribirlo.")
    verbos.add_parser("lint")
    return raiz


def test_entran_las_hojas_y_no_los_sustantivos_con_verbos() -> None:
    nombres = [e.nombre for e in manual.entradas(_parser())]
    assert nombres == ["tuku init", "tuku entry add", "tuku entry lint"]


def test_la_entrada_normaliza_espacios_y_quita_el_prefijo_a_mano() -> None:
    init = manual.entradas(_parser())[0]
    assert init.que_hace == "Siembra un vault."
    assert init.a_mano == "copiar."


def test_lo_que_falta_se_dice_en_vez_de_omitirse() -> None:
    texto = manual.documento(manual.entradas(_parser()))
    assert "## tuku entry lint\n\n**Qué hace:** sin declarar.\n**A mano:** sin declarar.\n" in (
        texto
    )


def test_el_documento_es_determinista_y_lleva_type() -> None:
    lista = manual.entradas(_parser())
    texto = manual.documento(lista)
    assert texto == manual.documento(lista)
    assert texto.startswith("---\ntype: Config\n---\n")


def test_un_parser_vacio_deja_solo_el_encabezado() -> None:
    assert manual.documento([]).startswith("---\ntype: Config\n---\n")
    assert "## " not in manual.documento([])


def test_todo_comando_del_cli_declara_como_hacerlo_a_mano() -> None:
    """Principio 1: un comando sin su "A mano" es una dependencia disfrazada."""
    sin = [e.nombre for e in manual.entradas(cli._construir_parser()) if not e.a_mano]
    assert not sin, f"sin epilog 'A mano': {sin}"
