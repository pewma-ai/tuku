"""`entry update` y `entry move`: ubican por fragmento el último registro que calza."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from tuku import entry, init, scope, todo

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent
DIA = date(2026, 8, 11)

TRES = """---
from: 2026-08-10
to: 2026-08-16
---

# Plan

- un punto del plan que no es registro

# Actividad diaria

## Martes 11 de agosto

- 07:00 - [personal](ambitos/personal/personal.md) llamé a Rodolfo por la cotización
- 07:00 - [personal](ambitos/personal/personal.md) **señal**: el Colegio pagó tarde
- 07:00 - [personal](ambitos/personal/personal.md) llamé a Rodolfo por el presupuesto
- [personal](ambitos/personal/personal.md) recordé la reunión con Ximena
"""


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    v = init.init(tmp_path / "v", home=RAIZ_REPO, desde=date(2026, 8, 10))
    scope.crear(v, "colegio-los-robles")
    return v


def _ahora(vault: Path) -> str:
    return (vault / "AHORA.md").read_text(encoding="utf-8")


def test_lee_los_registros_de_los_dias_con_y_sin_hora() -> None:
    lista = entry.registros(TRES)
    assert [(r.hora, r.cuerpo[:6]) for r in lista] == [
        ("07:00", "llamé "),
        ("07:00", "**seña"),
        ("07:00", "llamé "),
        ("", "record"),
    ]
    assert {r.dia for r in lista} == {"Martes 11 de agosto"}
    assert lista[0].ambito == "personal"


def test_ubica_el_ultimo_que_calza_sin_distinguir_mayusculas_ni_tildes() -> None:
    r = entry.ubicar(TRES, "llame a RODOLFO")
    assert r is not None and r.cuerpo.endswith("el presupuesto")
    r = entry.ubicar(TRES, "rodolfo por la cotizacion")
    assert r is not None and r.cuerpo.endswith("la cotización")
    assert entry.ubicar(TRES, "Rodolfo", hora="08:00") is None
    assert entry.ubicar(TRES, "Rodolfo", dia="Miércoles 12 de agosto") is None
    assert entry.ubicar(TRES, "punto del plan") is None


def test_update_corrige_el_ultimo_registro_y_la_fila_del_pendiente(vault: Path) -> None:
    todo.abrir_en_vault(
        vault, body="enviar la cotización", scope="personal", day=DIA, hour="09:00"
    )
    r = entry.actualizar_en_vault(
        vault, match="cotización", body="**pendiente**: enviar el presupuesto"
    )
    assert r.ok and "su fila en PENDIENTES.md" in r.mensaje
    assert "personal.md) **pendiente**: enviar el presupuesto" in _ahora(vault)
    assert todo.cuerpos((vault / "PENDIENTES.md").read_text(encoding="utf-8")) == [
        "enviar el presupuesto"
    ]

    otra = entry.actualizar_en_vault(
        vault, match="presupuesto", body="**pendiente**: enviar el presupuesto"
    )
    assert otra.ok and "ya decía eso" in otra.mensaje


def test_update_rechaza_sin_registro_que_calce_y_fuera_del_ciclo(vault: Path) -> None:
    antes = _ahora(vault)
    r = entry.actualizar_en_vault(vault, match="nada de esto", body="x")
    assert not r.ok and "ningún registro de AHORA.md contiene «nada de esto»" in r.mensaje
    r = entry.actualizar_en_vault(vault, match="x", body="y", day=date(2026, 7, 6))
    assert not r.ok and "solo AHORA.md" in r.mensaje
    assert _ahora(vault) == antes


def test_move_cambia_el_ambito_y_la_fila_del_pendiente_abierto(vault: Path) -> None:
    todo.abrir_en_vault(
        vault, body="enviar la cotización", scope="personal", day=DIA, hour="09:00"
    )
    r = entry.mover_en_vault(vault, match="cotización", scope="colegio-los-robles")
    assert r.ok and "su fila en PENDIENTES.md" in r.mensaje
    assert (
        "- 09:00 - [colegio-los-robles](ambitos/colegio-los-robles/colegio-los-robles.md) "
        "**pendiente**: enviar la cotización"
    ) in _ahora(vault)
    fila = todo.filas((vault / "PENDIENTES.md").read_text(encoding="utf-8"))[0]
    assert fila.ambito == "colegio-los-robles"

    otra = entry.mover_en_vault(vault, match="cotización", scope="colegio-los-robles")
    assert otra.ok and "ya era de colegio-los-robles" in otra.mensaje


def test_move_llega_a_un_ciclo_cerrado_con_la_ruta_desde_bitacoras(vault: Path) -> None:
    (vault / "bitacoras").mkdir()
    cerrada = vault / "bitacoras" / "bitacora-2026-08-03-2026-08-09.md"
    cerrada.write_text(
        "---\ntype: Logbook\nstatus: stable\nfrom: 2026-08-03\nto: 2026-08-09\n---\n\n"
        "## Miércoles 5 de agosto\n\n- 10:00 - [personal](../ambitos/personal/personal.md) "
        "hablé con don Rodolfo\n",
        encoding="utf-8",
    )
    r = entry.mover_en_vault(
        vault, match="don Rodolfo", scope="colegio-los-robles", day=date(2026, 8, 5)
    )
    assert r.ok
    assert (
        "- 10:00 - [colegio-los-robles](../ambitos/colegio-los-robles/colegio-los-robles.md) "
        "hablé con don Rodolfo"
    ) in cerrada.read_text(encoding="utf-8")


def test_move_rechaza_un_ambito_que_no_existe_y_un_dia_sin_ciclo(vault: Path) -> None:
    assert not entry.mover_en_vault(vault, match="x", scope="no-existe").ok
    r = entry.mover_en_vault(vault, match="x", scope="personal", day=date(2026, 7, 6))
    assert not r.ok and "ni AHORA.md ni ninguna bitácora" in r.mensaje


def test_create_en_un_dia_pasado_sin_hora_no_inventa_una(vault: Path) -> None:
    hoy = date.today()
    pasado = date(2026, 8, 10)
    if hoy <= pasado:
        pytest.skip("el reloj de la máquina está antes del ciclo de prueba")
    r = entry.add_al_vault(vault, body="llamé a Rodolfo", scope="personal", day=pasado)
    assert r.ok
    assert "- [personal](ambitos/personal/personal.md) llamé a Rodolfo" in _ahora(vault)
