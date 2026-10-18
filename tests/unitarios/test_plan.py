"""Las reglas de `entry create`, `todo open`, `todo close` y `note create`, sobre texto.

Cada planner recibe lo que leyó del vault (`State`) y el instante (`AHORA`), y devuelve
un `Change` o el rechazo. El ejecutor `plan.apply` se prueba una vez, sobre un vault.
"""

from __future__ import annotations

import os
from datetime import date, datetime
from pathlib import Path

from conftest import AHORA
from tuku import entry, init, note, todo
from tuku.plan import Change, State, apply
from tuku.resultado import Resultado
from tuku.scope_tree import Tree

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent
DIA = date(2026, 8, 11)
PERSONAL = "[personal](ambitos/personal/personal.md)"
BODEGA = "[bodega](ambitos/bodega/bodega.md)"

LOGBOOK = (
    "---\ntype: Logbook\nfrom: 2026-08-10\nto: 2026-08-16\n---\n\n# Actividad diaria\n\n"
    + "".join(
        f"## {dia}\n\n"
        for dia in (
            "Lunes 10 de agosto",
            "Martes 11 de agosto",
            "Miércoles 12 de agosto",
            "Jueves 13 de agosto",
            "Viernes 14 de agosto",
            "Sábado 15 de agosto",
            "Domingo 16 de agosto",
        )
    )
)
TODO = (
    "---\ntype: Todo\n---\n\n"
    "| Horizonte | Vence | Ámbito | Detalle |\n| --- | --- | --- | --- |\n"
)
TREE = Tree(
    Path("/v"),
    frozenset({"personal", "bodega"}),
    {n: f"ambitos/{n}/{n}.md" for n in ("personal", "bodega")},
    frozenset({"personal", "bodega"}),
)


def state(
    logbook: str = LOGBOOK,
    rows: str = TODO,
    horizons: tuple[str, ...] = ("esta semana", "próxima semana"),
    default_scope: str | None = None,
) -> State:
    return State(
        TREE, logbook=logbook, todo=rows, horizons=horizons, default_scope=default_scope
    )


def plan_open(
    st: State | None = None,
    *,
    body: str = "pagar la patente",
    scope: str | None = "personal",
    due: str = "",
    day: date | None = DIA,
    hour: str | None = "14:20",
    now: datetime = AHORA,
) -> Change | Resultado:
    return todo.plan_open(
        st or state(),
        body=body,
        scope=scope,
        horizon=None,
        due=due,
        day=day,
        hour=hour,
        now=now,
    )


def plan_close(
    st: State,
    *,
    body: str = "pagar la patente",
    scope: str | None = None,
    day: date | None = DIA,
    hour: str | None = "19:05",
) -> Change | Resultado:
    return todo.plan_close(st, body=body, scope=scope, day=day, hour=hour, now=AHORA)


def plan_add(
    *,
    body: str = "llamé a Rodolfo",
    scope: str | None = "personal",
    day: date | None = DIA,
    hour: str | None = "09:12",
) -> Change | Resultado:
    st = State(TREE, logbook=LOGBOOK)
    return entry.plan_add(st, body=body, scope=scope, day=day, hour=hour, now=AHORA)


def change(plan: Change | Resultado) -> Change:
    assert isinstance(plan, Change), plan
    return plan


def rejection(plan: Change | Resultado) -> str:
    assert isinstance(plan, Resultado) and not plan.ok, plan
    return plan.mensaje


def records(logbook: str, heading: str) -> list[str]:
    seccion = logbook.split(f"## {heading}\n", 1)[1].split("\n## ", 1)[0]
    return [x for x in seccion.splitlines() if x.startswith("- ")]


def rows(table: str) -> list[str]:
    return [x for x in table.splitlines() if x.startswith("| ") and "Horizonte" not in x][1:]


# --- todo open ----------------------------------------------------------------


