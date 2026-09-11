"""tuku todo open / tuku todo close: las dos consecuencias deterministas.

Fase 2 de `devel/epics.md`. `**pendiente**` abre, `~~(Hecho)~~` cierra
(`spec/bitacora.md`). El cuerpo es el mismo texto en los tres lugares: el
registro que abre, la fila de `PENDIENTES.md` y el registro que cierra. **Abrir
es copiar, cerrar es encontrar y borrar.** Ninguna de las dos interpreta nada, y
por eso este paso no necesita LLM.

Operan **por registro**, no reconciliando el archivo. `PENDIENTES.md` es fuente
de verdad y no se regenera desde las bitácoras (`spec/pendientes.md`, regla 7):
un reconciliador borraría los pendientes abiertos en ciclos anteriores que el
`AHORA.md` en curso ya no menciona. La idempotencia se paga a mano: abrir
comprueba que la fila no esté, cerrar que la pareja exista.

El archivo es **una sola tabla**, `| Horizonte | Cuándo | Ámbito | Detalle |`.
El horizonte y la fecha son columnas y no estructura: bajar de escalón o agendar
mueve o edita una fila, y nunca crea ni destruye secciones.

**Qué lee y escribe:** las funciones de este módulo solo tocan `PENDIENTES.md`,
que es la fuente de verdad. La línea del registro llega como argumento; quien la
escribió en `AHORA.md` fue `tuku entry add`. El comando `tuku todo open` escribe
además las dos vistas derivadas, `AHORA.md` y `ambitos/PENDIENTES-AMBITOS.md`,
llamando a `tuku.propagate`; con `--no-propagate` no lo hace y el lote propaga
una sola vez al final.
**A mano:** agregar la fila con su horizonte, o borrarla al cerrarlo, y copiar
el pendiente bajo su día y en el callout de su ámbito.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from tuku.resultado import Resultado

ABRE = "**pendiente**"
CIERRA = "~~(Hecho)~~"

#: Un registro con marca de la ontología cerrada. La clasificación abierta que
#: puede venir después de la marca no participa: no cambia la consecuencia.
_REGISTRO = re.compile(
    r"^- \d{2}:\d{2} - "
    r"(?:\[\[(?P<ambito>[^\]\n]+)\]\] )?"
    r"(?P<marca>\*\*pendiente\*\*|~~\(Hecho\)~~)"
    r"(?: \*\*[^*\n]+\*\*)?"
    r": (?P<cuerpo>.+)$"
)

#: Una fila de la tabla: cuatro celdas. La cabecera y el separador tienen la
#: misma forma y se descartan aparte.
_FILA = re.compile(
    r"^\|(?P<horizonte>[^|\n]*)\|(?P<cuando>[^|\n]*)\|"
    r"(?P<ambito>[^|\n]*)\|(?P<cuerpo>[^|\n]*)\|\s*$"
)

_ENLACE = re.compile(r"^\[\[(?P<ambito>[^\]\n]+)\]\]$")

CABECERA = "| Horizonte | Cuándo | Ámbito | Detalle |"

#: La escalera del template vanilla, y solo el punto de partida: los escalones
#: son del autor y salen de `### Horizontes` en su libro de estilo
#: (`spec/pendientes.md`). Quien opera sobre un vault pasa la del autor con
#: `escalera_de`; esta queda como el valor por defecto de las funciones puras,
#: que no leen disco.
ESCALERA = (
    "esta semana",
    "próxima semana",
    "fin de mes",
    "con fecha",
)

ESTA_SEMANA = "esta semana"
CON_FECHA = "con fecha"


@dataclass(frozen=True)
class Marca:
    """Lo que una línea de bitácora le pide a `PENDIENTES.md`."""

    marca: str
    ambito: str | None
    cuerpo: str


@dataclass(frozen=True)
class Fila:
    """Una fila de la tabla de pendientes."""

    horizonte: str
    cuando: str
    ambito: str | None
    cuerpo: str

    def linea(self) -> str:
        ambito = f"[[{self.ambito}]]" if self.ambito else ""
        return f"| {self.horizonte} | {self.cuando} | {ambito} | {self.cuerpo} |"


class SinTabla(Exception):
    """`PENDIENTES.md` no tiene la tabla que la operación necesita."""


def slug(nombre: str) -> str:
    """El nombre sin acentos ni espacios: `próxima semana` → `proxima-semana`."""
    plano = unicodedata.normalize("NFKD", nombre.strip().lower())
    plano = "".join(c for c in plano if not unicodedata.combining(c))
    return re.sub(r"\s+", "-", plano)


def escalera_de(horizontes: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    """La escalera del autor: sus escalones más `con fecha`, que es del sistema.

    Si el libro de estilo no declara ninguno, queda la del template. El autor que
    renombra sus horizontes ("esta quincena", "este turno") tiene que seguir
    obteniendo el mismo orden en la tabla, y eso es lo que esta función sostiene:
    antes el orden salía de una constante y un escalón renombrado caía al final.
    """
    propios = tuple(h for h in horizontes if slug(h) != slug(CON_FECHA))
    return (*propios, CON_FECHA) if propios else ESCALERA


def canonico(horizonte: str, escalera: tuple[str, ...] = ESCALERA) -> str:
    """El horizonte tal como se escribe en la tabla, aceptando `proxima-semana`."""
    buscado = slug(horizonte)
    for nombre in escalera:
        if slug(nombre) == buscado:
            return nombre
    return horizonte.strip()


def parsear(linea: str) -> Marca | None:
    """La marca de la ontología cerrada de una línea, o `None` si no lleva.

    Estricta a propósito: `**Pendiente**` no es `**pendiente**` y acá no se
    reconoce, que es lo que `tuku entry lint` reporta por separado.
    """
    m = _REGISTRO.match(linea)
    if m is None:
        return None
    return Marca(m.group("marca"), m.group("ambito"), m.group("cuerpo"))


def _es_separador(linea: str) -> bool:
    return bool(linea.strip()) and set(linea.strip()) <= set("| -:")


def _parsear_fila(linea: str) -> Fila | None:
    """La fila de datos de una línea, o `None` si es cabecera, separador u otra cosa."""
    if _es_separador(linea):
        return None
    m = _FILA.match(linea)
    if m is None:
        return None
    horizonte = m.group("horizonte").strip()
    if horizonte == "Horizonte" and m.group("cuerpo").strip() == "Detalle":
        return None
    ambito = m.group("ambito").strip()
    enlace = _ENLACE.match(ambito)
    return Fila(
        horizonte,
        m.group("cuando").strip(),
        enlace.group("ambito") if enlace else None,
        m.group("cuerpo").strip(),
    )


def _rango_tabla(lineas: list[str]) -> tuple[int, int]:
    """Índices [inicio, fin) de las filas de datos, tras el separador de la tabla."""
    for i, linea in enumerate(lineas):
        if _es_separador(linea) and linea.strip().startswith("|"):
            fin = i + 1
            while fin < len(lineas) and _parsear_fila(lineas[fin]) is not None:
                fin += 1
            return i + 1, fin
    raise SinTabla(
        f"PENDIENTES.md no tiene la tabla de pendientes. "
        f"Agrégale la cabecera `{CABECERA}` y su separador."
    )


def filas(pendientes: str, horizonte: str | None = None) -> list[Fila]:
    """Las filas de la tabla, en el orden del archivo. Filtra por horizonte si se pide."""
    lineas = pendientes.splitlines()
    ini, fin = _rango_tabla(lineas)
    todas = [f for linea in lineas[ini:fin] if (f := _parsear_fila(linea))]
    if horizonte is None:
        return todas
    buscado = slug(horizonte)
    return [f for f in todas if slug(f.horizonte) == buscado]


def cuerpos(pendientes: str, horizonte: str | None = None) -> list[str]:
    """Los detalles de las filas, en orden."""
    return [f.cuerpo for f in filas(pendientes, horizonte)]


def _clave(fila: Fila, escalera: tuple[str, ...] = ESCALERA) -> tuple[int, str]:
    """Por dónde va la fila: escalón de la escalera, y dentro por fecha.

    Un horizonte que no está en la escalera va al final, y las filas sin fecha
    después de las fechadas del mismo escalón.
    """
    escalones = [slug(n) for n in escalera]
    propio = slug(fila.horizonte)
    orden = escalones.index(propio) if propio in escalones else len(escalones)
    return orden, fila.cuando or "9999-99-99"


def abrir(
    pendientes: str,
    marca: Marca,
    *,
    horizon: str = ESTA_SEMANA,
    horizonte: str | None = None,
    when: str = "",
    cuando: str | None = None,
    escalera: tuple[str, ...] = ESCALERA,
) -> str:
    """Copia el cuerpo del registro como fila. Idempotente.

    `spec/pendientes.md`: todo pendiente nuevo va a la tabla única de
    `PENDIENTES.md`, ordenado por escalón y por fecha.

    Si el detalle ya existe no duplica la fila: un registro repetido en la
    bitácora no abre dos veces el mismo pendiente.
    """
    dest_horizon = horizonte if horizonte is not None else horizon
    dest_when = cuando if cuando is not None else when
    fila = Fila(
        horizonte=canonico(dest_horizon, escalera),
        cuando=dest_when.strip(),
        ambito=marca.ambito,
        cuerpo=marca.cuerpo,
    )
    lineas = pendientes.splitlines()
    ini, fin = _rango_tabla(lineas)
    existentes = [f for linea in lineas[ini:fin] if (f := _parsear_fila(linea))]

    if fila in existentes:
        return pendientes

    clave = _clave(fila, escalera)
    desplazamiento = next(
        (i for i, f in enumerate(existentes) if _clave(f, escalera) > clave), len(existentes)
    )
    corte = ini + desplazamiento
    nuevas = [*lineas[:corte], fila.linea(), *lineas[corte:]]
    texto = "\n".join(nuevas)
    return texto + "\n" if pendientes.endswith("\n") else texto


def horizontes(pendientes: str) -> list[str]:
    """Los horizontes que aparecen en la tabla, sin repetir, en el orden del archivo."""
    vistos: list[str] = []
    for fila in filas(pendientes):
        if fila.horizonte not in vistos:
            vistos.append(fila.horizonte)
    return vistos


@dataclass(frozen=True)
class ConsecuenciaPendiente:
    """Una marca de la bitácora cuyo comando de consecuencia nunca se corrió."""

    cuerpo: str
    marca: str

    @property
    def comando(self) -> str:
        return "tuku todo open" if self.marca == ABRE else "tuku todo close"


def sin_consecuencia(ahora: str, pendientes: str) -> list[ConsecuenciaPendiente]:
    """Las marcas del ciclo en curso que la tabla no refleja.

    Es el modo de falla más caro del sistema y el único que no deja señal:
    `tuku entry add` escribe el registro y nada más, así que un `**pendiente**`
    cuyo `tuku todo open` no se corrió deja un archivo perfectamente bien formado
    al que le falta la mitad. Nada lo delata al leerlo; solo cruzando los dos
    archivos aparece.

    Dos casos, y ninguno mira `bitacoras/`: un pendiente que viene arrastrado de
    un ciclo anterior está en la tabla sin marca en `AHORA.md`, y eso es correcto.

    1. Un `**pendiente**` que no está en la tabla, salvo que el mismo ciclo lo
       cierre después: abrir y cerrar el mismo día no deja fila, y está bien.
    2. Un `~~(Hecho)~~` cuyo cuerpo sigue en la tabla.
    """
    marcas = [m for linea in ahora.splitlines() if (m := parsear(linea))]
    abiertos = [m.cuerpo for m in marcas if m.marca == ABRE]
    cerrados = {m.cuerpo for m in marcas if m.marca == CIERRA}
    en_tabla = set(cuerpos(pendientes))

    faltan = [
        ConsecuenciaPendiente(c, ABRE)
        for c in dict.fromkeys(abiertos)
        if c not in en_tabla and c not in cerrados
    ]
    faltan += [
        ConsecuenciaPendiente(m.cuerpo, CIERRA)
        for m in marcas
        if m.marca == CIERRA and m.cuerpo in en_tabla
    ]
    return faltan


def duplicados(pendientes: str) -> list[str]:
    """Detalles que aparecen en más de una fila. Regla 1 de `spec/pendientes.md`.

    Es lo que reporta `tuku todo lint`: un pendiente está en exactamente una
    fila, siempre. La misma tarea en dos horizontes es el error que el vault
    real tuvo que prohibir por escrito.
    """
    vistos: dict[str, int] = {}
    for fila in filas(pendientes):
        vistos[fila.cuerpo] = vistos.get(fila.cuerpo, 0) + 1
    return [cuerpo for cuerpo, veces in vistos.items() if veces > 1]


def cerrar(pendientes: str, marca: Marca) -> tuple[str, bool]:
    """Borra la fila cuyo detalle coincide. Devuelve el texto y si hubo pareja.

    El emparejamiento es **literal**: el cierre repite el texto del pendiente en
    vez de reescribirlo, y por eso encontrarlo no necesita juicio. Sin pareja no
    se inventa nada: se devuelve el texto intacto y `False`, y quien invoca lo
    reporta. Con `PENDIENTES.md` como fuente de verdad, un cierre inventado deja
    el archivo mintiendo.
    """
    lineas = pendientes.splitlines()
    for i, linea in enumerate(lineas):
        f = _parsear_fila(linea)
        if f is not None and f.cuerpo == marca.cuerpo:
            restantes = [*lineas[:i], *lineas[i + 1 :]]
            texto = "\n".join(restantes)
            return (texto + "\n" if pendientes.endswith("\n") else texto), True
    return pendientes, False


def abrir_en_vault(
    vault: Path,
    *,
    body: str,
    scope: str | None = None,
    horizon: str = ESTA_SEMANA,
    when: str = "",
    propagate: bool = True,
    record: bool = True,
    day: date | None = None,
    hour: str | None = None,
) -> Resultado:
    """Abre un pendiente, estampa huella en la bitácora y propaga las vistas.

    Recibe los campos, no la línea del registro: abrir **es** el pendiente, y la
    marca la lleva implícita el verbo. Normalmente lo llama `tuku entry add` al
    ver un `**pendiente**` (con `record=False` porque el registro ya se escribió);
    como comando directo estampa además la constancia cronológica en `AHORA.md`
    (`spec/pendientes.md`, regla de huella obligatoria).

    Propagar es parte de abrir: si la vista quedara para un segundo comando, el
    pendiente existiría sin aparecer en su día, que es la falla silenciosa que
    `spec/pendientes.md` persigue. `propagate=False` es la escotilla del lote,
    que propaga una sola vez al final.
    """
    from tuku.ahora import encabezado_de
    from tuku.config import archivo_vault, leer_config
    from tuku.entry import add as entry_add
    from tuku.entry import componer
    from tuku.propagate import propagar

    limpio_scope = scope.strip().strip("[]") if scope else None
    marca = Marca(ABRE, limpio_scope, body.strip())
    escalera = escalera_de(leer_config(vault).horizontes)
    if when.strip() and horizon == ESTA_SEMANA:
        horizon = CON_FECHA
    horizon = canonico(horizon, escalera)

    if record:
        ahora_path = archivo_vault(vault, "AHORA.md")
        ahora_actual = ahora_path.read_text(encoding="utf-8")
        ya_abierto = any(
            (m := parsear(lin)) is not None and m.marca == ABRE and m.cuerpo == marca.cuerpo
            for lin in ahora_actual.splitlines()
        )
        if not ya_abierto:
            dia_encabezado = encabezado_de(day or date.today())
            hora = hour or datetime.now().strftime("%H:%M")
            linea = componer(hora=hora, scope=limpio_scope, body=f"{ABRE}: {marca.cuerpo}")
            try:
                ahora_texto = entry_add(ahora_actual, [linea], day=dia_encabezado)
                ahora_path.write_text(ahora_texto, encoding="utf-8")
            except ValueError as e:
                return Resultado.rechazo(str(e))

    ruta = archivo_vault(vault, "PENDIENTES.md")
    ruta.write_text(
        abrir(
            ruta.read_text(encoding="utf-8"),
            marca,
            horizon=horizon,
            when=when,
            escalera=escalera,
        ),
        encoding="utf-8",
    )
    if record:
        from tuku import scope as ambitos

        for amb in ambitos.leer(vault):
            ambitos.actualizar_pagina(vault, amb.nombre)
    if propagate:
        propagar(vault)
    return Resultado.hecho(f"pendiente abierto en «{horizon}»: {marca.cuerpo}")


def cerrar_en_vault(
    vault: Path,
    *,
    body: str,
    propagate: bool = True,
    record: bool = True,
    day: date | None = None,
    hour: str | None = None,
    scope: str | None = None,
) -> Resultado:
    """Cierra un pendiente por su cuerpo, estampando su huella en la bitácora.

    Un cierre sin pareja **no es un fallo**: es el caso normal del día uno
    (`devel/epics.md`). Se reporta, el registro queda escrito y `PENDIENTES.md`
    no se toca, porque inventar el pendiente que falta dejaría el archivo
    mintiendo.
    """
    from tuku.ahora import encabezado_de
    from tuku.config import archivo_vault
    from tuku.entry import add as entry_add
    from tuku.entry import componer
    from tuku.propagate import propagar

    marca = Marca(CIERRA, None, body.strip())
    ruta = archivo_vault(vault, "PENDIENTES.md")
    pendientes_texto = ruta.read_text(encoding="utf-8")

    ambito_encontrado: str | None = None
    for f in filas(pendientes_texto):
        if f.cuerpo == marca.cuerpo:
            ambito_encontrado = f.ambito
            break

    texto, hubo_pareja = cerrar(pendientes_texto, marca)
    if hubo_pareja:
        ruta.write_text(texto, encoding="utf-8")

    if record:
        ahora_path = archivo_vault(vault, "AHORA.md")
        ahora_actual = ahora_path.read_text(encoding="utf-8")
        ya_cerrado = any(
            (m := parsear(lin)) is not None and m.marca == CIERRA and m.cuerpo == marca.cuerpo
            for lin in ahora_actual.splitlines()
        )
        if not ya_cerrado:
            ambito_final = scope if scope is not None else ambito_encontrado
            dia_encabezado = encabezado_de(day or date.today())
            hora = hour or datetime.now().strftime("%H:%M")
            linea = componer(hora=hora, scope=ambito_final, body=f"{CIERRA}: {marca.cuerpo}")
            try:
                ahora_texto = entry_add(ahora_actual, [linea], day=dia_encabezado)
                ahora_path.write_text(ahora_texto, encoding="utf-8")
            except ValueError as e:
                return Resultado.rechazo(str(e))

    if record:
        from tuku import scope as ambitos

        for amb in ambitos.leer(vault):
            ambitos.actualizar_pagina(vault, amb.nombre)

    if propagate:
        propagar(vault)

    if not hubo_pareja:
        return Resultado.hecho(
            f"no había ningún pendiente abierto con el cuerpo {marca.cuerpo!r}, "
            f"así que no se borró nada. El registro queda escrito. Si esperabas "
            f"cerrarlo, revisa que el texto coincida palabra por palabra."
        )
    return Resultado.hecho(f"pendiente cerrado: {marca.cuerpo}")


def propagar_vistas(vault: Path) -> Resultado:
    """Regenera las vistas derivadas de `PENDIENTES.md`."""
    from tuku.propagate import propagar

    cambiados = propagar(vault)
    if not cambiados:
        return Resultado.hecho("las vistas ya estaban al día.")
    return Resultado.hecho("\n".join(f"regenerado: {ruta}" for ruta in cambiados))


def lint_del_vault(vault: Path) -> Resultado:
    """Revisa los pendientes y reporta; no escribe."""
    from tuku.config import archivo_vault

    pendientes = archivo_vault(vault, "PENDIENTES.md").read_text(encoding="utf-8")
    repetidos = duplicados(pendientes)
    if not repetidos:
        return Resultado.hecho("sin hallazgos.")
    lineas = [
        f"PENDIENTES.md: error: {cuerpo!r} aparece en más de una fila. "
        f"Déjalo en una sola: un pendiente está en exactamente un horizonte."
        for cuerpo in repetidos
    ]
    return Resultado.rechazo("\n".join([*lineas, f"{len(repetidos)} error(es)."]), error=False)
