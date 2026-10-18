"""tuku todo open / tuku todo close: las dos consecuencias deterministas.

Fase 2 de `devel/epics.md`. `**pendiente**` abre, `(Hecho)` cierra
(`spec/bitacora.md`). El cuerpo es el mismo texto en los tres lugares: el
registro que abre, la fila de `PENDIENTES.md` y el registro que cierra. **Abrir
es copiar, cerrar es encontrar y borrar.** Ninguna de las dos interpreta nada, y
por eso este paso no necesita LLM.

Operan **por registro**, no reconciliando el archivo. `PENDIENTES.md` es fuente
de verdad y no se regenera desde las bitácoras (`spec/pendientes.md`, regla 7):
un reconciliador borraría los pendientes abiertos en ciclos anteriores que el
`AHORA.md` en curso ya no menciona. La idempotencia se paga a mano: abrir
comprueba que la fila no esté, cerrar que la pareja exista.

El archivo es **una sola tabla**, `| Horizonte | Vence | Ámbito | Detalle |`.
El horizonte y la fecha son columnas y no estructura: bajar de escalón o agendar
mueve o edita una fila, y nunca crea ni destruye secciones.

**Qué lee y escribe:** las funciones de este módulo solo tocan `PENDIENTES.md`,
que es la fuente de verdad. Los casos de uso `abrir_en_vault` y `cerrar_en_vault`
escriben además el registro en `AHORA.md` y regeneran las dos vistas derivadas,
la región de cada día de `AHORA.md` y `ambitos/PENDIENTES-AMBITOS.md`, llamando
a `tuku.regenerate`; con `--no-regenerate` no las rehace y el lote regenera
una sola vez al final.
**A mano:** agregar la fila con su horizonte, o borrarla al cerrarlo, y copiar
el pendiente bajo su día y en el callout de su ámbito.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from tuku import archivo, link
from tuku.resultado import Resultado

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


def avisos_de_plazo(due: str, day: date | None, hour: str | None) -> tuple[str, ...]:
    """Lo raro de un vencimiento, que no lo impide: ya pasó, o es anterior a la promesa.

    Registrar algo que ya venció es legítimo ("se me pasó pagar la luz"), y
    estar atrasado se calcula (`spec/pendientes.md`): el pendiente se abre y el
    comando alerta.
    """
    if not due:
        return ()
    ahora = datetime.now()
    dia, _, h = due.partition(" ")
    vence = datetime.fromisoformat(f"{dia} {h or '23:59'}")
    prometido = datetime.fromisoformat(
        f"{(day or ahora.date()).isoformat()} {hour or ahora.strftime('%H:%M')}"
    )
    if (day or hour) and vence < prometido:
        return (f"vence el {due}, antes de {prometido:%Y-%m-%d %H:%M}, cuando se promete.",)
    if vence < ahora:
        return (f"vence el {due}, que ya pasó: el pendiente nace atrasado.",)
    return ()


def abrir_en_vault(
    vault: Path,
    *,
    body: str,
    scope: str | None = None,
    horizon: str | None = None,
    due: str = "",
    regenerar: bool = True,
    day: date | None = None,
    hour: str | None = None,
) -> Resultado:
    """Abre un pendiente, estampa huella en la bitácora y regenera las vistas.

    Recibe los campos, no la línea del registro: abrir **es** el pendiente, y la
    marca la lleva implícita el verbo. Es la única vía: `tuku entry create` rechaza
    un `**pendiente**` y manda acá. El registro en `AHORA.md` se escribe salvo que
    ya esté.

    Regenerar es parte de abrir: si la vista quedara para un segundo comando, el
    pendiente existiría sin aparecer en su día, que es la falla silenciosa que
    `spec/pendientes.md` persigue. `regenerar=False` es la escotilla del lote,
    que regenera una sola vez al final.

    `day` y `hour` son cuándo se prometió y `due`, para cuándo es, como se
    escribe en la columna `Vence`: `AAAA-MM-DD` o `AAAA-MM-DD HH:MM`
    (`spec/pendientes.md`). Un `day` posterior a HOY se rechaza: el registro
    de algo que todavía no se dijo no existe, y la fecha del pendiente va en
    `due`. Con `due`, el horizonte es `con fecha`; sin ninguno de los dos, el
    primer escalón del autor.
    """
    from tuku import scope as ambitos
    from tuku.ahora import encabezado_de
    from tuku.config import archivo_vault, leer_config
    from tuku.entry import add as entry_add
    from tuku.entry import componer
    from tuku.regenerate import rehacer

    if day is not None and day > date.today():
        return Resultado.rechazo(
            f"el {day.isoformat()} todavía no llega: `--at` es cuándo se prometió. "
            f"Para que venza ese día: --due {day.isoformat()}"
        )
    limpio_scope = ambitos.canonico(vault, scope) if scope else None
    if limpio_scope and (rechazo := ambitos.rechazo_si_no_existe(vault, limpio_scope)):
        return rechazo
    from tuku import note

    cuerpo, avisos = note.enlazar(vault, body.strip(), "AHORA.md")
    marca = Marca(ABRE, limpio_scope, cuerpo)
    escalera = escalera_de(leer_config(vault).horizontes)
    horizon = CON_FECHA if due else canonico(horizon or escalera[0], escalera)

    ahora_path = archivo_vault(vault, "AHORA.md")
    ahora_actual = archivo.leer(ahora_path)
    ya_abierto = any(
        (m := parsear(lin)) is not None
        and m.marca == ABRE
        and clave(m.cuerpo) == clave(marca.cuerpo)
        for lin in ahora_actual.splitlines()
    )
    if not ya_abierto:
        dia_encabezado = encabezado_de(day or date.today())
        hora = hour or datetime.now().strftime("%H:%M")
        linea = componer(
            hora=hora,
            scope=limpio_scope,
            body=f"{ABRE}: {marca.cuerpo}",
            rutas=ambitos.rutas(vault),
        )
        try:
            ahora_texto = entry_add(ahora_actual, [linea], day=dia_encabezado)
            archivo.escribir(ahora_path, ahora_texto)
        except ValueError as e:
            return Resultado.rechazo(str(e))

    ruta = archivo_vault(vault, "PENDIENTES.md")
    archivo.escribir(
        ruta,
        abrir(
            archivo.leer(ruta),
            marca,
            horizon=horizon,
            due=due,
            escalera=escalera,
            rutas=ambitos.rutas(vault),
        ),
    )
    rehacer(vault, ["AHORA.md", "PENDIENTES.md"], salvo=() if regenerar else ("todo",))
    return Resultado.hecho(
        f"pendiente abierto en «{horizon}»: {marca.cuerpo}",
        avisos=(*avisos, *avisos_de_plazo(due, day, hour)),
    )


def cerrar_en_vault(
    vault: Path,
    *,
    body: str,
    regenerar: bool = True,
    day: date | None = None,
    hour: str | None = None,
    scope: str | None = None,
) -> Resultado:
    """Cierra un pendiente por su cuerpo, estampando su huella en la bitácora.

    Un cierre sin pareja **no es un fallo**: es el caso normal del día uno
    (`devel/epics.md`). Se reporta, el registro queda escrito y `PENDIENTES.md`
    no se toca, porque inventar el pendiente que falta dejaría el archivo
    mintiendo.

    **El cierre cae en el ámbito donde estaba el pendiente.** Sin `scope`, el
    registro toma el de la fila que cierra; solo si la fila no tiene, el
    `scope_default` de la config. Con `scope`, manda `scope`.
    """
    from tuku import scope as ambitos
    from tuku.ahora import encabezado_de
    from tuku.config import ambito_por_defecto, archivo_vault
    from tuku.entry import add as entry_add
    from tuku.entry import componer
    from tuku.regenerate import rehacer

    if scope:
        scope = ambitos.canonico(vault, scope)
        if (rechazo := ambitos.rechazo_si_no_existe(vault, scope)) is not None:
            return rechazo
    marca = Marca(CIERRA, None, body.strip())
    ruta = archivo_vault(vault, "PENDIENTES.md")
    pendientes_texto = archivo.leer(ruta)

    ambito_encontrado: str | None = None
    for f in filas(pendientes_texto):
        if clave(f.cuerpo) == clave(marca.cuerpo):
            ambito_encontrado = f.ambito
            break

    if (
        scope is None
        and ambito_encontrado is None
        and (por_defecto := ambito_por_defecto(vault))
    ):
        scope = ambitos.canonico(vault, por_defecto)
        if (rechazo := ambitos.rechazo_si_no_existe(vault, scope)) is not None:
            return rechazo

    texto, hubo_pareja = cerrar(pendientes_texto, marca)

    ahora_path = archivo_vault(vault, "AHORA.md")
    ahora_actual = archivo.leer(ahora_path)
    ya_cerrado = any(
        (m := parsear(lin)) is not None
        and m.marca == CIERRA
        and clave(m.cuerpo) == clave(marca.cuerpo)
        for lin in ahora_actual.splitlines()
    )
    if not ya_cerrado:
        ambito_final = scope if scope is not None else ambito_encontrado
        dia_encabezado = encabezado_de(day or date.today())
        hora = hour or datetime.now().strftime("%H:%M")
        linea = componer(
            hora=hora,
            scope=ambito_final,
            body=cierre(marca.cuerpo),
            rutas=ambitos.rutas(vault),
        )
        try:
            ahora_actual = entry_add(ahora_actual, [linea], day=dia_encabezado)
        except ValueError as e:
            return Resultado.rechazo(str(e))
    ahora_texto = quitar_aperturas_cerradas(ahora_actual, marca.cuerpo)
    if ahora_texto != archivo.leer(ahora_path):
        archivo.escribir(ahora_path, ahora_texto)

    if hubo_pareja:
        archivo.escribir(ruta, texto)
    rehacer(vault, ["AHORA.md", "PENDIENTES.md"], salvo=() if regenerar else ("todo",))

    if not hubo_pareja:
        return Resultado.hecho(
            f"cierre escrito: {marca.cuerpo}",
            avisos=(
                f"no había ningún pendiente abierto con el cuerpo {marca.cuerpo!r}, "
                f"así que no se borró nada. Si esperabas cerrarlo, revisa que el texto "
                f"coincida palabra por palabra.",
            ),
        )
    return Resultado.hecho(f"pendiente cerrado: {marca.cuerpo}")


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


def hallazgos_del_vault(vault: Path) -> list[str]:
    """`lint` sobre el vault: lee los archivos y calcula las vistas esperadas."""
    from tuku import regenerate, scope
    from tuku.config import archivo_vault

    pendientes = archivo.leer(archivo_vault(vault, "PENDIENTES.md"))
    ahora_path = vault / "AHORA.md"
    ahora = archivo.leer(ahora_path) if ahora_path.is_file() else None
    vistas: dict[str, tuple[str | None, str]] = {}
    if ahora is not None:
        vistas["AHORA.md"] = (
            ahora,
            regenerate.vistas_en_ahora(ahora, pendientes, scope.rutas(vault)),
        )
    ambitos_path = vault / regenerate.ARCHIVO_AMBITOS
    vistas[regenerate.ARCHIVO_AMBITOS.as_posix()] = (
        archivo.leer(ambitos_path) if ambitos_path.is_file() else None,
        regenerate.documento_del_vault(vault, pendientes),
    )
    historia = [archivo.leer(b) for b in sorted((vault / "bitacoras").glob("*.md"))]
    return lint(pendientes, ahora, vistas=vistas, historia=historia)


def lint_del_vault(vault: Path) -> Resultado:
    """Revisa los pendientes y reporta; no escribe."""
    hallazgos = hallazgos_del_vault(vault)
    if not hallazgos:
        return Resultado.hecho("sin hallazgos.")
    return Resultado.rechazo(
        "\n".join([*hallazgos, f"{len(hallazgos)} error(es)."]), error=False
    )
