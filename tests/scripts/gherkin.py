"""Corre un escenario leyendo su `.md`: el texto es la fuente ejecutable.

El comando de un escenario se escribía dos veces, en prosa en el `.md` y en
Python en el arnés, y las dos copias divergían en silencio. Acá el `.md` manda:
este módulo parsea sus bloques `bash` y los ejecuta. El arnés queda con lo único
que el texto no puede expresar, las aserciones sobre el resultado.

**El escenario se lee como lo que hace una persona.** No lleva `TUKU_HOME=`, ni
rutas de `playground/`, ni banderas que solo existen para el test: escribe
`tuku init mi-vault --date 2026-08-11` y nada más. Lo que el test necesita lo
pone el runner alrededor:

- el directorio de trabajo es `playground/<slug>/`, así que `mi-vault` cae
  dentro del repo, a la vista para el `## Qué se mira a mano`;
- `TUKU_HOME` apunta al checkout, así que la siembra copia de `template/` sin
  instalar nada ni tocar la red.

Un `.md` con varios `## Escenario:` reparte un subdirectorio por escenario, para
que los tres resultados del `001-03` se puedan mirar juntos en vez de pisarse.

Una línea que empieza con `tuku` se ejecuta **en proceso** (`cli.main`): es
rápida, comparte intérprete con el test y por eso el `001-05` puede parchar
`socket` alrededor de la llamada. Cualquier otra línea va por `bash`, que es
como entran `mkdir`, `grep` o `diff -r` sin caso especial.

Un fence ```agente``` no se ejecuta: marca el escenario como agéntico y lo deja
fuera de la corrida por defecto. Es provisorio. Cuando el epic 003 exponga un
comando para eso, el fence se vuelve un `bash` normal y esta convención muere.
"""

from __future__ import annotations

import io
import os
import re
import shlex
import shutil
import subprocess
import sys
import unicodedata
from collections.abc import Iterator
from contextlib import (
    ExitStack,
    contextmanager,
    redirect_stderr,
    redirect_stdout,
    suppress,
)
from dataclasses import dataclass, field
from datetime import date as real_date
from datetime import datetime as real_datetime
from pathlib import Path
from typing import Any
from unittest.mock import patch

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ_REPO / "src"))

sys.path.insert(0, str(RAIZ_REPO / "tests" / "scripts"))

import agente  # noqa: E402
import vault  # noqa: E402

ESCENARIOS = RAIZ_REPO / "tests" / "escenarios"

#: Las palabras que abren un paso. `Y` y `Pero` continúan el paso anterior y
#: heredan su tipo, como en cualquier Gherkin.
_PALABRAS = ("Dado", "Cuando", "Entonces", "Y", "Pero")
_PASO = re.compile(rf"^({'|'.join(_PALABRAS)})\b(.*)$")
_FENCE = re.compile(r"^```(\w*)\s*$")
_TITULO = re.compile(r"^##\s+Escenario:\s*(.+?)\s*$")

#: El encabezado que hace de `Background`: sus comandos corren antes de cada
#: escenario del archivo. Es donde un paso de la cadena declara de qué estado
#: parte, con el `cp -r` del paso anterior a la vista.
_FONDO = "## Estado inicial"


class EscenarioNoEncontrado(LookupError):
    """El `.md` no tiene un `## Escenario:` con ese título."""


class PasoFallido(AssertionError):
    """Un comando de `Dado` o `Entonces` falló, y sin él el escenario no prueba nada."""


@dataclass
class Paso:
    """Un paso del escenario y los comandos que lleva colgando."""

    tipo: str  # Dado, Cuando o Entonces, ya resuelto para Y y Pero
    texto: str
    comandos: list[str] = field(default_factory=list)
    agente: list[str] = field(default_factory=list)


