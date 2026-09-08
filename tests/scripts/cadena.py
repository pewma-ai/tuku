"""Paso de cadena: prepara el vault inicial de un escenario 002-YY y compara estados.

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

#: Los pasos preparados en esta sesión de pytest. Una carpeta de `playground/`
#: que sobrevive de una corrida anterior puede traer el vault de otro template,
#: y heredarla hace fallar al paso siguiente por algo que no es su defecto. El
#: registro convierte ese rojo confuso en un mensaje que dice qué correr.
_PREPARADOS: set[str] = set()


def preparar_paso(slug: str, *, previo: str | None, desde: date) -> Path:
    """Deja el vault inicial de `slug` en `playground/<slug>/` y lo devuelve."""
    destino = preparar_playground(slug)
    if previo is None:
        init(destino, variante="vanilla", desde=desde, home=RAIZ_REPO)
        _PREPARADOS.add(slug)
        return destino

    if previo not in _PREPARADOS:
        raise NotImplementedError(
            f"el paso previo {previo!r} no se corrió en esta sesión de pytest, así "
            f"que su playground/ no es de fiar. Corre la cadena entera (`uv run "
            f"pytest tests/escenarios/`) o el paso previo antes que este. "
            f"Reproducir la cadena desde el fixture del epic queda pendiente."
        )

    origen = RAIZ_REPO / "playground" / previo
    if not origen.is_dir():
        raise NotImplementedError(
            f"el paso previo {previo!r} se preparó pero su playground/ no está. "
            f"Algo lo borró a mitad de la corrida."
        )
    shutil.copytree(origen, destino)
    _PREPARADOS.add(slug)
    return destino


def instantanea(raiz: Path) -> dict[str, bytes]:
    """El contenido de todos los archivos del vault, por ruta relativa."""
    return {
        str(p.relative_to(raiz)): p.read_bytes() for p in sorted(raiz.rglob("*")) if p.is_file()
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


def correr_cli(argv: list[str]) -> tuple[int, str, str]:
    """Llama a `tuku.cli.main(argv)` capturando stdout, stderr y código de salida."""
    import io
    from contextlib import redirect_stderr, redirect_stdout

    from tuku.cli import main

    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            codigo = main(argv)
        except SystemExit as e:
            codigo = e.code if isinstance(e.code, int) else 1
    return codigo, out.getvalue(), err.getvalue()

