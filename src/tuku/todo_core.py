"""El núcleo de `todo`: marcas, tabla de `PENDIENTES.md` y su lint, en texto.

Funciones puras de texto a texto: no leen disco ni el reloj. `todo` las reexporta
junto a los casos de uso `abrir_en_vault` y `cerrar_en_vault`, que son los que
leen, escriben y regeneran (`spec/pendientes.md`).
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date

from tuku import link

ABRE = "**pendiente**"


CIERRA = "(Hecho)"


#: Un registro con marca de la ontología cerrada. La clasificación abierta que
#: puede venir después de la marca no participa: no cambia la consecuencia.
_REGISTRO = re.compile(
    r"^- (?:\d{2}:\d{2} - )?"
    rf"(?:(?P<ambito>{link.ENLACE}) )?"
    r"(?P<marca>\*\*pendiente\*\*|\(Hecho\))"
    r"(?: \*\*[^*\n]+\*\*)?"
    r": (?P<cuerpo>.+)$"
)


#: Un cierre tal como llega por `--body`, con o sin clasificación abierta y con
#: el cuerpo tachado o sin tachar.
_CIERRE_ENTRADA = re.compile(r"^\(Hecho\)(?P<clasif> \*\*[^*\n]+\*\*)?: (?P<cuerpo>.+)$")


#: Una celda de la tabla: un `|` dentro del texto va escapado, `\|`, como en
#: cualquier tabla Markdown.
_CELDA = r"(?:[^|\n\\]|\\.)*"


#: Una fila de la tabla: cuatro celdas. La cabecera y el separador tienen la
#: misma forma y se descartan aparte.
_FILA = re.compile(
    rf"^\|(?P<horizonte>{_CELDA})\|(?P<vence>{_CELDA})\|"
    rf"(?P<ambito>{_CELDA})\|(?P<cuerpo>{_CELDA})\|\s*$"
)


CABECERA = "| Horizonte | Vence | Ámbito | Detalle |"


#: La escalera del template vanilla, y solo el punto de partida: los escalones
#: son del autor y salen de la tabla de `reglas/pendientes.user.md`
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
    vence: str
    ambito: str | None
    cuerpo: str

    @property
    def dia(self) -> date | None:
        """El día en que vence, sin la hora; `None` si no tiene o no se lee."""
        try:
            return date.fromisoformat(self.vence.split()[0]) if self.vence else None
        except ValueError:
            return None

    @property
    def hora(self) -> str | None:
        """La hora en que vence, si la lleva."""
        partes = self.vence.split()
        return partes[1] if len(partes) == 2 else None

    def linea(self, rutas: Mapping[str, str] | None = None) -> str:
        """La fila como línea de la tabla; el link se escribe desde `PENDIENTES.md`."""
        ambito = link.enlace_ambito(self.ambito, "PENDIENTES.md", rutas) if self.ambito else ""
        cuerpo = self.cuerpo.replace("|", r"\|")
        return f"| {self.horizonte} | {self.vence} | {ambito} | {cuerpo} |"


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
    reconoce, que es lo que `tuku doctor entry` reporta por separado.
    """
    m = _REGISTRO.match(linea)
    if m is None:
        return None
    enlace = m.group("ambito")
    marca = m.group("marca")
    cuerpo = m.group("cuerpo")
    if marca == CIERRA:
        cuerpo = _destachar(cuerpo)
    return Marca(marca, link.nombre_de(enlace) if enlace else None, cuerpo)


_PREFIJO_DE_MARCA = re.compile(r"^(?:\*\*pendiente\*\*|\(Hecho\))(?: \*\*[^*\n]+\*\*)?: ")


def prefijo_de_marca(cuerpo: str) -> str:
    """La marca con que empieza el cuerpo de un registro (`**pendiente**: `), o `""`."""
    m = _PREFIJO_DE_MARCA.match(cuerpo)
    return m.group(0) if m else ""


def _destachar(cuerpo: str) -> str:
    """El cuerpo sin la tachadura que lo envuelve: `~~avisar~~` → `avisar`."""
    m = re.fullmatch(r"~~(.+)~~", cuerpo.strip())
    return m.group(1) if m else cuerpo


def cierre(cuerpo: str) -> str:
    """El cierre canónico: la marca a la vista y el cuerpo tachado.

    `(Hecho): ~~avisar de los GGCC~~`. Lo tachado es lo que ya se hizo, y la
    marca queda legible para el lector y para el comando.
    """
    return f"{CIERRA}: ~~{_destachar(cuerpo)}~~"


