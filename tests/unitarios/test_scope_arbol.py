"""El árbol de ámbitos: sin archivos vacíos, anidados, `scope move` y `scope rename`."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from tuku import init, scope
from tuku.cli import EXITO, RECHAZO, main

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent
HOY = "2026-08-11"
CUERPO = "presentar el marco"


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    return init.init(tmp_path / "v", home=RAIZ_REPO, desde=date(2026, 8, 10))


def _tuku(vault: Path, *argv: str) -> int:
    return main([*argv, "--vault", str(vault)])


def _crear(vault: Path, nombre: str, *extra: str) -> int:
    return _tuku(vault, "scope", "create", nombre, "--at", f"{HOY} 18:45", *extra)


def _foto(vault: Path) -> dict[str, bytes]:
    return {str(p.relative_to(vault)): p.read_bytes() for p in vault.rglob("*") if p.is_file()}


def _leer(vault: Path, *partes: str) -> str:
    return vault.joinpath(*partes).read_text(encoding="utf-8")


def _con_faena(vault: Path) -> None:
    assert _crear(vault, "faena") == EXITO
    assert _crear(vault, "faena-ai", "--parent", "faena") == EXITO


def _con_registros(vault: Path) -> None:
    """`faena` y un `faena-ai` plano, con un registro y un pendiente."""
    assert _crear(vault, "faena") == EXITO
    assert _crear(vault, "faena-ai") == EXITO
    assert (
        _tuku(
            vault, "entry", "create", "--scope", "faena-ai", "--at", f"{HOY} 19:00",
            "--body", "**nota**: revisé el marco",
        )
        == EXITO
    )  # fmt: skip
    assert (
        _tuku(
            vault, "todo", "open", "--scope", "faena-ai", "--at", f"{HOY} 19:05",
            "--due", "2026-08-12", "--body", CUERPO,
        )
        == EXITO
    )  # fmt: skip


def _con_ruta_vieja(vault: Path, ruta: str) -> list[str]:
    """Los archivos que todavía nombran la ruta de antes."""
    return [
        str(p.relative_to(vault))
        for p in vault.rglob("*.md")
        if ruta in p.read_text(encoding="utf-8")
    ]


def _callouts(vault: Path) -> dict[str, list[str]]:
    """Las líneas del callout de cada ámbito en `PENDIENTES-AMBITOS.md`, por ancla."""
    salida: dict[str, list[str]] = {}
    for bloque in _leer(vault, "ambitos", "PENDIENTES-AMBITOS.md").split("\n\n"):
        lineas = bloque.strip().splitlines()
        if lineas and lineas[0].startswith("> [!todo] Pendientes en"):
            salida[lineas[0].rsplit("^", 1)[1]] = lineas
    return salida


def _colgando(vault: Path, viejo: str) -> list[str]:
    """Los archivos que todavía nombran el ámbito por su nombre de antes."""
    return [
        str(p.relative_to(vault))
        for p in vault.rglob("*.md")
        if f"ambitos/{viejo}/" in (t := p.read_text(encoding="utf-8"))
        or f"^{viejo}" in t
        or f"[{viejo}](" in t
    ]


def test_un_ambito_nuevo_lleva_solo_su_pagina_y_el_template_no_siembra_reglas_vacias(
    vault: Path,
) -> None:
    assert _crear(vault, "depto-centro") == EXITO
    nombres = sorted(p.name for p in (vault / "ambitos" / "depto-centro").iterdir())
    assert nombres == ["depto-centro.md"]

    assert "Apertura de la semana" in _leer(vault, "ambitos", "CADENCIAS.md")
    assert sorted(p.name for p in (vault / "ambitos" / "personal").iterdir()) == [
        "CAPACIDAD.md",
        "personal.md",
    ]
    assert (vault / "ambitos" / "AGENTS.md").is_file()


def test_un_ambito_bajo_otro_vive_en_su_carpeta_y_se_enlaza_con_su_ruta_completa(
    vault: Path,
) -> None:
    _con_faena(vault)
    pagina = vault / "ambitos" / "faena" / "faena-ai" / "faena-ai.md"
    assert "![[../../PENDIENTES-AMBITOS.md#^faena-ai]]" in pagina.read_text(encoding="utf-8")
    constancia = (
        "[faena-ai](ambitos/faena/faena-ai/faena-ai.md) "
        "**nota**: abrí el ámbito bajo [faena](ambitos/faena/faena.md)"
    )
    assert constancia in _leer(vault, "AHORA.md")

    argv = ("entry", "create", "--scope", "faena-ai", "--at", f"{HOY} 19:00", "--body", "x")
    assert _tuku(vault, *argv) == EXITO
    assert "[faena-ai](ambitos/faena/faena-ai/faena-ai.md) x" in _leer(vault, "AHORA.md")
    assert _tuku(vault, "scope", "lint") == EXITO
    assert _tuku(vault, "doctor") == EXITO


def test_el_documento_de_ambitos_sigue_el_arbol_y_cada_callout_lleva_solo_lo_suyo(
    vault: Path,
) -> None:
    _con_faena(vault)
    assert _callouts(vault)["faena-ai"] == [
        "> [!todo] Pendientes en **Faena / Faena Ai** ^faena-ai"
    ], "un ámbito sin pendientes lleva solo el título"
    callouts = [
        linea
        for linea in _leer(vault, "ambitos", "PENDIENTES-AMBITOS.md").splitlines()
        if linea.startswith("> [!todo]")
    ]
    assert callouts == [
        "> [!todo] Pendientes en **Faena** ^faena",
        "> [!todo] Pendientes en **Faena / Faena Ai** ^faena-ai",
        "> [!todo] Pendientes en **Personal** ^personal",
    ]

    argv = ("todo", "open", "--scope", "faena-ai", "--at", f"{HOY} 19:05", "--body", CUERPO)
    assert _tuku(vault, *argv) == EXITO
    bloques = _callouts(vault)
    assert CUERPO in "\n".join(bloques["faena-ai"])
    assert bloques["faena"] == ["> [!todo] Pendientes en **Faena** ^faena"]


def test_crear_bajo_el_mismo_padre_es_idempotente_y_lo_imposible_se_rechaza_sin_escribir(
    vault: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    antes = _foto(vault)
    assert _crear(vault, "faena-ai", "--parent", "faena") == RECHAZO
    assert "tuku scope create faena" in capsys.readouterr().err, "el padre tiene que existir"
    assert _foto(vault) == antes

    _con_faena(vault)
    antes = _foto(vault)
    assert _crear(vault, "faena-ai", "--parent", "faena") == EXITO
    assert _foto(vault) == antes

    assert _crear(vault, "otro") == EXITO
    for argv, dice in [
        (
            ("scope", "move", "no-existe", "--parent", "faena"),
            "no existe el ámbito 'no-existe'",
        ),
        (("scope", "move", "faena-ai", "--parent", "no-existe"), "tuku scope create no-existe"),
        (("scope", "move", "faena", "--parent", "faena-ai"), "dentro de sí mismo"),
    ]:
        antes = _foto(vault)
        assert _tuku(vault, *argv) == RECHAZO, argv
        assert dice in capsys.readouterr().err, argv
        assert _foto(vault) == antes, argv

    antes = _foto(vault)
    assert _crear(vault, "otro", "--parent", "faena") == RECHAZO
    assert "tuku scope move otro --parent faena" in capsys.readouterr().err
    assert _foto(vault) == antes


def test_mover_un_ambito_arrastra_todo_es_idempotente_y_se_deshace_sin_padre(
    vault: Path,
) -> None:
    _con_registros(vault)
    plano = _foto(vault)
    assert _tuku(vault, "scope", "move", "faena-ai", "--parent", "faena") == EXITO

    assert not (vault / "ambitos" / "faena-ai").exists()
    pagina = vault / "ambitos" / "faena" / "faena-ai" / "faena-ai.md"
    assert "![[../../PENDIENTES-AMBITOS.md#^faena-ai]]" in pagina.read_text(encoding="utf-8")
    for archivo in ("AHORA.md", "PENDIENTES.md"):
        texto = _leer(vault, archivo)
        assert "ambitos/faena-ai/" not in texto, archivo
        assert "ambitos/faena/faena-ai/faena-ai.md" in texto, archivo
    assert _con_ruta_vieja(vault, "ambitos/faena-ai/") == []
    assert _tuku(vault, "doctor") == EXITO

    movido = _foto(vault)
    assert _tuku(vault, "scope", "move", "faena-ai", "--parent", "faena") == EXITO
    assert _foto(vault) == movido

    assert _tuku(vault, "scope", "move", "faena-ai") == EXITO
    assert (vault / "ambitos" / "faena-ai" / "faena-ai.md").is_file()
    assert not (vault / "ambitos" / "faena" / "faena-ai").exists()
    assert _foto(vault) == plano
    assert _tuku(vault, "doctor") == EXITO


def test_renombrar_un_ambito_anidado_arrastra_todo(vault: Path) -> None:
    _con_registros(vault)
    assert _tuku(vault, "scope", "move", "faena-ai", "--parent", "faena") == EXITO
    assert _tuku(vault, "scope", "rename", "faena-ai", "faena-ia") == EXITO

    assert (vault / "ambitos" / "faena" / "faena-ia" / "faena-ia.md").is_file()
    assert not (vault / "ambitos" / "faena" / "faena-ai").exists()
    assert _colgando(vault, "faena-ai") == []
    assert "ambitos/faena/faena-ia/faena-ia.md" in _leer(vault, "AHORA.md")
    assert _tuku(vault, "doctor") == EXITO


def _hijos(vault: Path, *ruta: str) -> list[str]:
    """Las líneas del callout "En X:" de una página, o `[]` si no lo tiene."""
    lineas = _leer(vault, *ruta).splitlines()
    inicio = next((i for i, x in enumerate(lineas) if x.startswith("> [!abstract]+ En ")), None)
    if inicio is None:
        return []
    fin = next((i for i in range(inicio, len(lineas)) if not lineas[i].startswith(">")), None)
    return lineas[inicio:fin]


def test_la_pagina_del_padre_lista_sus_hijos_directos_y_los_sigue_al_moverlos(
    vault: Path,
) -> None:
    pagina = ("ambitos", "faena", "faena.md")
    _con_faena(vault)
    assert _crear(vault, "faena-uno", "--parent", "faena") == EXITO
    assert _crear(vault, "nieto", "--parent", "faena-ai") == EXITO
    assert _hijos(vault, *pagina) == [
        "> [!abstract]+ En **Faena**:",
        "> - [faena-ai](faena-ai/faena-ai.md)",
        "> - [faena-uno](faena-uno/faena-uno.md)",
    ]
    assert _leer(vault, *pagina).index("![[") < _leer(vault, *pagina).index("> [!abstract]")
    assert _hijos(vault, "ambitos", "faena", "faena-ai", "faena-ai.md") == [
        "> [!abstract]+ En **Faena Ai**:",
        "> - [nieto](nieto/nieto.md)",
    ]
    assert _hijos(vault, "ambitos", "personal", "personal.md") == []

    antes = _foto(vault)
    assert _crear(vault, "faena-uno", "--parent", "faena") == EXITO
    assert _foto(vault) == antes

    assert _tuku(vault, "scope", "rename", "faena-uno", "faena-dos") == EXITO
    assert "> - [faena-dos](faena-dos/faena-dos.md)" in _hijos(vault, *pagina)

    assert _tuku(vault, "scope", "move", "faena-dos", "--parent", "faena-ai") == EXITO
    assert _hijos(vault, *pagina) == [
        "> [!abstract]+ En **Faena**:",
        "> - [faena-ai](faena-ai/faena-ai.md)",
    ]
    assert "> - [faena-dos](../faena-dos/faena-dos.md)" not in _hijos(vault, *pagina)
    assert "> - [faena-dos](faena-dos/faena-dos.md)" in _hijos(
        vault, "ambitos", "faena", "faena-ai", "faena-ai.md"
    )

    assert _tuku(vault, "scope", "move", "faena-ai") == EXITO
    assert _tuku(vault, "scope", "move", "faena-dos") == EXITO
    assert _hijos(vault, *pagina) == []
    assert _tuku(vault, "doctor") == EXITO


def test_renombrar_el_padre_retitula_su_callout(vault: Path) -> None:
    _con_faena(vault)
    assert _tuku(vault, "scope", "rename", "faena", "trabajo") == EXITO
    assert _hijos(vault, "ambitos", "trabajo", "trabajo.md") == [
        "> [!abstract]+ En **Trabajo**:",
        "> - [faena-ai](faena-ai/faena-ai.md)",
    ]


def test_al_abrir_el_callout_entran_los_hijos_que_ya_tenia_el_padre(vault: Path) -> None:
    _con_faena(vault)
    pagina = vault / "ambitos" / "faena" / "faena.md"
    texto = pagina.read_text(encoding="utf-8")
    pagina.write_text("\n".join(x for x in texto.splitlines() if not x.startswith(">")) + "\n")
    assert _hijos(vault, "ambitos", "faena", "faena.md") == []

    assert _crear(vault, "faena-dos", "--parent", "faena") == EXITO
    assert _hijos(vault, "ambitos", "faena", "faena.md") == [
        "> [!abstract]+ En **Faena**:",
        "> - [faena-ai](faena-ai/faena-ai.md)",
        "> - [faena-dos](faena-dos/faena-dos.md)",
    ]


def test_regenerate_scope_recrea_la_lista_de_hijos_de_cada_padre(vault: Path) -> None:
    _con_faena(vault)
    assert _crear(vault, "faena-dos", "--parent", "faena") == EXITO
    sano = _foto(vault)
    padre = vault / "ambitos" / "faena" / "faena.md"
    texto = padre.read_text(encoding="utf-8")
    padre.write_text(
        texto.replace(
            "> - [faena-ai](faena-ai/faena-ai.md)\n", "> - [viejo](viejo/viejo.md)\n"
        ),
        encoding="utf-8",
    )
    hoja = vault / "ambitos" / "faena" / "faena-dos" / "faena-dos.md"
    hoja.write_text(
        hoja.read_text(encoding="utf-8").replace(
            "## Esta semana",
            "> [!abstract]+ En **Faena Dos**:\n> - [x](x/x.md)\n\n## Esta semana",
        ),
        encoding="utf-8",
    )

    assert _tuku(vault, "regenerate", "todo") == EXITO
    assert "viejo" in _leer(vault, "ambitos", "faena", "faena.md")

    assert _tuku(vault, "regenerate", "scope") == EXITO
    assert _foto(vault) == sano

    assert _tuku(vault, "regenerate", "scope") == EXITO
    assert _foto(vault) == sano


def test_el_callout_lista_los_ambitos_y_despues_las_categorias_anidadas_y_plegables(
    vault: Path,
) -> None:
    assert _crear(vault, "negocio") == EXITO
    for categoria in ("proveedores", "clientes"):
        (vault / "ambitos" / "negocio" / categoria).mkdir()
    for nombre, padre in (
        ("papelera-del-sur", "proveedores"),
        ("temporada-marzo", "negocio"),
        ("colegio-los-robles", "clientes"),
        ("bodega", "negocio"),
        ("importadora-andina", "proveedores"),
        ("jardin-semillita", "clientes"),
    ):
        assert _crear(vault, nombre, "--parent", padre) == EXITO

    esperado = [
        "> [!abstract]+ En **Negocio**:",
        "> - [bodega](bodega/bodega.md)",
        "> - [temporada-marzo](temporada-marzo/temporada-marzo.md)",
        "> ---",
        "> > [!abstract]+ Clientes",
        "> > - [colegio-los-robles](clientes/colegio-los-robles/colegio-los-robles.md)",
        "> > - [jardin-semillita](clientes/jardin-semillita/jardin-semillita.md)",
        "> ---",
        "> > [!abstract]+ Proveedores",
        "> > - [importadora-andina](proveedores/importadora-andina/importadora-andina.md)",
        "> > - [papelera-del-sur](proveedores/papelera-del-sur/papelera-del-sur.md)",
    ]
    pagina = ("ambitos", "negocio", "negocio.md")
    assert _hijos(vault, *pagina) == esperado

    # lo que deja `create` es lo que rehace `regenerate scope`, en cualquier orden de creación
    sano = _foto(vault)
    assert _tuku(vault, "regenerate", "scope") == EXITO
    assert _foto(vault) == sano

    # mover y renombrar mantienen el orden y las categorías
    assert _tuku(vault, "scope", "rename", "bodega", "almacen") == EXITO
    assert _hijos(vault, *pagina)[1] == "> - [almacen](almacen/almacen.md)"
    assert _tuku(vault, "scope", "move", "jardin-semillita", "--parent", "proveedores") == EXITO
    assert "> > - [jardin-semillita](proveedores/jardin-semillita/jardin-semillita.md)" in (
        _hijos(vault, *pagina)
    )
    assert _tuku(vault, "regenerate", "scope") == EXITO
    assert _tuku(vault, "doctor") == EXITO


def _parent(vault: Path, *ruta: str) -> str | None:
    return scope.parent_de(_leer(vault, *ruta))


def test_cada_ambito_hijo_declara_en_su_frontmatter_la_carpeta_en_que_cuelga(
    vault: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert _crear(vault, "negocio") == EXITO
    (vault / "ambitos" / "negocio" / "clientes").mkdir()
    assert _crear(vault, "bodega", "--parent", "negocio") == EXITO
    assert _crear(vault, "colegio", "--parent", "clientes") == EXITO

    assert _parent(vault, "ambitos", "negocio", "negocio.md") is None
    assert _parent(vault, "ambitos", "negocio", "bodega", "bodega.md") == "ambitos/negocio"
    assert (
        _parent(vault, "ambitos", "negocio", "clientes", "colegio", "colegio.md")
        == "ambitos/negocio/clientes"
    )
    assert "parent:" not in _leer(vault, "ambitos", "personal", "personal.md")

    # renombrar un ámbito cambia el parent de sus descendientes; mover, el del movido
    assert _tuku(vault, "scope", "rename", "negocio", "pyme") == EXITO
    assert _parent(vault, "ambitos", "pyme", "bodega", "bodega.md") == "ambitos/pyme"
    assert _tuku(vault, "scope", "move", "colegio", "--parent", "bodega") == EXITO
    assert (
        _parent(vault, "ambitos", "pyme", "bodega", "colegio", "colegio.md")
        == "ambitos/pyme/bodega"
    )
    assert _tuku(vault, "scope", "move", "colegio") == EXITO
    assert _parent(vault, "ambitos", "colegio", "colegio.md") is None

    # el desfase se reporta y `regenerate scope` lo repara
    pagina = vault / "ambitos" / "pyme" / "bodega" / "bodega.md"
    texto = pagina.read_text(encoding="utf-8")
    pagina.write_text(texto.replace("parent: ambitos/pyme", "parent: ambitos/otro"), "utf-8")
    capsys.readouterr()
    assert _tuku(vault, "scope", "lint") == RECHAZO
    salida = capsys.readouterr()
    assert "parent: ambitos/otro" in salida.err + salida.out
    assert "tuku regenerate scope" in salida.err + salida.out
    assert _tuku(vault, "regenerate", "scope") == EXITO
    assert _parent(vault, "ambitos", "pyme", "bodega", "bodega.md") == "ambitos/pyme"
    assert _tuku(vault, "scope", "lint") == EXITO


def test_la_constancia_enlaza_al_ambito_padre_y_nombra_las_categorias_del_camino(
    vault: Path,
) -> None:
    assert _crear(vault, "negocio") == EXITO
    (vault / "ambitos" / "negocio" / "clientes").mkdir()
    (vault / "ambitos" / "suelta").mkdir()
    assert _crear(vault, "colegio", "--parent", "clientes") == EXITO
    assert _crear(vault, "bodega", "--parent", "negocio") == EXITO
    assert _crear(vault, "huerfano", "--parent", "suelta") == EXITO

    lineas = _leer(vault, "AHORA.md").splitlines()
    negocio = "[negocio](ambitos/negocio/negocio.md)"
    nota = "**nota**: abrí el ámbito"
    esperadas = [
        "[colegio](ambitos/negocio/clientes/colegio/colegio.md) "
        f"{nota} bajo {negocio}, en clientes",
        f"[bodega](ambitos/negocio/bodega/bodega.md) {nota} bajo {negocio}",
        f"[huerfano](ambitos/suelta/huerfano/huerfano.md) {nota} bajo suelta",
    ]
    for esperada in esperadas:
        assert any(x.endswith(esperada) for x in lineas), esperada
