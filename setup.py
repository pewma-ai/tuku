"""Puente de build: empaqueta `template/` dentro del wheel.

`pyproject.toml` define el proyecto; esto solo agrega un paso al build. Un
`pipx install` / `uv tool install` construye el wheel y descarta el clon del
repositorio, así que el árbol que `tuku init` necesita (hoy, solo `template/`)
tiene que viajar dentro del paquete. Se copia a `src/tuku/_home/` antes de que
setuptools recolecte `package-data`.

En el checkout de trabajo ese directorio no existe (está en `.gitignore`) y
`tuku.init` cae a la raíz del repositorio. Ver `src/tuku/init.py`, `resolver_home`.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py as _build_py

_RAIZ = Path(__file__).resolve().parent
_DESTINO_HOME = _RAIZ / "src" / "tuku" / "_home"


def _empaquetar_home() -> None:
    origen = _RAIZ / "template"
    if not origen.is_dir():
        return
    if _DESTINO_HOME.exists():
        shutil.rmtree(_DESTINO_HOME)
    _DESTINO_HOME.mkdir(parents=True)
    shutil.copytree(origen, _DESTINO_HOME / "template")


class build_py(_build_py):
    def finalize_options(self) -> None:
        _empaquetar_home()
        super().finalize_options()


setup(cmdclass={"build_py": build_py})
