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

import gherkin  # noqa: E402
import vault  # noqa: E402

from tuku.init import init  # noqa: E402

#: Reexportadas desde `vault`, donde viven ahora: el runner de escenarios
#: también las usa y no puede importar este módulo (lo importa él).
instantanea = vault.instantanea
delta = vault.delta

def _vault_del_paso(slug: str) -> Path:
    """Dónde quedó el vault de un paso, esté migrado al runner o no.

    Un paso que todavía usa este módulo deja el vault en `playground/<slug>/`.
    Uno migrado al runner de escenarios lo deja en
    `playground/<slug>/<primer escenario>/mi-vault/`, porque allá cada escenario
    tiene su carpeta y el vault se llama como lo nombra el `.md`.
    """
    directo = vault.PLAYGROUND / slug
    if (directo / "AHORA.md").is_file():
        return directo
    escenarios = gherkin.leer_escenarios(slug)
    if escenarios:
        migrado = directo / gherkin.slugificar(escenarios[0].titulo) / "mi-vault"
        if (migrado / "AHORA.md").is_file():
            return migrado
    return directo


def preparar_paso(slug: str, *, previo: str | None, desde: date) -> Path:
    """Deja el vault inicial de `slug` en `playground/<slug>/` y lo devuelve.

    El borrado del epic entero lo hace el `XXX-00` una sola vez por sesión
    (`gherkin.preparar_epic`), así que la primera preparación de cada paso solo
    crea. Un paso que se prepara más de una vez (varios tests sobre el mismo
    escenario, cada uno partiendo del estado heredado sin las mutaciones del
    anterior) sí tiene que rehacer su carpeta, y ahí vuelve `vault.preparar_dir`.
    """
    gherkin.preparar_epic(gherkin.epic_de(slug))
    destino = vault.PLAYGROUND / slug
    if destino.exists():
        destino = vault.preparar_dir(destino)
    else:
        destino.mkdir(parents=True)
    if previo is None:
        init(destino, variante="vanilla", desde=desde, home=RAIZ_REPO)
        return destino

    origen = _vault_del_paso(previo)
    if not (origen / "AHORA.md").is_file():
        raise NotImplementedError(
            f"el paso previo {previo!r} no dejó su vault en {origen}. El `XXX-00` "
            f"del epic limpia `playground/` al empezar la sesión, así que lo que "
            f"hay ahí siempre es de esta corrida: si falta, es que el paso previo "
            f"no se corrió. Corre la cadena entera (`uv run pytest "
            f"tests/escenarios/`) o el paso previo antes que este."
        )
    shutil.copytree(origen, destino, dirs_exist_ok=True)
    return destino


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
