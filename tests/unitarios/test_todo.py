"""Unitarios de `tuku.todo`: la tabla única de `PENDIENTES.md`, sobre texto en memoria."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from tuku import todo  # noqa: E402

VACIA = f"# Pendientes\n\n{todo.CABECERA}\n| --- | --- | --- | --- |\n"

pytestmark = pytest.mark.unitario

P = "[personal](ambitos/personal/personal.md)"


def _con(*lineas: str) -> str:
    return VACIA + "".join(f"{linea}\n" for linea in lineas)


# --- parsear ----------------------------------------------------------------


def test_parsear_reconoce_aperturas_y_cierres() -> None:
    marca = todo.parsear("- 14:20 - [[personal]] **pendiente**: comprar una maleta")
    assert marca is not None
    assert (marca.marca, marca.ambito, marca.cuerpo) == (
        todo.ABRE,
        "personal",
        "comprar una maleta",
    )

    marca = todo.parsear("- 19:05 - (Hecho): ~~comprar una maleta~~")
    assert marca is not None and marca.marca == todo.CIERRA and marca.ambito is None

    marca = todo.parsear(f"- 19:05 - {P} (Hecho): ~~avisar de los GGCC~~")
    assert marca is not None
    assert (marca.marca, marca.ambito, marca.cuerpo) == (
        todo.CIERRA,
        "personal",
        "avisar de los GGCC",
    )

    marca = todo.parsear("- 19:05 - (Hecho) **hito**: ~~avisar de los GGCC~~")
    assert marca is not None and marca.cuerpo == "avisar de los GGCC"


def test_parsear_es_estricto_con_la_ontologia_cerrada() -> None:
    for linea in [
        "",
        "no es una línea de registro",
        "- 14:20 - un registro cualquiera sin marca",
        "- 14:20 - **pendiente** sin dos puntos",
        "- 13:00 - [[personal]] **Pendiente**: comprar una maleta",
        "- 19:05 - ~~(Hecho)~~: avisar de los GGCC",
        "- 19:05 - (hecho): ~~avisar~~",
    ]:
        assert todo.parsear(linea) is None, linea


# --- abrir y cerrar ---------------------------------------------------------


def test_abrir_copia_el_cuerpo_literal_y_es_idempotente() -> None:
    marca = todo.parsear("- 14:20 - [[personal]] **pendiente**: avisar de los GGCC")
    assert marca is not None

    una = todo.abrir(VACIA, marca)

    assert f"| esta semana |  | {P} | avisar de los GGCC |" in una
    assert todo.cuerpos(una, "esta semana") == ["avisar de los GGCC"]
    assert todo.abrir(una, marca) == una, "un registro repetido no abre dos veces"


def test_abrir_con_fecha_va_a_la_columna_vence_y_sin_tabla_se_niega() -> None:
    marca = todo.Marca(todo.ABRE, "personal", "pagar la sesión")

    fila = todo.filas(todo.abrir(VACIA, marca, horizon=todo.CON_FECHA, due="2026-08-12"))[0]
    assert (fila.horizonte, fila.vence) == (todo.CON_FECHA, "2026-08-12")

    with pytest.raises(todo.SinTabla):
        todo.abrir("# Pendientes\n\nsin tabla acá.\n", marca)


def test_cerrar_borra_la_fila_y_solo_si_hay_pareja_literal() -> None:
    abre = todo.Marca(todo.ABRE, "personal", "avisar de los GGCC")
    cierra = todo.Marca(todo.CIERRA, "personal", "avisar de los GGCC")
    con_fila = todo.abrir(VACIA, abre)

    texto, hubo_pareja = todo.cerrar(con_fila, cierra)
    assert hubo_pareja and todo.filas(texto) == []
    assert todo.CABECERA in texto, "se perdió la cabecera de la tabla"

    sin_pareja = todo.Marca(todo.CIERRA, "personal", "comprar una maleta")
    assert todo.cerrar(VACIA, sin_pareja) == (VACIA, False)

    casi = todo.Marca(todo.CIERRA, "personal", "avisar los GGCC")
    assert todo.cerrar(con_fila, casi) == (con_fila, False), "el emparejamiento es literal"


# --- lectura de la tabla ----------------------------------------------------


def test_filas_horizontes_y_duplicados() -> None:
    texto = _con(
        "| esta semana |  | [[personal]] | una cosa |",
        "| con fecha | 2026-08-12 |  | otra cosa |",
    )
    assert todo.horizontes(texto) == ["esta semana", "con fecha"]
    assert [f.cuerpo for f in todo.filas(texto)] == ["una cosa", "otra cosa"]
    assert todo.filas(texto, "con fecha")[0].vence == "2026-08-12"
    assert todo.duplicados(texto) == []

    repetido = _con(
        "| esta semana |  |  | avisar de los GGCC |",
        "| con fecha | 2026-08-12 |  | avisar de los GGCC |",
    )
    assert todo.duplicados(repetido) == ["avisar de los GGCC"]

    assert (todo.filas(VACIA), todo.horizontes(VACIA), todo.duplicados(VACIA)) == ([], [], [])


# --- vocabulario de horizontes ---------------------------------------------


def test_canonico_normaliza_y_deja_pasar_el_horizonte_propio() -> None:
    assert todo.canonico("Esta Semana") == todo.ESTA_SEMANA
    assert todo.canonico("  esta semana  ") == todo.ESTA_SEMANA
    assert todo.canonico("algún día") == "algún día"


def test_la_escalera_es_la_del_autor_y_con_fecha_va_ultima() -> None:
    assert todo.escalera_de(["esta quincena", "próxima quincena"]) == (
        "esta quincena",
        "próxima quincena",
        "con fecha",
    )
    assert todo.escalera_de(["esta semana", "con fecha"]) == ("esta semana", "con fecha")
    assert todo.escalera_de([]) == todo.ESCALERA

    escalera = todo.escalera_de(["esta quincena", "fin de temporada"])
    tabla = todo.abrir(
        VACIA,
        todo.Marca("**pendiente**", "[[personal]]", "pagar la patente"),
        horizon="con fecha",
        due="2026-08-20",
        escalera=escalera,
    )
    tabla = todo.abrir(
        tabla,
        todo.Marca("**pendiente**", "[[personal]]", "llamar al fletero"),
        horizon="esta quincena",
        escalera=escalera,
    )
    assert [f.horizonte for f in todo.filas(tabla)] == ["esta quincena", "con fecha"]


# --- marcas sin su consecuencia --------------------------------------------

AHORA_CON_MARCAS = (
    "## Martes 11 de agosto\n"
    "- 10:25 - [[personal]] **pendiente**: enviar la cotización a Los Robles\n"
    "- 11:00 - [[personal]] **pendiente**: llamar al banco\n"
    "- 12:00 - [[personal]] (Hecho): ~~llamar al banco~~\n"
)


def _tabla(*cuerpos: str) -> str:
    filas = "".join(f"| esta semana |  | [[personal]] | {c} |\n" for c in cuerpos)
    return f"{todo.CABECERA}\n| --- | --- | --- | --- |\n{filas}"


def test_sin_consecuencia_encuentra_aperturas_y_cierres_sin_aplicar() -> None:
    def faltan(*cuerpos: str) -> list[tuple[str, str]]:
        return [
            (c.cuerpo, c.marca)
            for c in todo.sin_consecuencia(AHORA_CON_MARCAS, _tabla(*cuerpos))
        ]

    assert faltan() == [("enviar la cotización a Los Robles", todo.ABRE)]
    assert faltan("enviar la cotización a Los Robles") == [], "abrir y cerrar el mismo ciclo"
    assert faltan("enviar la cotización a Los Robles", "llamar al banco") == [
        ("llamar al banco", todo.CIERRA)
    ]
    assert (
        todo.sin_consecuencia("## Martes 11 de agosto\n", _tabla("pagar la patente")) == []
    ), "un pendiente arrastrado de otro ciclo no se reporta"


# --- el cierre: la marca a la vista y el cuerpo tachado ----------------------


def test_el_cierre_deja_la_marca_a_la_vista_y_canonizar_lo_escribe_siempre_igual() -> None:
    assert todo.cierre("avisar de los GGCC") == "(Hecho): ~~avisar de los GGCC~~"
    for entrada in [
        "(Hecho): avisar de los GGCC",
        "(Hecho): ~~avisar de los GGCC~~",
        "  (Hecho): avisar de los GGCC  ",
    ]:
        assert todo.canonizar(entrada) == "(Hecho): ~~avisar de los GGCC~~"
    assert todo.canonizar("(Hecho) **hito**: x") == "(Hecho) **hito**: ~~x~~"
    for cuerpo in [
        "**pendiente**: avisar",
        "**señal**: la administradora responde",
        "",
        "(Hecho)",
    ]:
        assert todo.canonizar(cuerpo) == cuerpo


# --- los links y los espacios no cuentan al buscar un pendiente --------------

CON_LINK = "avisar a [Carmen](notas/carmen.md) de los GGCC"
SIN_LINK = "avisar a Carmen de los GGCC"


def test_clave_ignora_links_y_espacios_repetidos_pero_no_mayusculas() -> None:
    assert todo.clave(CON_LINK) == todo.clave(SIN_LINK)
    assert todo.clave("ver [[carmen|Carmen]] hoy") == "ver Carmen hoy"
    assert todo.clave("ver [[carmen]] hoy") == "ver carmen hoy"
    assert todo.clave("pagar  la\tluz ") == todo.clave("pagar la luz")
    assert todo.clave("Pagar la luz") != todo.clave("pagar la luz")


def test_con_y_sin_link_es_el_mismo_pendiente_en_todas_las_operaciones() -> None:
    sin = todo.Marca(todo.ABRE, "personal", SIN_LINK)
    con = todo.Marca(todo.ABRE, "personal", CON_LINK)
    cierra_con = todo.Marca(todo.CIERRA, "personal", CON_LINK)
    cierra_sin = todo.Marca(todo.CIERRA, "personal", SIN_LINK)

    una = todo.abrir(VACIA, sin)
    assert todo.abrir(una, con) == una

    for fila, cierre in [(sin, cierra_con), (con, cierra_sin)]:
        texto, hubo_pareja = todo.cerrar(todo.abrir(VACIA, fila), cierre)
        assert hubo_pareja and todo.filas(texto) == []

    assert todo.duplicados(_tabla(CON_LINK, SIN_LINK)) == [SIN_LINK]

    ahora = f"- 10:00 - {P} **pendiente**: {CON_LINK}\n"
    assert todo.sin_consecuencia(ahora, _tabla(SIN_LINK)) == []
    faltan = todo.sin_consecuencia(f"- 11:00 - {P} (Hecho): ~~{SIN_LINK}~~\n", _tabla(CON_LINK))
    assert [(c.cuerpo, c.marca) for c in faltan] == [(SIN_LINK, todo.CIERRA)]

    con_espacios = todo.Marca(todo.ABRE, "personal", "pagar  la\tluz ")
    base = todo.abrir(VACIA, todo.Marca(todo.ABRE, "personal", "pagar la luz"))
    assert todo.abrir(base, con_espacios) == base
    sin_fila, hubo_pareja = todo.cerrar(
        base, todo.Marca(todo.CIERRA, "personal", "pagar   la luz")
    )
    assert hubo_pareja and todo.cuerpos(sin_fila) == []


def test_reemplazar_cuerpo_busca_sin_links_y_conserva_el_resto() -> None:
    tabla = _tabla(SIN_LINK)
    nueva, hubo = todo.reemplazar_cuerpo(tabla, CON_LINK, "avisar a Carmen mañana")
    assert hubo
    assert todo.cuerpos(nueva) == ["avisar a Carmen mañana"]
    assert "| esta semana |  | [[personal]] |" in nueva
    assert todo.reemplazar_cuerpo(tabla, "otra cosa", "x") == (tabla, False)


def test_un_pipe_en_el_cuerpo_no_rompe_la_tabla() -> None:
    texto = todo.abrir(VACIA, todo.Marca(todo.ABRE, "personal", "luz | agua"))
    texto = todo.abrir(texto, todo.Marca(todo.ABRE, "personal", "comprar pan"))
    assert sorted(todo.cuerpos(texto)) == ["comprar pan", "luz | agua"]
    sin_fila, hubo_pareja = todo.cerrar(
        texto, todo.Marca(todo.CIERRA, "personal", "luz | agua")
    )
    assert hubo_pareja and todo.cuerpos(sin_fila) == ["comprar pan"]


# --- lint: lo que reporta `tuku doctor todo` -----------------------------------

DIA_CERRADO = (
    "## Martes 11 de agosto\n"
    "- 13:00 - **pendiente**: comprar una maleta\n"
    "- 14:20 - **pendiente**: avisar a [Carmen](notas/carmen.md)\n"
    "- 19:10 - (Hecho): ~~comprar una maleta~~\n"
    "\n"
    "## Miércoles 12 de agosto\n"
    "- 09:00 - (Hecho): ~~avisar a Carmen~~\n"
)


def test_lint_de_la_tabla_sana_y_de_duplicados() -> None:
    assert todo.lint(_con("| esta semana |  |  | una cosa |")) == []
    assert todo.lint(VACIA, None) == []

    (hallazgo,) = todo.lint(
        _con(
            "| esta semana |  |  | avisar de los GGCC |",
            "| con fecha | 2026-08-12 |  | avisar de los GGCC |",
        )
    )
    assert hallazgo.startswith("PENDIENTES.md: error:") and "una sola" in hallazgo


def test_lint_nombra_el_comando_que_corrige_cada_hallazgo() -> None:
    ahora = (
        "---\nfrom: 2026-08-10\nto: 2026-08-16\n---\n"
        f"## Martes 11 de agosto\n\n- 14:20 - {P} **pendiente**: avisar de los GGCC\n"
    )
    (hallazgo,) = todo.lint(VACIA, ahora)
    assert hallazgo.startswith("AHORA.md: error:")
    assert (
        "tuku todo open --scope personal --at '2026-08-11 14:20' --body 'avisar de los GGCC'"
        in hallazgo
    )

    tabla = todo.CABECERA + "\n| --- | --- | --- | --- |\n"
    hallazgos = todo.lint(tabla, DIA_CERRADO)
    assert any("AHORA.md:2:" in h and "tuku fix todo" in h for h in hallazgos), hallazgos

    vistas: dict[str, tuple[str | None, str]] = {
        "ambitos/PENDIENTES-AMBITOS.md": ("viejo", "nuevo"),
        "AHORA.md": ("igual", "igual"),
    }
    (hallazgo,) = todo.lint(VACIA, vistas=vistas)
    assert hallazgo.startswith("ambitos/PENDIENTES-AMBITOS.md: error:")
    assert "tuku regenerate todo" in hallazgo

    (hallazgo,) = todo.lint(VACIA, vistas={"ambitos/PENDIENTES-AMBITOS.md": (None, "x")})
    assert "tuku regenerate todo" in hallazgo


def test_las_aperturas_cerradas_el_mismo_dia_se_detectan_y_se_quitan() -> None:
    hallados = todo.cerrados_el_mismo_dia(DIA_CERRADO)
    assert [(a.linea, a.cuerpo, a.dia) for a in hallados] == [
        (2, "comprar una maleta", "Martes 11 de agosto")
    ]

    texto = todo.quitar_aperturas_cerradas(DIA_CERRADO)
    assert "**pendiente**: comprar una maleta" not in texto
    assert "(Hecho): ~~comprar una maleta~~" in texto
    assert "**pendiente**: avisar a [Carmen](notas/carmen.md)" in texto
    assert todo.quitar_aperturas_cerradas(texto) == texto
    assert todo.quitar_aperturas_cerradas(DIA_CERRADO, "otro") == DIA_CERRADO
