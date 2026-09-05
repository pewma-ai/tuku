#!/usr/bin/env python3
"""Instalar una variante de template/ en un directorio, para probar un escenario.

Hace exactamente lo que describe template/README.md §"Instalar a mano":
copia la variante y siembra AHORA.md con los siete días reales del ciclo,
a partir de una fecha. `template/` solo guarda estructuras iniciales en
Markdown; este script es el mecanismo que las instala, y vive en src/
porque es código de TUKU, no contenido del template.

No depende de nada fuera de la librería estándar, a propósito: si algún día
deja de correr, la instalación a mano descrita en template/README.md sigue
siendo el camino.

Uso:
    python3 src/install_test_scenario.py --variante vanilla --destino /ruta/destino
    python3 src/install_test_scenario.py --variante vanilla --destino /ruta --desde 2026-09-01

--desde fija el lunes del primer ciclo. Por defecto, el lunes de esta semana.
Si el destino ya existe, se borra y se reinstala sin preguntar: es lo que
permite pisar un escenario de playground/ al recrearlo, a propósito.

Esta herramienta es para probar, no para un usuario final: no confirma nada
porque se invoca en automático, muchas veces, contra directorios desechables.
El instalador para un usuario final es install.sh, que sí pregunta antes de
sobrescribir si el destino ya tiene contenido.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import date, timedelta
from pathlib import Path

RAIZ_REPO = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = RAIZ_REPO / "template"

DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


def lunes_de_esta_semana(hoy: date) -> date:
    return hoy - timedelta(days=hoy.weekday())


def sembrar_ahora(contenido: str, desde: date) -> str:
    """Reemplaza los placeholders de AHORA.md por fechas reales.

    No interpreta el archivo como YAML ni como Markdown estructurado:
    reemplaza texto literal. Si el template cambia de forma, este script
    hay que actualizarlo con él, no al revés.
    """
    hasta = desde + timedelta(days=6)
    contenido = contenido.replace("desde: AAAA-MM-DD", f"desde: {desde.isoformat()}")
    contenido = contenido.replace("hasta: AAAA-MM-DD", f"hasta: {hasta.isoformat()}")
    for i, nombre_dia in enumerate(DIAS):
        fecha = desde + timedelta(days=i)
        placeholder = f"## {nombre_dia} DD de mes"
        real = f"## {nombre_dia} {fecha.day} de {MESES[fecha.month - 1]}"
        contenido = contenido.replace(placeholder, real)
    return contenido


def instalar(variante: str, destino: Path, desde: date) -> Path:
    variante_dir = TEMPLATE_DIR / variante
    if not variante_dir.is_dir():
        sys.exit(f"no existe la variante: {variante_dir}")

    if destino.exists():
        shutil.rmtree(destino)
    shutil.copytree(variante_dir, destino)

    ahora = destino / "AHORA.md"
    if ahora.exists():
        ahora.write_text(sembrar_ahora(ahora.read_text(encoding="utf-8"), desde), encoding="utf-8")

    return destino


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--variante", required=True, help="carpeta bajo template/, p.ej. vanilla")
    parser.add_argument("--destino", required=True, type=Path, help="directorio donde instalar")
    parser.add_argument(
        "--desde", type=date.fromisoformat, default=None,
        help="lunes del primer ciclo (AAAA-MM-DD). Por defecto, el lunes de esta semana.",
    )
    args = parser.parse_args()

    desde = args.desde or lunes_de_esta_semana(date.today())
    instalar(args.variante, args.destino, desde)
    print(f"instalado '{args.variante}' en {args.destino} (ciclo desde {desde.isoformat()})")


if __name__ == "__main__":
    main()
