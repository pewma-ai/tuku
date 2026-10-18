"""tuku cycle: apertura y gestión de ciclos en AHORA.md.

`tuku process cycle` verifica si hay un `AHORA.md` abierto para la fecha deseada;
si no lo hay, lo crea a partir de la plantilla en `reglas/plantilla/AHORA.md`
con la semana completa (de lunes a domingo). Si ya cubre la fecha, no lo
modifica (idempotente).

Si hay una bitácora anterior en `bitacoras/`, el ciclo nuevo abre además el
pendiente `revisar la bitácora anterior`, con vencimiento el primer día: revisar
lo vivido antes de planificar lo que viene es lo que fuerza el aprendizaje.

**Qué lee y escribe:** lee `reglas/plantilla/AHORA.md` y `bitacoras/`, lee y
escribe `AHORA.md`, y escribe `PENDIENTES.md` y sus vistas.
**A mano:** copiar `reglas/plantilla/AHORA.md` a `AHORA.md` y sustituir las fechas
del frontmatter y de los encabezados de los días; con una bitácora anterior,
abrir `revisar la bitácora anterior` con `tuku todo open --due <el lunes>`.
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from tuku import archivo
from tuku.ahora import como_cerrar, rango
from tuku.config import resolver_plantilla_ahora
from tuku.init import DIAS, MESES
from tuku.resultado import Resultado

#: El pendiente con que abre todo ciclo que viene después de otro.
REVISAR_BITACORA = "revisar la bitácora anterior"


def calcular_rango_semanal(fecha: date) -> tuple[date, date]:
    """Calcula el rango [lunes, domingo] de la semana que contiene `fecha`."""
    lunes = fecha - timedelta(days=fecha.weekday())
    domingo = lunes + timedelta(days=6)
    return lunes, domingo


def sembrar_ahora(plantilla: str, desde: date) -> str:
    """Instancia la plantilla de AHORA.md para el ciclo semanal que comienza en `desde`."""
    hasta = desde + timedelta(days=6)
    contenido = plantilla.replace("from: AAAA-MM-DD", f"from: {desde.isoformat()}")
    contenido = contenido.replace("to: AAAA-MM-DD", f"to: {hasta.isoformat()}")

    for i in range(7):
        d = desde + timedelta(days=i)
        placeholder = f"## {DIAS[i]} DD de mes"
        real = f"## {DIAS[d.weekday()]} {d.day} de {MESES[d.month - 1]}"
        contenido = contenido.replace(placeholder, real)

    return contenido


def resolver_plantilla(vault: Path) -> str:
    """Busca la plantilla de AHORA.md en el vault o en el fallback de TUKU."""
    return resolver_plantilla_ahora(vault)


class CicloEnCurso(Exception):
    """Hay un ciclo abierto con registros y `fecha` cae fuera de él."""


def tiene_registros(ahora: str) -> bool:
    """Si el ciclo tiene algún registro escrito, con hora o sin ella."""
    from tuku.entry import registros

    return bool(registros(ahora))


def open_cycle(vault: Path, fecha: date | None = None) -> tuple[Path, bool]:
    """Verifica si `AHORA.md` cubre `fecha`; si no, lo crea desde la plantilla.

    Devuelve la ruta a `AHORA.md` y un booleano indicando si fue creado (`True`)
    o si ya existía cubriendo la fecha (`False`).

    Una fecha anterior al ciclo abierto se rechaza siempre con `CicloEnCurso`: un
    ciclo no se abre hacia atrás. Abrir un ciclo nuevo mientras hay otro **con
    registros** también se rechaza. Antes esto pisaba el archivo y los registros del ciclo
    anterior se perdían sin dejar rastro: `AHORA.md` es del conjunto canónico y
    nada lo sobreescribe sin aprobación (principio 3). Un ciclo vacío sí se
    regenera, porque no hay nada que perder.
    """
    vault = Path(vault)
    fecha = fecha or date.today()
    ahora_path = vault / "AHORA.md"

    if ahora_path.is_file():
        contenido = archivo.leer(ahora_path)
        limites = rango(contenido)
        if limites is not None:
            desde, hasta = limites
            if desde <= fecha <= hasta:
                return ahora_path, False
            if fecha < desde:
                raise CicloEnCurso(
                    f"un ciclo no se abre hacia atrás: AHORA.md va del {desde.isoformat()} "
                    f"al {hasta.isoformat()} y {fecha.isoformat()} es anterior. Revisa la "
                    "fecha de --at; lo de una semana ya cerrada va a mano en su bitácora."
                )
            if tiene_registros(contenido):
                raise CicloEnCurso(
                    f"hay un ciclo abierto con registros ({desde.isoformat()} a "
                    f"{hasta.isoformat()}) y {fecha.isoformat()} cae fuera. "
                    f"Ciérralo antes: {como_cerrar(desde, hasta)}, "
                    "y vuelve a correr esto."
                )

    desde, _ = calcular_rango_semanal(fecha)
    plantilla = resolver_plantilla(vault)
    contenido = sembrar_ahora(plantilla, desde)
    archivo.escribir(ahora_path, contenido)
    return ahora_path, True


def hay_bitacora_anterior(vault: Path) -> bool:
    """Si el autor ya cerró algún ciclo: `bitacoras/` tiene una bitácora."""
    return any((vault / "bitacoras").glob("bitacora-*.md"))


def abrir_en_vault(vault: Path, fecha: date | None = None) -> Resultado:
    """Abre el ciclo en `AHORA.md`, o confirma que ya cubre la fecha.

    Un ciclo nuevo que sigue a una bitácora cerrada abre el pendiente de
    revisarla, con vencimiento el primer día. Si ese pendiente no se puede abrir,
    el ciclo queda abierto y el motivo sale como aviso.
    """
    from tuku import todo

    try:
        ahora_path, creado = open_cycle(vault, fecha)
    except CicloEnCurso as e:
        return Resultado.rechazo(str(e))
    if not creado:
        return Resultado.hecho("AHORA.md ya cubre la fecha requerida.")
    mensaje = f"ciclo abierto en {ahora_path}."
    if not hay_bitacora_anterior(vault):
        return Resultado.hecho(mensaje)

    limites = rango(archivo.leer(ahora_path))
    desde = limites[0] if limites else calcular_rango_semanal(fecha or date.today())[0]
    apertura = todo.abrir_en_vault(
        vault, body=REVISAR_BITACORA, due=desde.isoformat(), day=fecha or date.today()
    )
    if not apertura.ok:
        return Resultado.hecho(
            mensaje, avisos=(f"no se abrió «{REVISAR_BITACORA}»: {apertura.mensaje}",)
        )
    return Resultado.hecho(f"{mensaje}\n{apertura.mensaje}", avisos=apertura.avisos)