@dataclass
class Escenario:
    """Un `## Escenario:` del `.md`, con sus pasos en orden."""

    slug: str
    titulo: str
    pasos: list[Paso]
    fondo: list[Paso] = field(default_factory=list)

    @property
    def todos_los_pasos(self) -> list[Paso]:
        """El `## Estado inicial` del archivo y después los pasos propios."""
        return [*self.fondo, *self.pasos]

    @property
    def es_agentico(self) -> bool:
        return any(p.agente for p in self.pasos)


@dataclass
class Resultado:
    """Lo que dejó un comando del escenario."""

    comando: str
    codigo: int
    stdout: str
    stderr: str


@dataclass
class Corrida:
    """Lo que dejó correr un escenario: dónde, y qué dijo cada comando."""

    escenario: Escenario
    dir: Path  #: el directorio de trabajo, dentro de `playground/`
    codigo: int  #: el del último `Cuando`, que es el caso corriente
    stdout: str
    stderr: str
    resultados: list[Resultado] = field(default_factory=list)
    antes: dict[str, bytes] = field(default_factory=dict)
    despues: dict[str, bytes] = field(default_factory=dict)
    turnos: list[agente.Turno] = field(default_factory=list)

    @property
    def turno(self) -> agente.Turno:
        """El único turno del escenario. Falla si hay otro número.

        El epic 003 es de un turno por escenario a propósito: con dos, un fallo
        podría venir de dos sitios. La conversación es el epic 004.
        """
        if len(self.turnos) != 1:
            raise EscenarioNoEncontrado(
                f"{self.escenario.slug} tiene {len(self.turnos)} turnos de agente, no uno"
            )
        return self.turnos[0]

    @property
    def delta(self) -> dict[str, str]:
        """Qué cambió entre el estado que dejaron los `Dado` y el final.

        El `README.md` de escenarios lo pide así: el assert es el diff entre dos
        estados, no una comparación de árbol completo. Así se ven los efectos
        colaterales que un assert por archivo no mira, y la idempotencia sale
        gratis, porque el segundo pase de una operación tiene que dar vacío.
        """
        return vault.delta(self.antes, self.despues)

    def delta_de(self, sub: str) -> dict[str, str]:
        """El `delta` acotado a un subdirectorio, con las rutas relativas a él.

        Un escenario puede tener más de un vault en su directorio de trabajo, y
        lo que afirma es qué cambió dentro de uno.
        """
        prefijo = f"{sub}/"
        return {
            ruta[len(prefijo) :]: cambio
            for ruta, cambio in self.delta.items()
            if ruta.startswith(prefijo)
        }

    def ruta(self, *partes: str) -> Path:
        """Una ruta relativa al directorio de trabajo del escenario."""
        return self.dir.joinpath(*partes)

    def de(self, fragmento: str) -> Resultado:
        """El resultado del comando que contiene `fragmento`. Falla si no hay uno solo.

        Para escenarios que corren el mismo comando sobre varios vaults: el
        arnés pide el que le interesa por un trozo de su texto, sin repetirlo
        entero ni depender del orden.
        """
        calzan = [r for r in self.resultados if fragmento in r.comando]
        if len(calzan) != 1:
            corridos = [r.comando for r in self.resultados]
            raise EscenarioNoEncontrado(
                f"{fragmento!r} calza con {len(calzan)} comandos de "
                f"{self.escenario.slug}. Se corrieron: {corridos}"
            )
        return calzan[0]


#: Largo máximo del nombre de carpeta de un escenario. Corto a propósito: la
#: ruta aparece escrita a mano en los `cp -r` con que un paso hereda del
#: anterior, y una ruta larga ahí no se lee. Treinta caracteres bastan porque
#: los títulos se eligen para distinguirse temprano, no por casualidad: si dos
#: escenarios de un mismo `.md` colisionan, es que empiezan igual y hay que
#: renombrar uno.
_LARGO_SLUG = 30


