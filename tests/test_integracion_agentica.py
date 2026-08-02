"""Tests de integración agéntica — Fase 5.

Arquitectura de la suite:
- Tests deterministas (sin agente): verifican la lógica sin LLM.
  Corren siempre. Cubren F5.2, F5.3, F5.4, e init con .hermes/.
- Tests agénticos (con @pytest.mark.agentic): gastan tokens.
  Excluidos por defecto; activar con `pytest -m agentic`.

Reglas:
- Ningún test toca datos reales (todo en tmp_path / perfil_tmp).
- Todos los ids de entidad citados en el texto deben existir en el perfil.
- Todo test agéntico tiene su gemelo sin agente.

Ver `devel/checklist-implementacion.md` §F5 y ADR 0018.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from tuku.core.agent import (
    AgentError,
    build_tesauro_context,
    escribir_registro,
    registrar_conversacional,
)
from tuku.core.cadence import abrir_ciclo, cerrar_ciclo
from tuku.core.init import _provisionar_hermes, init_perfil


# ---------------------------------------------------------------------------
# F5.0 — tuku init provisiona .hermes/ (ADR 0018)
# ---------------------------------------------------------------------------


def test_init_crea_hermes_dir_cuando_hermes_instalado(tmp_path: Path) -> None:
    """Si ~/.hermes existe, init_perfil crea .hermes/ en el perfil."""
    sistema = Path.home() / ".hermes"
    if not sistema.exists():
        pytest.skip("~/.hermes no existe en este entorno")

    perfil = tmp_path / "perfil"
    perfil.mkdir()
    init_perfil(perfil)

    hermes_dir = perfil / ".hermes"
    assert hermes_dir.is_dir(), ".hermes/ debe existir tras tuku init"
    assert (hermes_dir / "config.yaml").exists(), "config.yaml mínimo debe estar sembrado"


def test_init_hermes_enlaza_credenciales(tmp_path: Path) -> None:
    """Los symlinks de credenciales apuntan a ~/.hermes/ original."""
    sistema = Path.home() / ".hermes"
    if not sistema.exists():
        pytest.skip("~/.hermes no existe en este entorno")

    perfil = tmp_path / "perfil"
    perfil.mkdir()
    init_perfil(perfil)

    hermes_dir = perfil / ".hermes"
    for cred in [".env", "auth.json"]:
        src = sistema / cred
        dst = hermes_dir / cred
        if src.exists():
            assert dst.is_symlink(), f"{cred} debe ser symlink"
            assert dst.resolve() == src.resolve(), f"{cred} debe apuntar a ~/.hermes/{cred}"


def test_init_hermes_es_idempotente(tmp_path: Path) -> None:
    """Llamar init_perfil dos veces no rompe .hermes/."""
    sistema = Path.home() / ".hermes"
    if not sistema.exists():
        pytest.skip("~/.hermes no existe en este entorno")

    perfil = tmp_path / "perfil"
    perfil.mkdir()
    init_perfil(perfil)
    init_perfil(perfil)  # segunda llamada no debe fallar

    assert (perfil / ".hermes").is_dir()


def test_init_sin_hermes_no_falla(tmp_path: Path, monkeypatch) -> None:
    """Si ~/.hermes no existe, init_perfil termina limpio (sin excepción)."""
    monkeypatch.setattr("tuku.core.init.Path.home", lambda: tmp_path / "fake-home")

    perfil = tmp_path / "perfil"
    perfil.mkdir()
    result = init_perfil(perfil)

    assert result == perfil.resolve()
    assert not (perfil / ".hermes").exists()


def test_gitignore_contiene_hermes(tmp_path: Path) -> None:
    """.gitignore del perfil debe excluir .hermes/."""
    perfil = tmp_path / "perfil"
    perfil.mkdir()
    init_perfil(perfil)

    gitignore = (perfil / ".gitignore").read_text(encoding="utf-8")
    assert ".hermes/" in gitignore, ".gitignore debe excluir el directorio .hermes/"


# ---------------------------------------------------------------------------
# F5.3 — abrir_ciclo estructura canónica
# ---------------------------------------------------------------------------


def test_abrir_ciclo_front_matter_completo(perfil_tmp: Path) -> None:
    """abrir_ciclo siembra front matter con cycle_type, cycle_start y status."""
    ruta = abrir_ciclo(
        perfil_tmp,
        "2026-W32",
        cycle_type="semana",
        cycle_start="2026-08-03",
        cycle_end="2026-08-09",
    )

    assert ruta.exists()
    texto = ruta.read_text(encoding="utf-8")

    assert "cycle_type: semana" in texto
    assert "cycle_start: 2026-08-03" in texto
    assert "cycle_end: 2026-08-09" in texto
    assert "status: open" in texto


def test_abrir_ciclo_secciones_obligatorias(perfil_tmp: Path) -> None:
    """abrir_ciclo incluye las secciones obligatorias del plan (C5)."""
    ruta = abrir_ciclo(perfil_tmp, "2026-test")
    texto = ruta.read_text(encoding="utf-8")

    assert "## Intención" in texto
    assert "## No entra (y por qué)" in texto
    assert "## Restricciones y contexto" in texto


def test_cerrar_ciclo_secciones_c7(perfil_tmp: Path) -> None:
    """cerrar_ciclo siembra las cinco secciones obligatorias de C7."""
    abrir_ciclo(perfil_tmp, "2026-W32")
    ruta = cerrar_ciclo(perfil_tmp, "2026-W32")

    texto = ruta.read_text(encoding="utf-8")

    assert "## TL;DR" in texto
    assert "## Avances" in texto
    assert "## Desviaciones" in texto
    assert "## Aprendizajes" in texto
    assert "## Momentum y señales" in texto


def test_cerrar_ciclo_marca_plan_closed(perfil_tmp: Path) -> None:
    """cerrar_ciclo actualiza status del plan a closed."""
    abrir_ciclo(perfil_tmp, "2026-W33")
    cerrar_ciclo(perfil_tmp, "2026-W33")

    plan = perfil_tmp / "ciclos" / "plan_2026-W33.md"
    assert "status: closed" in plan.read_text(encoding="utf-8")


def test_cerrar_ciclo_sin_plan_previo_no_falla(perfil_tmp: Path) -> None:
    """cerrar_ciclo funciona aunque no exista plan previo (crea resultados igual)."""
    ruta = cerrar_ciclo(perfil_tmp, "ciclo-sin-plan")
    assert ruta.exists()
    assert "## TL;DR" in ruta.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# F5.4 — tesauro vivo acotado
# ---------------------------------------------------------------------------


def test_tesauro_respeta_limite_chars(perfil_tmp: Path) -> None:
    """build_tesauro_context nunca supera MAX_TESAURO_CHARS."""
    from tuku.core.agent import MAX_TESAURO_CHARS

    # Sembrar muchas entidades para que el tesauro sea grande
    entidades_dir = perfil_tmp / "entidades" / "trabajo"
    entidades_dir.mkdir(parents=True, exist_ok=True)
    for i in range(200):
        (entidades_dir / f"entidad-{i:03d}.md").write_text(
            f"---\nid: entidad-{i:03d}\ntype: proyecto\nlifecycle: vigente\n---\n",
            encoding="utf-8",
        )

    ctx = build_tesauro_context(perfil_tmp)
    assert len(ctx) <= MAX_TESAURO_CHARS, "El tesauro debe respetar el límite de caracteres"


def test_tesauro_excluye_archivadas(perfil_tmp: Path) -> None:
    """Las entidades archivadas no aparecen en el tesauro."""
    ent_dir = perfil_tmp / "entidades" / "personal"
    ent_dir.mkdir(parents=True, exist_ok=True)
    (ent_dir / "arch-ent.md").write_text(
        "---\nid: arch-ent\ntype: proyecto\nlifecycle: archivada\n---\n",
        encoding="utf-8",
    )

    ctx = build_tesauro_context(perfil_tmp)
    assert "arch-ent" not in ctx


def test_tesauro_incluye_vigentes(perfil_tmp: Path) -> None:
    """Las entidades vigentes aparecen en el tesauro."""
    ent_dir = perfil_tmp / "entidades" / "personal"
    ent_dir.mkdir(parents=True, exist_ok=True)
    (ent_dir / "proj-activo.md").write_text(
        "---\nid: proj-activo\ntype: proyecto\nlifecycle: vigente\n---\n",
        encoding="utf-8",
    )

    ctx = build_tesauro_context(perfil_tmp)
    assert "proj-activo" in ctx


# ---------------------------------------------------------------------------
# F5.2 — captura conversacional (sin agente)
# ---------------------------------------------------------------------------


def test_registrar_detecta_entrada(perfil_tmp: Path) -> None:
    """Texto sin verbos de acción → entrada de bitácora."""
    tipo, canonico = registrar_conversacional(
        perfil_tmp,
        "Excelente reunión con el equipo, se cerró el trimestre bien.",
        sin_agente=True,
    )
    assert tipo == "entrada"
    assert canonico.startswith("- ")


def test_registrar_detecta_tarea(perfil_tmp: Path) -> None:
    """Texto con verbo de acción urgente → tarea posicional."""
    tipo, canonico = registrar_conversacional(
        perfil_tmp,
        "Hay que preparar la propuesta para el lunes.",
        sin_agente=True,
    )
    assert tipo == "tarea"
    assert "- [ ]" in canonico
    assert "^t-" in canonico


def test_registrar_clasifica_hito(perfil_tmp: Path) -> None:
    """Tag #hito → clasificación Hito en la entrada."""
    tipo, canonico = registrar_conversacional(
        perfil_tmp,
        "Lanzamos el producto en producción #hito",
        sin_agente=True,
    )
    assert tipo == "entrada"
    assert "Hito" in canonico


