"""Tests del escenario 005-05-las-notas-de-la-pyme.

Notas libres con su `## Ver además`, el lint que nombra un enlace sin motivo y la
primera nota tipada (una persona).

Ejecutable directo: `python3 tests/escenarios/test_005_05_las_notas_de_la_pyme.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import gherkin  # noqa: E402

from tuku.cli import EXITO  # noqa: E402

SLUG = "005-05-las-notas-de-la-pyme"
BASE = "005-01-las-dos-semanas-de-andrea"
CADENA_BASE = (
    "el árbol de Andrea nace con su negocio",
    "la primera semana se registra día por día",
    "la semana se cierra a mano y abre la siguiente",
    "la segunda semana cae sobre lo ya escrito",
)
LIBRES = "las notas del negocio se escriben y pasan el lint"
TODAS = "note lint sin archivo revisa solo las notas"
SIN_MOTIVO = "un enlace del cuerpo sin motivo en Ver además se nombra"
TIPADA = "la primera nota tipada es una persona"
NOTAS = (
    "como-cotizo",
    "condiciones-de-pago-por-canal",
    "proveedores-y-sus-plazos-reales",
)


def _correr(titulo: str) -> gherkin.Corrida:
    for previo in CADENA_BASE:
        gherkin.correr(BASE, previo)
    if titulo != LIBRES:
        gherkin.correr(SLUG, LIBRES)
    if titulo in (SIN_MOTIVO, TIPADA):
        gherkin.correr(SLUG, TODAS)
    return gherkin.correr(SLUG, titulo)


def _nota(corrida: gherkin.Corrida, nombre: str) -> str:
    return corrida.ruta("mi-vault", "notas", f"{nombre}.md").read_text(encoding="utf-8")


def test_005_05_las_tres_notas_existen_con_su_ver_ademas() -> None:
    corrida = _correr(LIBRES)
    for nombre in NOTAS:
        nota = _nota(corrida, nombre)
        assert nota.startswith("---\ntype: Note\n"), nombre
        assert "## Ver además" in nota, nombre
        enlace = nota.split("## Ver además", 1)[1]
        assert "(../ambitos/negocio/negocio.md) — " in enlace, f"{nombre}: el ámbito sin motivo"


def test_005_05_cada_nota_deja_su_constancia_el_domingo() -> None:
    corrida = _correr(LIBRES)
    ahora = corrida.ruta("mi-vault", "AHORA.md").read_text(encoding="utf-8")
    domingo = ahora.split("## Domingo 23 de agosto", 1)[1]
    for nombre in NOTAS:
        assert f"(notas/{nombre}.md)" in domingo, nombre


def test_005_05_note_lint_sin_archivo_revisa_solo_las_notas() -> None:
    """`notas/AGENTS.md` es del sistema y no es una nota: no le falta ningún `Ver además`."""
    corrida = _correr(TODAS)
    assert corrida.codigo == EXITO, corrida.stdout + corrida.stderr
    assert "AGENTS.md" not in corrida.stdout + corrida.stderr


def _doctor(corrida: gherkin.Corrida) -> int:
    """El código del `tuku doctor` a secas: `de` no lo distingue de `tuku doctor note …`."""
    [revision] = [r for r in corrida.resultados if r.comando.endswith("tuku doctor")]
    return revision.codigo


def test_005_05_cada_nota_pasa_su_lint() -> None:
    corrida = _correr(LIBRES)
    lints = [r for r in corrida.resultados if "doctor note" in r.comando]
    assert len(lints) == 3 and all(r.codigo == EXITO for r in lints)


def test_005_05_el_vault_con_notas_esta_sano() -> None:
    assert _doctor(_correr(LIBRES)) == EXITO


def test_005_05_un_enlace_del_cuerpo_que_ver_ademas_no_lista_se_nombra() -> None:
    corrida = _correr(SIN_MOTIVO)
    assert corrida.codigo != EXITO, "el lint dejó pasar un enlace saliente sin motivo"
    salida = corrida.stdout + corrida.stderr
    assert "condiciones-de-pago-por-canal.md" in salida and "Ver además" in salida


def test_005_05_una_nota_tipada_declara_su_subtype() -> None:
    corrida = _correr(TIPADA)
    nota = _nota(corrida, "patricia-lillo")
    assert "type: Note" in nota and "subtype: persona" in nota
    assert "## Ver además" in nota.split("subtype: persona", 1)[1]
    assert "liceo-tecnico-andes.md) — " in nota


def test_005_05_el_libro_describe_la_plantilla_de_persona() -> None:
    corrida = _correr(TIPADA)
    libro = corrida.ruta("mi-vault", "LIBRO-DE-ESTILO.md").read_text(encoding="utf-8")
    assert "--subtype persona" in libro


def test_005_05_con_la_nota_tipada_el_vault_sigue_sano() -> None:
    corrida = _correr(TIPADA)
    assert _doctor(corrida) == EXITO
