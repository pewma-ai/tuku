"""Tests del escenario 005-03-reorganizar-con-historia.

Mover y renombrar ámbitos anidados en un vault con dos semanas y una bitácora
cerrada: ningún link queda sin resolver, ni siquiera los del archivo histórico.

Ejecutable directo: `python3 tests/escenarios/test_005_03_reorganizar_con_historia.py`
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import gherkin  # noqa: E402

from tuku.cli import EXITO, RECHAZO  # noqa: E402

SLUG = "005-03-reorganizar-con-historia"
BASE = "005-01-las-dos-semanas-de-andrea"
CADENA_BASE = (
    "el árbol de Andrea nace con su negocio",
    "la primera semana se registra día por día",
    "la semana se cierra a mano y abre la siguiente",
    "la segunda semana cae sobre lo ya escrito",
)
REORGANIZAR = "mover y renombrar ámbitos anidados mantiene cada link"
CONSERVA = "lo que el ámbito tenía sigue siendo suyo"
REPETIR = "repetir la reorganización deja el vault igual"
LINK = re.compile(r"\]\(([^)#]+\.md)\)")


def _correr(titulo: str) -> gherkin.Corrida:
    for previo in CADENA_BASE:
        gherkin.correr(BASE, previo)
    for previo in (REORGANIZAR, CONSERVA, REPETIR):
        if previo == titulo:
            break
        gherkin.correr(SLUG, previo)
    return gherkin.correr(SLUG, titulo)


def _archivos(corrida: gherkin.Corrida) -> list[Path]:
    """Lo que escribió el autor y lo que se deriva de ello: no `reglas/` ni los `AGENTS.md`."""
    raiz = corrida.ruta("mi-vault")
    propios = [raiz / "AHORA.md", raiz / "PENDIENTES.md"]
    for carpeta in ("ambitos", "bitacoras", "notas"):
        propios += [p for p in sorted((raiz / carpeta).rglob("*.md")) if p.name != "AGENTS.md"]
    return propios


def test_005_03_los_ambitos_quedan_en_su_lugar_nuevo() -> None:
    corrida = _correr(REORGANIZAR)
    ambitos = corrida.ruta("mi-vault", "ambitos")
    assert (ambitos / "negocio/temporada-marzo/canal-feria/canal-feria.md").is_file()
    assert not (ambitos / "negocio/canal-feria").exists()
    assert (ambitos / "negocio/clientes/liceo-andes/liceo-andes.md").is_file()
    assert not (ambitos / "negocio/clientes/liceo-tecnico-andes").exists()


def test_005_03_toda_mencion_usa_la_ruta_y_el_nombre_nuevos() -> None:
    corrida = _correr(REORGANIZAR)
    viejos = ("negocio/canal-feria/", "liceo-tecnico-andes")
    for archivo in _archivos(corrida):
        texto = archivo.read_text(encoding="utf-8")
        for viejo in viejos:
            assert viejo not in texto, f"{archivo.relative_to(corrida.dir)} nombra {viejo!r}"


def test_005_03_todo_link_del_vault_resuelve_incluida_la_bitacora_cerrada() -> None:
    corrida = _correr(REORGANIZAR)
    cerrada = corrida.ruta("mi-vault", "bitacoras", "bitacora-2026-08-10-2026-08-16.md")
    for archivo in _archivos(corrida):
        for destino in LINK.findall(archivo.read_text(encoding="utf-8")):
            if destino.startswith(("http", "file:")):
                continue
            assert (archivo.parent / destino).resolve().exists(), f"{archivo.name}: {destino}"
    assert "../ambitos/negocio/temporada-marzo/canal-feria/canal-feria.md" in cerrada.read_text(
        encoding="utf-8"
    )
    assert corrida.de("tuku doctor").codigo == EXITO


def test_005_03_mover_y_renombrar_ya_dejan_lo_derivado_como_lo_dejaria_regenerar() -> None:
    corrida = _correr(CONSERVA)
    assert corrida.delta_de("mi-vault") == {}


def test_005_03_las_keywords_siguen_a_su_ambito() -> None:
    corrida = _correr(CONSERVA)
    pagina = corrida.ruta(
        "mi-vault", "ambitos", "negocio", "clientes", "liceo-andes", "liceo-andes.md"
    ).read_text(encoding="utf-8")
    linea = next(x for x in pagina.splitlines() if x.startswith("keywords:"))
    # el nombre no vive en las keywords: renombrar no las toca
    assert "liceo-tecnico-andes" not in linea
    for palabra in ("Patricia", "Lillo"):
        assert palabra in linea


def test_005_03_repetir_deja_el_vault_igual_y_el_nombre_viejo_se_rechaza() -> None:
    corrida = _correr(REPETIR)
    mover = corrida.de("scope move")
    renombrar = corrida.de("scope rename")
    assert mover.codigo == EXITO
    assert corrida.delta_de("mi-vault") == {}
    assert renombrar.codigo == RECHAZO
    assert "liceo-tecnico-andes" in renombrar.stderr