def test_open_writes_the_record_and_the_row_at_the_first_horizon() -> None:
    plan = change(plan_open())
    assert records(plan.files["AHORA.md"], "Martes 11 de agosto") == [
        f"- 14:20 - {PERSONAL} **pendiente**: pagar la patente"
    ]
    assert rows(plan.files["PENDIENTES.md"]) == [
        f"| esta semana |  | {PERSONAL} | pagar la patente |"
    ]
    assert plan.message == "pendiente abierto en «esta semana»: pagar la patente"
    assert plan.regenerate == ("AHORA.md", "PENDIENTES.md")

    quincena = state(horizons=("esta quincena", "este mes"))
    plan = change(plan_open(quincena, body="x", scope=None))
    assert rows(plan.files["PENDIENTES.md"]) == ["| esta quincena |  |  | x |"]


def test_open_without_day_or_hour_is_now_and_due_sets_the_date_horizon() -> None:
    plan = change(plan_open(day=None, hour=None))
    assert records(plan.files["AHORA.md"], "Miércoles 12 de agosto") == [
        f"- 09:00 - {PERSONAL} **pendiente**: pagar la patente"
    ]

    con_fecha = change(plan_open(hour="21:30", due="2026-08-13"))
    assert records(con_fecha.files["AHORA.md"], "Martes 11 de agosto") == [
        f"- 21:30 - {PERSONAL} **pendiente**: pagar la patente"
    ]
    assert rows(con_fecha.files["PENDIENTES.md"]) == [
        f"| con fecha | 2026-08-13 | {PERSONAL} | pagar la patente |"
    ]
    assert con_fecha.warnings == ()


def test_open_warns_when_the_deadline_has_passed_or_precedes_the_promise() -> None:
    (ya_paso,) = change(plan_open(day=None, hour=None, due="2026-08-10")).warnings
    assert "ya pasó" in ya_paso
    (antes,) = change(plan_open(hour="10:00", due="2026-08-11 09:00")).warnings
    assert "antes de" in antes
    assert change(plan_open(day=None, hour=None, due="2026-08-12 10:00")).warnings == ()


def test_open_rejects_a_future_day_an_unknown_scope_and_a_day_outside_the_cycle() -> None:
    assert "--due 2026-08-13" in rejection(plan_open(day=date(2026, 8, 13)))
    assert "tuku scope create casa" in rejection(plan_open(scope="casa"))
    assert "fuera del ciclo" in rejection(plan_open(day=date(2026, 7, 1)))


def test_open_twice_leaves_one_record_and_one_row_even_if_the_links_differ() -> None:
    con_link = "avisar a [Carmen](notas/carmen.md) de los GGCC"
    primero = change(plan_open(body=con_link))
    abierto = state(primero.files["AHORA.md"], primero.files["PENDIENTES.md"])
    segundo = change(plan_open(abierto, body="avisar a Carmen de los GGCC", hour="15:00"))
    assert segundo.files == primero.files


# --- todo close ---------------------------------------------------------------


def test_close_removes_the_row_and_writes_the_check_mark() -> None:
    abierto = change(plan_open())
    plan = change(plan_close(state(abierto.files["AHORA.md"], abierto.files["PENDIENTES.md"])))
    assert rows(plan.files["PENDIENTES.md"]) == []
    assert plan.message == "pendiente cerrado: pagar la patente"
    assert plan.warnings == ()


def test_close_lands_in_the_scope_of_the_row_then_the_default_then_the_given_one() -> None:
    def cierre(st: State, scope: str | None = None) -> str:
        plan = change(plan_close(st, body="contar el stock", scope=scope))
        return records(plan.files["AHORA.md"], "Martes 11 de agosto")[-1]

    def con_fila(scope: str | None, default_scope: str | None = None) -> State:
        abierto = change(plan_open(body="contar el stock", scope=scope))
        return state(rows=abierto.files["PENDIENTES.md"], default_scope=default_scope)

    assert cierre(con_fila("bodega")) == f"- 19:05 - {BODEGA} (Hecho): ~~contar el stock~~"
    en_personal = cierre(con_fila("bodega"), "personal")
    assert en_personal == f"- 19:05 - {PERSONAL} (Hecho): ~~contar el stock~~"
    assert cierre(con_fila(None)) == "- 19:05 - (Hecho): ~~contar el stock~~"
    por_defecto = cierre(con_fila(None, "personal"))
    assert por_defecto == f"- 19:05 - {PERSONAL} (Hecho): ~~contar el stock~~"
    sin_crear = plan_close(con_fila(None, "casa"), body="contar el stock")
    assert "tuku scope create casa" in rejection(sin_crear)


