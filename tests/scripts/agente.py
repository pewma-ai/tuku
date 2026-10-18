"""Arnés de agente: correr un turno dentro de un vault y ver qué ejecutó.

El agente invoca a `tuku`, nunca al revés. Acá no hay ningún comando de TUKU que
abra un modelo: lo que hay es lo que hace falta para **observar** a un agente que
ya opera un vault por su cuenta, que es material de pruebas y no del producto.

Dos piezas:

- La configuración del arnés, que sale del entorno. Hoy `agy`, mañana otro, sin
  tocar un solo test.
- El shim: un `tuku` puesto al frente del `PATH` que anota `argv` y delega en el
  real. El agente no coopera ni sabe que está siendo observado, y lo que queda es
  una lista de comandos que se relee, se compara y se vuelve a correr.

Cada llamada es un turno. Una `Sesion` encadena varios sobre la misma
conversación del arnés, que es lo que necesita el epic 004
([`../escenarios/004-00-la-conversacion.md`](../escenarios/004-00-la-conversacion.md)).
"""

from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import socketserver
import subprocess
import sys
import tempfile
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent

#: Cómo se le pasa un turno a cada arnés. `{prompt}` y `{modelo}` se sustituyen;
#: los argumentos de `modelo` se omiten enteros si no hay modelo configurado.
#:
#: Verificado contra `agy` real: `agy -p "..."` deja la respuesta en stdout y sale
#: 0. Su `--conversation <id>` retoma una conversación (verificado: el segundo
#: turno recuerda el primero y conserva el id), y `--output-format json` entrega
#: el `conversation_id` y la respuesta en `response`. Eso es `continuar` y `json`.
#:
#: **`aislar` no es opcional y no es cosmético.** Un arnés moderno resuelve un
#: "proyecto" a partir de la máquina y no del `cwd`, así que un turno lanzado
#: dentro del vault de prueba puede contestar sobre el vault real del autor. Pasó:
#: el primer turno del `003-02` respondió con rutas de `mac-jpgil` y con el nombre
#: de su administradora de verdad, y dos de los tres tests pasaron igual, porque
#: un agente que mira otro vault tampoco toca este. Sin aislamiento, el epic mide
#: la configuración de la máquina y no el `AGENTS.md` que dice medir.
#:
#: Ahí va también lo que deja al agente **ejecutar**. Un `tuku` del agente corre
#: fuera de su sandbox, porque el shim necesita un socket y el sandbox bloquea toda
#: red, y escribir el vault desde un comando también. Auto-aprobar toda herramienta
#: (`--dangerously-skip-permissions`) dejaba al agente saltarse el sandbox para lo
#: que quisiera: en el `004-03` leyó el escenario que lo evalúa. Por eso el arnés
#: **no** auto-aprueba: en headless todo comando que no esté en `permissions.allow`
#: se rechaza, y el agente solo puede salir del sandbox con `tuku`. Eso exige la
#: regla `command(tuku)` en los ajustes del arnés, y `motivo_no_disponible` avisa
#: cuando falta (`_REGLA_DE_PERMISO`).
#:
#: `sesion` es opcional y dice cómo pedirle al arnés **la conversación entera**,
#: no solo el texto final. Lo que un turno devuelve por stdout es su conclusión;
#: lo que hizo para llegar ahí (qué leyó, qué se preguntó, qué descartó) explica
#: los fallos que la traza y el diff no explican. El arnés que no sepa entregarla
#: omite la clave y el turno queda con lo que haya, que es lo que pasa con `agy`.
#: Cómo se le pide a `hermes` la sesión del turno. Su base de sesiones es por
#: perfil, y el perfil de las pruebas solo tiene las de las pruebas, así que
#: filtrar por el `cwd` del escenario devuelve exactamente sus turnos.
#:
#: Por esto el turno va por `chat --oneshot` y no por el `-z` de una línea, que
#: es más limpio de invocar y **no deja rastro**: ni sesión, ni log, ni nada que
#: exportar después. El precio es que `-Q` antepone su `session_id:` al stdout.
_EXPORTA_HERMES = [
    "-p",
    "{perfil}",
    "sessions",
    "export",
    "--format",
    "jsonl",
    "--cwd",
    "{cwd}",
    "--yes",
    "-",
]

#: Lo que se antepone al dictado en los arneses que **no descubren solos** el
#: documento del vault. Claude Code busca `CLAUDE.md` y no `AGENTS.md`, y quien
#: se lo cubre en la máquina del autor es un hook de su configuración, que es
#: justamente lo que `aislar` apaga.
#:
#: **Dice dónde mirar, no qué dice.** Esa es la línea, y es la que separa esto
#: de un prompt de test que invalida el escenario: el contenido sigue saliendo
#: entero del vault, y un `AGENTS.md` que no alcance sigue haciendo fallar al
#: turno. Es además lo que una persona escribe de verdad la primera vez que
#: abre un agente dentro de un vault.
#:
#: Que un arnés lo necesite y otro no es una asimetría real y por eso está
#: declarada acá y no escondida en el prompt del escenario.
PREAMBULO = "Lee AGENTS.md antes de nada y opera este directorio según lo que diga. "


