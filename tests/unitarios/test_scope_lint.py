"""Tests unitarios de tuku scope lint y validaciones estructurales de ámbitos."""

from __future__ import annotations

from pathlib import Path

from tuku import scope


def test_scope_lint_vault_sano(tmp_path: Path) -> None:
    ambitos_dir = tmp_path / "ambitos"
    personal_dir = ambitos_dir / "personal"
    personal_dir.mkdir(parents=True)
    (ambitos_dir / "AGENTS.md").write_text("", encoding="utf-8")
    (ambitos_dir / "CADENCIAS.md").write_text("", encoding="utf-8")
    (personal_dir / "AGENTS.md").write_text("", encoding="utf-8")
    (personal_dir / "CADENCIAS.md").write_text("", encoding="utf-8")
    (personal_dir / "personal.md").write_text(
        "---\ntype: Scope\n---\n# personal\n\n![[../PENDIENTES-AMBITOS.md#^personal]]\n",
        encoding="utf-8",
    )
    callout_esperado = (
        "---\ntype: Pending\n---\n\n"
        "> [!todo] Pendientes en **Personal** ^personal\n> SIN PENDIENTES\n"
    )
    (ambitos_dir / "PENDIENTES-AMBITOS.md").write_text(
        callout_esperado,
        encoding="utf-8",
    )
    (tmp_path / "AHORA.md").write_text(
        "---\ntype: Logbook\n---\n## Lunes 7 de septiembre\n- 10:00 - [[personal]] nota\n",
        encoding="utf-8",
    )

    hallazgos = scope.lint(tmp_path)
    assert not hallazgos


def test_scope_lint_falta_transclusion(tmp_path: Path) -> None:
    ambitos_dir = tmp_path / "ambitos"
    personal_dir = ambitos_dir / "personal"
    personal_dir.mkdir(parents=True)
    (personal_dir / "personal.md").write_text(
        "---\ntype: Scope\n---\n# personal\n\nTexto sin transclusión.\n",
        encoding="utf-8",
    )
    (ambitos_dir / "PENDIENTES-AMBITOS.md").write_text(
        "> [!todo] Pendientes en **Personal** ^personal\n> SIN PENDIENTES\n",
        encoding="utf-8",
    )

    hallazgos = scope.lint_transclusiones(tmp_path)
    assert len(hallazgos) == 1
    assert "falta la transclusión a PENDIENTES-AMBITOS.md" in hallazgos[0]
    assert "PENDIENTES-AMBITOS.md#^personal" in hallazgos[0]


def test_scope_lint_falta_callout_en_pendientes_ambitos(tmp_path: Path) -> None:
    ambitos_dir = tmp_path / "ambitos"
    personal_dir = ambitos_dir / "personal"
    personal_dir.mkdir(parents=True)
    (personal_dir / "personal.md").write_text(
        "---\ntype: Scope\n---\n# personal\n\n![[../PENDIENTES-AMBITOS.md#^personal]]\n",
        encoding="utf-8",
    )
    # PENDIENTES-AMBITOS sin el callout de personal
    (ambitos_dir / "PENDIENTES-AMBITOS.md").write_text(
        "---\ntype: Pending\n---\n\n# Pendientes\n",
        encoding="utf-8",
    )

    hallazgos = scope.lint_callouts(tmp_path)
    assert len(hallazgos) == 1
    assert "falta el callout para el ámbito 'personal'" in hallazgos[0]


def test_scope_lint_falta_archivo_pendientes_ambitos(tmp_path: Path) -> None:
    ambitos_dir = tmp_path / "ambitos"
    ambitos_dir.mkdir(parents=True)
    hallazgos = scope.lint_callouts(tmp_path)
    assert len(hallazgos) == 1
    assert "error: falta el archivo" in hallazgos[0]


def test_scope_lint_registro_apunta_a_categoria(tmp_path: Path) -> None:
    ambitos_dir = tmp_path / "ambitos"
    clientes_dir = ambitos_dir / "clientes"
    clientes_dir.mkdir(parents=True)  # No tiene clientes.md, por ende es categoría
    (ambitos_dir / "PENDIENTES-AMBITOS.md").write_text("", encoding="utf-8")
    (tmp_path / "AHORA.md").write_text(
        "- 10:00 - [[clientes]] reunión\n",
        encoding="utf-8",
    )

    hallazgos = scope.lint(tmp_path)
    assert any("categoría" in h for h in hallazgos)
