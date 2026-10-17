"""El árbol de ámbitos: sin archivos vacíos, anidados, `scope move` y `scope rename`."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from tuku import init
from tuku.cli import EXITO, RECHAZO, main

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent
HOY = "2026-08-11"
CUERPO = "presentar el marco"


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    return init.init(tmp_path / "v", home=RAIZ_REPO, desde=date(2026, 8, 10))


def _tuku(vault: Path, *argv: str) -> int:
    return main([*argv, "--vault", str(vault)])


def _crear(vault: Path, nombre: str, *extra: str) -> int:
    return _tuku(vault, "scope", "create", nombre, "--at", f"{HOY} 18:45", *extra)


def _foto(vault: Path) -> dict[str, bytes]:
    return {str(p.relative_to(vault)): p.read_bytes() for p in vault.rglob("*") if p.is_file()}


def _leer(vault: Path, *partes: str) -> str:
    return vault.joinpath(*partes).read_text(encoding="utf-8")


def _con_faena(vault: Path) -> None:
    assert _crear(vault, "faena") == EXITO
    assert _crear(vault, "faena-ai", "--parent", "faena") == EXITO


def _con_registros(vault: Path) -> None:
    """`faena` y un `faena-ai` plano, con un registro y un pendiente."""
    assert _crear(vault, "faena") == EXITO
    assert _crear(vault, "faena-ai") == EXITO
    assert (
        _tuku(
            vault, "entry", "add", "--scope", "faena-ai", "--at", f"{HOY} 19:00",
            "--body", "**nota**: revisé el marco",
        )
        == EXITO
    )  # fmt: skip
    assert (
        _tuku(
            vault, "todo", "open", "--scope", "faena-ai", "--at", f"{HOY} 19:05",
            "--due", "2026-08-12", "--body", CUERPO,
        )
        == EXITO
    )  # fmt: skip


def _con_ruta_vieja(vault: Path, ruta: str) -> list[str]:
    """Los archivos que todavía nombran la ruta de antes."""
    return [
        str(p.relative_to(vault))
        for p in vault.rglob("*.md")
        if ruta in p.read_text(encoding="utf-8")
    ]


def _callouts(vault: Path) -> dict[str, list[str]]:
    """Las líneas del callout de cada ámbito en `PENDIENTES-AMBITOS.md`, por ancla."""
    salida: dict[str, list[str]] = {}
    for bloque in _leer(vault, "ambitos", "PENDIENTES-AMBITOS.md").split("\n\n"):
        lineas = bloque.strip().splitlines()
        if lineas and lineas[0].startswith("> [!todo] Pendientes en"):
            salida[lineas[0].rsplit("^", 1)[1]] = lineas
    return salida


def _colgando(vault: Path, viejo: str) -> list[str]:
    """Los archivos que todavía nombran el ámbito por su nombre de antes."""
    return [
        str(p.relative_to(vault))
        for p in vault.rglob("*.md")
        if f"ambitos/{viejo}/" in (t := p.read_text(encoding="utf-8"))
        or f"^{viejo}" in t
        or f"[{viejo}](" in t
    ]


def test_un_ambito_nuevo_lleva_solo_su_pagina_y_el_template_no_siembra_reglas_vacias(
    vault: Path,
) -> None:
    assert _crear(vault, "depto-centro") == EXITO
    nombres = sorted(p.name for p in (vault / "ambitos" / "depto-centro").iterdir())
    assert nombres == ["depto-centro.md"]

    assert "Apertura de la semana" in _leer(vault, "ambitos", "CADENCIAS.md")
    assert sorted(p.name for p in (vault / "ambitos" / "personal").iterdir()) == [
        "CAPACIDAD.md",
        "personal.md",
    ]
    assert (vault / "ambitos" / "AGENTS.md").is_file()


def test_un_ambito_bajo_otro_vive_en_su_carpeta_y_se_enlaza_con_su_ruta_completa(
    vault: Path,
) -> None:
    _con_faena(vault)
    pagina = vault / "ambitos" / "faena" / "faena-ai" / "faena-ai.md"
    assert "![[../../PENDIENTES-AMBITOS.md#^faena-ai]]" in pagina.read_text(encoding="utf-8")
    constancia = "[faena-ai](ambitos/faena/faena-ai/faena-ai.md) **nota**: abrí el ámbito"
    assert constancia in _leer(vault, "AHORA.md")

    argv = ("entry", "add", "--scope", "faena-ai", "--at", f"{HOY} 19:00", "--body", "x")
    assert _tuku(vault, *argv) == EXITO
    assert "[faena-ai](ambitos/faena/faena-ai/faena-ai.md) x" in _leer(vault, "AHORA.md")
    assert _tuku(vault, "scope", "lint") == EXITO
    assert _tuku(vault, "doctor") == EXITO


def test_el_documento_de_ambitos_sigue_el_arbol_y_cada_callout_lleva_solo_lo_suyo(
    vault: Path,
) -> None:
    _con_faena(vault)
    assert _callouts(vault)["faena-ai"] == [
        "> [!todo] Pendientes en **Faena / Faena Ai** ^faena-ai"
    ], "un ámbito sin pendientes lleva solo el título"
    callouts = [
        linea
        for linea in _leer(vault, "ambitos", "PENDIENTES-AMBITOS.md").splitlines()
        if linea.startswith("> [!todo]")
    ]
    assert callouts == [
        "> [!todo] Pendientes en **Faena** ^faena",
        "> [!todo] Pendientes en **Faena / Faena Ai** ^faena-ai",
        "> [!todo] Pendientes en **Personal** ^personal",
    ]

    argv = ("todo", "open", "--scope", "faena-ai", "--at", f"{HOY} 19:05", "--body", CUERPO)
    assert _tuku(vault, *argv) == EXITO
    bloques = _callouts(vault)
    assert CUERPO in "\n".join(bloques["faena-ai"])
    assert bloques["faena"] == ["> [!todo] Pendientes en **Faena** ^faena"]


def test_crear_bajo_el_mismo_padre_es_idempotente_y_lo_imposible_se_rechaza_sin_escribir(
    vault: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    antes = _foto(vault)
    assert _crear(vault, "faena-ai", "--parent", "faena") == RECHAZO
    assert "tuku scope create faena" in capsys.readouterr().err, "el padre tiene que existir"
    assert _foto(vault) == antes

    _con_faena(vault)
    antes = _foto(vault)
    assert _crear(vault, "faena-ai", "--parent", "faena") == EXITO
    assert _foto(vault) == antes

    assert _crear(vault, "otro") == EXITO
    for argv, dice in [
        (
            ("scope", "move", "no-existe", "--parent", "faena"),
            "no existe el ámbito 'no-existe'",
        ),
        (("scope", "move", "faena-ai", "--parent", "no-existe"), "tuku scope create no-existe"),
        (("scope", "move", "faena", "--parent", "faena-ai"), "dentro de sí mismo"),
    ]:
        antes = _foto(vault)
        assert _tuku(vault, *argv) == RECHAZO, argv
        assert dice in capsys.readouterr().err, argv
        assert _foto(vault) == antes, argv

    antes = _foto(vault)
    assert _crear(vault, "otro", "--parent", "faena") == RECHAZO
    assert "tuku scope move otro --parent faena" in capsys.readouterr().err
    assert _foto(vault) == antes


def test_mover_un_ambito_arrastra_todo_es_idempotente_y_se_deshace_sin_padre(
    vault: Path,
) -> None:
    _con_registros(vault)
    plano = _foto(vault)
    assert _tuku(vault, "scope", "move", "faena-ai", "--parent", "faena") == EXITO

    assert not (vault / "ambitos" / "faena-ai").exists()
    pagina = vault / "ambitos" / "faena" / "faena-ai" / "faena-ai.md"
    assert "![[../../PENDIENTES-AMBITOS.md#^faena-ai]]" in pagina.read_text(encoding="utf-8")
    for archivo in ("AHORA.md", "PENDIENTES.md"):
        texto = _leer(vault, archivo)
        assert "ambitos/faena-ai/" not in texto, archivo
        assert "ambitos/faena/faena-ai/faena-ai.md" in texto, archivo
    assert _con_ruta_vieja(vault, "ambitos/faena-ai/") == []
    assert _tuku(vault, "doctor") == EXITO

    movido = _foto(vault)
    assert _tuku(vault, "scope", "move", "faena-ai", "--parent", "faena") == EXITO
    assert _foto(vault) == movido

    assert _tuku(vault, "scope", "move", "faena-ai") == EXITO
    assert (vault / "ambitos" / "faena-ai" / "faena-ai.md").is_file()
    assert not (vault / "ambitos" / "faena" / "faena-ai").exists()
    assert _foto(vault) == plano
    assert _tuku(vault, "doctor") == EXITO


def test_renombrar_un_ambito_anidado_arrastra_todo(vault: Path) -> None:
    _con_registros(vault)
    assert _tuku(vault, "scope", "move", "faena-ai", "--parent", "faena") == EXITO
    assert _tuku(vault, "scope", "rename", "faena-ai", "faena-ia") == EXITO

    assert (vault / "ambitos" / "faena" / "faena-ia" / "faena-ia.md").is_file()
    assert not (vault / "ambitos" / "faena" / "faena-ai").exists()
    assert _colgando(vault, "faena-ai") == []
    assert "ambitos/faena/faena-ia/faena-ia.md" in _leer(vault, "AHORA.md")
    assert _tuku(vault, "doctor") == EXITO