#: Con cuánto esfuerzo piensa el agente, cuando el arnés sabe pedirlo, y con qué
#: modelo cuando el escenario no nombra ninguno.
#:
#: **El default es lo barato y lo mínimo, y eso es una afirmación del epic, no un
#: ahorro.** El comportamiento que el `AGENTS.md` describe es simple: leer una
#: tabla de despacho y ejecutar la fila que corresponde. Un documento que solo
#: funciona con el modelo más caro pensando al máximo no cumple lo que promete,
#: porque lo que estaría resolviendo el turno es el modelo y no el vault. Correr
#: barato es la forma de que el resultado sea atribuible al documento.
#:
#: Se suben con `TUKU_AGENTE_MODELO` y `TUKU_AGENTE_ESFUERZO` cuando lo que se
#: quiere medir es justamente el techo.
ESFUERZO = "low"

#: Cómo se le pregunta a un arnés cuál es su modelo más barato. **No va
#: hardcodeado**: un identificador escrito acá envejece con el primer modelo
#: nuevo, y entonces el epic corre con lo que había el día que alguien lo
#: escribió. El CLI sabe qué modelos tiene hoy, así que se le pregunta.
#:
#: Dos formas, según lo que el arnés ofrezca. Si sabe listarlos, se lee la
#: lista. Si no, se le pregunta al agente en un turno de una línea, que es lo
#: que uno haría a mano. La respuesta se cachea por sesión: es configuración
#: del instrumento, no parte de ningún escenario.
DIME_TU_MODELO = (
    "¿Cuál es el identificador exacto del modelo más barato y rápido que puedo "
    "pasarle a --model en este CLI? Responde solo el identificador, sin ninguna "
    "otra palabra."
)

#: Lo que delata a un modelo barato en una lista de identificadores.
BARATOS = ("haiku", "flash", "mini", "lite", "small")

_MODELOS: dict[str, str | None] = {}

ARNESES: dict[str, dict[str, list[str]]] = {
    "agy": {
        "aislar": ["--new-project", "--sandbox"],
        "prompt": ["-p", "{prompt}"],
        "modelo": ["--model", "{modelo}"],
        "esfuerzo": ["--effort", "{esfuerzo}"],
        "listar": ["models"],
        "continuar": ["--conversation", "{id}"],
        "json": ["--output-format", "stream-json"],
    },
    "hermes": {
        "aislar": ["-p", "{perfil}", "chat", "--oneshot", "--quiet", "--yolo"],
        "prompt": ["-q", "{prompt}"],
        "modelo": ["-m", "{modelo}"],
        "sesion": _EXPORTA_HERMES,
    },
    "claude": {
        "aislar": [
            "--setting-sources",
            "",
            "--strict-mcp-config",
            "--dangerously-skip-permissions",
        ],
        "prompt": ["-p", "{prompt}"],
        "modelo": ["--model", "{modelo}"],
        "esfuerzo": ["--effort", "{esfuerzo}"],
        "preambulo": [PREAMBULO],
    },
}

#: Cómo se aísla `claude`, que es el caso que costó y el que fijó la regla.
#: `--setting-sources` sin fuentes ignora la configuración de usuario, de
#: proyecto y local; `--strict-mcp-config` deja fuera los servidores MCP de la
#: máquina. Lo que eso apaga de paso es el hook que carga los `AGENTS.md`, y por
#: eso el arnés lleva `preambulo`: el documento entra por el vault, no por la
#: configuración del autor.
#:
#: `--restricted` haría casi todo esto de una vez y no sirve: quita Bash, y sin
#: Bash el agente no puede ejecutar `tuku`, que es lo único que el epic mira.

#: El perfil por defecto de los arneses que tienen perfiles. En `hermes` un
#: perfil es una instalación aparte, con su propia configuración, su base de
#: sesiones y su `SOUL.md`, y `-p` la elige por invocación.
#:
#: **Va vacío a propósito.** El epic 003 afirma que el `AGENTS.md` del vault
#: basta para que cualquier agente opere igual, así que un perfil que sepa de
#: TUKU (una skill, una instrucción en su `SOUL.md`) invalida el escenario por
#: la misma puerta que un prompt de test que explique lo que el vault ya dice.
#: Si un turno acierta, tiene que ser atribuible al vault y a nada más.
PERFIL = "tuku"

#: Cuánto se espera un turno antes de darlo por colgado. Un tope contra el
#: cuelgue, no un presupuesto: un turno de una frase termina en medio minuto y
#: no le cuesta nada que el techo esté alto. El del día completo del `003-06`
#: son once frases y ronda los cinco minutos, así que 300 lo dejaba al filo. Se
#: ajusta con `TUKU_AGENTE_TIMEOUT`.
TIMEOUT = 600


#: Cómo se identifica **el hecho** sobre el que actúa una invocación, para
#: distinguir dos hechos de un hecho intentado dos veces. Un agente que corre
#: `note create "T"` sin cuerpo, lo ve rechazado y vuelve con `--body`, no
#: escribió dos notas: escribió una, al segundo intento. Contar eso como un
#: comando de más hace fallar al agente que se corrige, que es exactamente el
#: que uno quiere.
#:
#: El sujeto sale de lo que no cambia entre los dos intentos: el argumento
#: posicional (el título de una nota, el nombre de un ámbito) o el `--at` que
#: ubica un registro. Dos invocaciones del mismo verbo sobre el mismo
#: sujeto, **seguidas**, son un intento y su corrección. Separadas por otro
#: comando, no: ahí el agente ya siguió adelante y volver es otra cosa.
_UBICAN = ("--at", "--due")