def test_close_without_a_row_reports_it_and_leaves_the_table() -> None:
    plan = change(plan_close(state(), body="algo que nunca se abrió"))
    assert plan.message == "cierre escrito: algo que nunca se abrió"
    assert "palabra por palabra" in plan.warnings[0]
    assert plan.files["PENDIENTES.md"] == TODO
    assert records(plan.files["AHORA.md"], "Martes 11 de agosto") == [
        "- 19:05 - (Hecho): ~~algo que nunca se abrió~~"
    ]


def test_close_matches_ignoring_links_removes_the_same_day_opening_and_is_idempotent() -> None:
    con_link = "avisar a [Carmen](notas/carmen.md) de los GGCC"
    sin_link = "avisar a Carmen de los GGCC"
    abierto = change(plan_open(body=sin_link))
    st = state(abierto.files["AHORA.md"], abierto.files["PENDIENTES.md"])
    cierre = change(plan_close(st, body=con_link))
    assert rows(cierre.files["PENDIENTES.md"]) == []
    assert records(cierre.files["AHORA.md"], "Martes 11 de agosto") == [
        f"- 19:05 - {PERSONAL} (Hecho): ~~{con_link}~~"
    ]

    cerrado = state(cierre.files["AHORA.md"], cierre.files["PENDIENTES.md"])
    assert change(plan_close(cerrado, body=sin_link)).files == cierre.files


# --- entry create -------------------------------------------------------------


def test_add_takes_the_hour_from_now_only_when_the_day_is_today() -> None:
    plan = change(plan_add(day=None, hour=None))
    assert records(plan.files["AHORA.md"], "Miércoles 12 de agosto") == [
        f"- 09:00 - {PERSONAL} llamé a Rodolfo"
    ]
    assert plan.regenerate == ("AHORA.md",)

    pasado = change(plan_add(hour=None))
    assert records(pasado.files["AHORA.md"], "Martes 11 de agosto") == [
        f"- {PERSONAL} llamé a Rodolfo"
    ]


def test_add_rejects_a_future_day_an_unknown_scope_and_a_day_outside_the_cycle() -> None:
    assert "todo open --due 2026-08-13" in rejection(plan_add(day=date(2026, 8, 13)))
    assert "tuku scope create casa" in rejection(plan_add(scope="casa"))
    assert "fuera del ciclo" in rejection(plan_add(day=date(2026, 7, 1)))


def test_add_sends_open_and_close_marks_to_their_command() -> None:
    sin_link = "avisar a Carmen de los GGCC"
    abre = rejection(plan_add(body=f"**pendiente**: {sin_link}", hour="14:20"))
    comando = f"tuku todo open --scope personal --at '2026-08-11 14:20' --body '{sin_link}'"
    assert comando in abre
    cierra = rejection(plan_add(body=f"(Hecho): ~~{sin_link}~~", scope=None, hour="19:05"))
    assert f"tuku todo close --at '2026-08-11 19:05' '{sin_link}'" in cierra


# --- note create --------------------------------------------------------------


def plan_note(
    *,
    title: str = "Contrato del colegio",
    scope: str | None = "personal",
    day: date | None = DIA,
    hour: str | None = "10:00",
    record: bool = True,
    subtype: str | None = None,
    logbook: str | None = LOGBOOK,
    notes: frozenset[str] = frozenset(),
    note_types: tuple[str, ...] = ("persona",),
) -> Change | Resultado:
    st = note.NoteState(TREE, logbook=logbook, notes=notes, note_types=note_types)
    return note.plan_create(
        st,
        title=title,
        body="Lo redactó [don Rodolfo](rodolfo-cifuentes.md)",
        scope=scope,
        day=day,
        hour=hour,
        record=record,
        subtype=subtype,
        now=AHORA,
    )


