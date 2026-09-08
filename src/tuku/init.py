"""tuku init: siembra un vault nuevo copiando una variante de `template/`.

Reemplaza a `install.sh` y a `src/install_test_scenario.py`. Copia
`<TUKU_HOME>/template/<variante>` al destino y resuelve las fechas del primer
ciclo en `AHORA.md`. **No toca la red:** es copia de archivos y nada más.

`TUKU_HOME` es el árbol de TUKU instalado. Se resuelve, en este orden:

1. el argumento `home=` (lo usan los tests, que apuntan al checkout de trabajo);
2. la variable de entorno `TUKU_HOME`;
3. `~/.tuku`, si ya existe y contiene `template/`;
4. los datos que el wheel trae empaquetados en `tuku/_home/` (una instalación
   por `pipx` / `uv tool install`). La primera vez que se siembra desde ahí, el
   árbol se copia a `~/.tuku`, para que quede a la vista y editable;
5. la raíz del checkout, subiendo desde este archivo (desarrollo sin instalar).

La lógica vive acá y es importable; `tuku/cli.py` es una capa fina de argparse
encima. Los tests llaman a `init()` directo, sin subprocesos.
"""

from __future__ import annotations

import os
import shutil
from datetime import date, timedelta
from pathlib import Path

_PAQUETE = Path(__file__).resolve().parent
_HOME_EMPAQUETADO = _PAQUETE / "_home"

#: El template escribe los siete encabezados en el orden fijo Lunes..Domingo;
#: `DIAS[i]` localiza el placeholder i-ésimo. El nombre real de cada día sale de
#: `fecha.weekday()`, no de esa posición: si `desde` no es lunes, ambos difieren
#: a propósito. Nada en `spec/` obliga a que un ciclo semanal empiece en lunes.
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]

_MARCADOR_AUTOR = "**Nombre del autor:**"


class DestinoNoVacio(Exception):
    """El directorio destino ya tiene contenido y no se pidió `force`."""


class TukuHomeInvalido(Exception):
    """No se encontró un árbol de TUKU con `template/` en ninguna ubicación."""


class MarcadorAutorFaltante(Exception):
    """No se encontró el marcador del autor en LIBRO-DE-ESTILO.md."""


def _tiene_template(p: Path) -> bool:
    return (p / "template").is_dir()


def _raiz_checkout() -> Path | None:
    """La raíz del repositorio, subiendo desde este archivo. `None` si no está."""
    for ancestro in _PAQUETE.parents:
        if (ancestro / "template").is_dir() and (ancestro / "pyproject.toml").is_file():
            return ancestro
    return None


def resolver_home(home: Path | str | None = None) -> Path:
    """Devuelve el árbol de TUKU instalado, según la cascada del módulo.

    Si la única fuente disponible es la copia empaquetada en el wheel y `~/.tuku`
    todavía no existe, la copia se materializa ahí y se devuelve esa ruta: es la
    forma de que `~/.tuku` quede poblado tras un `pipx install`, sin red.
    """
    if home is not None:
        h = Path(home).expanduser()
        if not _tiene_template(h):
            raise TukuHomeInvalido(f"{h} no contiene template/")
        return h

    entorno = os.environ.get("TUKU_HOME")
    if entorno:
        h = Path(entorno).expanduser()
        if not _tiene_template(h):
            raise TukuHomeInvalido(f"TUKU_HOME={h} no contiene template/")
        return h

    predeterminado = Path("~/.tuku").expanduser()
    if _tiene_template(predeterminado):
        return predeterminado

    if _tiene_template(_HOME_EMPAQUETADO):
        if not predeterminado.exists():
            shutil.copytree(_HOME_EMPAQUETADO, predeterminado)
            return predeterminado
        return _HOME_EMPAQUETADO

    raiz = _raiz_checkout()
    if raiz is not None:
        return raiz

    raise TukuHomeInvalido(
        "no se encontró un árbol de TUKU: ni el argumento home, ni TUKU_HOME, ni "
        "~/.tuku, ni una copia empaquetada, ni un checkout. ¿Instalaste con "
        "`pipx install` / `uv tool install`?"
    )


def lunes_de_esta_semana(hoy: date) -> date:
    return hoy - timedelta(days=hoy.weekday())


