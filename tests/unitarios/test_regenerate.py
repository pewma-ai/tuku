"""`tuku regenerate`: valida el canónico antes de escribir, y cada tema regenera lo suyo."""

from __future__ import annotations

from pathlib import Path

from tuku.cli import EXITO, main
from tuku.regenerate import TEMAS, regenerar

A_MANO = "- 10:00 - [personal](ambitos/personal/personal.md) **nota**: escrito a mano"
VISTA = Path("ambitos") / "PENDIENTES-AMBITOS.md"
PAGINA = Path("ambitos") / "personal" / "personal.md"
COMANDOS = Path("reglas") / "comandos.tuku.md"


def _desfasado(tmp_path: Path) -> Path:
    """Un vault donde cada derivado está atrasado respecto de su fuente."""
    v = tmp_path / "v"
    assert main(["init", str(v), "--at", "2026-08-11"]) == EXITO
    ahora = v / "AHORA.md"
    ahora.write_text(
        ahora.read_text(encoding="utf-8").replace(
            "## Martes 11 de agosto\n", f"## Martes 11 de agosto\n{A_MANO}\n"
        ),
        encoding="utf-8",
    )
    (v / VISTA).unlink()
    (v / COMANDOS).write_text("viejo\n", encoding="utf-8")
    return v


def test_rechaza_si_no_hay_tabla_de_pendientes(tmp_path: Path) -> None:
    (tmp_path / "PENDIENTES.md").write_text("sin tabla", encoding="utf-8")
    r = regenerar(tmp_path)
    assert not r.ok
    assert "PENDIENTES.md" in r.mensaje


def test_los_temas_son_todo_scope_y_comandos() -> None:
    assert TEMAS == ("todo", "scope", "comandos")


def test_todo_regenera_las_vistas_y_deja_lo_demas(tmp_path: Path) -> None:
    v = _desfasado(tmp_path)
    regenerar(v, tema="todo", comandos="nuevo\n")
    assert (v / VISTA).is_file()
    assert "escrito a mano" not in (v / PAGINA).read_text(encoding="utf-8")
    assert (v / COMANDOS).read_text(encoding="utf-8") == "viejo\n"


def test_scope_lleva_las_entradas_a_la_pagina_del_ambito(tmp_path: Path) -> None:
    v = _desfasado(tmp_path)
    regenerar(v, tema="scope", comandos="nuevo\n")
    assert "escrito a mano" in (v / PAGINA).read_text(encoding="utf-8")
    assert not (v / VISTA).exists()
    assert (v / COMANDOS).read_text(encoding="utf-8") == "viejo\n"


def test_comandos_reescribe_solo_las_reglas(tmp_path: Path) -> None:
    v = _desfasado(tmp_path)
    ahora = (v / "AHORA.md").read_bytes()
    regenerar(v, tema="comandos", comandos="nuevo\n")
    assert (v / COMANDOS).read_text(encoding="utf-8") == "nuevo\n"
    assert (v / "AHORA.md").read_bytes() == ahora
    assert not (v / VISTA).exists()
    assert "escrito a mano" not in (v / PAGINA).read_text(encoding="utf-8")


def test_comandos_no_necesita_un_canonico_sano(tmp_path: Path) -> None:
    v = _desfasado(tmp_path)
    (v / "PENDIENTES.md").write_text("sin tabla", encoding="utf-8")
    assert regenerar(v, tema="comandos", comandos="nuevo\n").ok
    assert not regenerar(v, tema="todo").ok


def test_sin_tema_regenera_los_tres(tmp_path: Path) -> None:
    v = _desfasado(tmp_path)
    regenerar(v, comandos="nuevo\n")
    assert (v / VISTA).is_file()
    assert "escrito a mano" in (v / PAGINA).read_text(encoding="utf-8")
    assert (v / COMANDOS).read_text(encoding="utf-8") == "nuevo\n"


def test_cada_tema_es_idempotente(tmp_path: Path) -> None:
    v = _desfasado(tmp_path)
    for tema in TEMAS:
        regenerar(v, tema=tema, comandos="nuevo\n")
        assert "al día" in regenerar(v, tema=tema, comandos="nuevo\n").mensaje


def test_el_cli_acepta_los_tres_temas(tmp_path: Path) -> None:
    v = _desfasado(tmp_path)
    for tema in TEMAS:
        assert main(["regenerate", tema, "--vault", str(v)]) == EXITO
