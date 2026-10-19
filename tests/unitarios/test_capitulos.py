"""Los capítulos `##` con una sola tabla que leen los comandos."""

from __future__ import annotations

from tuku import capitulos

TEXTO = """---
type: Style Guide
---

# Libro

Antes del primer capítulo.

## Uno

| A | B |
| --- | --- |
| `x` | 1 |

### Subtítulo libre

Prosa.

## Dos

```markdown
## No soy un capítulo

| fila | de ejemplo |
```

![Otro](reglas/otro.md) y de nuevo ![Otro](reglas/otro.md)

| C |
| --- |
| `y` |

Separada por prosa.

| D |
| --- |
"""


def test_los_capitulos_se_piden_por_nombre_y_traen_sus_tablas() -> None:
    nombres = [c.nombre for c in capitulos.separar(TEXTO)]
    assert nombres == ["Uno", "Dos"], (
        "una valla no abre capítulo y lo anterior a `##` no es de nadie"
    )
    assert capitulos.capitulo(TEXTO, "Tres") is None
    assert capitulos.capitulo(TEXTO, "Uno").linea == 9  # type: ignore[union-attr]

    assert capitulos.tabla_unica(TEXTO, "Uno") == [["A", "B"], ["`x`", "1"]]
    dos = capitulos.capitulo(TEXTO, "Dos")
    assert dos is not None and dos.tablas() == [[["C"], ["`y`"]], [["D"]]], (
        "la prosa separa las tablas y la valla no cuenta"
    )
    assert [c.nombre for c in capitulos.exceso_de_tablas(TEXTO)] == ["Dos"]
    assert capitulos.transclusiones(TEXTO) == ["reglas/otro.md"]


def test_expandir_reemplaza_la_transclusion_por_los_capitulos_del_archivo() -> None:
    otro = (
        "---\ntype: Config\n---\n\n# Título\n\n> aviso\n\n## Datos\n\n| X |\n| --- |\n| `a` |\n"
    )
    libro = (
        "## Cap\n\nantes\n\n![Otro](reglas/otro.md)\n\n"
        "![Falta](reglas/falta.md)\n\n![Fuera](../afuera.md)\n"
    )
    salida = capitulos.expandir(libro, {"reglas/otro.md": otro}.get)

    assert "### Datos" in salida and "| `a` |" in salida, "baja a ### dentro del capítulo"
    assert "Título" not in salida and "aviso" not in salida, "lo anterior al primer ## no entra"
    assert "> [!warning] falta reglas/falta.md" in salida
    assert "> [!warning] falta ../afuera.md" in salida, "una ruta que sale del vault no se lee"
    assert salida.startswith("## Cap\n\nantes\n\n### Datos")

    en_valla = "## Cap\n\n```\n![Otro](reglas/otro.md)\n```\n"
    assert capitulos.expandir(en_valla, {"reglas/otro.md": otro}.get) == en_valla.rstrip("\n")
