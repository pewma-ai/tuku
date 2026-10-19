"""Notas enlazables: la columna "Enlazable" del libro decide qué trae `context note`."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pytest

from conftest import AHORA
from tuku import context, entry, init, note, todo, vocab
from tuku.config import limite_de_notas

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent
HOY = AHORA.date()

LIBRO = """### Tipos de nota

| Tipo | Para qué | Cuidado | Enlazable |
| --- | --- | --- | --- |
| `persona` | Trabajar con alguien. | Lo que se le mostraría. | sí |
| `idea` | Pensar algo. | Nada. | no |

## Otra sección
"""


def test_el_libro_dice_que_tipos_se_enlazan_y_el_template_enlaza_personas() -> None:
    assert vocab.enlazables(LIBRO) == ["persona"]
    sin_columna = "### Tipos de nota\n\n| Tipo | Para qué |\n| --- | --- |\n| `persona` | x |\n"
    assert vocab.enlazables(sin_columna) == []
    assert vocab.enlazables("# Libro sin tipos\n") == []
    libro = RAIZ_REPO / "template" / "vanilla" / "LIBRO-DE-ESTILO.md"
    assert vocab.enlazables(libro.read_text(encoding="utf-8")) == ["persona"]


def _nota(v: Path, nombre: str, subtype: str, titulo: str, aliases: str = "") -> None:
    extra = f"aliases: [{aliases}]\n" if aliases else ""
    (v / "notas" / f"{nombre}.md").write_text(
        f"---\ntype: Note\nsubtype: {subtype}\n{extra}---\n# {titulo}\n", encoding="utf-8"
    )


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    v = init.init(tmp_path / "v", home=RAIZ_REPO, desde=date(2026, 8, 10))
    _nota(v, "rodolfo-cifuentes", "persona", "Rodolfo Cifuentes", "don Rodolfo")
    _nota(v, "teletrabajo", "idea", "Teletrabajo")
    return v


def test_los_comandos_no_enlazan_solos(vault: Path) -> None:
    """Qué nota enlazar lo decide el agente con `tuku context note`, no el comando."""
    entry.add_al_vault(
        vault,
        body="hablé con don Rodolfo",
        day=date(2026, 8, 11),
        hour="07:41",
        now=AHORA,
    )
    r = todo.abrir_en_vault(
        vault,
        body="mandarle el contrato a Rodolfo Cifuentes",
        day=date(2026, 8, 11),
        hour="09:00",
        now=AHORA,
    )
    assert r.ok and not r.avisos
    for nombre in ("AHORA.md", "PENDIENTES.md"):
        assert "rodolfo-cifuentes.md" not in (vault / nombre).read_text(encoding="utf-8")


def test_note_create_lista_en_ver_ademas_los_links_del_cuerpo(vault: Path) -> None:
    r = note.crear_con_constancia(
        vault,
        title="Contrato del colegio",
        body="Lo redactó [don Rodolfo](rodolfo-cifuentes.md) y [Rodolfo](rodolfo-cifuentes.md)",
        day=date(2026, 8, 11),
        hour="10:00",
        now=AHORA,
    )
    assert r.ok
    texto = (vault / "notas" / "contrato-del-colegio.md").read_text(encoding="utf-8")
    assert texto.count("* [don Rodolfo](rodolfo-cifuentes.md) — mencionada en el cuerpo.") == 1
    assert note.lint(texto) == []


def test_subtype_se_escribe_si_la_tabla_lo_lista_y_se_rechaza_si_no(vault: Path) -> None:
    r = note.crear_con_constancia(
        vault,
        title="Patricia Lillo",
        body="Jefa de UTP.",
        subtype="persona",
        record=False,
        now=AHORA,
    )
    assert r.ok
    texto = (vault / "notas" / "patricia-lillo.md").read_text(encoding="utf-8")
    assert texto.startswith("---\ntype: Note\nsubtype: persona\ncreated: ")
    assert note.campo(texto, "updated") == note.campo(texto, "created")
    assert note.subtype(texto) == "persona"

    antes = sorted(p.name for p in (vault / "notas").iterdir())
    r = note.crear_con_constancia(
        vault, title="Un cliente", body="x", subtype="cliente", now=AHORA
    )
    assert not r.ok and "no es un tipo de nota" in r.mensaje and "`persona`" in r.mensaje
    assert "agrega una fila" in r.mensaje
    assert sorted(p.name for p in (vault / "notas").iterdir()) == antes


def _actualizada(v: Path, nombre: str, dia: str) -> None:
    """La nota `nombre` pasa a tener `updated: dia`."""
    ruta = v / "notas" / f"{nombre}.md"
    ruta.write_text(
        note.con_updated(ruta.read_text(encoding="utf-8"), date.fromisoformat(dia)),
        encoding="utf-8",
    )


def test_context_note_lista_por_tipo_enlazable_y_dice_cuando_no_hay(vault: Path) -> None:
    assert context.del_vault(vault, "note", now=AHORA).mensaje == (
        "## persona\n\n- notas/rodolfo-cifuentes.md: Rodolfo Cifuentes; aliases: don Rodolfo"
    )
    libro = vault / "LIBRO-DE-ESTILO.md"
    libro.write_text(
        libro.read_text(encoding="utf-8").replace("| sí |", "| no |"), encoding="utf-8"
    )
    assert context.del_vault(vault, "note", now=AHORA).mensaje == (
        "sin tipos enlazables en `### Tipos de nota`."
    ), "sin tipos enlazables lo dice"


def test_context_note_trae_las_ultimas_hasta_un_limite_que_cae_a_25(vault: Path) -> None:
    for n in ("ana", "beto", "carla"):
        _nota(vault, n, "persona", n.capitalize())
    _actualizada(vault, "ana", "2026-08-01")
    _actualizada(vault, "rodolfo-cifuentes", "2026-08-05")
    _actualizada(vault, "beto", "2026-08-09")
    _actualizada(vault, "carla", "2026-08-10")
    config = vault / "reglas" / "config.tuku.md"
    assert limite_de_notas(vault) == 25
    for valor in ("diez", "0", "-3"):
        config.write_text(
            config.read_text(encoding="utf-8").replace("| `25` |", f"| `{valor}` |"),
            encoding="utf-8",
        )
        assert limite_de_notas(vault) == 25
        config.write_text(
            config.read_text(encoding="utf-8").replace(f"| `{valor}` |", "| `25` |"),
            encoding="utf-8",
        )
    config.write_text(
        config.read_text(encoding="utf-8").replace("| `25` |", "| `3` |"),
        encoding="utf-8",
    )
    salida = context.del_vault(vault, "note", now=AHORA).mensaje
    assert salida.splitlines()[2:] == [
        "- notas/carla.md: Carla",
        "- notas/beto.md: Beto",
        "- notas/rodolfo-cifuentes.md: Rodolfo Cifuentes; aliases: don Rodolfo",
    ]


def test_updated_se_mueve_al_renombrar_y_created_queda(vault: Path) -> None:
    note.crear_con_constancia(
        vault,
        title="Ana Pérez",
        body="Jefa de UTP.",
        day=date(2026, 8, 11),
        record=False,
        now=AHORA,
    )
    r = note.renombrar_en_vault(
        vault, "Ana Pérez", "Ana Pérez Soto", now=AHORA + timedelta(days=8)
    )
    assert r.ok
    texto = (vault / "notas" / "ana-perez-soto.md").read_text(encoding="utf-8")
    assert note.campo(texto, "updated") == "2026-08-20"
    assert note.campo(texto, "created") == "2026-08-11"
    assert texto.index("created:") < texto.index("updated:")


def test_con_updated_no_inventa_frontmatter_ni_duplica_el_campo() -> None:
    assert note.con_updated("# Sin frontmatter\n", date(2026, 8, 1)) == "# Sin frontmatter\n"
    una = note.con_updated("---\ntype: Note\n---\n# T\n", date(2026, 8, 1))
    dos = note.con_updated(una, date(2026, 8, 2))
    assert dos == "---\ntype: Note\nupdated: 2026-08-02\n---\n# T\n"
    assert note.modificada("---\ncreated: 2026-07-01\n---\n") == "2026-07-01"
    assert note.modificada("# nada") == ""
