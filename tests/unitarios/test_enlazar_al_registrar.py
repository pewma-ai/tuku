"""Enlazar al registrar: la columna "Enlazable" del libro decide qué notas se enlazan solas."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from tuku import context, entry, init, note, todo, vocab

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent
HOY = date(2026, 8, 12)

LIBRO = """### Tipos de nota

| Tipo | Para qué | Cuidado | Enlazable |
| --- | --- | --- | --- |
| `persona` | Trabajar con alguien. | Lo que se le mostraría. | sí |
| `idea` | Pensar algo. | Nada. | no |

## Otra sección
"""


def test_el_libro_dice_que_tipos_se_enlazan() -> None:
    assert vocab.enlazables(LIBRO) == ["persona"]
    sin_columna = "### Tipos de nota\n\n| Tipo | Para qué |\n| --- | --- |\n| `persona` | x |\n"
    assert vocab.enlazables(sin_columna) == []
    assert vocab.enlazables("# Libro sin tipos\n") == []


def test_el_template_enlaza_personas() -> None:
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


def test_entry_create_enlaza_la_persona_y_no_la_idea(vault: Path) -> None:
    r = entry.add_al_vault(
        vault,
        body="hablé con don Rodolfo del teletrabajo",
        day=date(2026, 8, 11),
        hour="07:41",
    )
    assert r.ok and not r.avisos
    ahora = (vault / "AHORA.md").read_text(encoding="utf-8")
    assert "hablé con [don Rodolfo](notas/rodolfo-cifuentes.md) del teletrabajo" in ahora


def test_todo_open_enlaza_en_la_bitacora_y_en_pendientes(vault: Path) -> None:
    r = todo.abrir_en_vault(
        vault,
        body="mandarle el contrato a Rodolfo Cifuentes",
        day=date(2026, 8, 11),
        hour="09:00",
    )
    assert r.ok
    enlace = "[Rodolfo Cifuentes](notas/rodolfo-cifuentes.md)"
    assert enlace in (vault / "AHORA.md").read_text(encoding="utf-8")
    assert enlace in (vault / "PENDIENTES.md").read_text(encoding="utf-8")


def test_note_create_enlaza_a_otra_persona_y_no_a_si_misma(vault: Path) -> None:
    r = note.crear_con_constancia(
        vault,
        title="Contrato del colegio",
        body="Lo redactó don Rodolfo.",
        day=date(2026, 8, 11),
        hour="10:00",
    )
    assert r.ok
    texto = (vault / "notas" / "contrato-del-colegio.md").read_text(encoding="utf-8")
    assert "Lo redactó [don Rodolfo](rodolfo-cifuentes.md)." in texto

    note.crear_con_constancia(
        vault,
        title="Ana Pérez",
        body="Ana Pérez es la jefa de UTP.",
        day=date(2026, 8, 11),
        hour="10:05",
        record=False,
    )
    propia = (vault / "notas" / "ana-perez.md").read_text(encoding="utf-8")
    assert "Ana Pérez es la jefa de UTP." in propia


def test_un_nombre_de_dos_personas_queda_sin_link_y_avisa(vault: Path) -> None:
    _nota(vault, "rodolfo-perez", "persona", "Rodolfo Pérez", "don Rodolfo")
    r = entry.add_al_vault(
        vault, body="llamé a don Rodolfo", day=date(2026, 8, 11), hour="08:00"
    )
    assert r.ok
    assert "- 08:00 - llamé a don Rodolfo" in (vault / "AHORA.md").read_text(encoding="utf-8")
    [aviso] = r.avisos
    assert "'don rodolfo' nombra a más de una nota" in aviso


def test_context_note_lista_solo_los_tipos_enlazables(vault: Path) -> None:
    entry.add_al_vault(
        vault,
        body="leí [teletrabajo](notas/teletrabajo.md) con don Rodolfo",
        day=date(2026, 8, 11),
        hour="07:41",
    )
    assert context.del_vault(vault, "note", hoy=HOY).mensaje == (
        "- notas/rodolfo-cifuentes.md (persona), mencionada el 2026-08-11"
    )
