"""Tests de las dos vistas derivadas de PENDIENTES.md."""

from __future__ import annotations

from datetime import date

from tuku.propagate import documento_ambitos, propagar_ahora, region_del_dia
from tuku.todo import filas

P = "[personal](ambitos/personal/personal.md)"

PENDIENTES = (
    "---\n"
    "type: Todo\n"
    "---\n\n"
    "| Horizonte | Vence | Ámbito | Detalle |\n"
    "| --------- | ------ | ------ | ------- |\n"
    f"| esta semana |  | {P} | comprar una maleta |\n"
    f"| con fecha | 2026-09-08 | {P} | pagar la sesión con el psicólogo |\n"
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
    f"- 09:12 - {P} **nota**: cuerpo\n\n"
    "## Miércoles 9 de septiembre\n\n"
    "---\n"
)


def test_region_del_dia_solo_lleva_los_de_esa_fecha() -> None:
    assert region_del_dia(filas(PENDIENTES), date(2026, 9, 8)) == [
        "> [!todo] Pendientes del día",
        f"> - {P} - pagar la sesión con el psicólogo",
    ]
    assert region_del_dia(filas(PENDIENTES), date(2026, 9, 9)) == [
        "> [!todo] Pendientes del día",
        "> - renovar el pasaporte",
    ], "sin ámbito va sin enlace"


def test_propagar_ahora_reemplaza_la_region_entera_antes_del_primer_registro() -> None:
    una = propagar_ahora(AHORA, PENDIENTES)
    assert "comprar una maleta" not in una, "un pendiente sin fecha no aparece en ningún día"

    lineas = una.splitlines()
    i = lineas.index("## Martes 8 de septiembre")
    assert lineas[i + 1] == "> [!todo] Pendientes del día"
    assert lineas[i + 2] == f"> - {P} - pagar la sesión con el psicólogo"
    assert lineas[i + 3] == ""
    assert lineas[i + 4].startswith("- 09:12 - ")

    viejo = AHORA.replace(
        "## Martes 8 de septiembre\n",
        f"## Martes 8 de septiembre\n- {P} - lo que ya no toca\n",
    )
    texto = propagar_ahora(viejo, PENDIENTES)
    assert "lo que ya no toca" not in texto
    assert texto.count(f"> - {P} - pagar la sesión con el psicólogo") == 1
    assert f"- 09:12 - {P} **nota**: cuerpo" in texto

    assert propagar_ahora(una, PENDIENTES) == una, "propagar dos veces no cambia nada"


def test_documento_de_ambitos_agrupa_ordena_y_deja_su_callout_a_cada_ambito() -> None:
    documento = documento_ambitos(PENDIENTES, ["personal", "depto-centro"])
    assert "> [!todo] Pendientes en **Personal** ^personal" in documento
    assert "> - comprar una maleta" in documento
    assert "> - Sep/08 - pagar la sesión con el psicólogo" in documento
    assert "renovar el pasaporte" not in documento, "sin ámbito no entra en ningún callout"
    assert [b.strip() for b in documento.split("\n\n") if "Depto Centro" in b] == [
        "> [!todo] Pendientes en **Depto Centro** ^depto-centro"
    ], "un ámbito sin pendientes igual tiene su callout"
    assert documento == documento_ambitos(PENDIENTES, ["personal", "depto-centro"])

    personalizado = documento_ambitos(
        PENDIENTES, ["personal"], display_names={"personal": "Mi Vida Personal"}
    )
    assert "> [!todo] Pendientes en **Mi Vida Personal** ^personal" in personalizado

    formato = documento_ambitos(PENDIENTES, ["personal"], formato="DD/MM/AAAA")
    assert "> - 08/09/2026 - pagar la sesión con el psicólogo" in formato


def test_en_el_ambito_van_primero_los_fechados_por_fecha() -> None:
    tabla = PENDIENTES + (
        f"| con fecha | 2026-09-07 | {P} | llamar al banco |\n"
        f"| esta semana |  | {P} | ordenar el escritorio |\n"
    )
    callout = documento_ambitos(tabla, ["personal"]).split("^personal\n", 1)[1]

    assert callout.splitlines() == [
        "> - Sep/07 - llamar al banco",
        "> - Sep/08 - pagar la sesión con el psicólogo",
        "> - comprar una maleta",
        "> - ordenar el escritorio",
    ]
