"""Unitarios de `tuku.todo`: la tabla única de `PENDIENTES.md`.

`todo.py` es el corazón de los pendientes y era el módulo puro más grande sin
un solo test unitario: se probaba entero por escenarios E2E, que son caros y
tardan en decir dónde está el fallo.

Todo lo que hay acá opera sobre texto en memoria, sin tocar disco. Los casos de
uso que sí escriben (`abrir_en_vault`, `cerrar_en_vault`) quedan para los
escenarios, que es donde se verifican sus efectos completos.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from tuku import todo  # noqa: E402

VACIA = f"# Pendientes\n\n{todo.CABECERA}\n| --- | --- | --- | --- |\n"

pytestmark = pytest.mark.unitario


def _con(*lineas: str) -> str:
    return VACIA + "".join(f"{linea}\n" for linea in lineas)


# --- parsear: qué le pide una línea de bitácora a PENDIENTES.md -------------


def test_parsear_reconoce_una_apertura_con_ambito() -> None:
    marca = todo.parsear("- 14:20 - [[personal]] **pendiente**: comprar una maleta")
    assert marca is not None
    assert marca.marca == todo.ABRE
    assert marca.ambito == "personal"
    assert marca.cuerpo == "comprar una maleta"


def test_parsear_reconoce_un_cierre_sin_ambito() -> None:
    marca = todo.parsear("- 19:05 - ~~(Hecho)~~: comprar una maleta")
    assert marca is not None
    assert marca.marca == todo.CIERRA
    assert marca.ambito is None


def test_parsear_es_estricto_con_la_ontologia_cerrada() -> None:
    """`**Pendiente**` no es `**pendiente**`: el comando no interpreta."""
    assert todo.parsear("- 13:00 - [[personal]] **Pendiente**: comprar una maleta") is None


@pytest.mark.parametrize(
    "linea",
    [
        "",
        "- 14:20 - un registro cualquiera sin marca",
        "no es una línea de registro",
        "- 14:20 - **pendiente** sin dos puntos",
    ],
)
def test_parsear_devuelve_none_ante_lo_que_no_es_una_marca(linea: str) -> None:
    assert todo.parsear(linea) is None


# --- abrir: copiar el cuerpo literal ---------------------------------------


def test_abrir_copia_el_cuerpo_literal_como_fila() -> None:
    marca = todo.parsear("- 14:20 - [[personal]] **pendiente**: avisar de los GGCC")
    assert marca is not None

    texto = todo.abrir(VACIA, marca)

    assert "| esta semana |  | [[personal]] | avisar de los GGCC |" in texto
    assert todo.cuerpos(texto, "esta semana") == ["avisar de los GGCC"]


def test_abrir_dos_veces_no_duplica_la_fila() -> None:
    marca = todo.parsear("- 14:20 - [[personal]] **pendiente**: avisar de los GGCC")
    assert marca is not None

    una = todo.abrir(VACIA, marca)
    dos = todo.abrir(una, marca)

    assert una == dos, "un registro repetido no abre dos veces el mismo pendiente"
    assert len(todo.filas(dos)) == 1


def test_abrir_con_fecha_deja_la_fecha_en_la_columna_cuando() -> None:
    marca = todo.parsear("- 09:00 - [[personal]] **pendiente**: pagar la sesión")
    assert marca is not None

    texto = todo.abrir(VACIA, marca, horizon=todo.CON_FECHA, when="2026-08-12")

    fila = todo.filas(texto)[0]
    assert fila.horizonte == todo.CON_FECHA
    assert fila.cuando == "2026-08-12"
    assert todo.cuerpos(texto, "esta semana") == [], "no debía pasar por la escalera"


def test_abrir_sin_tabla_se_niega_en_vez_de_inventarla() -> None:
    with pytest.raises(todo.SinTabla):
        marca = todo.parsear("- 14:20 - **pendiente**: algo")
        assert marca is not None
        todo.abrir("# Pendientes\n\nsin tabla acá.\n", marca)


# --- cerrar: borrar, y no inventar nada ------------------------------------


def test_cerrar_borra_la_fila_y_deja_la_cabecera() -> None:
    abre = todo.parsear("- 14:20 - [[personal]] **pendiente**: avisar de los GGCC")
    cierra = todo.parsear("- 19:05 - [[personal]] ~~(Hecho)~~: avisar de los GGCC")
    assert abre is not None and cierra is not None

    texto, hubo_pareja = todo.cerrar(todo.abrir(VACIA, abre), cierra)

    assert hubo_pareja
    assert todo.filas(texto) == []
    assert todo.CABECERA in texto, "se perdió la cabecera de la tabla"


def test_cerrar_sin_pareja_no_toca_nada_y_lo_dice() -> None:
    """El caso negativo más importante: un cierre inventado deja el archivo mintiendo."""
    cierra = todo.parsear("- 19:10 - [[personal]] ~~(Hecho)~~: comprar una maleta")
    assert cierra is not None

    texto, hubo_pareja = todo.cerrar(VACIA, cierra)

    assert not hubo_pareja
    assert texto == VACIA, "PENDIENTES.md cambió ante un cierre sin pareja"


def test_cerrar_empareja_por_el_cuerpo_literal_y_no_por_semejanza() -> None:
    abre = todo.parsear("- 14:20 - **pendiente**: avisar de los GGCC")
    casi = todo.parsear("- 19:05 - ~~(Hecho)~~: avisar los GGCC")
    assert abre is not None and casi is not None

    con_fila = todo.abrir(VACIA, abre)
    texto, hubo_pareja = todo.cerrar(con_fila, casi)

    assert not hubo_pareja, "el emparejamiento es literal, no semántico"
    assert texto == con_fila


# --- lectura de la tabla ----------------------------------------------------


def test_filas_y_horizontes_leen_lo_que_hay() -> None:
    texto = _con(
        "| esta semana |  | [[personal]] | una cosa |",
        "| con fecha | 2026-08-12 |  | otra cosa |",
    )

    assert todo.horizontes(texto) == ["esta semana", "con fecha"]
    assert [f.cuerpo for f in todo.filas(texto)] == ["una cosa", "otra cosa"]
    assert todo.filas(texto, "con fecha")[0].cuando == "2026-08-12"


def test_duplicados_encuentra_el_mismo_cuerpo_en_dos_filas() -> None:
    """Regla 1 de `spec/pendientes.md`: un pendiente está en exactamente un horizonte."""
    texto = _con(
        "| esta semana |  |  | avisar de los GGCC |",
        "| con fecha | 2026-08-12 |  | avisar de los GGCC |",
    )

    assert todo.duplicados(texto) == ["avisar de los GGCC"]


def test_duplicados_no_reporta_nada_sobre_una_tabla_sana() -> None:
    assert todo.duplicados(_con("| esta semana |  |  | una cosa |")) == []


def test_una_tabla_vacia_no_tiene_filas_ni_horizontes() -> None:
    assert todo.filas(VACIA) == []
    assert todo.horizontes(VACIA) == []
    assert todo.duplicados(VACIA) == []


# --- vocabulario de horizontes ---------------------------------------------


def test_canonico_normaliza_lo_que_el_autor_escribe() -> None:
    assert todo.canonico("Esta Semana") == todo.ESTA_SEMANA
    assert todo.canonico("  esta semana  ") == todo.ESTA_SEMANA


def test_canonico_deja_pasar_un_horizonte_propio_del_autor() -> None:
    """La escalera es del autor: un horizonte que no está en ESCALERA no se rechaza."""
    assert todo.canonico("algún día") == "algún día"


def test_escalera_de_pone_con_fecha_al_final() -> None:
    """`con fecha` es del sistema y va último, lo declare o no el libro de estilo."""
    assert todo.escalera_de(["esta quincena", "próxima quincena"]) == (
        "esta quincena",
        "próxima quincena",
        "con fecha",
    )
    assert todo.escalera_de(["esta semana", "con fecha"]) == ("esta semana", "con fecha")


def test_escalera_de_sin_horizontes_declarados_cae_en_la_del_template() -> None:
    assert todo.escalera_de([]) == todo.ESCALERA


def test_un_horizonte_renombrado_por_el_autor_ordena_como_el_primero() -> None:
    """La promesa del libro de estilo: renombrar los escalones no rompe el orden.

    Antes el orden salía de una constante, así que `esta quincena` no estaba en
    la escalera y su fila caía al final de la tabla, detrás de `con fecha`. El
    libro de estilo prometía justo lo contrario: "se renombran en esta tabla y el
    sistema sigue funcionando igual".
    """
    escalera = todo.escalera_de(["esta quincena", "fin de temporada"])
    tabla = todo.abrir(
        VACIA,
        todo.Marca("**pendiente**", "[[personal]]", "pagar la patente"),
        horizon="con fecha",
        when="2026-08-20",
        escalera=escalera,
    )
    tabla = todo.abrir(
        tabla,
        todo.Marca("**pendiente**", "[[personal]]", "llamar al fletero"),
        horizon="esta quincena",
        escalera=escalera,
    )
    filas = todo.filas(tabla)
    assert [f.horizonte for f in filas] == ["esta quincena", "con fecha"]


# --- marcas sin su consecuencia --------------------------------------------

AHORA_CON_MARCAS = (
    "## Martes 11 de agosto\n"
    "- 10:25 - [[personal]] **pendiente**: enviar la cotización a Los Robles\n"
    "- 11:00 - [[personal]] **pendiente**: llamar al banco\n"
    "- 12:00 - [[personal]] ~~(Hecho)~~: llamar al banco\n"
)


def _tabla(*cuerpos: str) -> str:
    filas = "".join(f"| esta semana |  | [[personal]] | {c} |\n" for c in cuerpos)
    return f"{todo.CABECERA}\n| --- | --- | --- | --- |\n{filas}"


def test_sin_consecuencia_encuentra_el_pendiente_que_nunca_se_abrio() -> None:
    faltan = todo.sin_consecuencia(AHORA_CON_MARCAS, _tabla())
    assert [(c.cuerpo, c.comando) for c in faltan] == [
        ("enviar la cotización a Los Robles", "tuku todo open")
    ]


def test_abrir_y_cerrar_el_mismo_ciclo_no_deja_fila_y_esta_bien() -> None:
    """`llamar al banco` se abre y se cierra el mismo día: la tabla queda sin él."""
    tabla = _tabla("enviar la cotización a Los Robles")
    assert todo.sin_consecuencia(AHORA_CON_MARCAS, tabla) == []


def test_sin_consecuencia_encuentra_el_cierre_que_nunca_se_aplico() -> None:
    faltan = todo.sin_consecuencia(
        AHORA_CON_MARCAS, _tabla("enviar la cotización a Los Robles", "llamar al banco")
    )
    assert [(c.cuerpo, c.comando) for c in faltan] == [("llamar al banco", "tuku todo close")]


def test_un_pendiente_arrastrado_de_otro_ciclo_no_se_reporta() -> None:
    """Está en la tabla sin marca en `AHORA.md` porque viene de un ciclo anterior."""
    assert todo.sin_consecuencia("## Martes 11 de agosto\n", _tabla("pagar la patente")) == []
