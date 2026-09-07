"""Paso de cadena: prepara el vault inicial de un escenario 002-YYY y compara estados.

Los escenarios del epic 002 están encadenados (ver `../escenarios/README.md`):
el estado inicial de un paso es el estado final del anterior. El primero
(`previo=None`) parte de un vault vanilla recién instalado; los demás heredan
copiando el `playground/` del paso previo.

`delta` es lo que el escenario afirma: no el árbol completo, sino qué cambió
entre dos instantáneas. Así se ven los efectos colaterales y la idempotencia
sale gratis, porque el segundo pase de una operación tiene que dar delta vacío.
"""

from __future__ import annotations

import shutil
import sys
from datetime import date
from pathlib import Path

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ_REPO / "src"))
sys.path.insert(0, str(RAIZ_REPO / "tests" / "scripts"))

from vault import preparar_playground  # noqa: E402

from tuku.init import init  # noqa: E402


def preparar_paso(slug: str, *, previo: str | None, desde: date) -> Path:
    """Deja el vault inicial de `slug` en `playground/<slug>/` y lo devuelve."""
    destino = preparar_playground(slug)
    if previo is None:
        init(destino, variante="vanilla", desde=desde, home=RAIZ_REPO)
        return destino

    origen = RAIZ_REPO / "playground" / previo
    if not origen.is_dir():
        raise NotImplementedError(
            f"el paso previo {previo!r} no está en playground/. Por ahora hay que "
            f"correrlo antes en la misma sesión de pytest. Reproducir la cadena "
            f"entera desde el fixture del epic queda pendiente."
        )
    shutil.copytree(origen, destino)
    return destino


def instantanea(raiz: Path) -> dict[str, bytes]:
    """El contenido de todos los archivos del vault, por ruta relativa."""
    return {
        str(p.relative_to(raiz)): p.read_bytes()
        for p in sorted(raiz.rglob("*"))
        if p.is_file()
    }


def delta(antes: dict[str, bytes], despues: dict[str, bytes]) -> dict[str, str]:
    """Rutas que cambiaron entre dos instantáneas: 'nuevo', 'borrado' o 'modificado'."""
    cambios: dict[str, str] = {}
    for ruta in antes.keys() | despues.keys():
        anterior, posterior = antes.get(ruta), despues.get(ruta)
        if anterior == posterior:
            continue
        cambios[ruta] = (
            "nuevo" if anterior is None else "borrado" if posterior is None else "modificado"
        )
    return cambios
