"""tuku process: las rutinas con nombre del vault.

Hay dos clases (`spec/despacho.md`): las de `tuku`, deterministas, que corren
como comando (`tuku process cycle`), y las que el autor escribe en `procesos/`,
que el agente ejecuta leyendo su archivo. `tuku process` sin nombre lista las
dos.

**A mano:** mirar la lista de abajo y los archivos de `procesos/`.
"""

from __future__ import annotations

from pathlib import Path

from tuku import archivo
from tuku.resultado import Resultado

#: Los procesos de `tuku`: su nombre y qué hacen.
DE_TUKU = {
    "cycle": "abre en AHORA.md la semana que contiene --at, desde reglas/plantilla/AHORA.md",
}


def _titulo(ruta: Path) -> str:
    """El primer encabezado del archivo, o su nombre si no tiene."""
    for linea in archivo.leer(ruta).splitlines():
        if linea.startswith("# "):
            return linea.removeprefix("# ").strip()
    return ruta.stem


def listar(vault: Path) -> Resultado:
    """Los procesos de `tuku` y los de `procesos/`, cada uno con lo que hace."""
    lineas = ["De tuku, se corren con `tuku process NOMBRE`:"]
    lineas += [f"- {nombre}: {que}" for nombre, que in DE_TUKU.items()]
    carpeta = vault / "procesos"
    propios = sorted(carpeta.glob("*.md")) if carpeta.is_dir() else []
    lineas += ["", "Del autor, en procesos/, se ejecutan leyendo su archivo:"]
    lineas += [f"- procesos/{r.name}: {_titulo(r)}" for r in propios] or ["- ninguno todavía."]
    return Resultado.hecho("\n".join(lineas))
