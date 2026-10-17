"""Tests unitarios de la inserción y composición de registros en AHORA.md."""

from __future__ import annotations

import pytest

from tuku.entry import _clave_hora, add, componer

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

P = "[personal](ambitos/personal/personal.md)"


def test_componer_arma_la_linea_del_registro() -> None:
    assert (
        componer(hora="14:30", scope="personal", body="**pendiente**: pagar la cuenta")
        == f"- 14:30 - {P} **pendiente**: pagar la cuenta"
    )
    assert componer(hora="08:15", scope=None, body="desayuno") == "- 08:15 - desayuno"
    assert (
        componer(hora="09:00", scope="[[trabajo]]", body="reunión")
        == "- 09:00 - [trabajo](ambitos/trabajo/trabajo.md) reunión"
    )
    rutas = {"pewma": "ambitos/trabajo/pewma/pewma.md"}
    assert (
        componer(hora="09:00", scope="pewma", body="reunión", rutas=rutas)
        == "- 09:00 - [pewma](ambitos/trabajo/pewma/pewma.md) reunión"
    )
    assert (
        componer(hora="19:05", scope="personal", body="(Hecho): avisar de los GGCC")
        == f"- 19:05 - {P} (Hecho): ~~avisar de los GGCC~~"
    )


def test_clave_hora_extrae_horas_y_minutos_y_rechaza_lo_malformado() -> None:
    assert _clave_hora("- 09:45 - registro") == (9, 45)
    assert _clave_hora("- 23:59 - fin") == (23, 59)
    for linea in ("09:45 - falta guion inicial", "- 9:45 - hora con un solo digito"):
        with pytest.raises(ValueError, match="no empieza con '- HH:MM - '"):
            _clave_hora(linea)


def test_add_respeta_lo_que_viene_despues_del_dia() -> None:
    final = "---\n(lo que el autor escriba al final)"
    ultimo = add(AHORA, ["- 09:00 - **nota**: cuerpo"], dia="Domingo 13 de septiembre")
    assert "- 09:00 - **nota**: cuerpo" in ultimo
    assert ultimo.rstrip("\n").endswith(final)

    medio = add(AHORA, ["- 08:00 - **nota**: cuerpo"], dia="Lunes 7 de septiembre")
    assert "## Domingo 13 de septiembre" in medio
    assert medio.rstrip("\n").endswith(final)

    assert add(AHORA, [], dia="Lunes 7 de septiembre") == AHORA


def test_add_es_idempotente_ordena_y_no_duplica_menciones_enlazadas() -> None:
    dia = "Lunes 7 de septiembre"
    linea = "- 10:00 - una línea"
    primero = add(AHORA, [linea], dia=dia)
    assert add(primero, [linea], dia=dia) == primero
    assert primero.count(linea) == 1

    enlazada = "- 18:40 - la boleta del [depto-centro](ambitos/depto-centro/depto-centro.md)"
    con_mencion = add(AHORA, [enlazada], dia=dia)
    assert add(con_mencion, ["- 18:40 - la boleta del depto centro"], dia=dia) == con_mencion

    texto = add(AHORA, ["- 15:00 - tarde", "- 09:00 - temprano", "- 12:00 - mediodia"], dia=dia)
    assert texto.index("- 09:00 - temprano") < texto.index("- 12:00 - mediodia")
    assert texto.index("- 12:00 - mediodia") < texto.index("- 15:00 - tarde")


def test_add_resuelve_el_dia_y_lo_inserta_en_orden() -> None:
    assert add(AHORA, ["- 10:00 - r1"], day="Lunes 7 de septiembre") == add(
        AHORA, ["- 10:00 - r1"], dia="## Lunes 7 de septiembre"
    )
    texto = add(AHORA, ["- 11:00 - registro miércoles"], dia="Miércoles 9 de septiembre")
    assert (
        texto.index("## Lunes 7 de septiembre")
        < texto.index("## Miércoles 9 de septiembre")
        < texto.index("## Domingo 13 de septiembre")
    )


def test_add_rechaza_un_dia_fuera_del_ciclo_o_inexistente() -> None:
    with pytest.raises(ValueError, match="cae fuera del ciclo abierto"):
        add(AHORA, ["- 10:00 - r"], dia="Martes 22 de septiembre")
    with pytest.raises(ValueError, match="no existe el encabezado"):
        add(
            "## Lunes 7 de septiembre\n\n- 08:00 - texto\n",
            ["- 10:00 - r"],
            dia="Viernes 11 de septiembre",
        )