def test_note_writes_the_file_its_record_and_asks_for_the_scope_page() -> None:
    plan = change(plan_note())
    texto = plan.files["notas/contrato-del-colegio.md"]
    assert texto.startswith("---\ntype: Note\ncreated: 2026-08-11\nupdated: 2026-08-11\n---")
    assert "* [don Rodolfo](rodolfo-cifuentes.md) — mencionada en el cuerpo." in texto
    assert records(plan.files["AHORA.md"], "Martes 11 de agosto") == [
        f"- 10:00 - {PERSONAL} **nota**: escribí la nota "
        "[contrato-del-colegio](notas/contrato-del-colegio.md)"
    ]
    assert plan.pages == ("personal",)
    assert plan.message == "nota creada en /v/notas/contrato-del-colegio.md."

    tipada = change(plan_note(subtype=" Persona ", record=False))
    assert "subtype: persona\n" in tipada.files["notas/contrato-del-colegio.md"]
    assert "AHORA.md" not in tipada.files and tipada.pages == ()


def test_note_keeps_an_existing_note_and_does_not_repeat_the_record() -> None:
    primera = change(plan_note())
    ya_hecha = plan_note(
        logbook=primera.files["AHORA.md"], notes=frozenset({"contrato-del-colegio.md"})
    )
    assert change(ya_hecha).files == {}
    sin_ahora = change(plan_note(logbook=None))
    assert list(sin_ahora.files) == ["notas/contrato-del-colegio.md"]


def test_note_rejects_a_bad_title_subtype_scope_or_day() -> None:
    assert "sin letras ni números" in rejection(plan_note(title="¿?"))
    sin_tipo = rejection(plan_note(subtype="cliente"))
    assert "no es un tipo de nota" in sin_tipo and "`persona`" in sin_tipo
    assert "tuku scope create casa" in rejection(plan_note(scope="casa"))
    assert "fuera del ciclo" in rejection(plan_note(day=date(2026, 7, 1)))


# --- el ejecutor --------------------------------------------------------------


def test_apply_writes_only_what_differs_and_regenerates(tmp_path: Path) -> None:
    vault = init.init(tmp_path / "v", home=RAIZ_REPO, desde=date(2026, 8, 10))

    def abrir(
        body: str = "pagar la patente", *, regenerar: bool = True, due: str = ""
    ) -> Resultado:
        return todo.abrir_en_vault(
            vault,
            body=body,
            scope="personal",
            due=due,
            day=DIA,
            hour="14:20",
            regenerar=regenerar,
            now=AHORA,
        )

    r = abrir()
    assert r.ok and r.mensaje == "pendiente abierto en «esta semana»: pagar la patente"
    ahora = vault / "AHORA.md"
    assert "**pendiente**: pagar la patente" in ahora.read_text(encoding="utf-8")
    assert "pagar la patente" in (vault / "PENDIENTES.md").read_text(encoding="utf-8")

    os.utime(ahora, ns=(1, 1))
    assert abrir().ok
    assert ahora.stat().st_mtime_ns == 1, "abrir dos veces no reescribe AHORA.md"

    vista = vault / "ambitos" / "PENDIENTES-AMBITOS.md"
    antes = vista.read_bytes()
    assert abrir("otro", regenerar=False).ok
    assert vista.read_bytes() == antes, "--no-regenerate deja las vistas como estaban"

    assert abrir("con hora", due="2026-08-13 09:00").ok
    assert "> - Ago/13 09:00 - con hora" in vista.read_text(encoding="utf-8")
    assert todo.cerrar_en_vault(vault, body="otro", day=DIA, hour="19:05", now=AHORA).ok
    assert entry.add_al_vault(vault, body="comí", day=DIA, hour="20:00", now=AHORA).ok

    rechazo = Resultado.rechazo("no")
    assert apply(vault, rechazo) is rechazo
    assert apply(vault, Change({}, "nada"), skip=("todo",)).mensaje == "nada"