def _sujeto(argv: list[str]) -> tuple[str, ...]:
    """Qué hecho toca esta invocación: el verbo, más lo que lo identifica."""
    verbo = tuple(x for x in argv[:2] if not x.startswith("-"))
    posicionales = tuple(
        x
        for i, x in enumerate(argv[len(verbo) :])
        if not x.startswith("-") and not (i and argv[len(verbo) + i - 1].startswith("-"))
    )
    ubicacion = tuple(
        f"{bandera}={argv[i + 1]}"
        for i, bandera in enumerate(argv)
        if bandera in _UBICAN and i + 1 < len(argv)
    )
    return verbo + posicionales + ubicacion


#: Los comandos que solo leen: `doctor`, `vocab`, `style` y todo `lint`. Cualquier
#: otro toca el vault, así que un comando nuevo cuenta como escritura sin
#: registrarlo acá. Un agente que corre un `--help` antes de escribir, o un
#: `tuku doctor` al terminar, hace lo correcto, y tampoco entra en la
#: traducción de un dictado: esa es la secuencia de los que escriben.
LEEN = ("doctor", "vocab", "style")

#: Los comandos con subcomando: su verbo son dos palabras (`entry create`).
GRUPOS = ("cycle", "entry", "todo", "scope", "note")


def escribe(argv: list[str]) -> bool:
    """`argv` toca el vault: no es ayuda, ni un comando de lectura, ni un `lint`."""
    if not argv or es_ayuda(argv):
        return False
    return argv[0] not in LEEN and argv[1:2] != ["lint"]


def verbo(argv: list[str]) -> str:
    """El comando sin sus argumentos: `scope move`, o `regenerate`."""
    return " ".join(argv[:2] if argv[0] in GRUPOS else argv[:1])


def es_ayuda(argv: list[str]) -> bool:
    """`-h`, `--help` o una abreviatura que argparse acepta, como `--h`."""
    return any(a == "-h" or (len(a) > 2 and "--help".startswith(a)) for a in argv)


#: Lo que el runner de pruebas deja en el entorno y el agente no debe heredar.
#: El agente corre dentro del vault como en la vida real, y en la vida real
#: nadie lo lanza desde dentro de un `uv run pytest`. Un entorno de Python
#: ajeno le cambia dónde importa y dónde escribe: con estas puestas, `hermes`
#: dejó de guardar la sesión del turno, y el arnés se quedó sin la evidencia
#: que sabía dar. Es la misma doctrina que `aislar`, aplicada al entorno.
DEL_RUNNER = frozenset(
    {
        "VIRTUAL_ENV",
        "PYTHONPATH",
        "PYTHONHOME",
        "PYTHONSTARTUP",
        "PYTEST_CURRENT_TEST",
        "UV",
        "UV_RUN_RECURSION_DEPTH",
    }
)


def _path_sin_venv() -> str:
    """El `PATH` sin el `bin/` del entorno virtual que corre la suite."""
    venv = os.environ.get("VIRTUAL_ENV")
    partes = os.environ.get("PATH", "").split(os.pathsep)
    if venv:
        partes = [x for x in partes if not x.startswith(f"{venv}{os.sep}")]
    return os.pathsep.join(partes)


class ArnesNoDisponible(RuntimeError):
    """No hay con qué correr el turno. El escenario se salta, no falla."""


@dataclass
class Sesion:
    """La conversación de un arnés entre turnos.

    Nace sin `id`; el primer turno lo recibe del arnés y los siguientes retoman
    esa conversación por él.
    """

    id: str | None = None


def _eventos(stdout: str) -> list[dict[str, Any]]:
    """Los objetos JSON de la salida, de una línea cada uno (`stream-json`) o entera."""
    try:
        dato = json.loads(stdout)
    except json.JSONDecodeError:
        dato = None
    if isinstance(dato, dict):
        return [dato]
    salida = []
    for linea in stdout.splitlines():
        try:
            d = json.loads(linea)
        except json.JSONDecodeError:
            continue
        if isinstance(d, dict):
            salida.append(d)
    return salida


def leer_sesion(stdout: str, sesion: Sesion) -> str:
    """El texto de la respuesta, y el id de la conversación guardado en `sesion`.

    Entiende la salida entera en un JSON y el `stream-json`, donde la respuesta
    viene en el evento `result`. Una salida que no es ninguna de las dos vuelve
    tal cual y deja la sesión como estaba: el turno falla por lo que dijo el
    agente, no por el formato.
    """
    respuesta: object = None
    for evento in _eventos(stdout):
        interno = evento.get("result")
        dato: dict[str, Any] = interno if isinstance(interno, dict) else evento
        if isinstance(dato.get("conversation_id"), str):
            sesion.id = dato["conversation_id"]
        if isinstance(dato.get("response"), str):
            respuesta = dato["response"]
    return respuesta if isinstance(respuesta, str) else stdout