def test_registrar_verifica_entidad_inexistente(perfil_tmp: Path) -> None:
    """Si el texto cita una entidad que no existe, debe lanzar AgentError."""
    with pytest.raises(AgentError, match="[Vv]erificaci"):
        registrar_conversacional(
            perfil_tmp,
            "Reunión con [entidad-inexistente](../entidades/trabajo/entidad-inexistente.md)",
            sin_agente=True,
        )


def test_escribir_registro_entrada_crea_archivo(perfil_tmp: Path) -> None:
    """escribir_registro crea entradas/YYYY-MM.md si no existe."""
    tipo, canonico = registrar_conversacional(
        perfil_tmp,
        "Buena jornada de trabajo hoy.",
        sin_agente=True,
    )
    destino = escribir_registro(perfil_tmp, tipo, canonico)

    assert destino.exists()
    contenido = destino.read_text(encoding="utf-8")
    assert canonico in contenido


def test_escribir_registro_tarea_va_a_tareas(perfil_tmp: Path) -> None:
    """escribir_registro de tarea escribe en tareas/tareas.md."""
    tipo, canonico = registrar_conversacional(
        perfil_tmp,
        "Hay que revisar el informe mensual.",
        sin_agente=True,
    )
    destino = escribir_registro(perfil_tmp, tipo, canonico)

    assert destino.name == "tareas.md"
    assert canonico in destino.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# CLI — tuku registrar / abrir / cerrar