def slugificar(texto: str) -> str:
    """El nombre de carpeta de un escenario, derivado de su título.

    Corta por palabra completa, nunca a mitad: `crear-ahora-md-a-partir-de-la`
    y no `crear-ahora-md-a-partir-de-la-p`.
    """
    plano = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    limpio = re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", plano.lower())).strip("-")
    if len(limpio) <= _LARGO_SLUG:
        return limpio
    corte = limpio[: _LARGO_SLUG + 1].rfind("-")
    return (limpio[:corte] if corte > 0 else limpio[:_LARGO_SLUG]).strip("-")


def leer_escenarios(slug: str) -> list[Escenario]:
    """Los `## Escenario:` del `.md`, en el orden en que están escritos."""
    ruta = ESCENARIOS / f"{slug}.md"
    if not ruta.is_file():
        raise FileNotFoundError(f"no existe el escenario {ruta}")

    escenarios: list[Escenario] = []
    pasos: list[Paso] = []
    fondo: list[Paso] = []
    titulo: str | None = None
    en_fondo = False
    tipo = "Dado"
    lenguaje: str | None = None

    for linea in ruta.read_text(encoding="utf-8").splitlines():
        fence = _FENCE.match(linea)
        if fence:
            lenguaje = None if lenguaje is not None else fence.group(1)
            continue
        if lenguaje is not None:
            # Dentro de un fence: solo cuentan los que el escenario ejecuta, y
            # solo si cuelgan de un paso. Un bloque suelto es documentación.
            cuerpo = linea.strip()
            if en_fondo and not fondo:
                # El `## Estado inicial` es prosa: sus comandos no cuelgan de
                # ningún `Dado`, así que se les da uno implícito.
                fondo.append(Paso(tipo="Dado", texto="el estado inicial del escenario"))
            destino_pasos = fondo if en_fondo else pasos
            if destino_pasos and cuerpo and not cuerpo.startswith("#"):
                if lenguaje == "bash":
                    destino_pasos[-1].comandos.append(cuerpo)
                elif lenguaje == "agente":
                    destino_pasos[-1].agente.append(cuerpo)
            continue

        if linea.startswith("#"):
            # Cualquier encabezado cierra el escenario en curso. Sin esto, los
            # bloques de "## Cómo se corre" se leerían como pasos suyos.
            if titulo is not None:
                escenarios.append(Escenario(slug, titulo, pasos, fondo))
            titulo, pasos, tipo = None, [], "Dado"
            en_fondo = linea.strip() == _FONDO
            encabezado = _TITULO.match(linea)
            if encabezado:
                titulo = encabezado.group(1)
            continue

        paso = _PASO.match(linea.strip())
        if paso and (titulo is not None or en_fondo):
            palabra, resto = paso.group(1), paso.group(2).strip()
            if palabra not in ("Y", "Pero"):
                tipo = palabra
            (fondo if en_fondo else pasos).append(Paso(tipo=tipo, texto=resto))

    if titulo is not None:
        escenarios.append(Escenario(slug, titulo, pasos, fondo))
    return escenarios


def buscar(slug: str, titulo: str) -> Escenario:
    """El escenario cuyo título contiene `titulo`. Falla si no hay uno solo."""
    candidatos = [e for e in leer_escenarios(slug) if titulo.lower() in e.titulo.lower()]
    if not candidatos:
        disponibles = [e.titulo for e in leer_escenarios(slug)]
        raise EscenarioNoEncontrado(
            f"{slug}: ningún escenario dice {titulo!r}. Hay: {disponibles}"
        )
    if len(candidatos) > 1:
        raise EscenarioNoEncontrado(
            f"{slug}: {titulo!r} calza con varios: {[e.titulo for e in candidatos]}"
        )
    return candidatos[0]


#: Los epics ya preparados en esta sesión de pytest.
_PREPARADOS: set[str] = set()

