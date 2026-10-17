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


def test_cada_sustantivo_entra_con_sus_verbos_anidados_y_descripcion_normalizada() -> None:
    entradas = manual.entradas(_parser())
    assert [(e.nombre, e.nivel, e.invocable) for e in entradas] == [
        ("tuku init", 1, True),
        ("tuku entry", 1, False),
        ("tuku entry add", 2, True),
        ("tuku entry lint", 2, True),
    ]
    assert entradas[0].que_hace == "Siembra un vault."


def test_el_documento_es_determinista_anida_y_dice_lo_que_falta() -> None:
    entradas = manual.entradas(_parser())
    texto = manual.documento(entradas)
    assert texto == manual.documento(entradas)
    assert texto.startswith("---\ntype: Config\n---\n")
    assert "\n## tuku entry\n\nRegistros.\n" in texto
    assert "\n### tuku entry add\n\nEscribe un registro.\n" in texto
    assert "### tuku entry lint\n\nSin descripción.\n" in texto

    vacio = manual.documento([])
    assert vacio.startswith("---\ntype: Config\n---\n") and "## " not in vacio


def test_toda_ayuda_dice_que_archivos_del_vault_toca() -> None:
    """Principio 1: la ayuda alcanza para hacerlo sin `tuku`, y sin jerga de código."""
    archivos = (".md", "ambitos/", "notas/", "reglas/", "template/")
    jerga = ("def ", "import ", "module", "function", "class ")
    entradas = manual.entradas(cli._construir_parser())
    assert len(entradas) > 20
    for e in entradas:
        assert e.que_hace.strip(), f"{e.nombre} no tiene descripción"
        if e.invocable:
            assert any(a in e.que_hace for a in archivos), f"{e.nombre} no nombra archivos"
            assert not any(j in e.que_hace for j in jerga), f"{e.nombre} usa jerga de código"
