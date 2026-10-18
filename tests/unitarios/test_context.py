"""`tuku context`: registros recientes, ámbitos, pendientes, vocabulario y notas."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from tuku import context, entry, init, scope, todo
from tuku.cli import EXITO, main

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent
HOY = date(2026, 8, 12)


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
    )
    todo.abrir_en_vault(
        v,
        body="enviar la cotización",
        scope="personal",
        due="2026-08-11",
        day=date(2026, 8, 10),
        hour="09:00",
    )
    return v


def test_since_es_un_numero_de_dias_o_una_fecha() -> None:
    assert context.desde(None, HOY) == date(2026, 8, 10)
    assert context.desde("7", HOY) == date(2026, 8, 5)
    assert context.desde("2026-08-01", HOY) == date(2026, 8, 1)
    with pytest.raises(ValueError, match="--since 7"):
        context.desde("ayer", HOY)


def test_entry_lee_los_dias_desde_since_tambien_en_un_ciclo_cerrado(vault: Path) -> None:
    salida = context.del_vault(vault, "entry", "3", hoy=HOY).mensaje
    assert "## Domingo 9 de agosto\n- 18:00 - revisé las cuentas" in salida
    assert "llamé a [don Rodolfo]" in salida
    assert "entregué los cuadernos" not in salida


def test_scope_todo_y_note(vault: Path) -> None:
    assert "- colegio-los-robles: don-rodolfo, lr" in context.del_vault(vault, "scope").mensaje
    pendientes = context.del_vault(vault, "todo", hoy=HOY).mensaje
    assert (
        "- con fecha, vence 2026-08-11, atrasado: enviar la cotización (personal)" in pendientes
    )
    notas = context.del_vault(vault, "note", hoy=HOY).mensaje
    assert notas == "- notas/rodolfo-cifuentes.md (persona), mencionada el 2026-08-11"


def test_sin_tema_trae_todos_y_since_malo_rechaza(vault: Path) -> None:
    todo_junto = context.del_vault(vault, hoy=HOY).mensaje
    for titulo in (
        "# Registros desde",
        "# Ámbitos",
        "# Pendientes",
        "# Vocabulario",
        "# Notas",
    ):
        assert titulo in todo_junto
    assert not context.del_vault(vault, since="ayer", hoy=HOY).ok
    assert main(["context", "scope", "--vault", str(vault)]) == EXITO
