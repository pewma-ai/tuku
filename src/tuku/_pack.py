"""Copia `template/`, `docs/` y `spec/` a `src/tuku/_home/`, el árbol del wheel.

`tuku init` necesita `template/`, y un `uv tool install` descarta el clon del
repositorio, así que el árbol tiene que ir empaquetado. `docs/` y `spec/` van
para que quien use TUKU (persona o agente) pueda leer el marco rector y las
specs sin el repositorio. Lo llaman dos lados:

- `setup.py`, en el build, para que setuptools recolecte el `package-data`.
- el hook de pre-commit, cuando cambia algo bajo `template/`, para que la copia
  del checkout no quede atrás de la fuente. Importa porque `resolver_home`
  prefiere la copia empaquetada al checkout: una copia vieja se usa en silencio.

`_home/` está en `.gitignore`: es derivado y nunca se versiona.

**Qué lee y escribe:** lee `template/`, `docs/` y `spec/`, escribe `src/tuku/_home/`.
**A mano:** `rm -rf src/tuku/_home && mkdir src/tuku/_home`, y copiar ahí
`template`, `docs` y `spec`.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

_PAQUETE = Path(__file__).resolve().parent
DESTINO = _PAQUETE / "_home"

#: Lo que viaja en el wheel. `template/` es obligatorio; el resto es referencia.
CARPETAS = ("template", "docs", "spec")


def raiz_checkout() -> Path | None:
    """La raíz del repositorio, subiendo desde este archivo. `None` si no está."""
    for ancestro in _PAQUETE.parents:
        if (ancestro / "template").is_dir() and (ancestro / "pyproject.toml").is_file():
            return ancestro
    return None


def empaquetar(raiz: Path | None = None) -> Path | None:
    """Regenera `_home/` desde el checkout. `None` si no hay checkout que copiar."""
    base = raiz if raiz is not None else raiz_checkout()
    if base is None or not (base / "template").is_dir():
        return None
    if DESTINO.exists():
        shutil.rmtree(DESTINO)
    DESTINO.mkdir(parents=True)
    for carpeta in CARPETAS:
        if (base / carpeta).is_dir():
            shutil.copytree(base / carpeta, DESTINO / carpeta)
    return DESTINO


def main() -> int:
    destino = empaquetar()
    if destino is None:
        print("_pack: no hay checkout con template/; nada que empaquetar.")
        return 0
    print(f"_pack: {destino} regenerado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