def canonizar(body: str) -> str:
    """El cuerpo de un registro con su cierre en forma canónica, si es un cierre.

    Acepta `(Hecho): cuerpo` y `(Hecho): ~~cuerpo~~`, con o sin clasificación
    abierta, y escribe siempre la misma. Cualquier otro cuerpo vuelve igual:
    quien dicta no necesita saber dónde va la tachadura.
    """
    m = _CIERRE_ENTRADA.match(body.strip())
    if m is None:
        return body.strip()
    return f"{CIERRA}{m.group('clasif') or ''}: ~~{_destachar(m.group('cuerpo'))}~~"


def clave(cuerpo: str) -> str:
    """Con qué se compara el cuerpo de un pendiente: sin links y sin espacios sobrantes.

    El mismo pendiente puede llevar un link en la bitácora y no llevarlo en
    `PENDIENTES.md`, o al revés. Al buscar cuál cerrar, o si ya existe, lo que
    cuenta es lo que se lee.
    """
    return " ".join(link.sin_links(cuerpo).split())


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
    return Fila(
        horizonte,
        m.group("vence").strip(),
        link.nombre_de(ambito) if ambito else None,
        m.group("cuerpo").strip().replace(r"\|", "|"),
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
    return orden, fila.vence or "9999-99-99"


def abrir(
    pendientes: str,
    marca: Marca,
    *,
    horizon: str = ESTA_SEMANA,
    due: str = "",
    escalera: tuple[str, ...] = ESCALERA,
    rutas: Mapping[str, str] | None = None,
) -> str:
    """Copia el cuerpo del registro como fila. Idempotente.

    `spec/pendientes.md`: todo pendiente nuevo va a la tabla única de
    `PENDIENTES.md`, ordenado por escalón y por fecha.

    Si el detalle ya existe no duplica la fila: un registro repetido en la
    bitácora no abre dos veces el mismo pendiente.
    """
    fila = Fila(
        horizonte=canonico(horizon, escalera),
        vence=due.strip(),
        ambito=marca.ambito,
        cuerpo=marca.cuerpo,
    )
    lineas = pendientes.splitlines()
    ini, fin = _rango_tabla(lineas)
    existentes = [f for linea in lineas[ini:fin] if (f := _parsear_fila(linea))]

    if any(_misma_fila(f, fila) for f in existentes):
        return pendientes

    clave = _clave(fila, escalera)
    desplazamiento = next(
        (i for i, f in enumerate(existentes) if _clave(f, escalera) > clave), len(existentes)
    )
    corte = ini + desplazamiento
    nuevas = [*lineas[:corte], fila.linea(rutas), *lineas[corte:]]
    texto = "\n".join(nuevas)
    return texto + "\n" if pendientes.endswith("\n") else texto


def _misma_fila(a: Fila, b: Fila) -> bool:
    """Dos filas son la misma si solo difieren en los links de su detalle."""
    return (a.horizonte, a.vence, a.ambito, clave(a.cuerpo)) == (
        b.horizonte,
        b.vence,
        b.ambito,
        clave(b.cuerpo),
    )


def reemplazar_cuerpo(pendientes: str, viejo: str, nuevo: str) -> tuple[str, bool]:
    """Cambia el detalle de la fila que dice `viejo` por `nuevo`. Conserva el resto.

    Encuentra la fila comparando sin links, así que sirve aunque la bitácora
    lleve un link que la tabla no tiene.
    """
    lineas = pendientes.splitlines(keepends=True)
    buscado = clave(viejo)
    for i, linea in enumerate(lineas):
        fila = _parsear_fila(linea.rstrip("\n"))
        m = _FILA.match(linea.rstrip("\n"))
        if fila is not None and m is not None and clave(fila.cuerpo) == buscado:
            lineas[i] = linea[: m.start("cuerpo")] + f" {nuevo} " + linea[m.end("cuerpo") :]
            return "".join(lineas), True
    return pendientes, False


def cambiar_ambito(
    pendientes: str, cuerpo: str, ambito: str, rutas: Mapping[str, str] | None = None
) -> tuple[str, bool]:
    """Pasa la fila que dice `cuerpo` al ámbito `ambito`. Conserva el resto de la fila.

    Encuentra la fila comparando sin links, como `reemplazar_cuerpo`.
    """
    lineas = pendientes.splitlines(keepends=True)
    buscado = clave(cuerpo)
    for i, linea in enumerate(lineas):
        fila = _parsear_fila(linea.rstrip("\n"))
        m = _FILA.match(linea.rstrip("\n"))
        if fila is not None and m is not None and clave(fila.cuerpo) == buscado:
            enlace = link.enlace_ambito(ambito, "PENDIENTES.md", rutas)
            lineas[i] = linea[: m.start("ambito")] + f" {enlace} " + linea[m.end("ambito") :]
            return "".join(lineas), True
    return pendientes, False


def horizontes(pendientes: str) -> list[str]:
    """Los horizontes que aparecen en la tabla, sin repetir, en el orden del archivo."""
    vistos: list[str] = []
    for fila in filas(pendientes):
        if fila.horizonte not in vistos:
            vistos.append(fila.horizonte)
    return vistos


def comando_de(
    marca: str,
    cuerpo: str,
    *,
    ambito: str | None = None,
    day: date | None = None,
    hour: str | None = None,
) -> str:
    """El `tuku todo open` o `close` entero que escribe esa marca, listo para correr."""
    import shlex

    es_open = marca == ABRE
    partes = ["tuku todo open" if es_open else "tuku todo close"]
    if ambito:
        partes.append(f"--scope {shlex.quote(ambito)}")
    if cuando := " ".join(x for x in (day.isoformat() if day else "", hour or "") if x):
        partes.append(f"--at {shlex.quote(cuando)}")
    partes.append(f"--body {shlex.quote(cuerpo)}" if es_open else shlex.quote(cuerpo))
    return " ".join(partes)


@dataclass(frozen=True)
class ConsecuenciaPendiente:
    """Una marca de la bitácora cuyo comando de consecuencia nunca se corrió."""

    cuerpo: str
    marca: str
    ambito: str | None = None
    dia: date | None = None
    hora: str | None = None

    @property
    def comando(self) -> str:
        return comando_de(
            self.marca, self.cuerpo, ambito=self.ambito, day=self.dia, hour=self.hora
        )


@dataclass(frozen=True)
class AperturaCerrada:
    """Un `**pendiente**` cuyo `(Hecho)` está en el mismo día de `AHORA.md`."""

    linea: int  #: 1-based, la del registro que abrió
    cuerpo: str
    dia: str  #: el encabezado del día, sin `## `


def cerrados_el_mismo_dia(ahora: str) -> list[AperturaCerrada]:
    """Los pendientes que se abrieron y se cerraron bajo el mismo día.

    De esos queda solo el cierre: el registro que abrió ya no dice nada que el
    `(Hecho)` no diga. Un pendiente que se cerró otro día conserva los dos.
    """
    hallados: list[AperturaCerrada] = []
    dia = ""
    aperturas: list[tuple[int, Marca]] = []
    cierres: set[str] = set()

    def cerrar_dia() -> None:
        hallados.extend(
            AperturaCerrada(n, m.cuerpo, dia)
            for n, m in aperturas
            if clave(m.cuerpo) in cierres
        )

    for n, linea in enumerate(ahora.splitlines(), start=1):
        if linea.startswith("## "):
            cerrar_dia()
            dia, aperturas, cierres = linea[3:].strip(), [], set()
            continue
        if (m := parsear(linea)) is None:
            continue
        if m.marca == ABRE:
            aperturas.append((n, m))
        elif m.marca == CIERRA:
            cierres.add(clave(m.cuerpo))
    cerrar_dia()
    return hallados


def quitar_aperturas_cerradas(ahora: str, cuerpo: str | None = None) -> str:
    """`ahora` sin los registros que abrieron un pendiente cerrado el mismo día.

    Con `cuerpo`, solo los de ese pendiente.
    """
    sobran = {
        a.linea
        for a in cerrados_el_mismo_dia(ahora)
        if cuerpo is None or clave(a.cuerpo) == clave(cuerpo)
    }
    if not sobran:
        return ahora
    lineas = ahora.splitlines(keepends=True)
    return "".join(x for n, x in enumerate(lineas, start=1) if n not in sobran)


def sin_consecuencia(ahora: str, pendientes: str) -> list[ConsecuenciaPendiente]:
    """Las marcas del ciclo en curso que la tabla no refleja.

    Es el modo de falla más caro del sistema y el único que no deja señal: un
    `**pendiente**` escrito a mano en `AHORA.md`, sin pasar por `tuku todo open`,
    deja un archivo perfectamente bien formado al que le falta la mitad. Nada lo
    delata al leerlo; solo cruzando los dos archivos aparece.

    Dos casos, y ninguno mira `bitacoras/`: un pendiente que viene arrastrado de
    un ciclo anterior está en la tabla sin marca en `AHORA.md`, y eso es correcto.

    1. Un `**pendiente**` que no está en la tabla, salvo que el mismo ciclo lo
       cierre después: abrir y cerrar el mismo día no deja fila, y está bien.
    2. Un `(Hecho)` cuyo cuerpo sigue en la tabla.
    """
    from tuku.ahora import dias

    fechas = {i: fecha for i, _, fecha in dias(ahora)}
    ubicadas: list[ConsecuenciaPendiente] = []
    dia: date | None = None
    for i, linea in enumerate(ahora.splitlines()):
        if i in fechas:
            dia = fechas[i]
        if m := parsear(linea):
            ubicadas.append(ConsecuenciaPendiente(m.cuerpo, m.marca, m.ambito, dia, linea[2:7]))
    abiertos = {clave(c.cuerpo): c for c in ubicadas if c.marca == ABRE}
    cerrados = {clave(c.cuerpo) for c in ubicadas if c.marca == CIERRA}
    en_tabla = {clave(c) for c in cuerpos(pendientes)}

    faltan = [c for k, c in abiertos.items() if k not in en_tabla and k not in cerrados]
    faltan += [c for c in ubicadas if c.marca == CIERRA and clave(c.cuerpo) in en_tabla]
    return faltan


def huerfanas(pendientes: str, registros: Iterable[str]) -> list[Fila]:
    """Las filas de la tabla que ningún registro `**pendiente**` abrió.

    `registros` son los textos donde puede estar la apertura: `AHORA.md` y las
    bitácoras cerradas, porque un pendiente arrastrado de un ciclo anterior
    conserva su registro en la bitácora donde nació. Una fila sin apertura en
    ninguno quedó así por una edición: el registro perdió su marca o se borró.
    """
    abiertos = {
        clave(m.cuerpo)
        for texto in registros
        for linea in texto.splitlines()
        if (m := parsear(linea)) is not None and m.marca == ABRE
    }
    return [f for f in filas(pendientes) if clave(f.cuerpo) not in abiertos]


def duplicados(pendientes: str) -> list[str]:
    """Detalles que aparecen en más de una fila. Regla 1 de `spec/pendientes.md`.

    Es lo que reporta `tuku doctor todo`: un pendiente está en exactamente una
    fila, siempre. La misma tarea en dos horizontes es el error que el vault
    real tuvo que prohibir por escrito.
    """
    vistos: dict[str, int] = {}
    for fila in filas(pendientes):
        vistos[clave(fila.cuerpo)] = vistos.get(clave(fila.cuerpo), 0) + 1
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
        if f is not None and clave(f.cuerpo) == clave(marca.cuerpo):
            restantes = [*lineas[:i], *lineas[i + 1 :]]
            texto = "\n".join(restantes)
            return (texto + "\n" if pendientes.endswith("\n") else texto), True
    return pendientes, False


def lint(
    pendientes: str,
    ahora: str | None = None,
    *,
    vistas: Mapping[str, tuple[str | None, str]] | None = None,
    historia: Iterable[str] = (),
) -> list[str]:
    """Los hallazgos de `tuku doctor todo`, cada uno con su corrección. No lee disco.

    Cinco revisiones:

    1. Un detalle en más de una fila (regla 1).
    2. Una marca de `ahora` que la tabla no refleja (`sin_consecuencia`). La
       corrección es el comando original, que es idempotente.
    3. Una vista derivada que no es la que la tabla produce (regla 7). `vistas`
       mapea cada archivo a su texto actual y al que `tuku regenerate todo`
       escribiría; si difieren, la que está mal es la vista.
    4. Un pendiente abierto y cerrado el mismo día: sobra el registro que lo
       abrió, y lo quita `tuku fix todo`.
    5. Una fila sin registro `**pendiente**` en `ahora` ni en `historia` (los
       textos de las bitácoras cerradas): `huerfanas`.
    """
    hallazgos = [
        f"PENDIENTES.md: error: {cuerpo!r} aparece en más de una fila. "
        f"Déjalo en una sola: un pendiente está en exactamente un horizonte."
        for cuerpo in duplicados(pendientes)
    ]
    if ahora is not None:
        hallazgos += [
            f"AHORA.md: error: {c.cuerpo!r} lleva {c.marca} y la tabla no lo refleja. "
            f"Corre `{c.comando}`."
            for c in sin_consecuencia(ahora, pendientes)
        ]
    if ahora is not None:
        hallazgos += [
            f"AHORA.md:{a.linea}: error: {a.cuerpo!r} se abrió y se cerró el {a.dia}: "
            "sobra el registro que lo abrió. Corre `tuku fix todo`."
            for a in cerrados_el_mismo_dia(ahora)
        ]
    if ahora is not None:
        hallazgos += [
            f"PENDIENTES.md: error: la fila {f.cuerpo!r} no tiene registro "
            f"{ABRE} en AHORA.md ni en las bitácoras. "
            f"Corre `{comando_de(ABRE, f.cuerpo, ambito=f.ambito)}`."
            for f in huerfanas(pendientes, [ahora, *historia])
        ]
    for vista, (actual, esperado) in (vistas or {}).items():
        if actual != esperado:
            hallazgos.append(
                f"{vista}: error: la vista de pendientes no coincide con PENDIENTES.md. "
                "Corre `tuku regenerate todo`."
            )
    return hallazgos
