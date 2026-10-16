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


def test_cierra_aunque_solo_el_registro_de_cierre_lleve_el_link(vault: Path) -> None:
    _abre(vault, SIN_LINK)

    todo.cerrar_en_vault(vault, body=CON_LINK, scope="personal", day=DIA, hour="19:05")

    assert _tabla(vault) == []
    assert f"(Hecho): ~~{CON_LINK}~~" in _ahora(vault)


def test_cierra_aunque_solo_la_tabla_lleve_el_link(vault: Path) -> None:
    _abre(vault, CON_LINK)
    assert _tabla(vault) == [CON_LINK]

    r = todo.cerrar_en_vault(vault, body=SIN_LINK, day=DIA, hour="19:05")

    assert "pendiente cerrado" in r.mensaje
    assert _tabla(vault) == []
    assert f"(Hecho): ~~{SIN_LINK}~~" in _ahora(vault)


def test_cerrar_dos_veces_no_duplica_el_registro(vault: Path) -> None:
    _abre(vault, CON_LINK)
    todo.cerrar_en_vault(vault, body=SIN_LINK, day=DIA, hour="19:05")
    antes = _ahora(vault)

    todo.cerrar_en_vault(vault, body=CON_LINK, day=DIA, hour="19:10")

    assert _ahora(vault) == antes


def test_abrir_otra_vez_el_mismo_pendiente_con_o_sin_link_no_duplica(vault: Path) -> None:
    _abre(vault, CON_LINK)
    antes = _ahora(vault)
    todo.abrir_en_vault(vault, body=SIN_LINK, scope="personal", day=DIA, hour="15:00")

    assert len(_tabla(vault)) == 1
    assert _ahora(vault) == antes


def test_corregir_el_registro_encuentra_la_fila_aunque_difieran_en_links(vault: Path) -> None:
    _abre(vault, CON_LINK)
    (vault / "PENDIENTES.md").write_text(
        (vault / "PENDIENTES.md").read_text(encoding="utf-8").replace(CON_LINK, SIN_LINK),
        encoding="utf-8",
    )

    r = entry.corregir_en_vault(
        vault, body="**pendiente**: avisar a Carmen de los GGCC hoy", day=DIA, hour="14:20"
    )

    assert "su fila en PENDIENTES.md" in r.mensaje
    assert _tabla(vault) == ["avisar a Carmen de los GGCC hoy"]


def test_entry_add_rechaza_abrir_y_nombra_tuku_todo_open(vault: Path) -> None:
    antes = _ahora(vault)
    r = entry.add_al_vault(
        vault, body=f"**pendiente**: {SIN_LINK}", scope="personal", day=DIA, hour="14:20"
    )

    assert not r.ok
    assert (
        f"tuku todo open --scope personal --day 2026-08-11 --hour 14:20 --body '{SIN_LINK}'"
        in r.mensaje
    )
    assert _ahora(vault) == antes
    assert _tabla(vault) == []


def test_entry_add_rechaza_cerrar_y_nombra_tuku_todo_close(vault: Path) -> None:
    _abre(vault, SIN_LINK)
    r = entry.add_al_vault(vault, body=f"(Hecho): ~~{SIN_LINK}~~", day=DIA, hour="19:05")

    assert not r.ok
    assert f"tuku todo close --day 2026-08-11 --hour 19:05 --body '{SIN_LINK}'" in r.mensaje
    assert _tabla(vault) == [SIN_LINK]
