"""El autoarchivado: lo que sale de la ventana de `AHORA.md` pasa a bitácoras semanales."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import pytest

from tuku import archive, init
from tuku.cli import EXITO, main
from tuku.plan import Change

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent
P = "[personal](ambitos/personal/personal.md)"
P_ARCHIVADO = "[personal](../ambitos/personal/personal.md)"

#: Dos semanas y un poco más: la del lunes 19 (completa), la del 26 (completa) y el lunes 2.
AHORA = f"""---
type: Logbook
status: draft
---
# Actividad diaria

> [!abstract] Foco
> Cerrar la cotización.

> [!todo] Pendientes de los próximos 7 días
> - pagar la patente

## Lunes 2 de noviembre

- 08:00 - {P} sigue en la ventana

## Domingo 1 de noviembre

> [!todo] Pendientes del día
> - 18:00 - {P} - llevar las llaves

- 20:00 - {P} cena con [Carmen](notas/carmen.md)
- 09:00 - paseo

## Lunes 26 de octubre

- 10:00 - {P} reunión

## Domingo 25 de octubre

- 11:00 - {P} cierre de la semana

## Lunes 19 de octubre

- 07:30 - arranque
"""
DOMINGO_1 = "bitacoras/bitacora-20261026-20261101.md"
DOMINGO_25 = "bitacoras/bitacora-20261019-20261025.md"


def _plan(
    texto: str, hoy: date, history: dict[str, str] | None = None, weeks: int = 2
) -> Change:
    return archive.plan_archive(texto, history or {}, today=hoy, weeks=weeks)


def _aplicar(plan: Change, ahora: str, history: dict[str, str]) -> tuple[str, dict[str, str]]:
    nuevo = dict(history)
    nuevo.update({k: v for k, v in plan.files.items() if k != "AHORA.md"})
    return plan.files.get("AHORA.md", ahora), nuevo


def _registros(texto: str) -> list[str]:
    return [x for x in texto.splitlines() if x.startswith("- ")]


def test_la_ventana_empieza_el_lunes_de_la_semana_anterior() -> None:
    lunes, domingo = date(2026, 11, 2), date(2026, 11, 8)
    assert archive.window_start(lunes) == archive.window_start(domingo) == date(2026, 10, 26)
    assert archive.window_start(date(2026, 11, 9)) == date(2026, 11, 2)
    assert (lunes - archive.window_start(lunes)).days + 1 == 8
    assert (domingo - archive.window_start(domingo)).days + 1 == 14
    assert archive.window_start(lunes, 1) == lunes
    assert archive.window_start(lunes, 3) == date(2026, 10, 19)
    assert archive.week_of(date(2026, 10, 25)) == (date(2026, 10, 19), date(2026, 10, 25))


def test_el_domingo_no_archiva_la_semana_anterior_y_el_lunes_siguiente_si() -> None:
    domingo = _plan(AHORA, date(2026, 11, 8))
    assert DOMINGO_1 not in domingo.files
    assert "## Lunes 26 de octubre" in domingo.files["AHORA.md"]

    lunes = _plan(AHORA, date(2026, 11, 9))
    assert "## Lunes 26 de octubre" not in lunes.files["AHORA.md"]
    assert "## Lunes 26 de octubre" in lunes.files[DOMINGO_1]


def test_una_semana_completa_viaja_sola_con_sus_registros_y_sus_links_recalculados() -> None:
    plan = _plan(AHORA, date(2026, 11, 9))
    ahora, bitacora = plan.files["AHORA.md"], plan.files[DOMINGO_1]

    assert bitacora == (
        "---\ntype: Logbook\nstatus: stable\nfrom: 2026-10-26\nto: 2026-11-01\n---\n"
        "# Actividad diaria\n\n"
        "## Domingo 1 de noviembre\n\n"
        f"- 20:00 - {P_ARCHIVADO} cena con [Carmen](../notas/carmen.md)\n"
        "- 09:00 - paseo\n\n"
        "## Lunes 26 de octubre\n\n"
        f"- 10:00 - {P_ARCHIVADO} reunión\n"
    )
    assert "Foco" not in bitacora and "Pendientes" not in bitacora
    assert "## Lunes 2 de noviembre" in ahora and "Foco" in ahora
    assert "cena con" not in ahora and "from:" not in ahora
    assert plan.regenerate == ("AHORA.md", "bitacoras/")


def test_una_semana_parcial_crea_la_bitacora_con_los_dias_que_hay() -> None:
    plan = _plan(AHORA, date(2026, 11, 4))
    assert set(plan.files) == {"AHORA.md", DOMINGO_25}
    assert _registros(plan.files[DOMINGO_25]) == [
        f"- 11:00 - {P_ARCHIVADO} cierre de la semana",
        "- 07:30 - arranque",
    ]
    assert plan.files[DOMINGO_25].index("Domingo 25") < plan.files[DOMINGO_25].index("Lunes 19")
    assert "from: 2026-10-19\nto: 2026-10-25" in plan.files[DOMINGO_25]
    assert "## Domingo 25 de octubre" not in plan.files["AHORA.md"]
    assert "## Lunes 26 de octubre" in plan.files["AHORA.md"]


def test_una_bitacora_existente_se_completa_sin_duplicar_ni_reordenar() -> None:
    existente = (
        "---\ntype: Logbook\nstatus: stable\nfrom: 2026-10-19\nto: 2026-10-25\n---\n"
        "# Actividad diaria\n\n"
        "## Domingo 25 de octubre\n\n"
        f"- 18:00 - {P_ARCHIVADO} registrado con fecha antigua\n"
        f"- 11:00 - {P_ARCHIVADO} cierre de la semana\n"
    )
    plan = _plan(AHORA, date(2026, 11, 4), {DOMINGO_25: existente})
    texto = plan.files[DOMINGO_25]
    assert _registros(texto) == [
        f"- 18:00 - {P_ARCHIVADO} registrado con fecha antigua",
        f"- 11:00 - {P_ARCHIVADO} cierre de la semana",
        "- 07:30 - arranque",
    ]
    assert texto.count("cierre de la semana") == 1
    assert texto.count("## Domingo 25 de octubre") == 1
    assert texto.index("Domingo 25") < texto.index("Lunes 19")


def test_una_bitacora_con_nombre_de_ciclo_que_cubre_el_dia_tambien_se_completa() -> None:
    vieja = "bitacoras/bitacora-2026-10-12-2026-10-25-turno.md"
    texto = (
        "---\ntype: Logbook\nstatus: stable\nfrom: 2026-10-12\nto: 2026-10-25\n---\n"
        "# Actividad diaria\n"
    )
    plan = _plan(AHORA, date(2026, 11, 4), {vieja: texto})
    assert DOMINGO_25 not in plan.files
    assert "cierre de la semana" in plan.files[vieja]


def test_archivar_dos_veces_no_cambia_nada() -> None:
    plan = _plan(AHORA, date(2026, 11, 9))
    ahora, history = _aplicar(plan, AHORA, {})
    otra = _plan(ahora, date(2026, 11, 9), history)
    assert otra.files == {} and otra.message == ""


def test_sin_dias_antiguos_no_hay_cambio() -> None:
    assert _plan(AHORA, date(2026, 11, 2)).files.keys() == {"AHORA.md", DOMINGO_25}
    sin_antiguos = "".join(AHORA.partition("## Domingo 25")[0:1])
    assert _plan(sin_antiguos, date(2026, 11, 2)).files == {}


def test_un_dia_sin_registros_se_descarta_sin_crear_bitacora() -> None:
    vacio = (
        "---\ntype: Logbook\n---\n# Actividad diaria\n\n"
        "## Lunes 19 de octubre\n\n"
    )
    plan = _plan(vacio, date(2026, 11, 9))
    assert set(plan.files) == {"AHORA.md"} and "## Lunes 19" not in plan.files["AHORA.md"]


def test_un_ahora_sembrado_con_ciclos_pierde_cycle_from_y_to_al_escribir() -> None:
    viejo = (
        "---\ntype: Logbook\nstatus: draft\ncycle: semana\nfrom: 2026-01-05\nto: 2026-01-11\n"
        "---\n# Actividad diaria\n\n## Lunes 7 de diciembre\n\n- 08:00 - hoy\n"
    )
    plan = _plan(viejo, date(2026, 12, 7))
    assert plan.files["AHORA.md"].startswith("---\ntype: Logbook\nstatus: draft\n---\n")
    assert "- 08:00 - hoy" in plan.files["AHORA.md"] and plan.message == ""
    assert _plan(plan.files["AHORA.md"], date(2026, 12, 7)).files == {}
    assert len(archive.lint_legacy(viejo, ciclo_user_md=True)) == 2
    assert archive.lint_legacy(plan.files["AHORA.md"], ciclo_user_md=False) == []


# --- sobre un vault ------------------------------------------------------------


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    return init.init(tmp_path / "v", home=RAIZ_REPO)


def _tuku(vault: Path, ahora: datetime, *argv: str) -> int:
    return main([*argv, "--vault", str(vault)], now=ahora)


def _foto(vault: Path) -> dict[str, bytes]:
    return {str(p.relative_to(vault)): p.read_bytes() for p in vault.rglob("*") if p.is_file()}


def _leer(vault: Path, ruta: str) -> str:
    return (vault / ruta).read_text(encoding="utf-8")


SEMANA_1 = datetime(2026, 10, 28, 10, 0)
LUNES_2 = datetime(2026, 11, 9, 8, 0)


def test_un_comando_que_escribe_archiva_primero_y_repetirlo_no_cambia_nada(vault: Path) -> None:
    cuerpo = ("entry", "create", "--scope", "personal", "--body")
    assert _tuku(vault, SEMANA_1, *cuerpo, "reunión del miércoles") == EXITO
    assert "reunión del miércoles" in _leer(vault, "AHORA.md")

    assert _tuku(vault, LUNES_2, *cuerpo, "reunión del lunes siguiente") == EXITO
    ahora = _leer(vault, "AHORA.md")
    assert "reunión del lunes siguiente" in ahora and "reunión del miércoles" not in ahora
    semana = _leer(vault, DOMINGO_1)
    assert (
        "- 10:00 - [personal](../ambitos/personal/personal.md) reunión del miércoles" in semana
    )
    assert "status: stable" in semana
    pagina = _leer(vault, "ambitos/personal/personal.md")
    reciente = pagina.split("## Actividad reciente")[1]
    assert "- 28 - reunión del miércoles" in reciente, "sale de la bitácora"
    assert "reunión del lunes siguiente" in pagina.split("## Actividad reciente")[0]

    foto = _foto(vault)
    assert _tuku(vault, LUNES_2, "regenerate", "todo") == EXITO
    assert _foto(vault) == foto


ESCRIBEN: list[tuple[str, ...]] = [
    ("entry", "create", "--body", "hoy"),
    ("todo", "open", "--body", "pagar la patente"),
    ("todo", "close", "pagar la patente"),
    ("note", "create", "Una nota", "--body", "x"),
    ("note", "rename", "Una nota", "Otra nota"),
    ("scope", "create", "taller"),
    ("scope", "update", "casa", "--keyword", "hogar"),
    ("scope", "move", "casa", "--parent", "personal"),
    ("scope", "rename", "casa", "hogar"),
    ("regenerate", "scope"),
]


@pytest.mark.parametrize("argv", ESCRIBEN, ids=lambda a: " ".join(a[:2]))
def test_cada_comando_que_escribe_archiva_primero(vault: Path, argv: tuple[str, ...]) -> None:
    assert _tuku(vault, SEMANA_1, "scope", "create", "casa") == EXITO
    assert _tuku(vault, SEMANA_1, "note", "create", "Una nota", "--body", "x") == EXITO
    assert _tuku(vault, SEMANA_1, "entry", "create", "--body", "del miércoles") == EXITO
    assert DOMINGO_1 not in _foto(vault)

    _tuku(vault, LUNES_2, *argv)
    assert "del miércoles" in _leer(vault, DOMINGO_1)
    assert "del miércoles" not in _leer(vault, "AHORA.md")


def test_los_comandos_que_solo_leen_no_archivan(vault: Path) -> None:
    assert _tuku(vault, SEMANA_1, "entry", "create", "--body", "algo de la semana") == EXITO
    foto = _foto(vault)
    for argv in (("context",), ("context", "entry"), ("doctor",), ("doctor", "archive")):
        _tuku(vault, LUNES_2, *argv)
        assert _foto(vault) == foto, argv


def test_un_registro_antiguo_va_a_su_bitacora_y_entry_update_y_move_lo_encuentran(
    vault: Path,
) -> None:
    semana = "bitacoras/bitacora-20261019-20261025.md"
    assert _tuku(vault, LUNES_2, "scope", "create", "casa", "--at", "2026-10-22 10:00") == EXITO
    assert "abrí el ámbito" in _leer(vault, semana)
    assert "casa" not in _leer(vault, "AHORA.md").split("# Actividad diaria")[1]

    crear = ("entry", "create", "--scope", "personal", "--at", "2026-10-21 09:00")
    assert _tuku(vault, LUNES_2, *crear, "--body", "llamé a Rodolfo") == EXITO
    registro = "- 09:00 - [personal](../ambitos/personal/personal.md) llamé a Rodolfo"
    assert registro in _leer(vault, semana)
    assert "Rodolfo" not in _leer(vault, "AHORA.md")
    assert "from: 2026-10-19\nto: 2026-10-25" in _leer(vault, semana)
    assert _leer(vault, semana).index("Jueves 22") < _leer(vault, semana).index("Miércoles 21")

    foto = _foto(vault)
    assert _tuku(vault, LUNES_2, *crear, "--body", "llamé a Rodolfo") == EXITO
    assert _foto(vault) == foto, "repetir el registro antiguo no cambia nada"

    actualizar = ("entry", "update", "2026-10-21", "--match", "Rodolfo")
    assert _tuku(vault, LUNES_2, *actualizar, "--body", "llamé a don Rodolfo") == EXITO
    mover = ("entry", "move", "2026-10-21", "--match", "Rodolfo", "--scope", "casa")
    assert _tuku(vault, LUNES_2, *mover) == EXITO
    assert "- 09:00 - [casa](../ambitos/casa/casa.md) llamé a don Rodolfo" in _leer(
        vault, semana
    )


def test_un_dia_futuro_se_rechaza_y_no_deja_nada(vault: Path) -> None:
    foto = _foto(vault)
    futuro = ("entry", "create", "--at", "2026-11-20 09:00", "--body", "x")
    assert _tuku(vault, LUNES_2, *futuro) != EXITO
    archivado = {k: v for k, v in _foto(vault).items() if k not in foto}
    assert archivado == {} or all(k.startswith("bitacoras/") for k in archivado)


def test_doctor_archive_avisa_de_los_dias_antiguos_sin_archivarlos(
    vault: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert _tuku(vault, SEMANA_1, "entry", "create", "--body", "del miércoles") == EXITO
    capsys.readouterr()
    assert _tuku(vault, LUNES_2, "doctor", "archive") == EXITO
    salida = capsys.readouterr()
    assert "aviso: el día 2026-10-28 es anterior a la ventana" in salida.out + salida.err
    assert "del miércoles" in _leer(vault, "AHORA.md")


def test_un_vault_sembrado_con_ciclos_funciona_y_doctor_avisa_sin_fallar(
    vault: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    ahora = vault / "AHORA.md"
    ahora.write_text(
        _leer(vault, "AHORA.md").replace(
            "status: draft\n",
            "status: draft\ncycle: semana\nfrom: 2026-10-26\nto: 2026-11-01\n",
        ),
        encoding="utf-8",
    )
    (vault / "reglas" / "ciclo.user.md").write_text("| Ciclo | Días |\n|---|---|\n", "utf-8")
    capsys.readouterr()
    assert _tuku(vault, SEMANA_1, "doctor", "archive") == EXITO
    salida = capsys.readouterr()
    assert "`cycle`, `from` o `to`" in salida.out + salida.err
    assert "reglas/ciclo.user.md: aviso" in salida.out + salida.err

    assert _tuku(vault, SEMANA_1, "entry", "create", "--body", "hoy") == EXITO
    assert "cycle:" not in _leer(vault, "AHORA.md") and "hoy" in _leer(vault, "AHORA.md")


def test_doctor_avisa_de_dias_antiguos_y_falla_si_la_bitacora_no_dice_su_nombre() -> None:
    avisos = archive.lint_window(AHORA, today=date(2026, 11, 9), weeks=2)
    assert len(avisos) == 4 and "2026-11-01" in avisos[0] and "archiva" in avisos[0]
    assert archive.lint_window(AHORA, today=date(2026, 11, 2), weeks=2)[0].count("2026-10-25")
    assert archive.lint_window(AHORA, today=date(2026, 10, 28), weeks=2) == []

    bien = _plan(AHORA, date(2026, 11, 9)).files
    assert archive.lint_history({k: v for k, v in bien.items() if k != "AHORA.md"}) == []
    mal = {DOMINGO_1: bien[DOMINGO_1].replace("to: 2026-11-01", "to: 2026-11-02")}
    (hallazgo,) = archive.lint_history(mal)
    assert DOMINGO_1 in hallazgo and "error" in hallazgo and "2026-11-02" in hallazgo
    sin_rango = {DOMINGO_1: "---\ntype: Logbook\n---\n"}
    assert "no tiene `from` y `to`" in archive.lint_history(sin_rango)[0]
    assert (
        archive.lint_history({"bitacoras/bitacora-2026-10-12-2026-10-18-semana.md": "x"}) == []
    )
