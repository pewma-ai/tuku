"""Puente de build: empaqueta `template/` dentro del wheel.

`pyproject.toml` define el proyecto; esto solo agrega un paso al build. Un
`pipx install` / `uv tool install` construye el wheel y descarta el clon del
repositorio, así que el árbol que `tuku init` necesita (hoy, solo `template/`)
tiene que viajar dentro del paquete. Se copia a `src/tuku/_home/` antes de que
setuptools recolecte `package-data`. La copia misma vive en `tuku._pack`, que
también corre desde el hook de pre-commit cuando cambia `template/`.

En el checkout de trabajo ese directorio no existe (está en `.gitignore`) y
`tuku.init` cae a la raíz del repositorio. Ver `src/tuku/init.py`, `resolver_home`.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py as _build_py

_RAIZ = Path(__file__).resolve().parent


def _empaquetar_home() -> None:
    """Llama a `tuku._pack` por ruta: en el build el paquete aún no es importable."""
    origen = _RAIZ / "src" / "tuku" / "_pack.py"
    spec = importlib.util.spec_from_file_location("_tuku_pack", origen)
    if spec is None or spec.loader is None:
        return
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    modulo.empaquetar(_RAIZ)


class build_py(_build_py):
    def finalize_options(self) -> None:
        _empaquetar_home()
        super().finalize_options()


setup(cmdclass={"build_py": build_py})
