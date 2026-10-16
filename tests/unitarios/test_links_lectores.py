"""Los lectores aceptan los dos formatos y los escritores solo producen Markdown."""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from tuku import cli, propagate, rename, scope, todo

MD = "[personal](ambitos/personal/personal.md)"


def test_parsear_acepta_wikilink_y_link_markdown() -> None:
    wiki = todo.parsear("- 14:20 - [[personal]] **pendiente**: comprar pan")
    md = todo.parsear(f"- 14:20 - {MD} **pendiente**: comprar pan")
    assert wiki is not None and md is not None
    assert wiki == md and md.ambito == "personal"


def test_parsear_un_ambito_anidado_toma_el_nombre_del_archivo() -> None:
    m = todo.parsear("- 14:20 - [pewma](ambitos/trabajo/pewma/pewma.md) **pendiente**: x")
    assert m is not None and m.ambito == "pewma"


def test_la_fila_se_lee_y_se_escribe_en_markdown() -> None:
    fila = todo.Fila("esta semana", "", "personal", "comprar pan")
    assert fila.linea() == f"| esta semana |  | {MD} | comprar pan |"
    tabla = f"| Horizonte | Vence | Ámbito | Detalle |\n| - | - | - | - |\n{fila.linea()}\n"
    assert todo.filas(tabla) == [fila]
    con_wiki = tabla.replace(MD, "[[personal]]")
    assert todo.filas(con_wiki) == [fila]


def test_la_fila_de_un_ambito_anidado_lleva_su_ruta_completa() -> None:
    fila = todo.Fila("esta semana", "", "pewma", "x")
    linea = fila.linea({"pewma": "ambitos/trabajo/pewma/pewma.md"})
    assert "[pewma](ambitos/trabajo/pewma/pewma.md)" in linea


def test_propagar_escribe_la_region_en_markdown_con_ruta_anidada() -> None:
    fila = todo.Fila("con fecha", "2026-09-08", "pewma", "x")
    linea = propagate.linea_del_dia(fila, {"pewma": "ambitos/trabajo/pewma/pewma.md"})
    assert linea == "- [pewma](ambitos/trabajo/pewma/pewma.md) - x"


def test_renombrar_cambia_texto_y_ruta_de_un_link_markdown() -> None:
    texto = "ver [personal](ambitos/personal/personal.md#a) y [otro](ambitos/otro/otro.md)"
    salida, n = rename.renombrar_enlaces(texto, "personal", "propio")
    assert n == 1
    assert salida == "ver [propio](ambitos/propio/propio.md#a) y [otro](ambitos/otro/otro.md)"


def test_renombrar_no_toca_el_texto_que_eligio_el_autor() -> None:
    salida, n = rename.renombrar_enlaces(
        "[mi casa](ambitos/personal/personal.md)", "personal", "propio"
    )
    assert (salida, n) == ("[mi casa](ambitos/propio/propio.md)", 1)


def test_renombrar_una_nota_cambia_solo_el_archivo() -> None:
    salida, n = rename.renombrar_enlaces("[gastos](notas/gastos.md)", "gastos", "cobros")
    assert (salida, n) == ("[cobros](notas/cobros.md)", 1)


def test_cuerpo_del_registro_con_link_markdown() -> None:
    ahora = f"## Lunes 7\n- 09:00 - {MD} **señal**: algo\n"
    assert rename.cuerpo_del_registro(ahora, "Lunes 7", "09:00") == "**señal**: algo"


def test_la_actividad_del_ambito_reescribe_las_rutas_de_los_otros_links() -> None:
    ahora = (
        "---\ntype: Logbook\nfrom: 2026-09-07\nto: 2026-09-13\n---\n\n"
        "## Lunes 7 de septiembre\n\n"
        f"- 09:00 - {MD} **nota**: escribí [n](notas/n.md) con [otro](ambitos/otro/otro.md)\n\n"
        "---\n"
    )
    actividad = scope.extraer_actividad_ambito(ahora, "personal")
    [linea] = actividad["## Lunes 7 de septiembre"]
    assert linea == (
        "- **nota**: escribí [n](../../notas/n.md) con [otro](../otro/otro.md)"
    )


def test_la_actividad_acepta_el_registro_con_wikilink() -> None:
    ahora = "## Lunes 7\n\n- 09:00 - [[personal]] **señal**: algo\n"
    assert scope.extraer_actividad_ambito(ahora, "personal") == {
        "## Lunes 7": ["- **señal**: algo"]
    }


def test_rutas_trae_ambitos_anidados_actividades_y_categorias(tmp_path: Path) -> None:
    def tocar(rel: str) -> None:
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("", encoding="utf-8")

    tocar("ambitos/trabajo/pewma/pewma.md")
    tocar("ambitos/trabajo/pewma/reunion.md")
    tocar("ambitos/trabajo/AGENTS.md")
    assert scope.rutas(tmp_path) == {
        "trabajo": "ambitos/trabajo",
        "pewma": "ambitos/trabajo/pewma/pewma.md",
        "reunion": "ambitos/trabajo/pewma/reunion.md",
    }


def _parsers(p: argparse.ArgumentParser, camino: str = "tuku") -> list[tuple[str, str | None]]:
    """Cada sustantivo y cada verbo del árbol de argparse, con su `description`."""
    salida = []
    for accion in p._actions:
        if isinstance(accion, argparse._SubParsersAction):
            for nombre, sub in accion.choices.items():
                ruta = f"{camino} {nombre}"
                salida.append((ruta, sub.description))
                salida += _parsers(sub, ruta)
    return salida


def test_todo_sustantivo_y_verbo_explica_para_que_existe() -> None:
    parsers = _parsers(cli._construir_parser())
    assert len(parsers) > 20
    sin = [ruta for ruta, descripcion in parsers if not (descripcion or "").strip()]
    assert not sin, f"sin `description`: {sin}"


def test_doctor_con_un_tema_desconocido_es_error_de_uso(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as e:
        cli.main(["doctor", "inexistente"])
    assert e.value.code == cli.USO
    assert "invalid choice" in capsys.readouterr().err


def test_fix_sin_tema_es_error_de_uso() -> None:
    with pytest.raises(SystemExit) as e:
        cli.main(["fix"])
    assert e.value.code == cli.USO


def test_el_sustantivo_link_ya_no_existe() -> None:
    assert "link backfill" not in cli.comandos()
    assert {"fix", "doctor"} <= cli.comandos()
