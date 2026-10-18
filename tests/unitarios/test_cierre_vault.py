"""Cerrar un pendiente sobre un vault en disco: la marca a la vista y el cuerpo tachado.

El mismo pendiente puede llevar un link en la bitácora y no en `PENDIENTES.md`
(o al revés): al cerrarlo cuenta lo que se lee, no los links.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from tuku import entry, init, todo

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent
DIA = date(2026, 8, 11)
CON_LINK = "avisar a [Carmen](notas/carmen.md) de los GGCC"
SIN_LINK = "avisar a Carmen de los GGCC"


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    return init.init(tmp_path / "v", home=RAIZ_REPO, desde=date(2026, 8, 10))


def _abre(vault: Path, cuerpo: str) -> None:
    todo.abrir_en_vault(vault, body=cuerpo, scope="personal", day=DIA, hour="14:20")


def _ahora(vault: Path) -> str:
    return (vault / "AHORA.md").read_text(encoding="utf-8")


def _tabla(vault: Path) -> list[str]:
    return todo.cuerpos((vault / "PENDIENTES.md").read_text(encoding="utf-8"))


def test_el_cierre_queda_con_la_marca_a_la_vista_y_el_cuerpo_tachado(vault: Path) -> None:
    _abre(vault, SIN_LINK)
    r = todo.cerrar_en_vault(vault, body=SIN_LINK, scope="personal", day=DIA, hour="19:05")

    assert r.ok, r.mensaje
    assert f"(Hecho): ~~{SIN_LINK}~~" in _ahora(vault)
    assert _tabla(vault) == []


def test_el_cierre_cae_en_el_ambito_donde_estaba_el_pendiente(vault: Path) -> None:
    from tuku import scope
    from tuku.cli import EXITO, main

    scope.crear_con_constancia(vault, "bodega", day=DIA, hour="14:00")
    todo.abrir_en_vault(vault, body="contar el stock", scope="bodega", day=DIA, hour="14:20")
    todo.abrir_en_vault(vault, body="llamar a Ana", day=DIA, hour="14:25")

    for texto, hora in (("contar el stock", "09:00"), ("llamar a Ana", "09:05")):
        cierre = ["todo", "close", texto, "--vault", str(vault), "--at", f"2026-08-12 {hora}"]
        assert main(cierre) == EXITO

    miercoles = _ahora(vault).split("## Miércoles 12 de agosto", 1)[1]
    assert "[bodega](ambitos/bodega/bodega.md) (Hecho): ~~contar el stock~~" in miercoles
    assert "[personal](ambitos/personal/personal.md) (Hecho): ~~llamar a Ana~~" in miercoles


def test_cierra_aunque_solo_el_registro_o_solo_la_tabla_lleve_el_link(vault: Path) -> None:
    _abre(vault, SIN_LINK)
    todo.cerrar_en_vault(vault, body=CON_LINK, scope="personal", day=DIA, hour="19:05")
    assert _tabla(vault) == []
    assert f"(Hecho): ~~{CON_LINK}~~" in _ahora(vault)

    _abre(vault, CON_LINK)
    assert _tabla(vault) == [CON_LINK]
    r = todo.cerrar_en_vault(vault, body=SIN_LINK, day=DIA, hour="19:20")
    assert "pendiente cerrado" in r.mensaje
    assert _tabla(vault) == []


def test_abrir_o_cerrar_dos_veces_no_duplica_con_o_sin_link(vault: Path) -> None:
    _abre(vault, CON_LINK)
    antes = _ahora(vault)
    todo.abrir_en_vault(vault, body=SIN_LINK, scope="personal", day=DIA, hour="15:00")
    assert len(_tabla(vault)) == 1
    assert _ahora(vault) == antes

    todo.cerrar_en_vault(vault, body=SIN_LINK, day=DIA, hour="19:05")
    cerrado = _ahora(vault)
    todo.cerrar_en_vault(vault, body=CON_LINK, day=DIA, hour="19:10")
    assert _ahora(vault) == cerrado


def test_corregir_el_registro_encuentra_la_fila_aunque_difieran_en_links(vault: Path) -> None:
    _abre(vault, CON_LINK)
    (vault / "PENDIENTES.md").write_text(
        (vault / "PENDIENTES.md").read_text(encoding="utf-8").replace(CON_LINK, SIN_LINK),
        encoding="utf-8",
    )

    r = entry.actualizar_en_vault(
        vault, match="GGCC", body="**pendiente**: avisar a Carmen de los GGCC hoy"
    )

    assert "su fila en PENDIENTES.md" in r.mensaje
    assert _tabla(vault) == ["avisar a Carmen de los GGCC hoy"]


def test_entry_add_rechaza_abrir_y_cerrar_y_nombra_el_comando(vault: Path) -> None:
    antes = _ahora(vault)
    r = entry.add_al_vault(
        vault, body=f"**pendiente**: {SIN_LINK}", scope="personal", day=DIA, hour="14:20"
    )
    assert not r.ok
    assert (
        f"tuku todo open --scope personal --at '2026-08-11 14:20' --body '{SIN_LINK}'"
        in r.mensaje
    )
    assert _ahora(vault) == antes
    assert _tabla(vault) == []

    _abre(vault, SIN_LINK)
    r = entry.add_al_vault(vault, body=f"(Hecho): ~~{SIN_LINK}~~", day=DIA, hour="19:05")
    assert not r.ok
    assert f"tuku todo close --at '2026-08-11 19:05' '{SIN_LINK}'" in r.mensaje
    assert _tabla(vault) == [SIN_LINK]