#: Lo que dejó cada escenario ya corrido en esta sesión, por slug y título.
#: Un escenario se corre **una vez**: varios tests pueden afirmar cosas
#: distintas sobre el mismo, y volver a ejecutarlo sería rehacer el mismo
#: trabajo y pisar el resultado que el autor va a mirar a mano.
_CORRIDAS: dict[tuple[str, str], Corrida] = {}

#: Los escenarios que ya fallaron, con su fallo. Un escenario se corre **una
#: vez por sesión, falle o no**: sin esto, un escenario que aborta antes de
#: cachear se vuelve a correr entero en cada test que lo pide, y en un epic
#: agéntico eso es un turno de modelo por test. El `003-08` con hermes daba
#: cuatro turnos de tres minutos para reportar cuatro veces el mismo fallo.
_FALLIDAS: dict[tuple[str, str], Exception] = {}


def epic_de(slug: str) -> str:
    """Los tres dígitos con los que abre el nombre de un escenario."""
    return slug.split("-", 1)[0]


def _escenario_de_preparacion(epic: str) -> Escenario | None:
    """El `## Escenario:` del `XXX-00`, que limpia el playground del epic."""
    candidatos = sorted(ESCENARIOS.glob(f"{epic}-00-*.md"))
    if not candidatos:
        return None
    escenarios = leer_escenarios(candidatos[0].stem)
    return escenarios[0] if escenarios else None


def preparar_epic(epic: str) -> None:
    """Corre el `XXX-00` del epic, una vez por sesión, antes de que nada escriba.

    Se dispara sola al preparar el primer directorio del epic, así que correr un
    escenario suelto con `-k` prepara igual que la corrida completa.
    """
    if epic in _PREPARADOS:
        return
    escenario = _escenario_de_preparacion(epic)
    if escenario is None:
        _PREPARADOS.add(epic)
        return

    vault.PLAYGROUND.mkdir(parents=True, exist_ok=True)
    for paso in escenario.pasos:
        for comando in paso.comandos:
            codigo, _, error = _correr_bash(comando, vault.PLAYGROUND)
            if codigo != 0:
                raise PasoFallido(
                    f"{escenario.slug}: la preparación del epic {epic} falló en "
                    f"`{comando}`: salió {codigo}. {error.strip()}"
                )
    _PREPARADOS.add(epic)


def _preparar_dir(escenario: Escenario) -> Path:
    """El directorio de trabajo del escenario: `playground/<slug>/<escenario>/`.

    Cada escenario recibe el suyo, siempre, aunque el `.md` tenga uno solo. Por
    dos razones: si los tres casos del `001-03` compartieran carpeta solo
    sobreviviría el último, y no habría nada que mirar a mano de los otros dos;
    y la profundidad tiene que ser la misma en todos, porque un paso de la
    cadena hereda del anterior con un `cp -r ../../<paso previo>/...` escrito en
    el `.md`.

    No borra: de eso se encargó `preparar_epic` una sola vez. Si la carpeta ya
    existe pese a la limpieza, es que dos escenarios distintos reclaman el mismo
    nombre, y eso se dice en vez de pisarlo en silencio.
    """
    vault.exigir_banco_limpio()
    vault.enlazar_fixtures()
    preparar_epic(epic_de(escenario.slug))
    destino = vault.PLAYGROUND / escenario.slug / slugificar(escenario.titulo)
    if destino.exists():
        # Cada escenario limpia lo suyo, y solo lo suyo. Antes el `XXX-00` del
        # epic borraba `playground/XXX-*` entero, y eso destruía el resultado de
        # los escenarios que esta corrida no iba a regenerar: un `uv run pytest`
        # normal se llevaba por delante los turnos agénticos del epic 003, que
        # cuestan tokens y no se repiten. La pelea con el sistema de archivos que
        # motivó aquel borrado único ya no aplica: una corrida cachea el
        # escenario, así que esto es un borrado por escenario y no por test.
        shutil.rmtree(destino)
    destino.mkdir(parents=True)
    return destino