def pasos_de(stdout: str) -> str:
    """Los pasos que dio el agente en un turno, uno por línea y con lo que tardó.

    Sale del `stream-json` sin filtrar nada: cada llamada al modelo y cada
    herramienta, para ver en qué se fue el tiempo. Vacío si la salida no es un
    `stream-json`.
    """
    lineas: list[str] = []
    final: dict[str, Any] = {}
    for e in _eventos(stdout):
        if e.get("event") == "result" and isinstance(e.get("result"), dict):
            final = e["result"]
        paso = e.get("step_update")
        if not isinstance(paso, dict) or paso.get("state") != "DONE":
            continue
        tipo, segundos = paso.get("step_type"), paso.get("duration_seconds") or 0
        if tipo == "agent_response":
            uso = paso.get("usage") or {}
            entrada, salida = uso.get("input_tokens", 0), uso.get("output_tokens", 0)
            que = f"modelo ({entrada} tokens de entrada, {salida} de salida)"
        elif tipo == "tool":
            info = paso.get("tool_info") or {}
            parametros = " ".join(str(v) for v in (info.get("parameters") or {}).values())
            que = f"{paso.get('tool_name')} {parametros}"[:240]
        else:
            continue
        lineas.append(f"{paso.get('step_index', 0):>3}  {segundos:5.1f} s  {que}")
    if not lineas:
        return ""
    total = final.get("duration_seconds")
    cierre = (
        f"total {total:.1f} s, {len(lineas)} pasos" if isinstance(total, int | float) else ""
    )
    return "\n".join([*lineas, cierre]).strip()


#: Una ruta en un parámetro de herramienta: absoluta, del hogar o que sube con `..`.
#: Una `/` suelta (un «sí / no» en un cuerpo) no es una ruta.
_RUTA = re.compile(r"""(?<![\w.:/-])(~?/[^\s'"`;|&<>()]+|\.\./[^\s'"`;|&<>()]*)""")


def fuera_del_vault(stdout: str, vault: Path) -> list[str]:
    """Lo que el agente tocó fuera de `vault` en un turno: la herramienta y la ruta.

    Mira los parámetros de cada herramienta del `stream-json`. Un agente que
    sale del vault puede encontrar el escenario que lo evalúa y copiar la
    respuesta, así que el turno que lo hizo no prueba nada, escriba lo que
    escriba. Vacío si la salida no es un `stream-json`.
    """
    raices = {str(vault), str(vault.resolve())}
    fuera: list[str] = []
    for e in _eventos(stdout):
        paso = e.get("step_update")
        if not isinstance(paso, dict) or paso.get("state") != "DONE":
            continue
        if paso.get("step_type") != "tool":
            continue
        info = paso.get("tool_info") or {}
        for valor in (info.get("parameters") or {}).values():
            for ruta in _RUTA.findall(str(valor)):
                if ruta == "/dev/null" or any(
                    ruta == r or ruta.startswith(r + "/") for r in raices
                ):
                    continue
                fuera.append(f"{paso.get('tool_name')} {ruta}")
    return list(dict.fromkeys(fuera))


@dataclass(frozen=True)
class Arnes:
    """Qué se ejecuta y cómo se le entrega el turno."""

    nombre: str
    ejecutable: str
    modelo: str | None
    perfil: str = PERFIL
    esfuerzo: str = ESFUERZO

    def argv(self, prompt: str, sesion: Sesion | None = None) -> list[str]:
        plantilla = ARNESES[self.nombre]
        if sesion is not None and "continuar" not in plantilla:
            raise ArnesNoDisponible(f"{self.nombre} no sabe retomar una conversación")
        partes = [
            self.ejecutable,
            *(a.format(perfil=self.perfil) for a in plantilla["aislar"]),
        ]
        if sesion is not None:
            partes += plantilla["json"]
            if sesion.id:
                partes += [a.format(id=sesion.id) for a in plantilla["continuar"]]
        modelo = self.modelo or modelo_barato(self.nombre, self.ejecutable)
        if modelo:
            partes += [a.format(modelo=modelo) for a in plantilla["modelo"]]
        if self.esfuerzo and "esfuerzo" in plantilla:
            partes += [a.format(esfuerzo=self.esfuerzo) for a in plantilla["esfuerzo"]]
        dictado = "".join(plantilla.get("preambulo", [])) + prompt
        partes += [a.format(prompt=dictado) for a in plantilla["prompt"]]
        return partes