# ---------------------------------------------------------------------------


def test_cli_registrar_dry_run(perfil_tmp: Path) -> None:
    """tuku registrar --dry-run imprime sin escribir."""
    from tuku.cli import main

    rc = main(["-p", str(perfil_tmp), "registrar", "Buena semana #hito", "--dry-run"])
    assert rc == 0


def test_cli_abrir_crea_plan(perfil_tmp: Path) -> None:
    """tuku abrir crea plan_*.md en ciclos/."""
    from tuku.cli import main

    rc = main([
        "-p", str(perfil_tmp), "abrir", "2026-W99",
        "--tipo", "semana", "--inicio", "2026-12-01", "--fin", "2026-12-07",
    ])
    assert rc == 0
    assert (perfil_tmp / "ciclos" / "plan_2026-W99.md").exists()


def test_cli_cerrar_crea_resultados(perfil_tmp: Path) -> None:
    """tuku cerrar crea resultados_*.md en ciclos/."""
    from tuku.cli import main

    main(["-p", str(perfil_tmp), "abrir", "2026-W98"])
    rc = main(["-p", str(perfil_tmp), "cerrar", "2026-W98"])

    assert rc == 0
    assert (perfil_tmp / "ciclos" / "resultados_2026-W98.md").exists()


# ---------------------------------------------------------------------------
# Tests agénticos (marcador `agentic` — excluidos por defecto)
# ---------------------------------------------------------------------------


@pytest.mark.agentic
def test_registrar_con_agente_produce_canonica(hermes_efimero: dict) -> None:
    """[AGENTE] registrar_conversacional con agente produce forma canónica parseable."""
    if shutil.which("hermes") is None:
        pytest.skip("hermes no instalado")

    from tuku.io.entry import Entry

    profile_dir = Path(hermes_efimero["HERMES_HOME"]).parent

    tipo, canonico = registrar_conversacional(
        profile_dir,
        "Cerramos el mes con muy buenos resultados. #hito",
        sin_agente=False,
    )

    assert tipo in ("entrada", "tarea")
    if tipo == "entrada":
        # Debe ser parseable
        entry = Entry.parse_line(canonico)
        assert entry.text


@pytest.mark.agentic
def test_hermes_mantiene_sesion_entre_llamadas(hermes_efimero: dict) -> None:
    """[AGENTE] run_hermes con --continue mantiene contexto entre llamadas."""
    if shutil.which("hermes") is None:
        pytest.skip("hermes no instalado")

    from tuku.core.agent import run_hermes

    profile_dir = Path(hermes_efimero["HERMES_HOME"]).parent

    r1 = run_hermes(profile_dir, "Recuerda el número 42 para la siguiente pregunta.")
    r2 = run_hermes(profile_dir, "¿Qué número te pedí que recordaras?")

    # La respuesta al segundo turno debe mencionar 42
    assert "42" in r2, f"Hermes no mantuvo el contexto: {r2!r}"