def _separar_entorno(partes: list[str]) -> tuple[dict[str, str], list[str]]:
    """Las asignaciones `VAR=valor` que preceden al comando, y el comando.

    `TUKU_HOME=roto tuku init mi-vault` es lo que una persona escribiría para
    probar una instalación rota, así que el escenario lo escribe así y el runner
    lo entiende.
    """
    entorno: dict[str, str] = {}
    while partes and "=" in partes[0] and not partes[0].startswith("="):
        nombre, _, valor = partes[0].partition("=")
        if not nombre.replace("_", "").isalnum():
            break
        entorno[nombre] = valor
        partes = partes[1:]
    return entorno, partes


@contextmanager
def _congelar_tiempo(tuku_now: str | None) -> Iterator[None]:
    """Congela deterministamente date.today() y datetime.now() en tuku para tests."""
    if not tuku_now:
        yield
        return

    val = tuku_now.strip().replace(" ", "T")
    if "T" in val:
        partes = val.split("T")
        fecha_parte = partes[0]
        hora_parte = partes[1]
        if len(hora_parte.split(":")) == 2:
            hora_parte += ":00"
        dt = real_datetime.fromisoformat(f"{fecha_parte}T{hora_parte}")
    else:
        dt = real_datetime.fromisoformat(f"{val}T00:00:00")
    d = dt.date()

    class FakeDate(real_date):
        @classmethod
        def today(cls) -> Any:
            return d

    class FakeDatetime(real_datetime):
        @classmethod
        def now(cls, tz: Any = None) -> Any:
            if tz is not None:
                return dt.astimezone(tz) if dt.tzinfo else dt.replace(tzinfo=tz)
            return dt

    modulos = [
        "tuku.entry",
        "tuku.todo",
        "tuku.note",
        "tuku.cycle",
        "tuku.init",
        "tuku.scope",
    ]
    with ExitStack() as stack:
        for mod in modulos:
            with suppress(AttributeError, ModuleNotFoundError):
                stack.enter_context(patch(f"{mod}.date", FakeDate))
            with suppress(AttributeError, ModuleNotFoundError):
                stack.enter_context(patch(f"{mod}.datetime", FakeDatetime))
        yield


def _correr_tuku(argv: list[str], entorno: dict[str, str]) -> tuple[int, str, str]:
    from tuku.cli import main

    previos = {k: os.environ.get(k) for k in entorno}
    os.environ.update(entorno)
    out, err = io.StringIO(), io.StringIO()
    tuku_now = entorno.get("TUKU_NOW")
    try:
        with _congelar_tiempo(tuku_now), redirect_stdout(out), redirect_stderr(err):
            try:
                codigo = main(argv)
            except SystemExit as e:
                codigo = e.code if isinstance(e.code, int) else 1
    finally:
        for k, v in previos.items():
            if v is None:
                del os.environ[k]
            else:
                os.environ[k] = v
    return codigo, out.getvalue(), err.getvalue()


def _correr_bash(comando: str, dir: Path) -> tuple[int, str, str]:
    p = subprocess.run(
        ["bash", "-c", comando], cwd=dir, capture_output=True, text=True, check=False
    )
    return p.returncode, p.stdout, p.stderr


#: Dónde corre el agente. Dentro del vault, que es como se opera en la vida
#: real: lee su `AGENTS.md` porque está ahí, no porque el prompt se lo pegue.
VAULT_DEL_ESCENARIO = "mi-vault"


def _correr_agente(paso: Paso, dir: Path) -> agente.Turno:
    """El turno que el paso lleva en su bloque ```agente```."""
    prompt = "\n".join(paso.agente)
    vault = dir / VAULT_DEL_ESCENARIO
    if not vault.is_dir():
        raise PasoFallido(
            f"el paso {paso.texto!r} es agéntico y no hay un {VAULT_DEL_ESCENARIO}/ "
            f"en {dir}. El agente corre dentro del vault, así que el escenario "
            f"tiene que haberlo sembrado en su `## Estado inicial`."
        )
    turno = agente.turno(vault, prompt)
    _dejar_a_la_vista(turno, dir)
    if turno.codigo != 0:
        raise PasoFallido(
            f"el turno de {paso.texto!r} salió {turno.codigo}: {turno.stderr.strip()}"
        )
    return turno