@dataclass
class Turno:
    """Lo que dejó un turno: lo que dijo el agente y lo que ejecutó."""

    prompt: str
    codigo: int
    stdout: str
    stderr: str
    traza: list[list[str]] = field(default_factory=list)
    conversacion: str = ""  #: los turnos intermedios, si el arnés sabe darlos
    crudo: str = ""  #: la salida del arnés sin filtrar

    @property
    def comandos(self) -> list[str]:
        """La traza como líneas de comando, para leerla y compararla."""
        return [shlex.join(["tuku", *argv]) for argv in self.traza]

    def invocaciones_de(self, *verbo: str) -> list[list[str]]:
        """Las invocaciones que empiezan con ese noun y verb, p. ej. `("entry", "create")`.

        **Las de ayuda no cuentan.** Un agente que no conoce un comando corre
        `tuku entry create --help` antes de usarlo, y eso es exactamente lo que
        debería hacer: no escribe nada y evita inventarse una opción. Contarlas
        haría fallar al agente prudente y pasar al que adivina.
        """
        largo = len(verbo)
        return [
            argv for argv in self.traza if tuple(argv[:largo]) == verbo and not es_ayuda(argv)
        ]

    @property
    def traduccion(self) -> list[str]:
        """La traducción del dictado: los comandos que escriben, en orden.

        Es la primera de las tres evidencias del epic 003 y la única que dice
        **cómo** llegó el agente al resultado. Dos agentes pueden dejar el mismo
        vault por caminos distintos, y uno de los dos estar mal: escribir el
        registro antes que su consecuencia no es un detalle de estilo, es lo que
        hace que la consecuencia se aplique releyendo lo escrito.

        Deja fuera lo que solo lee. Un `tuku entry create --help` antes de usarlo, o
        un `tuku doctor` al terminar, no son parte de la traducción.
        """
        return [verbo(argv) for argv in self.traza if escribe(argv)]

    @property
    def reintentos(self) -> list[str]:
        """Las invocaciones idénticas y seguidas: la misma llamada, repetida.

        No son dos hechos. Todo lo que escribe en TUKU es idempotente, así que
        la segunda no cambia el vault; es el arnés reintentando algo que ya
        había ocurrido. Un comando **distinto** de más sí es un defecto, y por
        eso se separan en vez de contarse juntos.
        """
        return [
            shlex.join(["tuku", *argv])
            for previa, argv in zip(self.traza, self.traza[1:], strict=False)
            if previa == argv
        ]

    @property
    def traduccion_sin_reintentos(self) -> list[str]:
        """La traducción con las repeticiones idénticas colapsadas.

        Lo que el dictado exigía, mirado sin el ruido del arnés. Colapsa los
        intentos consecutivos sobre **el mismo hecho**, no solo las llamadas
        idénticas: un `note create` rechazado por faltarle el cuerpo y su
        repetición con `--body` son una nota, escrita al segundo intento.

        Los escenarios que comparan contra el vault del 002 usan esta; el que
        quiera afirmar que no hubo reintentos lo dice aparte, con `reintentos`.
        """
        vistos: list[list[str]] = []
        for argv in self.traza:
            if not vistos or _sujeto(vistos[-1]) != _sujeto(argv):
                vistos.append(argv)
            else:
                # Mismo hecho, otra vez: se queda el último intento, que es el
                # que quedó escrito.
                vistos[-1] = argv
        return Turno(prompt="", codigo=0, stdout="", stderr="", traza=vistos).traduccion

    @property
    def escribio_a_mano(self) -> bool:
        """Si el vault cambió por fuera de `tuku`, el escenario ya no prueba nada.

        No se responde desde acá: lo dice el `delta` del escenario comparado con
        lo que la traza explica. Queda como recordatorio de que la traza sola no
        alcanza, y por eso las tres evidencias del epic son tres.
        """
        raise NotImplementedError("lo afirma el escenario con su delta, no el arnés")


def modelo_barato(nombre: str, ejecutable: str) -> str | None:
    """El identificador más barato que el arnés diga tener, o `None`.

    `None` es una respuesta válida y significa "corre con tu default": vale más
    eso que inventarse un identificador que el CLI va a rechazar.
    """
    if nombre in _MODELOS:
        return _MODELOS[nombre]
    plantilla = ARNESES[nombre]
    hallado: str | None = None
    if "listar" in plantilla:
        salida = subprocess.run(
            [ejecutable, *plantilla["listar"]], capture_output=True, text=True, timeout=60
        )
        ids = [x.split()[0] for x in salida.stdout.splitlines() if x.split()]
        # Por segmento del identificador: `mini` está dentro de `gemini`.
        baratos = [x for x in ids if any(b in x.lower().split("-") for b in BARATOS)]
        # Algunos arneses codifican el esfuerzo en el propio identificador
        # (`gemini-3.8-flash-low`), y ahí la lista viene de mayor a menor: sin
        # esta preferencia se elige el más caro de la familia más barata.
        hallado = next(
            (x for x in baratos if x.lower().endswith(f"-{ESFUERZO}")),
            next(iter(baratos), None),
        )
    else:
        salida = subprocess.run(
            [
                ejecutable,
                *plantilla["aislar"],
                *[a.format(prompt=DIME_TU_MODELO) for a in plantilla["prompt"]],
            ],
            capture_output=True,
            text=True,
            timeout=180,
        )
        respuesta = salida.stdout.strip().splitlines()
        hallado = respuesta[-1].strip() if respuesta else None
        if hallado and (" " in hallado or len(hallado) > 60):
            hallado = None  # contestó una frase: no es un identificador
    _MODELOS[nombre] = hallado
    return hallado


def configurado() -> Arnes:
    """El arnés que dice el entorno, con `agy` por defecto.

    `TUKU_AGENTE` elige cuál, `TUKU_AGENTE_BIN` el ejecutable, `TUKU_AGENTE_MODELO`
    el modelo y `TUKU_AGENTE_PERFIL` el perfil, donde el arnés tenga perfiles.
    """
    nombre = os.environ.get("TUKU_AGENTE", "agy")
    if nombre not in ARNESES:
        conocidos = ", ".join(sorted(ARNESES))
        raise ArnesNoDisponible(
            f"TUKU_AGENTE={nombre!r} no es un arnés conocido. Hay: {conocidos}. "
            f"Para agregar uno, dile a `ARNESES` cómo se le pasa un turno."
        )
    return Arnes(
        nombre=nombre,
        ejecutable=os.environ.get("TUKU_AGENTE_BIN", nombre),
        modelo=os.environ.get("TUKU_AGENTE_MODELO"),
        perfil=os.environ.get("TUKU_AGENTE_PERFIL", PERFIL),
        esfuerzo=os.environ.get("TUKU_AGENTE_ESFUERZO", ESFUERZO),
    )


