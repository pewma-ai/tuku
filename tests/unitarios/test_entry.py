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


def test_componer_con_scope_y_body() -> None:
    linea = componer(hora="14:30", scope="personal", body="**pendiente**: pagar la cuenta")
    assert linea == "- 14:30 - [[personal]] **pendiente**: pagar la cuenta"


def test_componer_sin_scope() -> None:
    linea = componer(hora="08:15", scope=None, body="desayuno con equipo")
    assert linea == "- 08:15 - desayuno con equipo"


def test_componer_con_corchetes_preexistentes_en_scope() -> None:
    linea = componer(hora="09:00", scope="[[trabajo]]", body="reunión")
    assert linea == "- 09:00 - [[trabajo]] reunión"


def test_clave_hora_extrae_horas_y_minutos() -> None:
    assert _clave_hora("- 09:45 - registro") == (9, 45)
    assert _clave_hora("- 00:00 - inicio") == (0, 0)
    assert _clave_hora("- 23:59 - fin") == (23, 59)


def test_clave_hora_linea_malformada_lanza_value_error() -> None:
    with pytest.raises(ValueError, match="no empieza con '- HH:MM - '"):
        _clave_hora("09:45 - falta guion inicial")

    with pytest.raises(ValueError, match="no empieza con '- HH:MM - '"):
        _clave_hora("- 9:45 - hora con un solo digito")


def test_add_en_el_ultimo_dia_no_se_come_lo_que_venga_despues() -> None:
    texto = add(AHORA, ["- 09:00 - **nota**: cuerpo"], dia="Domingo 13 de septiembre")
    assert "- 09:00 - **nota**: cuerpo" in texto
    assert texto.rstrip("\n").endswith("---\n(lo que el autor escriba al final)")


def test_add_en_un_dia_intermedio_no_toca_el_resto() -> None:
    texto = add(AHORA, ["- 08:00 - **nota**: cuerpo"], dia="Lunes 7 de septiembre")
    assert "## Domingo 13 de septiembre" in texto
    assert texto.rstrip("\n").endswith("---\n(lo que el autor escriba al final)")


def test_add_idempotente_no_duplica_lineas() -> None:
    linea = "- 10:00 - una línea"
    primero = add(AHORA, [linea], dia="Lunes 7 de septiembre")
    segundo = add(primero, [linea], dia="Lunes 7 de septiembre")
    assert primero == segundo
    assert segundo.count(linea) == 1


def test_add_ordena_por_hora_cronologicamente() -> None:
    lineas = [
        "- 15:00 - tarde",
        "- 09:00 - temprano",
        "- 12:00 - mediodia",
    ]
    texto = add(AHORA, lineas, dia="Lunes 7 de septiembre")
    idx_09 = texto.index("- 09:00 - temprano")
    idx_12 = texto.index("- 12:00 - mediodia")
    idx_15 = texto.index("- 15:00 - tarde")
    assert idx_09 < idx_12 < idx_15


def test_add_acepta_day_o_dia_con_o_sin_prefijo_hash() -> None:
    texto1 = add(AHORA, ["- 10:00 - r1"], day="Lunes 7 de septiembre")
    texto2 = add(AHORA, ["- 10:00 - r1"], dia="## Lunes 7 de septiembre")
    assert texto1 == texto2


def test_add_inserta_dia_nuevo_dentro_del_rango_en_orden() -> None:
    # AHORA tiene Lunes 7 y Domingo 13. Agregamos Miércoles 9.
    texto = add(AHORA, ["- 11:00 - registro miércoles"], dia="Miércoles 9 de septiembre")
    assert "## Miércoles 9 de septiembre" in texto
    idx_lun = texto.index("## Lunes 7 de septiembre")
    idx_mie = texto.index("## Miércoles 9 de septiembre")
    idx_dom = texto.index("## Domingo 13 de septiembre")
    assert idx_lun < idx_mie < idx_dom


def test_add_dia_fuera_del_rango_lanza_value_error() -> None:
    with pytest.raises(ValueError, match="cae fuera del ciclo abierto"):
        add(AHORA, ["- 10:00 - r"], dia="Martes 22 de septiembre")


def test_add_sin_rango_y_encabezado_inexistente_lanza_value_error() -> None:
    ahora_sin_fm = "## Lunes 7 de septiembre\n\n- 08:00 - texto\n"
    with pytest.raises(ValueError, match="no existe el encabezado"):
        add(ahora_sin_fm, ["- 10:00 - r"], dia="Viernes 11 de septiembre")


def test_add_sin_lineas_devuelve_texto_intacto() -> None:
    assert add(AHORA, [], dia="Lunes 7 de septiembre") == AHORA
