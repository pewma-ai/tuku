"""Tests de la inserción de registros en AHORA.md."""

from __future__ import annotations

from tuku.entry import add

AHORA = (
    "---\n"
    "type: Logbook\n"
    "from: 2026-09-07\n"
    "to: 2026-09-13\n"
    "---\n\n"
    "# Actividad diaria\n\n"
    "## Lunes 7 de septiembre\n\n"
    "## Domingo 13 de septiembre\n\n"
    "---\n"
    "(lo que el autor escriba al final)\n"
)


def test_add_en_el_ultimo_dia_no_se_come_lo_que_venga_despues() -> None:
    texto = add(AHORA, ["- 09:00 - **nota**: cuerpo"], dia="Domingo 13 de septiembre")

    assert "- 09:00 - **nota**: cuerpo" in texto
    assert texto.rstrip("\n").endswith("---\n(lo que el autor escriba al final)")


def test_add_en_un_dia_intermedio_no_toca_el_resto() -> None:
    texto = add(AHORA, ["- 08:00 - **nota**: cuerpo"], dia="Lunes 7 de septiembre")

    assert "## Domingo 13 de septiembre" in texto
    assert texto.rstrip("\n").endswith("---\n(lo que el autor escriba al final)")