def _dejar_a_la_vista(turno: agente.Turno, dir: Path) -> None:
    """Escribe el turno al lado del vault, para el `## Qué se mira a mano`.

    Un turno no repite resultado, así que lo que quedó de esta corrida es la
    única evidencia que va a existir de ella. El `.py` afirma lo que se puede
    afirmar; lo demás (si explicó el mecanismo en vez de decir qué quedó escrito,
    si preguntó algo que los registros ya respondían) solo se juzga leyéndolo.

    Va en `playground/<escenario>/`, un nivel por encima del directorio de
    trabajo. Ese nivel es el correcto por dos razones: agrupa las corridas del
    escenario, y **sobrevive**, porque lo que se borra al empezar una corrida es
    la carpeta del título, no la del escenario.

    El nombre lleva **arnés y fecha**, así que las corridas se acumulan en vez
    de pisarse. Eso importa justo cuando un escenario cuesta repetirlo: el
    `003-06` necesitó cuatro corridas para estabilizarse y las tres primeras
    eran la evidencia de por qué. Con el arnés delante, además, dos arneses
    sobre el mismo escenario quedan uno al lado del otro al listar.

    Nada de esto se versiona ni hace falta conservarlo: `playground/` está
    ignorado entero, y lo que se pierda se vuelve a generar corriendo de nuevo.
    """
    arnes = agente.configurado().nombre
    cuando = real_datetime.now().strftime("%Y-%m-%d-%H%M%S")
    comandos = "\n".join(turno.comandos) or "(ninguno)"
    bloques = [
        f"# {arnes} · {dir.parent.name} · {dir.name} · {cuando}",
        f"## Lo que dijo el autor\n\n{turno.prompt}",
        f"## Lo que respondió el agente\n\n{turno.stdout.strip()}",
        f"## Lo que ejecutó\n\n{comandos}",
    ]
    if turno.conversacion.strip():
        bloques.append(f"## La sesión entera\n\n{turno.conversacion.strip()}")
    salida = dir.parent / f"{arnes}.{cuando}.txt"
    salida.write_text("\n\n".join(bloques) + "\n", encoding="utf-8")


def _exigir_que_la_traza_explique(
    escenario: Escenario,
    turnos: list[agente.Turno],
    antes: dict[str, bytes],
    despues: dict[str, bytes],
) -> None:
    """Un vault que cambió sin que la traza lo explique invalida el escenario.

    La traza sale de un `tuku` puesto al frente del `PATH`, y eso se puede
    evadir sin querer: un arnés que ejecuta por **shell de login** relee el
    perfil del usuario, que vuelve a anteponer su `~/.local/bin`, y ahí gana el
    `tuku` instalado. Le pasó a `hermes`: encontró un `tuku` viejo, lo descartó
    con buen criterio y se fue al del checkout, dejando la traza en blanco.

    Sin esta comprobación el escenario falla igual, pero mintiendo: dice "la
    traducción fue []" como si el agente no hubiera hecho nada, cuando hizo lo
    correcto y el instrumento no miraba. Son dos defectos muy distintos y el
    mensaje tiene que decir cuál es.
    """
    if not turnos or any(t.traza for t in turnos):
        return
    cambios = vault.delta(antes, despues)
    if not cambios:
        return
    raise PasoFallido(
        f"{escenario.slug}: el vault cambió y la traza está vacía, así que el "
        f"agente no pasó por el shim y no hay evidencia de qué ejecutó. "
        f"Cambió: {sorted(cambios)}. Suele ser un `tuku` instalado que le gana "
        f"al shim en un shell de login: revisa `command -v tuku` dentro de uno "
        f"(`bash -lc 'command -v tuku'`)."
    )


