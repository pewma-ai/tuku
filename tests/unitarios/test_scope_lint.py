"""Tests unitarios de tuku doctor scope y validaciones estructurales de ámbitos."""

from __future__ import annotations

from pathlib import Path

from tuku import scope


def test_scope_lint_vault_sano(tmp_path: Path) -> None:
    ambitos_dir = tmp_path / "ambitos"
    personal_dir = ambitos_dir / "personal"
    personal_dir.mkdir(parents=True)
    (personal_dir / "personal.md").write_text(
        "---\ntype: Scope\n---\n# personal\n\n![[../PENDIENTES-AMBITOS.md#^personal]]\n",
        encoding="utf-8",
    )
    callout_esperado = (
        "---\ntype: Derived\n---\n\n> [!todo] Pendientes en **Personal** ^personal\n"
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


def test_scope_lint_nombra_transclusion_callout_y_archivo_que_faltan(tmp_path: Path) -> None:
    ambitos_dir = tmp_path / "ambitos"
    personal_dir = ambitos_dir / "personal"
    personal_dir.mkdir(parents=True)

    assert "error: falta el archivo" in scope.lint_callouts(tmp_path)[0]

    (personal_dir / "personal.md").write_text(
        "---\ntype: Scope\n---\n# personal\n\nTexto sin transclusión.\n", encoding="utf-8"
    )
    (ambitos_dir / "PENDIENTES-AMBITOS.md").write_text(
        "---\ntype: Derived\n---\n\n# Pendientes\n", encoding="utf-8"
    )
    [sin_transclusion] = scope.lint_transclusiones(tmp_path)
    assert "falta la transclusión a PENDIENTES-AMBITOS.md" in sin_transclusion
    assert "PENDIENTES-AMBITOS.md#^personal" in sin_transclusion

    [sin_callout] = scope.lint_callouts(tmp_path)
    assert "falta el callout para el ámbito 'personal'" in sin_callout


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
