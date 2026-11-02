"""Tests unitarios de la inserción y composición de registros en AHORA.md."""

from __future__ import annotations

from datetime import date

import pytest

from tuku.entry import _claves, add, componer

AHORA = (
    "---\n"
    "type: Logbook\n"
    "from: 2026-09-07\n"
    "to: 2026-09-13\n"
    "---\n\n"
    "# Actividad diaria\n\n"
    "## Domingo 13 de septiembre\n\n"
    "## Lunes 7 de septiembre\n\n"
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


def _seccion(texto: str, dia: str) -> list[str]:
    return texto.split(f"## {dia}\n", 1)[1].split("\n\n", 1)[0].splitlines()


def test_la_clave_de_un_registro_sin_hora_es_la_del_mas_antiguo_que_le_sigue() -> None:
    previas = [
        "- 23:59 - fin",
        "- llamé a Rodolfo",
        "- 09:45 - registro",
        "- sin hora al fondo",
    ]
    assert _claves(previas) == [(23, 59), (9, 45), (9, 45), (0, 0)]
    with pytest.raises(ValueError, match="un registro empieza con '- '"):
        add(AHORA, ["09:45 - falta guion inicial"], dia="Lunes 7 de septiembre")


def test_add_ordena_por_hora_descendente_y_el_nuevo_queda_arriba_entre_iguales() -> None:
    dia = "Lunes 7 de septiembre"
    texto = add(AHORA, ["- 10:00 - **nota**: primero"], dia=dia)
    texto = add(texto, ["- 08:00 - **nota**: temprano", "- 11:00 - **nota**: después"], dia=dia)
    assert _seccion(texto, dia) == [
        "- 11:00 - **nota**: después",
        "- 10:00 - **nota**: primero",
        "- 08:00 - **nota**: temprano",
    ]
    texto = add(texto, ["- 10:00 - **nota**: otro a la misma hora"], dia=dia)
    assert _seccion(texto, dia)[1:3] == [
        "- 10:00 - **nota**: otro a la misma hora",
        "- 10:00 - **nota**: primero",
    ]

    desordenadas = add(
        AHORA, ["- 15:00 - tarde", "- 09:00 - temprano", "- 12:00 - mediodia"], dia=dia
    )
    assert _seccion(desordenadas, dia) == [
        "- 15:00 - tarde",
        "- 12:00 - mediodia",
        "- 09:00 - temprano",
    ]


def test_un_registro_nuevo_sin_hora_queda_arriba_y_uno_existente_conserva_su_lugar() -> None:
    dia = "Lunes 7 de septiembre"
    base = add(AHORA, ["- 11:00 - a", "- 09:00 - b"], dia=dia)
    texto = add(base, ["- llamé a Rodolfo"], dia=dia)
    assert _seccion(texto, dia) == ["- llamé a Rodolfo", "- 11:00 - a", "- 09:00 - b"]

    con_hora = add(texto, ["- 11:00 - c", "- 10:00 - d"], dia=dia)
    assert _seccion(con_hora, dia) == [
        "- 11:00 - c",
        "- llamé a Rodolfo",
        "- 11:00 - a",
        "- 10:00 - d",
        "- 09:00 - b",
    ]
    assert add(con_hora, ["- llamé a Rodolfo"], dia=dia) == con_hora, "idempotente"


def test_add_respeta_lo_que_viene_despues_del_dia() -> None:
    final = "---\n(lo que el autor escriba al final)"
    ultimo = add(AHORA, ["- 09:00 - **nota**: cuerpo"], dia="Domingo 13 de septiembre")
    assert "- 09:00 - **nota**: cuerpo" in ultimo
    assert ultimo.rstrip("\n").endswith(final)

    medio = add(AHORA, ["- 08:00 - **nota**: cuerpo"], dia="Lunes 7 de septiembre")
    assert "## Domingo 13 de septiembre" in medio
    assert medio.rstrip("\n").endswith(final)

    assert add(AHORA, [], dia="Lunes 7 de septiembre") == AHORA


def test_add_es_idempotente_y_no_duplica_menciones_enlazadas() -> None:
    dia = "Lunes 7 de septiembre"
    linea = "- 10:00 - una línea"
    primero = add(AHORA, [linea], dia=dia)
    assert add(primero, [linea], dia=dia) == primero
    assert primero.count(linea) == 1

    enlazada = "- 18:40 - la boleta del [depto-centro](ambitos/depto-centro/depto-centro.md)"
    con_mencion = add(AHORA, [enlazada], dia=dia)
    assert add(con_mencion, ["- 18:40 - la boleta del depto centro"], dia=dia) == con_mencion


def test_add_crea_el_dia_en_su_lugar_entre_los_del_mas_nuevo_al_mas_viejo() -> None:
    assert add(AHORA, ["- 10:00 - r1"], day="Lunes 7 de septiembre") == add(
        AHORA, ["- 10:00 - r1"], dia="## Lunes 7 de septiembre"
    )
    texto = add(AHORA, ["- 11:00 - registro miércoles"], dia="Miércoles 9 de septiembre")
    assert (
        texto.index("## Domingo 13 de septiembre")
        < texto.index("## Miércoles 9 de septiembre")
        < texto.index("## Lunes 7 de septiembre")
    )
    nuevo = add(texto, ["- 08:00 - r"], dia="Martes 8 de septiembre")
    assert (
        nuevo.index("## Miércoles 9") < nuevo.index("## Martes 8") < nuevo.index("## Lunes 7")
    )
    assert add(nuevo, ["- 08:00 - r"], dia="Martes 8 de septiembre") == nuevo

    sin_lunes = AHORA.replace("## Lunes 7 de septiembre\n\n", "")
    assert add(sin_lunes, ["- 08:00 - r"], dia="Lunes 7 de septiembre").endswith(
        "## Lunes 7 de septiembre\n- 08:00 - r\n\n---\n(lo que el autor escriba al final)\n"
    ), "un día más viejo que todos va antes del cierre del archivo"


def test_add_conserva_el_callout_de_pendientes_del_dia() -> None:
    con_callout = AHORA.replace(
        "## Lunes 7 de septiembre\n",
        "## Lunes 7 de septiembre\n> [!todo] Pendientes del día\n> - llamar\n",
    )
    texto = add(con_callout, ["- 10:00 - r"], dia="Lunes 7 de septiembre")
    assert (
        "## Lunes 7 de septiembre\n> [!todo] Pendientes del día\n> - llamar\n\n- 10:00 - r"
        in texto
    )


def test_add_crea_un_dia_fuera_del_rango_y_rechaza_si_no_hay_rango() -> None:
    texto = add(AHORA, ["- 10:00 - r"], dia="Martes 22 de septiembre")
    assert texto.index("## Martes 22 de septiembre") < texto.index(
        "## Domingo 13 de septiembre"
    )
    assert "## Martes 22 de septiembre\n- 10:00 - r\n" in texto

    lejano = add(AHORA, ["- 10:00 - r"], dia="Jueves 4 de marzo", fecha=date(2021, 3, 4))
    assert lejano.index("## Lunes 7 de septiembre") < lejano.index("## Jueves 4 de marzo")

    with pytest.raises(ValueError, match="no existe el encabezado"):
        add(
            "## Lunes 7 de septiembre\n\n- 08:00 - texto\n",
            ["- 10:00 - r"],
            dia="Viernes 11 de septiembre",
        )
