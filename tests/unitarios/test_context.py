"""`tuku context`: registros recientes, ámbitos, pendientes, vocabulario y notas."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pytest

from conftest import AHORA
from tuku import context, entry, init, scope, todo
from tuku.cli import EXITO, main
from tuku.vocab import VocabularioIncompleto

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent
HOY = AHORA.date()
DIA = date(2026, 8, 10)


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    v = init.init(tmp_path / "v", home=RAIZ_REPO, desde=date(2026, 8, 10))
    scope.crear(v, "colegio-los-robles", palabras=["don Rodolfo", "LR"])
    (v / "bitacoras").mkdir()
    (v / "bitacoras" / "bitacora-2026-08-03-2026-08-09.md").write_text(
        "---\ntype: Logbook\nstatus: stable\nfrom: 2026-08-03\nto: 2026-08-09\n---\n\n"
        "## Sábado 8 de agosto\n\n- 10:00 - entregué los cuadernos\n\n"
        "## Domingo 9 de agosto\n\n- 18:00 - revisé las cuentas\n",
        encoding="utf-8",
    )
    (v / "notas" / "rodolfo-cifuentes.md").write_text(
        "---\ntype: Note\nsubtype: persona\n---\n# Rodolfo Cifuentes\n", encoding="utf-8"
    )
    entry.add_al_vault(
        v,
        body="llamé a [don Rodolfo](notas/rodolfo-cifuentes.md)",
        scope="colegio-los-robles",
        day=date(2026, 8, 11),
        hour="07:41",
        now=AHORA,
    )
    todo.abrir_en_vault(
        v,
        body="enviar la cotización",
        scope="personal",
        due="2026-08-11",
        day=date(2026, 8, 10),
        hour="09:00",
        now=AHORA,
    )
    return v


def test_since_es_un_numero_de_dias_o_una_fecha() -> None:
    assert context.desde(None, HOY) == date(2026, 8, 10)
    assert context.desde("7", HOY) == date(2026, 8, 5)
    assert context.desde("2026-08-01", HOY) == date(2026, 8, 1)
    with pytest.raises(ValueError, match="--since 7"):
        context.desde("ayer", HOY)


def test_entry_lee_los_dias_desde_since_tambien_en_un_ciclo_cerrado(vault: Path) -> None:
    salida = context.del_vault(vault, "entry", "3", now=AHORA).mensaje
    assert "## Domingo 9 de agosto\n- 18:00 - revisé las cuentas" in salida
    assert "llamé a [don Rodolfo]" in salida
    assert "entregué los cuadernos" not in salida


def test_scope_todo_y_note(vault: Path) -> None:
    assert (
        "- colegio-los-robles: don-rodolfo, lr"
        in context.del_vault(vault, "scope", now=AHORA).mensaje
    )
    pendientes = context.del_vault(vault, "todo", now=AHORA).mensaje
    assert (
        "- con fecha, vence 2026-08-11, atrasado: enviar la cotización (personal)" in pendientes
    )
    notas = context.del_vault(vault, "note", now=AHORA).mensaje
    assert notas == "## persona\n\n- notas/rodolfo-cifuentes.md: Rodolfo Cifuentes"


def test_late_deja_solo_los_pendientes_cuyo_vence_ya_paso(vault: Path) -> None:
    todo.abrir_en_vault(
        vault,
        body="recibir la cartulina",
        scope="personal",
        due="2026-08-12",
        day=date(2026, 8, 10),
        hour="09:05",
        now=AHORA,
    )
    todo.abrir_en_vault(
        vault,
        body="ordenar el archivo",
        scope="personal",
        day=DIA,
        hour="09:10",
        now=AHORA,
    )

    todos = context.del_vault(vault, "todo", now=AHORA).mensaje
    assert "recibir la cartulina" in todos and "ordenar el archivo" in todos

    tarde = context.del_vault(vault, "todo", now=AHORA, late=True).mensaje
    assert tarde == "- con fecha, vence 2026-08-11, atrasado: enviar la cotización (personal)"

    mañana = context.del_vault(vault, "todo", now=AHORA + timedelta(days=1), late=True).mensaje
    assert "recibir la cartulina" in mañana and "ordenar el archivo" not in mañana

    assert (
        context.del_vault(vault, "todo", now=AHORA - timedelta(days=2), late=True).mensaje
        == "sin pendientes atrasados."
    )


def test_late_sin_el_tema_todo_es_un_error_de_uso(
    vault: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(SystemExit) as e:
        main(["context", "scope", "--late", "--vault", str(vault)])
    assert e.value.code == 2
    assert "--late solo vale con el tema `todo`" in capsys.readouterr().err
    assert main(["context", "todo", "--late", "--vault", str(vault)]) == EXITO


def test_sin_tema_trae_todos_y_since_malo_rechaza(vault: Path) -> None:
    todo_junto = context.del_vault(vault, now=AHORA).mensaje
    for titulo in (
        "# Registros desde",
        "# Ámbitos",
        "# Pendientes",
        "# Vocabulario",
        "# Notas",
    ):
        assert titulo in todo_junto
    assert not context.del_vault(vault, since="ayer", now=AHORA).ok
    assert main(["context", "scope", "--vault", str(vault)]) == EXITO


def test_style_entrega_el_libro_con_las_reglas_transcluidas_y_un_capitulo_a_la_vez(
    vault: Path,
) -> None:
    libro = context.del_vault(vault, "style", now=AHORA).mensaje
    assert "![" not in libro, "cada transclusión se reemplaza por el archivo"
    assert (
        libro.index("## Para qué sirve")
        < libro.index("## Registro")
        < libro.index("## Pendiente")
    )
    assert "| `progreso` |" in libro and "| `esta semana` |" in libro
    assert "### Clasificaciones" in libro, "los capítulos de reglas/ bajan bajo el del libro"
    assert "Este archivo es del autor" not in libro, "lo anterior al primer capítulo no entra"

    pendiente = context.del_vault(vault, "style", now=AHORA, chapter="Pendiente").mensaje
    assert pendiente.startswith("## Pendiente") and "esta semana" in pendiente
    assert "## Registro" not in pendiente and "progreso" not in pendiente

    r = context.del_vault(vault, "style", now=AHORA, chapter="Nada")
    assert not r.ok and "«Registro»" in r.mensaje, "el rechazo lista los capítulos que hay"

    (vault / "reglas" / "notas.md").unlink()
    with pytest.raises(VocabularioIncompleto, match=r"falta reglas/notas\.md"):
        context.del_vault(vault, "style", now=AHORA)  # `main` lo traduce a un rechazo


def test_cadence_junta_las_del_arbol_con_su_origen_y_no_entra_en_todos(vault: Path) -> None:
    (vault / "ambitos" / "colegio-los-robles" / "CADENCIAS.md").write_text(
        "---\ntype: Cadence\n---\n\n# Cadencias\n\n## Reunión de apoderados\n\n"
        "**Cuándo:** primer lunes, mensual\n**Emite:** pendiente con fecha\n",
        encoding="utf-8",
    )
    salida = context.del_vault(vault, "cadence", now=AHORA).mensaje
    assert "origen: ambitos/CADENCIAS.md; alcance: ambitos" in salida
    assert (
        "origen: ambitos/colegio-los-robles/CADENCIAS.md; alcance: ambitos/colegio-los-robles"
        in salida
    )
    assert salida.index("## Apertura de la semana") < salida.index("## Reunión de apoderados")
    assert "Cadencias" not in context.del_vault(vault, now=AHORA).mensaje


def test_chapter_sin_el_tema_style_es_un_error_de_uso(
    vault: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(SystemExit) as e:
        main(["context", "todo", "--chapter", "Pendiente", "--vault", str(vault)])
    assert e.value.code == 2
    assert "--chapter solo vale con el tema `style`" in capsys.readouterr().err
    assert main(["context", "style", "--chapter", "Pendiente", "--vault", str(vault)]) == EXITO
