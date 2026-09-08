"""Tests de las dos vistas derivadas de PENDIENTES.md."""

from __future__ import annotations

from datetime import date

from tuku.propagate import documento_ambitos, propagar_ahora, region_del_dia
from tuku.todo import filas

PENDIENTES = (
    "---\n"
    "type: Pending\n"
    "---\n\n"
    "| Horizonte | Cuándo | Ámbito | Detalle |\n"
    "| --------- | ------ | ------ | ------- |\n"
    "| esta semana |  | [[personal]] | comprar una maleta |\n"
    "| con fecha | 2026-09-08 | [[personal]] | pagar la sesión con el psicólogo |\n"
    "| con fecha | 2026-09-09 |  | renovar el pasaporte |\n"
)

AHORA = (
    "---\n"
    "type: Logbook\n"
    "from: 2026-09-07\n"
    "to: 2026-09-13\n"
    "---\n\n"
    "# Actividad diaria\n\n"
    "## Lunes 7 de septiembre\n\n"
    "## Martes 8 de septiembre\n"
    "- 09:12 - [[personal]] **nota**: cuerpo\n\n"
    "## Miércoles 9 de septiembre\n\n"
    "---\n"
)


def test_region_del_dia_solo_lleva_los_de_esa_fecha() -> None:
    region = region_del_dia(filas(PENDIENTES), date(2026, 9, 8))

    assert region == [
        "> [!todo] Pendientes del día",
        "> - [[personal]] - pagar la sesión con el psicólogo",
    ]


def test_region_del_dia_sin_ambito_va_sin_enlace() -> None:
    assert region_del_dia(filas(PENDIENTES), date(2026, 9, 9)) == [
        "> [!todo] Pendientes del día",
        "> - renovar el pasaporte",
    ]


def test_un_pendiente_sin_fecha_no_aparece_en_ningun_dia() -> None:
    texto = propagar_ahora(AHORA, PENDIENTES)

    assert "comprar una maleta" not in texto


def test_la_region_se_reemplaza_entera_y_no_se_duplica() -> None:
    viejo = AHORA.replace(
        "## Martes 8 de septiembre\n",
        "## Martes 8 de septiembre\n- [[personal]] - lo que ya no toca\n",
    )
    texto = propagar_ahora(viejo, PENDIENTES)

    assert "lo que ya no toca" not in texto
    assert texto.count("> - [[personal]] - pagar la sesión con el psicólogo") == 1
    assert "- 09:12 - [[personal]] **nota**: cuerpo" in texto


def test_la_region_va_antes_del_primer_registro() -> None:
    lineas = propagar_ahora(AHORA, PENDIENTES).splitlines()
    i = lineas.index("## Martes 8 de septiembre")

    assert lineas[i + 1] == "> [!todo] Pendientes del día"
    assert lineas[i + 2] == "> - [[personal]] - pagar la sesión con el psicólogo"
    assert lineas[i + 3] == ""
    assert lineas[i + 4].startswith("- 09:12 - ")


def test_propagar_dos_veces_no_cambia_nada() -> None:
    una = propagar_ahora(AHORA, PENDIENTES)

    assert propagar_ahora(una, PENDIENTES) == una


def test_documento_de_ambitos_agrupa_por_ambito() -> None:
    documento = documento_ambitos(PENDIENTES, ["personal", "depto-centro"])

    assert "> [!todo] Pendientes en **Personal** ^personal" in documento
    assert "> - comprar una maleta" in documento
    assert "> - pagar la sesión con el psicólogo" in documento


def test_un_ambito_sin_pendientes_igual_tiene_su_callout() -> None:
    documento = documento_ambitos(PENDIENTES, ["personal", "depto-centro"])

    esperado = "> [!todo] Pendientes en **Depto Centro** ^depto-centro\n> SIN PENDIENTES"
    assert esperado in documento


def test_el_ancla_lleva_el_nombre_del_ambito_sin_md() -> None:
    documento = documento_ambitos(PENDIENTES, ["depto-centro"])
    titulos = [x for x in documento.splitlines() if x.startswith("> [!todo]")]

    assert titulos == ["> [!todo] Pendientes en **Depto Centro** ^depto-centro"]


def test_display_name_personalizado() -> None:
    documento = documento_ambitos(
        PENDIENTES,
        ["personal"],
        display_names={"personal": "Mi Vida Personal"},
    )
    assert "> [!todo] Pendientes en **Mi Vida Personal** ^personal" in documento


def test_un_pendiente_sin_ambito_no_entra_en_ningun_callout() -> None:
    documento = documento_ambitos(PENDIENTES, ["personal"])

    assert "renovar el pasaporte" not in documento


def test_el_documento_de_ambitos_es_estable() -> None:
    ambitos = ["personal", "depto-centro"]

    assert documento_ambitos(PENDIENTES, ambitos) == documento_ambitos(PENDIENTES, ambitos)