#: Dónde guarda cada arnés sus reglas de permiso y la que necesita el shim. Sin ella,
#: el primer `tuku` del agente se rechaza en headless y el turno termina vacío.
_REGLA_DE_PERMISO = {
    "agy": (Path(".gemini") / "antigravity-cli" / "settings.json", "command(tuku)"),
}


def _falta_permiso(nombre: str) -> str | None:
    """Por qué el arnés no dejaría correr `tuku`, o `None` si la regla está."""
    if nombre not in _REGLA_DE_PERMISO:
        return None
    ajustes, regla = _REGLA_DE_PERMISO[nombre]
    ruta = Path.home() / ajustes
    try:
        permitidas = json.loads(ruta.read_text(encoding="utf-8"))["permissions"]["allow"]
    except OSError, ValueError, KeyError, TypeError:
        permitidas = []
    if regla in permitidas:
        return None
    return (
        f"{nombre} no puede ejecutar `tuku` sin pedir permiso. Agrega {regla!r} a "
        f"permissions.allow en ~/{ajustes}."
    )


def motivo_no_disponible() -> str | None:
    """Por qué no se puede correr un turno, o `None` si sí se puede."""
    try:
        arnes = configurado()
    except ArnesNoDisponible as e:
        return str(e)
    if shutil.which(arnes.ejecutable) is None:
        return (
            f"no hay {arnes.ejecutable!r} en el PATH. Instálalo, o apunta a otro arnés "
            f"con TUKU_AGENTE (hay: {', '.join(sorted(ARNESES))})."
        )
    return _falta_permiso(arnes.nombre)


def disponible() -> bool:
    return motivo_no_disponible() is None


#: El shim. Anota `argv` y el directorio desde donde se llamó, y delega en el
#: `tuku` del checkout. Importa `main` en vez de reinvocar un ejecutable para no
#: depender de que TUKU esté instalado en la máquina que corre la suite.
#:
#: **El intérprete va escrito, no buscado.** Con `#!/usr/bin/env python3` el shim
#: dependía de que el `python3` del `PATH` fuera el de la suite, y dejó de serlo
#: en cuanto el arnés empezó a limpiarle el entorno al agente: el shim reventaba
#: sin dependencias y el agente, con razón, se iba a buscar otro `tuku`.
_EJECUTOR = """#!{python}
import json, os, sys
sys.path.insert(0, {src!r})
sys.path.insert(0, {scripts!r})
try:
    cwd = os.getcwd()
except Exception:
    cwd = os.environ.get("PWD", "")
from tuku.cli import main
import tiempo
ahora = os.environ.get("TUKU_NOW")
if ahora:
    print("nota: la fecha de hoy en este entorno es " + ahora + " (simulada)", file=sys.stderr)
try:
    with tiempo.congelar(ahora):
        codigo = main(sys.argv[1:])
except SystemExit as e:
    codigo = e.code if isinstance(e.code, int) else 1
traza_path = os.environ.get("TUKU_TRAZA")
if traza_path:
    anotacion = {{"argv": sys.argv[1:], "cwd": cwd, "codigo": codigo}}
    with open(traza_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(anotacion, ensure_ascii=False) + "\\n")
sys.exit(codigo)
"""


#: Lo que el agente ejecuta cuando escribe `tuku`: reenvía la llamada al puente.
#:
#: El sandbox del arnés impide leer el checkout y escribir en el vault desde un
#: comando de shell, así que un `tuku` que hiciera el trabajo ahí dentro
#: fallaría en su primera llamada y el agente, creyendo que no existe, lo
#: depuraría o editaría a mano. Este cliente solo necesita la biblioteca estándar
#: y un socket; el trabajo lo hace el puente, fuera del sandbox.
_CLIENTE = """#!{python}
import json, os, socket, sys
s = socket.socket(socket.AF_UNIX)
s.connect({socket!r})
s.sendall(json.dumps({{"argv": sys.argv[1:], "cwd": os.getcwd()}}).encode() + b"\\n")
datos = b""
while True:
    trozo = s.recv(65536)
    if not trozo:
        break
    datos += trozo
r = json.loads(datos)
sys.stdout.write(r["stdout"])
sys.stderr.write(r["stderr"])
sys.exit(r["codigo"])
"""


