"""Tests de las dos vistas derivadas de PENDIENTES.md."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from conftest import AHORA as INSTANTE
from tuku import init
from tuku.cli import main
from tuku.regenerate import (
    documento_ambitos,
    primer_escalon,
    region_de_la_ventana,
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


HOY = date(2026, 9, 8)

#: El foco es del autor: el bloque de la ventana va después, y el foco nunca se toca.
FOCO = "> [!abstract] Foco\n> Cerrar el trimestre del colegio.\n"

AHORA_NUEVO = (
    "---\n"
    "type: Logbook\n"
    "from: 2026-09-07\n"
    "to: 2026-09-13\n"
    "---\n"
    "# Actividad diaria\n\n"
    f"{FOCO}\n"
    "## Martes 8 de septiembre\n"
    f"- 09:12 - {P} **nota**: cuerpo\n\n"
    "## Lunes 7 de septiembre\n"
    "- 08:00 - arranque\n"
)

VENTANA = [
    "> [!todo] Pendientes de los próximos 7 días",
    f"> - {P} - comprar una maleta",
    f"> - Sep/08 - {P} - pagar la sesión con el psicólogo",
    "> - Sep/09 - renovar el pasaporte",
]


def _nuevo(ahora: str = AHORA_NUEVO, tabla: str = PENDIENTES, **kw: object) -> str:
    return vistas_en_ahora(ahora, tabla, hoy=HOY, **kw)  # type: ignore[arg-type]


def test_las_regiones_llevan_solo_lo_de_su_fecha() -> None:
    assert region_del_dia(filas(PENDIENTES), date(2026, 9, 8)) == [
        "> [!todo] Pendientes del día",
        f"> - {P} - pagar la sesión con el psicólogo",
    ]
    assert region_del_dia(filas(PENDIENTES), date(2026, 9, 9)) == [
        "> [!todo] Pendientes del día",
        "> - renovar el pasaporte",
    ], "sin ámbito va sin enlace"


def test_la_ventana_lleva_el_primer_escalon_sin_fecha_y_lo_que_vence_dentro() -> None:
    assert region_de_la_ventana(filas(PENDIENTES), HOY) == VENTANA

    lejos = PENDIENTES + "| con fecha | 2026-09-16 |  |  | llamar al banco |\n"
    assert region_de_la_ventana(filas(lejos), HOY) == VENTANA, (
        "hoy + 7 es el 15: el 16 no entra"
    )
    cerca = PENDIENTES + "| con fecha | 2026-09-15 |  |  | llamar al banco |\n"
    assert region_de_la_ventana(filas(cerca), HOY)[-1] == "> - Sep/15 - llamar al banco"
    assert (
        region_de_la_ventana(filas(lejos), HOY, ventana=10)[-1]
        == "> - Sep/16 - llamar al banco"
    )
    assert region_de_la_ventana(filas(lejos), HOY, ventana=10)[0].endswith("próximos 10 días")
    assert region_de_la_ventana(filas(PENDIENTES, "con fecha"), date(2026, 8, 1)) == []

    lejano = "| próxima semana |  | 2026-09-08 |  | sacar la basura |\n"
    assert region_de_la_ventana(filas(PENDIENTES + lejano), HOY) == VENTANA, (
        "un escalón que no es el primero y no ha vencido no entra"
    )


def test_los_atrasados_entran_a_la_ventana_marcados() -> None:
    tabla = PENDIENTES + (
        "| con fecha | 2026-09-01 | 2026-08-30 |  | pagar la patente |\n"
        "| esta semana |  | 2026-08-25 |  | ordenar el escritorio |\n"
    )
    region = region_de_la_ventana(filas(tabla), HOY)
    assert "> - Sep/01 - pagar la patente (atrasado)" in region
    assert "> - ordenar el escritorio (atrasado)" in region
    assert f"> - {P} - comprar una maleta" in region, "uno al día no lleva marca"


def test_vistas_en_ahora_rehace_el_bloque_del_dia_y_la_ventana_sin_tocar_el_foco() -> None:
    una = _nuevo()
    lineas = una.splitlines()
    i = lineas.index("# Actividad diaria")
    assert lineas[i : i + 4 + len(VENTANA) + 3] == [
        "# Actividad diaria",
        "",
        *FOCO.splitlines(),
        "",
        *VENTANA,
        "",
        "## Miércoles 9 de septiembre",
    ], "el foco queda intacto y la ventana va después"
    assert lineas.count(f"> - {P} - comprar una maleta") == 1

    j = lineas.index("## Martes 8 de septiembre")
    assert lineas[j + 1 : j + 4] == [
        "> [!todo] Pendientes del día",
        f"> - {P} - pagar la sesión con el psicólogo",
        "",
    ]
    assert lineas[j + 4].startswith("- 09:12 - ")

    assert _nuevo(una) == una, "regenerar dos veces no cambia nada"

    sin_maleta = PENDIENTES.replace(f"| esta semana |  | {P} | comprar una maleta |\n", "")
    menos = _nuevo(una, sin_maleta)
    assert "comprar una maleta" not in menos and FOCO in menos

    sin_nada = _nuevo(
        una, "| Horizonte | Vence | Ámbito | Detalle |\n| --- | --- | --- | --- |\n"
    )
    assert "Pendientes de los próximos" not in sin_nada and FOCO in sin_nada
    assert "\n\n\n" not in sin_nada


def test_el_bloque_reemplaza_al_de_la_semana_y_sin_foco_no_lo_inventa() -> None:
    viejo = AHORA_NUEVO.replace(
        FOCO + "\n", "> [!todo] Pendientes de esta semana\n> - lo viejo\n\n"
    )
    texto = _nuevo(viejo)
    assert "lo viejo" not in texto and "Pendientes de esta semana" not in texto
    assert "Cerrar el trimestre" not in texto and "[!abstract]" not in texto
    assert texto.count(VENTANA[0]) == 1

    manual = AHORA_NUEVO.replace(
        "# Actividad diaria\n\n", "# Actividad diaria\n\nUna nota del autor.\n\n"
    )
    assert "Una nota del autor.\n\n> [!abstract] Foco" in _nuevo(manual)


def test_un_dia_con_pendientes_con_fecha_nace_en_su_lugar_y_sin_hoy_no_se_toca() -> None:
    tabla = PENDIENTES + "| con fecha | 2026-09-10 |  |  | llamar al banco |\n"
    texto = _nuevo(tabla=tabla)
    orden = [
        texto.index("## Jueves 10 de septiembre"),
        texto.index("## Miércoles 9 de septiembre"),
        texto.index("## Martes 8 de septiembre"),
        texto.index("## Lunes 7 de septiembre"),
    ]
    assert orden == sorted(orden), (
        "los días futuros quedan arriba de hoy, del más nuevo al más viejo"
    )
    assert (
        "## Jueves 10 de septiembre\n> [!todo] Pendientes del día\n> - llamar al banco" in texto
    )
    assert "## Sábado 12" not in texto and "## Viernes 11" not in texto, (
        "solo nace el que hace falta"
    )
    assert texto == _nuevo(texto, tabla)

    assert vistas_en_ahora(AHORA_NUEVO, tabla).count("\n## ") == 2, (
        "sin hoy se rehacen las regiones de los días que hay, pero no nace ninguno"
    )
    fuera = "| con fecha | 2026-09-30 |  |  | mucho después |\n"
    assert "## Miércoles 30" not in _nuevo(tabla=PENDIENTES + fuera), "fuera de la ventana"


def test_vistas_en_ahora_rehace_las_regiones_enteras() -> None:
    viejo = AHORA_NUEVO.replace(
        "## Martes 8 de septiembre\n",
        f"## Martes 8 de septiembre\n- {P} - lo que ya no toca\n",
    )
    texto = _nuevo(viejo)
    assert "lo que ya no toca" not in texto
    assert texto.count(f"- {P} - pagar la sesión con el psicólogo") == 2, "día y ventana"
    assert f"- 09:12 - {P} **nota**: cuerpo" in texto

    con_registro = AHORA_NUEVO.replace(
        "## Martes 8 de septiembre\n",
        f"## Martes 8 de septiembre\n- {P} recordé la reunión con Ximena\n",
    )
    assert f"- {P} recordé la reunión con Ximena" in _nuevo(con_registro), (
        "un registro sin hora no es parte de la región"
    )


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


def test_el_primer_escalon_del_autor_entra_a_la_ventana_aunque_lo_renombre(
    tmp_path: Path,
) -> None:
    raiz = Path(__file__).resolve().parent.parent.parent
    vault = init.init(tmp_path / "v", home=raiz)
    assert primer_escalon(vault) == "esta semana"

    reglas = vault / "reglas" / "pendientes.user.md"
    reglas.write_text(
        re.sub(r"\| `esta semana`", "| `este turno`", reglas.read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    assert primer_escalon(vault) == "este turno"

    argv = ["todo", "open", "--body", "pagar la patente", "--vault", str(vault)]
    assert main(argv, now=INSTANTE) == 0
    pendientes = (vault / "PENDIENTES.md").read_text(encoding="utf-8")
    assert "| este turno |" in pendientes, "sin horizonte, el primero de la escalera del autor"
    ahora = (vault / "AHORA.md").read_text(encoding="utf-8")
    assert "> [!todo] Pendientes de los próximos 7 días" in ahora
    bloque = ahora.split("Pendientes de los próximos 7 días")[1].split("\n\n")[0]
    assert "pagar la patente" in bloque
