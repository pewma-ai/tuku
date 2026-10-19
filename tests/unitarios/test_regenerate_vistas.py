"""Tests de las dos vistas derivadas de PENDIENTES.md."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from conftest import AHORA as INSTANTE
from tuku import init
from tuku.cli import main
from tuku.regenerate import (
    documento_ambitos,
    primer_escalon,
    region_de_la_semana,
    region_del_dia,
    vistas_en_ahora,
)
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


def test_las_regiones_llevan_solo_lo_de_su_fecha() -> None:
    assert region_del_dia(filas(PENDIENTES), date(2026, 9, 8)) == [
        "> [!todo] Pendientes del día",
        f"> - {P} - pagar la sesión con el psicólogo",
    ]
    assert region_del_dia(filas(PENDIENTES), date(2026, 9, 9)) == [
        "> [!todo] Pendientes del día",
        "> - renovar el pasaporte",
    ], "sin ámbito va sin enlace"

    assert region_de_la_semana(filas(PENDIENTES)) == [
        "> [!todo] Pendientes de esta semana",
        f"> - {P} - comprar una maleta",
    ]
    assert region_de_la_semana(filas(PENDIENTES, "con fecha")) == []


def test_vistas_en_ahora_rehace_las_regiones_enteras() -> None:
    una = vistas_en_ahora(AHORA, PENDIENTES)
    lineas = una.splitlines()
    i = lineas.index("# Actividad diaria")
    assert lineas[i + 1 : i + 5] == [
        "",
        "> [!todo] Pendientes de esta semana",
        f"> - {P} - comprar una maleta",
        "",
    ], "la semana va bajo el título"
    assert lineas[i + 5] == "## Lunes 7 de septiembre"

    sin_maleta = PENDIENTES.replace(f"| esta semana |  | {P} | comprar una maleta |\n", "")
    texto = vistas_en_ahora(una, sin_maleta)
    assert "Pendientes de esta semana" not in texto
    sin = texto.splitlines()
    assert sin[sin.index("# Actividad diaria") + 1 :][:2] == ["", "## Lunes 7 de septiembre"]

    assert lineas.count(f"> - {P} - comprar una maleta") == 1, "solo en el callout de la semana"
    assert lineas.index("## Lunes 7 de septiembre") > lineas.index(
        f"> - {P} - comprar una maleta"
    )
    j = lineas.index("## Martes 8 de septiembre")
    assert lineas[j + 1] == "> [!todo] Pendientes del día"
    assert lineas[j + 2] == f"> - {P} - pagar la sesión con el psicólogo"
    assert lineas[j + 3] == ""
    assert lineas[j + 4].startswith("- 09:12 - ")

    viejo = AHORA.replace(
        "## Martes 8 de septiembre\n",
        f"## Martes 8 de septiembre\n- {P} - lo que ya no toca\n",
    )
    texto = vistas_en_ahora(viejo, PENDIENTES)
    assert "lo que ya no toca" not in texto
    assert texto.count(f"> - {P} - pagar la sesión con el psicólogo") == 1
    assert f"- 09:12 - {P} **nota**: cuerpo" in texto

    assert vistas_en_ahora(una, PENDIENTES) == una, "regenerar dos veces no cambia nada"

    con_registro = AHORA.replace(
        "## Martes 8 de septiembre\n",
        f"## Martes 8 de septiembre\n- {P} recordé la reunión con Ximena\n",
    )
    assert f"- {P} recordé la reunión con Ximena" in vistas_en_ahora(
        con_registro, PENDIENTES
    ), "un registro sin hora no es parte de la región"


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
    ], "van primero los fechados, por fecha"


def test_el_primer_escalon_del_autor_titula_el_callout_aunque_lo_renombre(
    tmp_path: Path,
) -> None:
    raiz = Path(__file__).resolve().parent.parent.parent
    vault = init.init(tmp_path / "v", home=raiz, desde=INSTANTE.date())
    assert primer_escalon(vault) == "esta semana"

    reglas = vault / "reglas" / "pendientes.md"
    reglas.write_text(
        reglas.read_text(encoding="utf-8").replace("| `esta semana` |", "| `este turno` |"),
        encoding="utf-8",
    )
    assert primer_escalon(vault) == "este turno"

    argv = ["todo", "open", "--body", "pagar la patente", "--vault", str(vault)]
    assert main(argv, now=INSTANTE) == 0
    pendientes = (vault / "PENDIENTES.md").read_text(encoding="utf-8")
    assert "| este turno |" in pendientes, "sin horizonte, el primero de la escalera del autor"
    ahora = (vault / "AHORA.md").read_text(encoding="utf-8")
    assert "> [!todo] Pendientes de este turno" in ahora
    assert "pagar la patente" in ahora.split("Pendientes de este turno")[1].split("\n\n")[0]