#: Una función de shell que llama al shim por ruta absoluta, para los arneses
#: que ejecutan en **shell de login**.
#:
#: Anteponer el shim al `PATH` no alcanza: un `bash -l` relee el perfil del
#: usuario, y un perfil que hace `export PATH="~/.local/bin:$PATH"` (el de esta
#: máquina, y el que deja `uv tool install`) vuelve a poner el `tuku` instalado
#: delante del shim. El agente ejecutaba el comando correcto contra el TUKU
#: equivocado y la traza quedaba vacía, que es el fallo que `gherkin` denuncia.
#:
#: Una función gana a cualquier `PATH` porque bash la resuelve antes, y el
#: perfil del usuario no la pisa. Se exporta para que la hereden los subshells,
#: y `declare -f` la conserva en los arneses que fotografían el entorno.
_FUNCION_SHIM = 'tuku() {{ "{shim}" "$@"; }}\nexport -f tuku 2>/dev/null || true\n'


def _sembrar_shim(dir: Path) -> Path:
    """Deja en `dir` el `tuku` del agente y el ejecutor real, y devuelve el archivo de traza."""
    ejecutor = dir / "ejecutor.py"
    ejecutor.write_text(
        _EJECUTOR.format(
            python=sys.executable,
            src=str(RAIZ_REPO / "src"),
            scripts=str(Path(__file__).parent),
        ),
        encoding="utf-8",
    )
    shim = dir / "tuku"
    shim.write_text(
        _CLIENTE.format(
            python=getattr(sys, "_base_executable", sys.executable),
            socket=str(dir / "puente.sock"),
        ),
        encoding="utf-8",
    )
    shim.chmod(0o755)
    (dir / "shim.bash").write_text(_FUNCION_SHIM.format(shim=shim), encoding="utf-8")
    return dir / "traza.jsonl"


