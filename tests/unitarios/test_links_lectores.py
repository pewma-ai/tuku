"""Los lectores aceptan los dos formatos y los escritores solo producen Markdown."""

from __future__ import annotations

from pathlib import Path

from tuku import entry, regenerate, rename, scope, todo

MD = "[personal](ambitos/personal/personal.md)"


def test_los_lectores_aceptan_wikilink_y_link_markdown() -> None:
    wiki = todo.parsear("- 14:20 - [[personal]] **pendiente**: comprar pan")
    md = todo.parsear(f"- 14:20 - {MD} **pendiente**: comprar pan")
    assert wiki is not None and md is not None
    assert wiki == md and md.ambito == "personal"

    anidado = todo.parsear("- 14:20 - [pewma](ambitos/trabajo/pewma/pewma.md) **pendiente**: x")
    assert anidado is not None and anidado.ambito == "pewma"

    ahora = f"## Lunes 7 de septiembre\n- 09:00 - {MD} **señal**: algo\n"
    assert [(r.hora, r.ambito, r.cuerpo) for r in entry.registros(ahora)] == [
        ("09:00", "personal", "**señal**: algo")
    ]

    wiki_ahora = "## Lunes 7\n\n- 09:00 - [[personal]] **señal**: algo\n"
    assert scope.extraer_actividad_ambito(wiki_ahora, "personal") == {
        "## Lunes 7": ["- **señal**: algo"]
    }


def test_los_escritores_producen_markdown_con_la_ruta_completa() -> None:
    fila = todo.Fila("esta semana", "", "personal", "comprar pan")
    assert fila.linea() == f"| esta semana |  | {MD} | comprar pan |"
    tabla = f"| Horizonte | Vence | Ámbito | Detalle |\n| - | - | - | - |\n{fila.linea()}\n"
    assert todo.filas(tabla) == [fila]
    assert todo.filas(tabla.replace(MD, "[[personal]]")) == [fila]

    rutas = {"pewma": "ambitos/trabajo/pewma/pewma.md"}
    anidada = todo.Fila("con fecha", "2026-09-08", "pewma", "x")
    assert "[pewma](ambitos/trabajo/pewma/pewma.md)" in anidada.linea(rutas)
    assert (
        regenerate.linea_del_dia(anidada, rutas)
        == "- [pewma](ambitos/trabajo/pewma/pewma.md) - x"
    )


def test_renombrar_cambia_texto_y_ruta_sin_tocar_lo_que_eligio_el_autor() -> None:
    texto = "ver [personal](ambitos/personal/personal.md#a) y [otro](ambitos/otro/otro.md)"
    assert rename.renombrar_enlaces(texto, "personal", "propio") == (
        "ver [propio](ambitos/propio/propio.md#a) y [otro](ambitos/otro/otro.md)",
        1,
    )
    assert rename.renombrar_enlaces(
        "[mi casa](ambitos/personal/personal.md)", "personal", "propio"
    ) == ("[mi casa](ambitos/propio/propio.md)", 1)
    assert rename.renombrar_enlaces("[gastos](notas/gastos.md)", "gastos", "cobros") == (
        "[cobros](notas/cobros.md)",
        1,
    )


def test_la_actividad_del_ambito_reescribe_las_rutas_de_los_otros_links() -> None:
    ahora = (
        "---\ntype: Logbook\nfrom: 2026-09-07\nto: 2026-09-13\n---\n\n"
        "## Lunes 7 de septiembre\n\n"
        f"- 09:00 - {MD} **nota**: escribí [n](notas/n.md) con [otro](ambitos/otro/otro.md)\n\n"
        "---\n"
    )
    [linea] = scope.extraer_actividad_ambito(ahora, "personal")["## Lunes 7 de septiembre"]
    assert linea == "- **nota**: escribí [n](../../notas/n.md) con [otro](../otro/otro.md)"


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
