"""Unitarios de `tuku.todo`: la tabla única de `PENDIENTES.md`, sobre texto en memoria."""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from tuku import todo  # noqa: E402

VACIA = f"# Pendientes\n\n{todo.CABECERA}\n| --- | --- | --- | --- | --- |\n"

pytestmark = pytest.mark.unitario

HOY = date(2026, 8, 5)

P = "[personal](ambitos/personal/personal.md)"


def _con(*lineas: str) -> str:
    return VACIA + "".join(f"{linea}\n" for linea in lineas)


# --- parsear ----------------------------------------------------------------


def test_parsear_reconoce_aperturas_y_cierres_y_es_estricto_con_la_ontologia_cerrada() -> None:
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


def test_abrir_copia_el_cuerpo_literal_es_idempotente_y_con_fecha_va_a_vence() -> None:
    marca = todo.parsear("- 14:20 - [[personal]] **pendiente**: avisar de los GGCC")
    assert marca is not None

    una = todo.abrir(VACIA, marca, created=HOY)

    assert f"| esta semana |  | 2026-08-05 | {P} | avisar de los GGCC |" in una
    assert todo.cuerpos(una, "esta semana") == ["avisar de los GGCC"]
    assert todo.abrir(una, marca, created=HOY) == una, "un registro repetido no abre dos veces"

    marca = todo.Marca(todo.ABRE, "personal", "pagar la sesión")

    fila = todo.filas(
        todo.abrir(VACIA, marca, horizon=todo.CON_FECHA, due="2026-08-12", created=HOY)
    )[0]
    assert (fila.horizonte, fila.vence) == (todo.CON_FECHA, "2026-08-12")

    with pytest.raises(todo.SinTabla):
        todo.abrir("# Pendientes\n\nsin tabla acá.\n", marca, created=HOY)


def test_cerrar_borra_la_fila_y_solo_si_hay_pareja_literal() -> None:
    abre = todo.Marca(todo.ABRE, "personal", "avisar de los GGCC")
    cierra = todo.Marca(todo.CIERRA, "personal", "avisar de los GGCC")
    con_fila = todo.abrir(VACIA, abre, created=HOY)

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


