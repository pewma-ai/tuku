"""Copia `template/` a `src/tuku/_home/`, el árbol que viaja dentro del wheel.

`tuku init` necesita `template/`, y un `uv tool install` descarta el clon del
repositorio, así que el árbol tiene que ir empaquetado. Lo llaman dos lados:

- `setup.py`, en el build, para que setuptools recolecte el `package-data`.
- el hook de pre-commit, cuando cambia algo bajo `template/`, para que la copia
  del checkout no quede atrás de la fuente. Importa porque `resolver_home`
  prefiere la copia empaquetada al checkout: una copia vieja se usa en silencio.

`_home/` está en `.gitignore`: es derivado y nunca se versiona.

**Qué lee y escribe:** lee `template/`, escribe `src/tuku/_home/`.
**A mano:** `rm -rf src/tuku/_home && cp -R template src/tuku/_home/template`.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

_PAQUETE = Path(__file__).resolve().parent
DESTINO = _PAQUETE / "_home"


def raiz_checkout() -> Path | None:
    """La raíz del repositorio, subiendo desde este archivo. `None` si no está."""
    for ancestro in _PAQUETE.parents:
        if (ancestro / "template").is_dir() and (ancestro / "pyproject.toml").is_file():
            return ancestro
    return None


def empaquetar(raiz: Path | None = None) -> Path | None:
    """Regenera `_home/` desde `template/`. `None` si no hay checkout que copiar."""
    base = raiz if raiz is not None else raiz_checkout()
    if base is None or not (base / "template").is_dir():
        return None
    if DESTINO.exists():
        shutil.rmtree(DESTINO)
    DESTINO.mkdir(parents=True)
    shutil.copytree(base / "template", DESTINO / "template")
    return DESTINO


def main() -> int:
    destino = empaquetar()
    if destino is None:
        print("_pack: no hay checkout con template/; nada que empaquetar.")
        return 0
    print(f"_pack: {destino} regenerado desde template/.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