def correr(slug: str, titulo: str) -> Corrida:
    """Ejecuta un escenario del `.md` y devuelve lo que dejó.

    Se ejecutan los `Dado` y `Cuando`; los `Entonces` solo cuando llevan comando,
    porque ahí el comando **es** la aserción. Un `Dado` o un `Entonces` que falla
    aborta: el `Cuando` no probaría lo que el escenario dice. Un `Cuando` que
    falla no aborta, porque hay escenarios cuyo tema es justamente el rechazo.
    """
    escenario = buscar(slug, titulo)
    clave = (slug, escenario.titulo)
    en_cache = _CORRIDAS.get(clave)
    if en_cache is not None:
        return en_cache
    fallo = _FALLIDAS.get(clave)
    if fallo is not None:
        raise fallo
    dir = _preparar_dir(escenario)

    codigo, salida, error = 0, "", ""
    resultados: list[Resultado] = []
    turnos: list[agente.Turno] = []
    antes: dict[str, bytes] = {}
    previo_home, previo_cwd = os.environ.get("TUKU_HOME"), Path.cwd()
    os.environ["TUKU_HOME"] = str(RAIZ_REPO)
    os.chdir(dir)
    try:
        for paso in escenario.todos_los_pasos:
            if paso.tipo == "Cuando" and not antes:
                # El estado del que parte la acción: todo lo anterior es `Dado`.
                antes = vault.instantanea(dir)
            if paso.agente:
                turnos.append(_correr_agente(paso, dir))
            for comando in paso.comandos:
                entorno, partes = _separar_entorno(shlex.split(comando))
                if partes and partes[0] == "tuku":
                    codigo, salida, error = _correr_tuku(partes[1:], entorno)
                else:
                    codigo, salida, error = _correr_bash(comando, dir)
                resultados.append(Resultado(comando, codigo, salida, error))
                if codigo != 0 and paso.tipo != "Cuando":
                    pista = ""
                    if comando.startswith("cp -r ../"):
                        pista = (
                            " Este paso hereda el estado del anterior, y el anterior no "
                            "corrió: corre la cadena entera (`uv run pytest "
                            "tests/escenarios/`) o el paso previo antes que este."
                        )
                    raise PasoFallido(
                        f"{slug}: falló un comando de '{paso.tipo} {paso.texto}': "
                        f"`{comando}` salió {codigo}. {error.strip()}{pista}"
                    )
    except Exception as e:
        # Un paso que falla también consume el turno: se cachea igual, y la
        # evidencia se archiva igual.
        _FALLIDAS[clave] = e
        vault.archivar(escenario.slug)
        raise
    finally:
        os.chdir(previo_cwd)
        if previo_home is None:
            del os.environ["TUKU_HOME"]
        else:
            os.environ["TUKU_HOME"] = previo_home

    # El escenario corre fuera del repo y el autor lee dentro: la copia cierra
    # esa distancia. Va en `finally` porque el turno que hay que mirar es
    # justamente el del escenario que falló, y antes se perdía: la comprobación
    # de la traza aborta, y con ella se iba la única evidencia de la corrida.
    try:
        _exigir_que_la_traza_explique(escenario, turnos, antes, vault.instantanea(dir))
    except Exception as e:
        _FALLIDAS[clave] = e
        raise
    finally:
        vault.archivar(escenario.slug)
    corrida = Corrida(
        escenario=escenario,
        dir=dir,
        codigo=codigo,
        stdout=salida,
        stderr=error,
        resultados=resultados,
        antes=antes,
        despues=vault.instantanea(dir),
        turnos=turnos,
    )
    _CORRIDAS[(slug, escenario.titulo)] = corrida
    return corrida
