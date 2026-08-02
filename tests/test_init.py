"""Pruebas de inicialización de perfil `tuku init` (F0.3).

Verifica la siembra de la estructura canónica, `.gitignore` y preservación de cambios.
"""

from pathlib import Path

from tuku.core.init import init_perfil


def test_tuku_init_crea_estructura_correcta(tmp_path: Path) -> None:
    """F0.3: Verifica la siembra del árbol canónico de directorios y .gitignore."""
    perfil_dir = tmp_path / "mi-tuku"
    res_dir = init_perfil(perfil_dir)

    assert res_dir == perfil_dir.resolve()
    assert (perfil_dir / ".tuku" / "config.yaml").exists()
    assert (perfil_dir / "entradas" / "entradas.md").exists()
    assert (perfil_dir / "tareas" / "tareas.md").exists()
    assert (perfil_dir / "estrategia" / "capacidad.md").exists()
    assert (perfil_dir / "estrategia" / "cadencias.md").exists()
    assert (perfil_dir / "notas" / "notas.md").exists()
    assert (perfil_dir / "notas" / "AGENTS.md").exists()
    assert (perfil_dir / "AGENTS.md").exists()

    gitignore_content = (perfil_dir / ".gitignore").read_text(encoding="utf-8")
    assert "tuku.log" in gitignore_content
    assert ".tuku/cache/" in gitignore_content


def test_tuku_init_es_idempotente(tmp_path: Path) -> None:
    """F0.3: Idempotencia de tuku init sin sobreescribir archivos existentes modificados."""
    perfil_dir = tmp_path / "mi-tuku"
    init_perfil(perfil_dir)

    # Modificamos un archivo sembrado
    entradas_file = perfil_dir / "entradas" / "entradas.md"
    entradas_file.write_text("## Modificado a mano", encoding="utf-8")

    # Volvemos a correr init
    init_perfil(perfil_dir)

    # No debe pisar el archivo modificado
    assert entradas_file.read_text(encoding="utf-8") == "## Modificado a mano"
