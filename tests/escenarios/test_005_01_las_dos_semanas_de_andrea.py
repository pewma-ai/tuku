"""Tests del escenario 005-01-las-dos-semanas-de-andrea.

Dos semanas de la Pyme del corpus con un comando por hecho. La segunda cae sobre
una primera ya archivada en `bitacoras/`: el vault deja de estar vacío.

Ejecutable directo: `python3 tests/escenarios/test_005_01_las_dos_semanas_de_andrea.py`
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import gherkin  # noqa: E402
from vault import placeholders_sin_sustituir  # noqa: E402

from tuku.cli import EXITO  # noqa: E402

SLUG = "005-01-las-dos-semanas-de-andrea"

CADENA = (
    "el árbol de Andrea nace con su negocio",
    "la primera semana se registra día por día",
    "la semana se cierra a mano y abre la siguiente",
    "la segunda semana cae sobre lo ya escrito",
    "repetir la segunda semana deja el vault igual",
)

#: Cada ámbito con la carpeta en que cuelga, desde `ambitos/`.
ARBOL = {
    "negocio": "negocio",
    "colegio-los-robles": "negocio/clientes",
    "jardin-semillita": "negocio/clientes",
    "liceo-tecnico-andes": "negocio/clientes",
    "libreria-el-compas": "negocio/clientes",
    "escuela-los-maitenes": "negocio/clientes",
    "importadora-andina": "negocio/proveedores",
    "papelera-del-sur": "negocio/proveedores",
    "bodega": "negocio",
    "temporada-marzo": "negocio",
    "catalogo-marzo": "negocio",
    "canal-feria": "negocio",
    "equipo": "negocio",
    "administracion": "administracion",
    "tributario": "administracion",
    "cobranza": "administracion",
    "financiamiento": "administracion",
    "personal": "personal",
}
CATEGORIAS = ("negocio/clientes", "negocio/proveedores")

ESTA = "esta semana"
PROXIMA = "próxima semana"
CON_FECHA = "con fecha"

#: La tabla de `PENDIENTES.md` al domingo 16: lo que la primera semana no cerró.
ABIERTOS_AL_16 = {
    (
        ESTA,
        "",
        "liceo-tecnico-andes",
        "cotizar de nuevo a Liceo Técnico Andes con precio ajustado",
    ),
    (ESTA, "", "financiamiento", "enviar los tres últimos F29 y el balance al banco"),
    (PROXIMA, "", "catalogo-marzo", "fotografiar el mobiliario para el catálogo de marzo"),
    (
        ESTA,
        "",
        "escuela-los-maitenes",
        "enviar cotización de material didáctico a Escuela Rural Los Maitenes",
    ),
    (
        ESTA,
        "",
        "temporada-marzo",
        "confirmar a Gloria Pinto el pedido de marzo por la mitad del volumen",
    ),
    (
        ESTA,
        "",
        "negocio",
        "cerrar la cotización de Colegio Los Robles durante la semana del 17 de agosto",
    ),
}
REVISION = (CON_FECHA, "2026-08-17", "", "revisar la bitácora anterior")

#: La tabla al domingo 23: lo de la primera semana que se cumplió salió, y lo que se
#: prometió en la segunda entró. Lo único que se arrastra intacto es lo que nadie cerró.
ABIERTOS_AL_23 = {
    (PROXIMA, "", "catalogo-marzo", "fotografiar el mobiliario para el catálogo de marzo"),
    (
        ESTA,
        "",
        "negocio",
        "cerrar la cotización de Colegio Los Robles durante la semana del 17 de agosto",
    ),
    (ESTA, "", "libreria-el-compas", "ofrecer reposición a Librería El Compás"),
    (ESTA, "", "catalogo-marzo", "enviar la lista de precios corregida a Paula Ibáñez"),
    (
        PROXIMA,
        "",
        "temporada-marzo",
        "consultar a Gloria Pinto si Importadora Andina trae línea Montessori",
    ),
    (ESTA, "", "bodega", "realizar el inventario de fin de mes con Katia Fuenzalida"),
    (
        ESTA,
        "",
        "escuela-los-maitenes",
        "decidir si se acepta el pedido de Escuela Los Maitenes a sesenta días",
    ),
}

BITACORA_1 = "bitacoras/bitacora-2026-08-10-2026-08-16.md"
LINK = re.compile(r"\]\(([^)]+)\)")


def _paso(titulo: str) -> gherkin.Corrida:
    """El escenario `titulo`, después de correr los que lo preceden en la cadena."""
    for previo in CADENA[: CADENA.index(titulo)]:
        gherkin.correr(SLUG, previo)
    return gherkin.correr(SLUG, titulo)


def _leer(corrida: gherkin.Corrida, *partes: str) -> str:
    return corrida.ruta("mi-vault", *partes).read_text(encoding="utf-8")


def _filas(pendientes: str) -> list[tuple[str, str, str, str]]:
    """Las filas de `PENDIENTES.md`: horizonte, vence, nombre del ámbito y detalle."""
    filas = []
    for linea in pendientes.splitlines():
        if not linea.startswith("|") or linea.startswith("| Horizonte") or "---" in linea[:6]:
            continue
        h, v, a, d = (c.strip() for c in linea.strip().strip("|").split("|", 3))
        nombre = re.match(r"\[([^\]]+)\]", a)
        filas.append((h, v, nombre.group(1) if nombre else "", d))
    return filas


def _registros(ahora: str, dia: str) -> list[str]:
    """Las líneas `- HH:MM - ` de un día de `AHORA.md`, en el orden en que están."""
    bloque = ahora.split(dia, 1)[1].split("\n## ", 1)[0]
    return [x for x in bloque.splitlines() if re.match(r"- \d\d:\d\d - ", x)]


def _sin_errores(corrida: gherkin.Corrida) -> None:
    for r in corrida.resultados:
        if r.comando.startswith("tuku") and "doctor" in r.comando:
            assert r.codigo == EXITO, f"{r.comando}: {r.stdout}{r.stderr}"


def test_005_01_los_frentes_de_la_pyme_cuelgan_donde_andrea_los_puso() -> None:
    corrida = _paso(CADENA[0])
    assert corrida.codigo == EXITO
    for nombre, padre in ARBOL.items():
        pagina = corrida.ruta("mi-vault", "ambitos", padre, nombre, f"{nombre}.md")
        if nombre == padre.split("/")[-1] and "/" not in padre:
            pagina = corrida.ruta("mi-vault", "ambitos", nombre, f"{nombre}.md")
        assert pagina.is_file(), f"falta la página de {nombre} en ambitos/{padre}"
    for categoria in CATEGORIAS:
        carpeta = corrida.ruta("mi-vault", "ambitos", categoria)
        assert carpeta.is_dir() and not (carpeta / f"{carpeta.name}.md").exists(), categoria


def test_005_01_las_palabras_que_delatan_un_frente_quedan_en_su_pagina() -> None:
    corrida = _paso(CADENA[0])
    pagina = corrida.ruta(
        "mi-vault",
        "ambitos",
        "negocio",
        "clientes",
        "liceo-tecnico-andes",
        "liceo-tecnico-andes.md",
    ).read_text(encoding="utf-8")
    linea = next(x for x in pagina.splitlines() if x.startswith("keywords:"))
    for palabra in ("liceo-andes", "patricia", "lillo"):
        assert palabra in linea, linea
    personal = _leer(corrida, "ambitos", "personal", "personal.md")
    assert "emilia" in personal and "vicente" in personal


def test_005_01_la_primera_semana_deja_los_pendientes_que_no_cerro() -> None:
    corrida = _paso(CADENA[1])
    ahora = _leer(corrida, "AHORA.md")
    assert set(_filas(_leer(corrida, "PENDIENTES.md"))) == ABIERTOS_AL_16
    # el martes 11 cierra lo pedido el lunes: el pedido a Papelera del Sur y la cotización
    martes = _registros(ahora, "## Martes 11 de agosto")
    assert any("(Hecho)" in x and "pedir cuadernos universitarios" in x for x in martes)
    horas = [re.match(r"- (\d\d:\d\d)", x).group(1) for x in martes]  # type: ignore[union-attr]
    assert horas == sorted(horas)
    assert "## Domingo 16 de agosto" in ahora
    _sin_errores(corrida)


def test_005_01_un_pendiente_con_dia_nace_con_fecha_y_uno_pospuesto_en_su_escalon() -> None:
    corrida = _paso(CADENA[1])
    ahora = _leer(corrida, "AHORA.md")
    # la reunión de apoderados se cerró a las 19:00 del jueves 13: no queda fila
    assert not any(
        "reunión de apoderados" in f[3] for f in _filas(_leer(corrida, "PENDIENTES.md"))
    )
    jueves = _registros(ahora, "## Jueves 13 de agosto")
    assert any("(Hecho)" in x and "reunión de apoderados" in x for x in jueves)
    lunes = _registros(ahora, "## Lunes 10 de agosto")
    assert any("**pendiente**" in x and "reunión de apoderados" in x for x in lunes)


def test_005_01_la_semana_archivada_se_lee_desde_bitacoras() -> None:
    corrida = _paso(CADENA[2])
    cerrada = _leer(corrida, BITACORA_1)
    assert (
        "status: stable" in cerrada
        and "from: 2026-08-10" in cerrada
        and "to: 2026-08-16" in cerrada
    )
    assert "## Domingo 16 de agosto" in cerrada
    enlaces = LINK.findall(cerrada)
    assert enlaces, "la bitácora cerrada no enlaza ningún ámbito"
    for destino in enlaces:
        assert corrida.ruta("mi-vault", "bitacoras", destino).resolve().exists(), destino
    _sin_errores(corrida)


def test_005_01_la_segunda_semana_abre_con_la_revision_de_la_anterior() -> None:
    corrida = _paso(CADENA[2])
    ahora = _leer(corrida, "AHORA.md")
    assert (
        "from: 2026-08-17" in ahora and "to: 2026-08-23" in ahora and "status: draft" in ahora
    )
    lunes = ahora.split("## Lunes 17 de agosto", 1)[1].split("\n## ", 1)[0]
    assert "revisar la bitácora anterior" in lunes
    assert set(_filas(_leer(corrida, "PENDIENTES.md"))) == ABIERTOS_AL_16 | {REVISION}
    assert not placeholders_sin_sustituir(corrida.ruta("mi-vault"))


def test_005_01_la_segunda_semana_cierra_lo_de_la_primera_y_suma_lo_suyo() -> None:
    corrida = _paso(CADENA[3])
    assert set(_filas(_leer(corrida, "PENDIENTES.md"))) == ABIERTOS_AL_23 | {REVISION}
    ahora = _leer(corrida, "AHORA.md")
    # el cierre de lo prometido en la semana anterior queda en el día en que se dijo
    lunes = _registros(ahora, "## Lunes 17 de agosto")
    assert any("(Hecho)" in x and "cotizar de nuevo a Liceo Técnico Andes" in x for x in lunes)
    _sin_errores(corrida)


def test_005_01_cada_pagina_de_ambito_cuenta_lo_suyo() -> None:
    corrida = _paso(CADENA[3])
    robles = _leer(
        corrida, "ambitos", "negocio", "clientes", "colegio-los-robles", "colegio-los-robles.md"
    )
    assert "![[../../../PENDIENTES-AMBITOS.md#^colegio-los-robles]]" in robles
    # la página cuenta el ciclo abierto: aprobación el martes, despacho el viernes
    assert robles.index("Martes 18 de agosto") < robles.index("Viernes 21 de agosto")
    assert "aprobó la cotización completa" in robles


def test_005_01_repetir_la_semana_deja_el_vault_igual() -> None:
    corrida = _paso(CADENA[4])
    assert corrida.delta_de("mi-vault") == {}
    _sin_errores(corrida)