def test_el_horizonte_se_normaliza_y_la_escalera_es_la_del_autor() -> None:
    assert todo.canonico("Esta Semana") == todo.ESTA_SEMANA
    assert todo.canonico("  esta semana  ") == todo.ESTA_SEMANA
    assert todo.canonico("algún día") == "algún día"

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
        created=HOY,
        escalera=escalera,
    )
    tabla = todo.abrir(
        tabla,
        todo.Marca("**pendiente**", "[[personal]]", "llamar al fletero"),
        horizon="esta quincena",
        created=HOY,
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
    filas = "".join(f"| esta semana |  | 2026-08-05 | [[personal]] | {c} |\n" for c in cuerpos)
    return f"{todo.CABECERA}\n| --- | --- | --- | --- | --- |\n{filas}"


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


def test_los_links_y_los_espacios_no_cuentan_al_buscar_un_pendiente() -> None:
    assert todo.clave(CON_LINK) == todo.clave(SIN_LINK)
    assert todo.clave("ver [[carmen|Carmen]] hoy") == "ver Carmen hoy"
    assert todo.clave("ver [[carmen]] hoy") == "ver carmen hoy"
    assert todo.clave("pagar  la\tluz ") == todo.clave("pagar la luz")
    assert todo.clave("Pagar la luz") != todo.clave("pagar la luz")

    sin = todo.Marca(todo.ABRE, "personal", SIN_LINK)
    con = todo.Marca(todo.ABRE, "personal", CON_LINK)
    cierra_con = todo.Marca(todo.CIERRA, "personal", CON_LINK)
    cierra_sin = todo.Marca(todo.CIERRA, "personal", SIN_LINK)

    una = todo.abrir(VACIA, sin, created=HOY)
    assert todo.abrir(una, con, created=HOY) == una

    for fila, cierre in [(sin, cierra_con), (con, cierra_sin)]:
        texto, hubo_pareja = todo.cerrar(todo.abrir(VACIA, fila, created=HOY), cierre)
        assert hubo_pareja and todo.filas(texto) == []

    assert todo.duplicados(_tabla(CON_LINK, SIN_LINK)) == [SIN_LINK]

    ahora = f"- 10:00 - {P} **pendiente**: {CON_LINK}\n"
    assert todo.sin_consecuencia(ahora, _tabla(SIN_LINK)) == []
    faltan = todo.sin_consecuencia(f"- 11:00 - {P} (Hecho): ~~{SIN_LINK}~~\n", _tabla(CON_LINK))
    assert [(c.cuerpo, c.marca) for c in faltan] == [(SIN_LINK, todo.CIERRA)]

    con_espacios = todo.Marca(todo.ABRE, "personal", "pagar  la\tluz ")
    base = todo.abrir(VACIA, todo.Marca(todo.ABRE, "personal", "pagar la luz"), created=HOY)
    assert todo.abrir(base, con_espacios, created=HOY) == base
    sin_fila, hubo_pareja = todo.cerrar(
        base, todo.Marca(todo.CIERRA, "personal", "pagar   la luz")
    )
    assert hubo_pareja and todo.cuerpos(sin_fila) == []

    tabla = _tabla(SIN_LINK)
    nueva, hubo = todo.reemplazar_cuerpo(tabla, CON_LINK, "avisar a Carmen mañana")
    assert hubo
    assert todo.cuerpos(nueva) == ["avisar a Carmen mañana"]
    assert "| esta semana |  | 2026-08-05 | [[personal]] |" in nueva
    assert todo.reemplazar_cuerpo(tabla, "otra cosa", "x") == (tabla, False)


def test_un_pipe_en_el_cuerpo_no_rompe_la_tabla() -> None:
    texto = todo.abrir(VACIA, todo.Marca(todo.ABRE, "personal", "luz | agua"), created=HOY)
    texto = todo.abrir(texto, todo.Marca(todo.ABRE, "personal", "comprar pan"), created=HOY)
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


def test_huerfanas_son_las_filas_sin_registro_pendiente_en_ahora_ni_en_la_historia() -> None:
    tabla = _tabla("enviar la cotización", "avisar de los GGCC", "pagar la patente")
    ahora = "## Martes 11 de agosto\n- 09:00 - **pendiente**: enviar la cotización\n"
    bitacora = (
        "## Lunes 3 de agosto\n- 08:00 - [[personal]] **pendiente**: avisar de los GGCC\n"
    )

    assert [f.cuerpo for f in todo.huerfanas(tabla, [ahora])] == [
        "avisar de los GGCC",
        "pagar la patente",
    ]
    assert [f.cuerpo for f in todo.huerfanas(tabla, [ahora, bitacora])] == ["pagar la patente"]
    assert todo.huerfanas(_tabla(), [ahora]) == []


def test_lint_nombra_el_comando_que_corrige_cada_hallazgo() -> None:
    ahora = (
        "---\nfrom: 2026-08-10\nto: 2026-08-16\n---\n"
        "## Martes 11 de agosto\n\n- 09:00 - llamar\n"
    )
    (hallazgo,) = todo.lint(_tabla("llamar a la administradora"), ahora)
    assert hallazgo.startswith("PENDIENTES.md: error:")
    assert "llamar a la administradora" in hallazgo
    assert "tuku todo open --scope personal --body 'llamar a la administradora'" in hallazgo
    assert (
        todo.lint(
            _tabla("llamar a la administradora"),
            ahora,
            historia=["- 09:00 - **pendiente**: llamar a la administradora\n"],
        )
        == []
    )

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

    tabla = todo.CABECERA + "\n| --- | --- | --- | --- | --- |\n"
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


# --- Creado y plazos --------------------------------------------------------

ESCALERA_3 = todo.escalera_de(["esta quincena", "próxima quincena", "este turno"])


def _fila(horizonte: str, creado: str, vence: str = "") -> todo.Fila:
    return todo.Fila(horizonte, vence, creado, None, "algo")


def test_la_fila_sin_creado_es_la_de_un_vault_anterior_y_se_lee_creada_hoy() -> None:
    antigua = "| esta semana |  | [[personal]] | una cosa |"
    (fila,) = todo.filas(_con(antigua))
    assert (fila.creado, fila.creado_dia, fila.cuerpo) == ("", None, "una cosa")
    assert todo.plazo(fila, HOY) == HOY + timedelta(days=7)
    assert not todo.atrasada(fila, HOY + timedelta(days=30)), "sin Creado siempre es de hoy"

    (vacia,) = todo.filas(_con("| esta semana |  |  | [[personal]] | una cosa |"))
    assert vacia.creado_dia is None and todo.plazo(vacia, HOY) == HOY + timedelta(days=7)


def test_cada_escalon_vence_por_su_posicion_y_no_por_su_texto() -> None:
    creado = "2026-08-05"
    esperado = {
        "esta quincena": date(2026, 8, 12),
        "próxima quincena": date(2026, 8, 19),
        "este turno": date(2026, 8, 30),
    }
    for horizonte, vence in esperado.items():
        assert todo.plazo(_fila(horizonte, creado), HOY, ESCALERA_3) == vence, horizonte

    assert todo.plazo(_fila("esta semana", creado), HOY) == date(2026, 8, 12)
    assert todo.plazo(_fila("próxima semana", creado), HOY) == date(2026, 8, 19)
    assert todo.plazo(_fila("fin de mes", creado), HOY) == date(2026, 8, 30)
    assert todo.plazo(_fila("fin de mes", "2026-12-10"), HOY) == date(2026, 12, 30)
    assert todo.plazo(_fila("fin de mes", "2028-02-03"), HOY) == date(2028, 2, 28)
    assert todo.plazo(_fila("fin de mes", "2026-08-31"), HOY) == date(2026, 8, 31), (
        "nunca antes de Creado"
    )

    assert todo.plazo(_fila("con fecha", creado), HOY) is None
    assert todo.plazo(_fila("algún día", creado), HOY) is None


def test_atrasada_por_vence_o_por_el_plazo_desde_creado() -> None:
    creado = "2026-08-05"
    assert not todo.atrasada(_fila("esta semana", creado), date(2026, 8, 12))
    assert todo.atrasada(_fila("esta semana", creado), date(2026, 8, 13))
    assert not todo.atrasada(_fila("próxima semana", creado), date(2026, 8, 19))
    assert todo.atrasada(_fila("próxima semana", creado), date(2026, 8, 20))

    con_fecha = _fila("con fecha", creado, vence="2026-08-10")
    assert todo.atrasada(con_fecha, date(2026, 8, 11))
    assert not todo.atrasada(con_fecha, date(2026, 8, 10))
    assert not todo.atrasada(_fila("con fecha", creado), date(2030, 1, 1)), "sin plazo"

    asi = _fila("esta semana", creado, vence="2026-09-01")
    assert not todo.atrasada(asi, date(2026, 8, 20)), "un Vence manda sobre el escalón"


def test_el_plazo_se_calcula_sobre_el_texto_de_la_tabla() -> None:
    tabla = _con(
        "| esta semana |  | 2026-08-01 |  | vieja |",
        "| próxima semana |  | 2026-08-01 |  | media |",
        "| fin de mes |  | 2026-08-01 |  | larga |",
        "| con fecha | 2026-08-20 | 2026-08-01 |  | fechada |",
    )
    hoy = date(2026, 8, 16)
    assert [f.cuerpo for f in todo.filas(tabla) if todo.atrasada(f, hoy)] == ["vieja", "media"]
    assert [f.cuerpo for f in todo.filas(tabla) if todo.atrasada(f, date(2026, 8, 31))] == [
        "vieja",
        "media",
        "larga",
        "fechada",
    ]


def test_migrar_pasa_la_tabla_de_cuatro_columnas_a_cinco_y_es_idempotente() -> None:
    antigua = (
        "# Pendientes\n\n| Horizonte | Vence | Ámbito | Detalle |\n| --- | --- | --- | --- |\n"
        f"| esta semana |  | {P} | una cosa |\n| con fecha | 2026-08-12 |  | otra |\n"
    )
    assert todo.sin_creado(antigua) and not todo.sin_creado(VACIA)
    (hallazgo,) = todo.lint(antigua)
    assert "`Creado`" in hallazgo and "tuku fix todo" in hallazgo

    nueva = todo.migrar(antigua, HOY)
    assert nueva.splitlines()[2] == todo.CABECERA
    assert f"| esta semana |  | 2026-08-05 | {P} | una cosa |" in nueva
    assert "| con fecha | 2026-08-12 | 2026-08-05 |  | otra |" in nueva
    assert not todo.sin_creado(nueva) and todo.lint(nueva) == []
    assert todo.migrar(nueva, date(2030, 1, 1)) == nueva
