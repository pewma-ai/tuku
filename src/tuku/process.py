"""tuku process: las rutinas con nombre del vault.

Las que el autor escribe en `procesos/` las ejecuta el agente leyendo su archivo.
`tuku` no trae ninguna propia que corra como comando; si algún día las trae,
`tuku process` sin nombre las lista junto a las del autor.

**A mano:** mirar los archivos de `procesos/`.
"""

from __future__ import annotations

from pathlib import Path

from tuku import archivo
from tuku.resultado import Resultado

#: Los procesos de `tuku` que corren como comando, con lo que hacen. Hoy ninguno.
DE_TUKU: dict[str, str] = {}


def _titulo(ruta: Path) -> str:
    """El primer encabezado del archivo, o su nombre si no tiene."""
    for linea in archivo.leer(ruta).splitlines():
        if linea.startswith("# "):
            return linea.removeprefix("# ").strip()
    return ruta.stem


def listar(vault: Path) -> Resultado:
    """Los procesos de `tuku`, si los hay, y los de `procesos/`, cada uno con lo que hace."""
    lineas: list[str] = []
    if DE_TUKU:
        lineas += ["De tuku, se corren con `tuku process NOMBRE`:"]
        lineas += [f"- {nombre}: {que}" for nombre, que in DE_TUKU.items()]
        lineas += [""]
    carpeta = vault / "procesos"
    propios = sorted(carpeta.glob("*.md")) if carpeta.is_dir() else []
    lineas += ["Del autor, en procesos/, se ejecutan leyendo su archivo:"]
    lineas += [f"- procesos/{r.name}: {_titulo(r)}" for r in propios] or ["- ninguno todavía."]
    return Resultado.hecho("\n".join(lineas))
