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
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
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


#: Lo que la plantilla deja para que la instalación ponga la zona real.
_PLACEHOLDER_TZ = "TZ-DEL-SISTEMA"

#: Cuando el sistema no dice cuál es su zona. No es una elección: es lo único
#: que no miente. El autor la corrige en `reglas/config.tuku.md`.
TZ_FALLBACK = "UTC"


def tz_del_sistema() -> str:
    """El nombre IANA de la zona horaria de esta máquina, o `TZ_FALLBACK`.

    Se lee del entorno y del sistema de archivos, sin dependencias externas:
    `TZ` si está puesta, el destino del symlink `/etc/localtime` (macOS y la
    mayoría de los Linux) y `/etc/timezone` (Debian). `datetime.astimezone()`
    no sirve, porque da la abreviatura local (`CLT`) y no el nombre IANA.
    """
    entorno = os.environ.get("TZ", "").strip()
    if entorno:
        return entorno

    localtime = Path("/etc/localtime")
    if localtime.is_symlink():
        partes = localtime.resolve().parts
        if "zoneinfo" in partes:
            corte = len(partes) - 1 - partes[::-1].index("zoneinfo")
            zona = "/".join(partes[corte + 1 :])
            if zona:
                return zona

    debian = Path("/etc/timezone")
    if debian.is_file():
        zona = debian.read_text(encoding="utf-8").strip()
        if zona:
            return zona

    return TZ_FALLBACK


def _sembrar_tz(destino: Path) -> None:
    """Pone la zona horaria de esta máquina en `reglas/config.tuku.md`."""
    config = destino / "reglas" / "config.tuku.md"
    if not config.is_file():
        return
    contenido = config.read_text(encoding="utf-8")
    if _PLACEHOLDER_TZ not in contenido:
        return
    config.write_text(contenido.replace(_PLACEHOLDER_TZ, tz_del_sistema()), encoding="utf-8")


def lunes_de_esta_semana(hoy: date) -> date:
    return hoy - timedelta(days=hoy.weekday())


def _sembrar_ahora(contenido: str, desde: date) -> str:
    """Reemplaza los placeholders de `AHORA.md` por fechas reales.

    Soporta plantillas con día inicial y final, y plantillas completas de 7 días.
    """
    hasta = desde + timedelta(days=6)
    dia_inicio = f"## {DIAS[desde.weekday()]} {desde.day} de {MESES[desde.month - 1]}"
    dia_fin = f"## {DIAS[hasta.weekday()]} {hasta.day} de {MESES[hasta.month - 1]}"

    contenido = contenido.replace("from: AAAA-MM-DD", f"from: {desde.isoformat()}")
    contenido = contenido.replace("to: AAAA-MM-DD", f"to: {hasta.isoformat()}")

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
    variant: str = "vanilla",
    variante: str | None = None,
    author: str | None = None,
    autor: str | None = None,
    desde: date | None = None,
    force: bool = False,
    home: Path | str | None = None,
) -> Path:
    """Siembra un vault de la `variant` en `destino` y devuelve su ruta.

    Sembrar en un directorio que ya tiene contenido se rechaza con
    `DestinoNoVacio`, salvo `force=True`, que lo reemplaza entero. `desde` fija
    el primer día del ciclo (por defecto, el lunes de esta semana). `author`, si
    se pasa y no viene vacío, se escribe en `LIBRO-DE-ESTILO.md`.
    """
    valor_variante = variante if variante is not None else variant
    valor_autor = autor if autor is not None else author
    destino = Path(destino).expanduser()
    home_dir = resolver_home(home)
    variante_dir = home_dir / "template" / valor_variante
    if not variante_dir.is_dir():
        raise TukuHomeInvalido(
            f"no existe la variante {valor_variante!r} en {home_dir / 'template'}"
        )

    if destino.exists() and any(destino.iterdir()):
        if not force:
            raise DestinoNoVacio(
                f"{destino} ya tiene contenido. Usa `tuku init --force` para reemplazarlo."
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

    _sembrar_tz(destino)

    if valor_autor and valor_autor.strip():
        _sembrar_autor(destino, valor_autor.strip())

    return destino
