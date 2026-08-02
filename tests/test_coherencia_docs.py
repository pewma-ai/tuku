"""Tests que corren HOY, sin motor.

Todo lo demás en esta suite espera a que exista código. Estos no: verifican que el
corpus documental —que es el insumo del desarrollo asistido por LLM— sea coherente.

Importan más de lo que parece. Un agente que lee `spec/` para implementar un parser
hereda cualquier enlace roto o referencia obsoleta como si fuera verdad. Que estos
tests estén en verde es la precondición para que el desarrollo asistido no se
construya sobre arena.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
DIRS_DOC = ["docs", "spec", "devel", "corpus"]

# Enlaces Markdown relativos, excluyendo los absolutos y anclas puras.
_ENLACE = re.compile(r"\[[^\]]*\]\((?P<destino>[^)#][^)]*?)\)")
_BLOQUE = re.compile(r"```.*?```", re.DOTALL)


def _sin_bloques_de_codigo(texto: str) -> str:
    """Elimina los bloques cercados antes de buscar enlaces.

    Los ejemplos de las specs enlazan a rutas de un perfil hipotético
    (`../entidades/trabajo/sw-responsible.md`), que no existen en este repositorio
    y no deben existir. Validarlos sería exigir que la documentación de un formato
    contenga datos de ejemplo reales.
    """
    return _BLOQUE.sub("", texto)


def _archivos_md() -> list[Path]:
    salida: list[Path] = []
    for d in DIRS_DOC:
        salida.extend(sorted((REPO / d).rglob("*.md")))
    salida.append(REPO / "README.md")
    return [p for p in salida if p.exists()]


@pytest.mark.parametrize("md", _archivos_md(), ids=lambda p: str(p.relative_to(REPO)))
def test_enlaces_relativos_resuelven(md: Path) -> None:
    """Ningún enlace relativo en la documentación apunta a un archivo inexistente."""
    rotos: list[str] = []
    texto = _sin_bloques_de_codigo(md.read_text(encoding="utf-8"))
    for m in _ENLACE.finditer(texto):
        destino = m.group("destino").strip()
        if destino.startswith(("http://", "https://", "mailto:", "/")):
            continue
        if destino.startswith("<") or destino in {"…", "ruta", "ruta.md"}:
            continue  # marcador de posición en prosa
        # Enlace citado como ejemplo (`[x](y.md)` entre comillas invertidas): es
        # muestra de formato, no una referencia navegable.
        if texto[: m.start()].count("`") % 2 == 1:
            continue
        objetivo = (md.parent / destino.split("#", 1)[0]).resolve()
        if not objetivo.exists():
            rotos.append(destino)
    assert not rotos, f"enlaces rotos en {md.relative_to(REPO)}: {rotos}"


def test_no_quedan_referencias_a_specs_eliminadas() -> None:
    """`spec/bitacora.md` y `docs/principios.md` se eliminaron.

    Ninguna referencia navegable o en código a esos archivos debe sobrevivir.
    """
    eliminadas = ["spec/bitacora.md", "bitacora.md", "docs/principios.md"]
    hallazgos: list[str] = []
    for md in _archivos_md():
        texto = md.read_text(encoding="utf-8")
        for nombre in eliminadas:
            if f"]({nombre})" in texto or f"`{nombre}`" in texto:
                hallazgos.append(f"{md.relative_to(REPO)} → {nombre}")
    assert not hallazgos, f"referencias a specs eliminadas: {hallazgos}"


def test_prefijos_de_invariante_no_colisionan() -> None:
    """Cada spec numera sus invariantes con una letra propia.

    `xfail(strict=True)` es deliberado: mientras la colisión exista, el test falla
    y la suite sigue verde; el día que alguien renombre el prefijo, el test pasa a
    XPASS y **rompe la suite**, obligando a borrar este marcador. Es la forma de
    que un bloqueante conocido no se convierta en un bloqueante olvidado.
    """
    from tests.specref import invariantes

    por_prefijo: dict[str, set[str]] = {}
    for inv in invariantes():
        por_prefijo.setdefault(inv.id[0], set()).add(inv.spec)

    colisiones = {p: sorted(s) for p, s in por_prefijo.items() if len(s) > 1}
    assert not colisiones, (
        f"prefijos compartidos por más de una spec: {colisiones}. "
        "Renombrar uno antes de implementar (plan §5, bloqueante 3)."
    )