class Puente:
    """Ejecuta los `tuku` del agente fuera de su sandbox y le devuelve la salida.

    Escucha en `puente.sock`, dentro del directorio del shim. Cada llamada corre
    el ejecutor con el entorno de la prueba y en el directorio desde el que la
    hizo el agente.
    """

    def __init__(self, dir: Path, entorno: dict[str, str]) -> None:
        self.ejecutor = dir / "ejecutor.py"
        self.entorno = entorno
        self.servidor = socketserver.ThreadingUnixStreamServer(
            str(dir / "puente.sock"), self._manejador()
        )
        self.servidor.daemon_threads = True

    def _manejador(self) -> type[socketserver.StreamRequestHandler]:
        puente = self

        class Manejador(socketserver.StreamRequestHandler):
            def handle(self) -> None:
                pedido = json.loads(self.rfile.readline())
                p = subprocess.run(
                    [sys.executable, str(puente.ejecutor), *pedido["argv"]],
                    cwd=pedido["cwd"],
                    env=puente.entorno,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                respuesta = {"codigo": p.returncode, "stdout": p.stdout, "stderr": p.stderr}
                self.wfile.write(json.dumps(respuesta).encode())

        return Manejador

    def __enter__(self) -> Puente:
        threading.Thread(target=self.servidor.serve_forever, daemon=True).start()
        return self

    def __exit__(self, *_: object) -> None:
        self.servidor.shutdown()
        self.servidor.server_close()


def _leer_traza(traza: Path) -> list[list[str]]:
    if not traza.is_file():
        return []
    lineas = traza.read_text(encoding="utf-8").splitlines()
    anotaciones = [json.loads(linea) for linea in lineas if linea.strip()]
    # Un comando que salió con error no escribió nada: no es parte de la traducción.
    return [x["argv"] for x in anotaciones if x.get("codigo", 0) == 0]


def _conversacion(arnes: Arnes, vault: Path, entorno: dict[str, str]) -> str:
    """Lo que el agente fue diciendo durante el turno, si el arnés sabe darlo.

    Nunca hace fallar un turno. Es evidencia para leer a mano, no una aserción:
    un arnés que no exporte su sesión, o que cambie el formato, deja el archivo
    con lo que haya y el escenario sigue afirmando sobre la traza y el diff.
    """
    export = ARNESES[arnes.nombre].get("sesion")
    if not export:
        return ""
    argv = [
        arnes.ejecutable,
        *(a.format(perfil=arnes.perfil, cwd=str(vault)) for a in export),
    ]
    try:
        p = subprocess.run(
            argv, env=entorno, capture_output=True, text=True, timeout=60, check=False
        )
    except (subprocess.TimeoutExpired, OSError) as e:
        return f"(no se pudo exportar la sesión: {e})"
    return p.stdout if p.returncode == 0 else f"(el export salió {p.returncode})\n{p.stderr}"


def con_reloj(prompt: str, ahora: str | None) -> str:
    """El turno precedido por la fecha y hora simuladas, como las da un cliente real.

    El agente no ve el `TUKU_NOW` del shim hasta que corre un `tuku`, y para
    entonces ya eligió el día y la hora de `--at` con el reloj de la máquina.
    """
    return f"(Hoy es {ahora}.)\n{prompt}" if ahora else prompt


def _correr_en_vivo(
    argv: list[str],
    cwd: Path,
    entorno: dict[str, str],
    espera: int,
    en_vivo: Callable[[str], None] | None,
    en_error: Callable[[str], None] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Corre el arnés y entrega cada línea de `stdout` a `en_vivo` y de `stderr` a `en_error`.

    Si pasa de `espera` segundos lo mata y levanta `TimeoutExpired` con lo que
    alcanzó a salir, igual que `subprocess.run`.
    """
    p = subprocess.Popen(
        argv,
        cwd=cwd,
        env=entorno,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    assert p.stdout is not None and p.stderr is not None
    stdout, stderr = p.stdout, p.stderr
    vencio = threading.Event()

    def _matar() -> None:
        vencio.set()
        p.kill()

    errores: list[str] = []

    def _leer_errores() -> None:
        for linea in stderr:
            errores.append(linea)
            if en_error is not None:
                en_error(linea.rstrip("\n"))

    lector = threading.Thread(target=_leer_errores, daemon=True)
    lector.start()
    reloj = threading.Timer(espera, _matar)
    reloj.start()
    salida: list[str] = []
    try:
        for linea in stdout:
            salida.append(linea)
            if en_vivo is not None:
                en_vivo(linea.rstrip("\n"))
        p.wait()
    except BaseException:
        # Un Ctrl-C a mitad de turno no puede dejar al agente escribiendo en el vault.
        p.kill()
        p.wait()
        raise
    finally:
        reloj.cancel()
        lector.join(timeout=5)
        stdout.close()
        stderr.close()
    if vencio.is_set():
        raise subprocess.TimeoutExpired(argv, espera, output="".join(salida))
    return subprocess.CompletedProcess(argv, p.returncode, "".join(salida), "".join(errores))


def turno(
    vault: Path,
    prompt: str,
    timeout: int | None = None,
    ahora: str | None = None,
    sesion: Sesion | None = None,
    en_vivo: Callable[[str], None] | None = None,
    en_error: Callable[[str], None] | None = None,
) -> Turno:
    """Un turno del agente dentro de `vault`, con la traza de lo que ejecutó.

    El agente corre **dentro del vault**, que es como se opera en la vida real:
    lee su `AGENTS.md` porque está ahí, no porque el prompt se lo pegue. Un prompt
    que explique lo que el `AGENTS.md` ya dice invalida el escenario.

    `ahora` (`AAAA-MM-DD HH:MM`) es la fecha simulada: el shim la aplica a cada
    `tuku` que el agente ejecuta y la anuncia por `stderr`, así el agente sabe
    que ese es el día de hoy.

    Con `sesion`, el turno retoma la conversación del anterior y deja en ella el
    id del arnés. Con `en_vivo` y `en_error`, cada línea que el arnés escribe por
    `stdout` y por `stderr` llega a esas funciones cuando sale y no al final del turno.
    """
    motivo = motivo_no_disponible()
    if motivo is not None:
        raise ArnesNoDisponible(motivo)
    arnes = configurado()
    plantilla = ARNESES[arnes.nombre]
    if sesion is None and "json" in plantilla and "continuar" in plantilla:
        # Salida estructurada aunque nadie retome la conversación: deja la traza.
        sesion = Sesion()

    with tempfile.TemporaryDirectory(prefix="tuku-shim-") as tmp:
        bin = Path(tmp)
        traza = _sembrar_shim(bin)
        base = {
            **{k: v for k, v in os.environ.items() if k not in DEL_RUNNER},
            "TUKU_TRAZA": str(traza),
            "TUKU_HOME": str(RAIZ_REPO),
            **({"TUKU_NOW": ahora} if ahora else {}),
        }
        entorno = {
            **base,
            "PATH": f"{bin}{os.pathsep}{_path_sin_venv()}",
            # Lo que bash no-interactivo sourcea al arrancar. Es por dónde entra
            # la función del shim en los arneses que ejecutan por shell de login.
            "BASH_ENV": str(bin / "shim.bash"),
            "ENV": str(bin / "shim.bash"),
        }
        espera = timeout or int(os.environ.get("TUKU_AGENTE_TIMEOUT", TIMEOUT))
        try:
            with Puente(bin, base):
                argv = arnes.argv(con_reloj(prompt, ahora), sesion)
                if en_vivo is not None or en_error is not None:
                    p = _correr_en_vivo(argv, vault, entorno, espera, en_vivo, en_error)
                else:
                    p = subprocess.run(
                        argv,
                        cwd=vault,
                        env=entorno,
                        capture_output=True,
                        text=True,
                        timeout=espera,
                        check=False,
                    )
        except subprocess.TimeoutExpired as e:
            parcial = (
                e.stdout.decode("utf-8", "replace") if isinstance(e.stdout, bytes) else e.stdout
            )
            return Turno(
                prompt=prompt,
                codigo=124,
                stdout="",
                stderr=f"el turno pasó de {espera}s sin terminar",
                traza=_leer_traza(traza),
                conversacion=pasos_de(parcial or ""),
                crudo=parcial or "",
            )
        stdout = leer_sesion(p.stdout, sesion) if sesion is not None else p.stdout
        return Turno(
            prompt=prompt,
            codigo=p.returncode,
            stdout=stdout,
            stderr=p.stderr,
            traza=_leer_traza(traza),
            conversacion=_conversacion(arnes, vault, entorno) or pasos_de(p.stdout),
            crudo=p.stdout,
        )


if __name__ == "__main__":
    motivo = motivo_no_disponible()
    if motivo is not None:
        print(f"arnés no disponible: {motivo}")
        sys.exit(1)
    arnes = configurado()
    print(f"arnés: {arnes.nombre} ({arnes.ejecutable}), modelo: {arnes.modelo or 'el suyo'}")
    print(f"un turno se invoca así: {arnes.argv('<el turno>')}")