def _sembrar_ahora(contenido: str, desde: date) -> str:
    """Reemplaza los placeholders de `AHORA.md` por fechas reales.

    Soporta plantillas con día inicial y final, y plantillas completas de 7 días.
    """
    hasta = desde + timedelta(days=6)
    dia_inicio = f"## {DIAS[desde.weekday()]} {desde.day} de {MESES[desde.month - 1]}"
    dia_fin = f"## {DIAS[hasta.weekday()]} {hasta.day} de {MESES[hasta.month - 1]}"

    contenido = contenido.replace("desde: AAAA-MM-DD", f"desde: {desde.isoformat()}")
    contenido = contenido.replace("hasta: AAAA-MM-DD", f"hasta: {hasta.isoformat()}")

    solo_extremos = (
        "## Lunes DD de mes" in contenido
        and "## Domingo DD de mes" in contenido
        and "## Martes DD de mes" not in contenido
    )
    if solo_extremos:
        contenido = contenido.replace("## Lunes DD de mes", dia_inicio)
        contenido = contenido.replace("## Domingo DD de mes", dia_fin)
    else:
        for i in range(7):
            fecha = desde + timedelta(days=i)
            placeholder = f"## {DIAS[i]} DD de mes"
            real = f"## {DIAS[fecha.weekday()]} {fecha.day} de {MESES[fecha.month - 1]}"
            contenido = contenido.replace(placeholder, real)
    return contenido



def _sembrar_autor(destino: Path, autor: str) -> None:
    """Escribe el nombre del autor en `LIBRO-DE-ESTILO.md` del vault sembrado.

    Calza por prefijo de línea, no por la oración entera: lo que el template pone
    tras la etiqueta ("por declarar...") es prosa que puede cambiar sin que esto
    deje de funcionar.
    """
    libro = destino / "LIBRO-DE-ESTILO.md"
    lineas = libro.read_text(encoding="utf-8").splitlines(keepends=True)
    for i, linea in enumerate(lineas):
        if linea.lstrip().startswith(_MARCADOR_AUTOR):
            fin = "\n" if linea.endswith("\n") else ""
            lineas[i] = f"{_MARCADOR_AUTOR} {autor}{fin}"
            libro.write_text("".join(lineas), encoding="utf-8")
            return
    raise MarcadorAutorFaltante(
        f"no se encontró la línea '{_MARCADOR_AUTOR}' en {libro}: "
        "agrégalo en la sección '## El autor'."
    )


def init(
    destino: Path | str,
    *,
    variante: str = "vanilla",
    autor: str | None = None,
    desde: date | None = None,
    force: bool = False,
    home: Path | str | None = None,
) -> Path:
    """Siembra un vault de la `variante` en `destino` y devuelve su ruta.

    Sembrar en un directorio que ya tiene contenido se rechaza con
    `DestinoNoVacio`, salvo `force=True`, que lo reemplaza entero. `desde` fija
    el primer día del ciclo (por defecto, el lunes de esta semana). `autor`, si
    se pasa y no viene vacío, se escribe en `LIBRO-DE-ESTILO.md`.
    """
    destino = Path(destino).expanduser()
    home_dir = resolver_home(home)
    variante_dir = home_dir / "template" / variante
    if not variante_dir.is_dir():
        raise TukuHomeInvalido(
            f"no existe la variante {variante!r} en {home_dir / 'template'}"
        )

    if destino.exists() and any(destino.iterdir()):
        if not force:
            raise DestinoNoVacio(
                f"{destino} ya tiene contenido. Usa `tuku init --force` para "
                "reemplazarlo."
            )
        shutil.rmtree(destino)

    shutil.copytree(variante_dir, destino, dirs_exist_ok=True)

    desde = desde or lunes_de_esta_semana(date.today())
    ahora = destino / "AHORA.md"
    plantilla_ahora = destino / "reglas" / "plantilla" / "AHORA.md"
    if plantilla_ahora.is_file():
        ahora.write_text(
            _sembrar_ahora(plantilla_ahora.read_text(encoding="utf-8"), desde), encoding="utf-8"
        )
    elif ahora.exists():
        ahora.write_text(
            _sembrar_ahora(ahora.read_text(encoding="utf-8"), desde), encoding="utf-8"
        )


    if autor and autor.strip():
        _sembrar_autor(destino, autor.strip())

    return destino
