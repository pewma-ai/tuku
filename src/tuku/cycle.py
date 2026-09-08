"""tuku cycle: apertura y gestión de ciclos en AHORA.md.

`tuku cycle open` verifica si hay un `AHORA.md` abierto para la fecha deseada;
si no lo hay, lo crea a partir de la plantilla en `reglas/plantilla/AHORA.md`
con la semana completa (de lunes a domingo). Si ya cubre la fecha, no lo
modifica (idempotente).

**Qué lee y escribe:** lee `reglas/plantilla/AHORA.md`, lee y escribe `AHORA.md`.
**A mano:** copiar `reglas/plantilla/AHORA.md` a `AHORA.md` y sustituir las fechas
del frontmatter y de los encabezados de los días.
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from tuku.ahora import rango
from tuku.config import resolver_plantilla_ahora
from tuku.init import DIAS, MESES


def calcular_rango_semanal(fecha: date) -> tuple[date, date]:
    """Calcula el rango [lunes, domingo] de la semana que contiene `fecha`."""
    lunes = fecha - timedelta(days=fecha.weekday())
    domingo = lunes + timedelta(days=6)
    return lunes, domingo


def sembrar_ahora(plantilla: str, desde: date) -> str:
    """Instancia la plantilla de AHORA.md para el ciclo semanal que comienza en `desde`."""
    hasta = desde + timedelta(days=6)
    contenido = plantilla.replace("desde: AAAA-MM-DD", f"desde: {desde.isoformat()}")
    contenido = contenido.replace("hasta: AAAA-MM-DD", f"hasta: {hasta.isoformat()}")

    for i in range(7):
        d = desde + timedelta(days=i)
        placeholder = f"## {DIAS[i]} DD de mes"
        real = f"## {DIAS[d.weekday()]} {d.day} de {MESES[d.month - 1]}"
        contenido = contenido.replace(placeholder, real)

    return contenido


def resolver_plantilla(vault: Path) -> str:
    """Busca la plantilla de AHORA.md en el vault o en el fallback de TUKU."""
    return resolver_plantilla_ahora(vault)


def open_cycle(vault: Path, fecha: date | None = None) -> tuple[Path, bool]:
    """Verifica si `AHORA.md` cubre `fecha`; si no, lo crea desde la plantilla.

    Devuelve la ruta a `AHORA.md` y un booleano indicando si fue creado (`True`)
    o si ya existía cubriendo la fecha (`False`).
    """
    vault = Path(vault)
    fecha = fecha or date.today()
    ahora_path = vault / "AHORA.md"

    if ahora_path.is_file():
        limites = rango(ahora_path.read_text(encoding="utf-8"))
        if limites is not None:
            desde, hasta = limites
            if desde <= fecha <= hasta:
                return ahora_path, False

    desde, _ = calcular_rango_semanal(fecha)
    plantilla = resolver_plantilla(vault)
    contenido = sembrar_ahora(plantilla, desde)
    ahora_path.write_text(contenido, encoding="utf-8")
    return ahora_path, True
