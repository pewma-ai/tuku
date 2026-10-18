"""Una conversación del epic 004 en pantalla, mientras corre.

Quien hace de Damián es Claude (Sonnet, esfuerzo bajo), que recibe el plan del
escenario y dice lo que toca en cada turno. Responde el agente del arnés, y todo
lo que escribe el arnés se muestra apenas llega: lo que dice, cada comando que
ejecuta con su salida, y lo que tardó cada paso.

La parte que decide qué se muestra (`Vista`) y la que lee el escenario
(`leer_plan`, `base_del`) no llaman a ningún modelo, y por eso se prueban en
`tests/test_tui.py`.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TextIO

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent
ESCENARIOS = RAIZ_REPO / "tests" / "escenarios"
PERSONA = RAIZ_REPO / "corpus" / "referencia" / "referencia-faena.md"

_AUTOR = re.compile(r'^```autor(?:\s+TUKU_NOW="([^"]*)")?\s*$')
_ITEM = re.compile(r"^(\d+)\.\s+(.*)$")
_TITULO = re.compile(r"^##\s+Escenario:\s*(.+?)\s*$")
_FILA = re.compile(r"^\|\s*(\d+)\s*\|[^|]*\|\s*(.+?)\s*\|\s*$")
_COMANDO = re.compile(r"`(?:tuku\s+)?((?:scope|todo|entry|note|cycle)\s+\w+)[^`]*`")
_COPIA = re.compile(r"^cp -r \.\./\.\./([^/\s]+)/([^/\s]+)/mi-vault \.$")


class EscenarioNoEncontrado(LookupError):
    """No hay un `.md` con ese id, o no es una conversación."""


@dataclass
class Esperado:
    """Lo que la tabla del escenario espera de un turno."""

    cambia: bool
    comandos: list[str]  #: los comandos `tuku` que tienen que aparecer entre los que escriben
    texto: str


@dataclass
class Plan:
    """Lo que el escenario le pide a Damián."""

    archivo: Path
    titulo: str
    ahora: str
    pasos: list[str]
    base: tuple[str, str] | None  #: carpeta y escenario del vault de partida
    esperado: dict[int, Esperado]  #: la columna «Delta del vault» de la tabla, por turno
    a_mano: list[str]  #: lo que el escenario deja para juzgar leyendo


def leer_plan(id: str) -> Plan:
    """El plan del escenario `id` (por ejemplo `004-03`), leído de su `.md`."""
    hallados = sorted(ESCENARIOS.glob(f"{id}-*.md"))
    if len(hallados) != 1:
        raise EscenarioNoEncontrado(
            f"hay {len(hallados)} escenarios que empiezan con {id!r} en {ESCENARIOS}"
        )
    archivo = hallados[0]
    titulo, ahora, pasos, base = "", "", [], None
    esperado: dict[int, Esperado] = {}
    a_mano: list[str] = []
    en_plan = en_tabla = en_mano = False
    for linea in archivo.read_text(encoding="utf-8").splitlines():
        if not titulo and (m := _TITULO.match(linea)):
            titulo = m.group(1)
        if en_plan:
            if linea.startswith("```"):
                en_plan = False
            elif m := _ITEM.match(linea):
                pasos.append(m.group(2))
            continue
        if m := _AUTOR.match(linea):
            en_plan, ahora = True, m.group(1) or ""
        elif m := _COPIA.match(linea):
            base = (m.group(1), m.group(2))
        elif linea.startswith("|") and "Delta del vault" in linea:
            en_tabla = True
        elif en_tabla and (m := _FILA.match(linea)):
            esperado[int(m.group(1))] = _esperado(m.group(2))
        elif en_tabla and not linea.startswith("|"):
            en_tabla = False
        if linea.startswith("## "):
            en_mano = linea.startswith("## Qué se mira a mano")
        elif en_mano and linea.startswith("- "):
            a_mano.append(linea[2:].strip())
    if not pasos:
        raise EscenarioNoEncontrado(f"{archivo.name} no tiene un plan ```autor``` con pasos")
    return Plan(archivo, titulo, ahora, pasos, base, esperado, a_mano)


def _esperado(celda: str) -> Esperado:
    """Lee la celda «Delta del vault»: `vacío…`, o lo que el turno tiene que escribir."""
    if celda.lower().startswith("vacío"):
        return Esperado(False, [], celda)
    comandos = list(dict.fromkeys(m.group(1) for m in _COMANDO.finditer(celda)))
    if not comandos:
        if re.search(r"\bcierres?\b", celda):
            comandos.append("todo close")
        if re.search(r"\bregistros?\b", celda):
            comandos.append("entry create")
        if re.search(r"\bpendientes?\b", celda) and "todo close" not in comandos:
            comandos.append("todo open")
    return Esperado(True, comandos, celda)


def zona_del_vault(vault: Path) -> str | None:
    """El campo `TZ` de `reglas/config.tuku.md` del vault, o `None` si no lo dice."""
    from tuku.config import parsear_config_md

    ruta = vault / "reglas" / "config.tuku.md"
    if not ruta.is_file():
        return None
    zona = parsear_config_md(ruta.read_text(encoding="utf-8")).get("TZ", "").strip("`")
    return zona or None


def _lugar(zona: str | None) -> str:
    """Cómo se le dice al modelo en qué español escribe: que lo infiera de la zona horaria."""
    if not zona:
        return "natural"
    return f"natural del país que corresponde a la zona horaria {zona}"


def prompt_de_damian(
    plan: Plan,
    historia: list[tuple[str, str]],
    n: int,
    persona: str | None = None,
    zona: str | None = None,
) -> str:
    """Lo que se le pide a quien hace de Damián en el turno `n`.

    Recibe **solo el paso que toca**. Con el plan entero, el modelo se adelanta a
    los pasos siguientes y ratifica en el primer turno.
    """
    quien = persona if persona is not None else _persona()
    dicho = "\n".join(f"Damián: {d}\nAgente: {a}" for d, a in historia) or "(nada todavía)"
    return (
        f"Eres Damián Ulloa conversando por chat con el agente de TUKU, que lleva tu "
        f"bitácora. Hoy es {plan.ahora}.\n\n"
        f"Quién eres:\n{quien}\n\n"
        f"Lo que ya se dijo:\n{dicho}\n\n"
        f"Ahora, en el turno {n}, lo que debes decir es esto (en tus palabras, sin "
        f"agregar nada que no esté acá):\n{plan.pasos[n - 1]}\n\n"
        f"Escribe SOLO lo que Damián le dice al agente: una o dos frases en español "
        f"{_lugar(zona)}, como las diría al chat, sin comillas, sin etiquetas como "
        "«Ratificado:», sin explicar y sin mencionar que sigues un plan. Si lo que "
        "debes decir responde algo que el agente preguntó, apóyate en su última "
        "respuesta.\n\n"
        "Entrega la frase entre las etiquetas <damian> y </damian>, y nada fuera de ellas."
    )


def _persona() -> str:
    """El apartado «El usuario» del corpus: quién es Damián."""
    texto = PERSONA.read_text(encoding="utf-8")
    return texto.split("## El usuario", 1)[1].split("\n---", 1)[0].strip()


def extraer_frase(salida: str) -> str:
    """La frase entre `<damian>` y `</damian>`; sin etiquetas, la salida entera.

    Sin ellas, el modelo a veces antepone un comentario sobre la tarea que no es parte
    de lo que Damián dice.
    """
    m = re.search(r"<damian>(.*?)</damian>", salida, re.S)
    return (m.group(1) if m else salida).strip()


def frase_de_damian(prompt: str, modelo: str = "sonnet", esfuerzo: str = "low") -> str:
    """Lo que dice Damián, según Claude. El prompt entra por `stdin`."""
    p = subprocess.run(
        [
            "claude",
            "-p",
            "--model",
            modelo,
            "--effort",
            esfuerzo,
            "--setting-sources",
            "",
            "--strict-mcp-config",
            "--tools",
            "",
        ],
        input=prompt,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if p.returncode != 0 or not p.stdout.strip():
        raise RuntimeError(
            f"Claude no contestó como Damián: {p.stderr.strip() or p.returncode}"
        )
    return extraer_frase(p.stdout)


_RESET = "\033[0m"
_ESTILOS = {
    "tenue": "\033[2m",
    "negrita": "\033[1m",
    "verde": "\033[32m",
    "cian": "\033[36m",
    "amarillo": "\033[33m",
    "rojo": "\033[31m",
    "magenta": "\033[35m",
}


class Vista:
    """Dibuja en pantalla lo que va llegando del arnés, línea a línea.

    Entiende el `stream-json` de `agy`: `init`, `step_update` (la respuesta del
    agente en pedazos, y cada herramienta con su salida) y `result`. Con `raw`
    imprime las líneas tal cual llegan.
    """

    def __init__(
        self,
        salida: TextIO | None = None,
        color: bool | None = None,
        raw: bool = False,
        max_lineas: int = 14,
    ) -> None:
        self.salida = salida or sys.stdout
        self.color = self.salida.isatty() if color is None else color
        self.raw = raw
        self.max_lineas = max_lineas
        self._escribiendo: int | None = None  #: paso de respuesta en curso
        self._anunciados: set[int] = set()
        self._cerrojo = threading.RLock()  #: stdout y stderr llegan en hilos distintos

    def _estilo(self, texto: str, *estilos: str) -> str:
        if not self.color or not estilos:
            return texto
        return "".join(_ESTILOS[e] for e in estilos) + texto + _RESET

    def _linea(self, texto: str = "", *estilos: str) -> None:
        self._cerrar_texto()
        self.salida.write(self._estilo(texto, *estilos) + "\n")
        self.salida.flush()

    def _cerrar_texto(self) -> None:
        if self._escribiendo is not None:
            self.salida.write("\n")
            self._escribiendo = None

    def turno(self, n: int, total: int, ahora: str) -> None:
        self._linea()
        self._linea(f"━━ Turno {n}/{total} · {ahora} ━━", "negrita")

    def damian(self, frase: str, segundos: float | None = None) -> None:
        cuanto = f" ({segundos:.1f} s)" if segundos is not None else ""
        self._linea(f"Damián{cuanto}", "amarillo", "negrita")
        for x in frase.splitlines() or [""]:
            self._linea(f"  {x}", "amarillo")

    def nota(self, texto: str) -> None:
        self._linea(texto, "tenue")

    def evento(self, linea: str) -> None:
        with self._cerrojo:
            self._evento(linea)

    def error(self, linea: str) -> None:
        """Una línea del `stderr` del arnés, en rojo. Si no hay, no se muestra nada."""
        if linea.strip():
            with self._cerrojo:
                self._linea(f"agy stderr: {linea}", "rojo")

    def _evento(self, linea: str) -> None:
        if self.raw:
            self._linea(linea)
            return
        try:
            e = json.loads(linea)
        except json.JSONDecodeError:
            self._linea(linea, "tenue")
            return
        if not isinstance(e, dict):
            self._linea(linea, "tenue")
            return
        tipo = e.get("event")
        if tipo == "init":
            i = e.get("init", {})
            self._linea(f"agente · {i.get('model', '?')} · {i.get('cwd', '')}", "tenue")
        elif tipo == "step_update":
            self._paso(e.get("step_update", {}))
        elif tipo == "result":
            r = e.get("result", {})
            llamadas = r.get("num_turns")
            self._linea(
                f"fin del turno · {r.get('status', '?')} · {_seg(r.get('duration_seconds'))}"
                + (
                    f" · {llamadas} {'llamada' if llamadas == 1 else 'llamadas'}"
                    if llamadas is not None
                    else ""
                ),
                "tenue",
            )
            u = r.get("usage") or {}
            if u:
                self._linea(
                    f"tokens · entrada {u.get('input_tokens', '?')} · "
                    f"salida {u.get('output_tokens', '?')} · "
                    f"razonamiento {u.get('thinking_tokens', '?')} · "
                    f"caché {u.get('cache_read_tokens', '?')} · "
                    f"total {u.get('total_tokens', '?')}",
                    "tenue",
                )

    def _paso(self, s: dict[str, Any]) -> None:
        tipo, indice, estado = s.get("step_type"), s.get("step_index"), s.get("state")
        if tipo == "agent_response":
            texto = s.get("text_delta") or ""
            if estado == "DONE":
                texto = texto.rstrip("\n")
            if texto.strip() or self._escribiendo is not None:
                if self._escribiendo is None:
                    self._cerrar_texto()
                    self.salida.write(self._estilo("Agente\n  ", "cian", "negrita"))
                    self._escribiendo = indice if isinstance(indice, int) else -1
                self.salida.write(self._estilo(texto.replace("\n", "\n  "), "cian"))
                self.salida.flush()
            if estado == "DONE":
                u = s.get("usage") or {}
                con_texto = self._escribiendo is not None
                self._linea(
                    f"  {'' if con_texto else 'modelo · '}{_seg(s.get('duration_seconds'))} · "
                    f"{u.get('input_tokens', '?')} → {u.get('output_tokens', '?')} tokens",
                    "tenue",
                )
        elif tipo == "tool":
            info = s.get("tool_info") or {}
            if isinstance(indice, int) and indice not in self._anunciados:
                self._anunciados.add(indice)
                self._linea(f"  {_llamada(info)}", "verde" if _es_tuku(info) else "magenta")
            if estado == "DONE":
                salida = info.get("output")
                if salida:
                    self._salida_de_herramienta(str(salida))
                self._linea(f"  {_seg(s.get('duration_seconds'))}", "tenue")
        elif estado == "DONE" and tipo not in ("user_input", "system_message"):
            self._linea(f"  · {tipo}", "tenue")

    def _salida_de_herramienta(self, salida: str) -> None:
        lineas = salida.replace("\r\n", "\n").rstrip("\n").split("\n")
        for x in lineas[: self.max_lineas]:
            self._linea(f"    {x}", "tenue")
        if len(lineas) > self.max_lineas:
            self._linea(f"    … {len(lineas) - self.max_lineas} líneas más", "tenue")

    def conclusion(self, c: Conclusion, plan: Plan, log: Path) -> None:
        self._linea()
        self._linea("━━ Conclusión ━━", "negrita")
        for ok, texto in c.chequeos:
            self._linea(f"  {'✓' if ok else '✗'} {texto}", "verde" if ok else "rojo")
        malos = sum(1 for ok, _ in c.chequeos if not ok)
        parcial = " (corrida parcial: faltan turnos del plan)" if c.parcial else ""
        if c.ok:
            self._linea(f"FUNCIONÓ{parcial}", "verde", "negrita")
        else:
            self._linea(f"NO FUNCIONÓ: {malos} chequeo(s) fallaron{parcial}", "rojo", "negrita")
        if plan.a_mano:
            self._linea("Queda por leer a mano (no se verifica solo):", "tenue")
            for x in plan.a_mano:
                self._linea(f"  - {x}", "tenue")
        self._linea(f"  conversación: {log}", "tenue")

    def cierre(self, registro: dict[str, Any]) -> None:
        escribe = registro["escribe"]
        self._linea(
            "Comandos que escriben: " + ("; ".join(escribe) if escribe else "ninguno"), "verde"
        )
        delta = registro["delta"]
        if delta:
            self._linea("Delta del vault:", "negrita")
            for ruta, cambio in delta.items():
                self._linea(f"  {ruta}: {cambio}")
        else:
            self._linea("Delta del vault: vacío", "tenue")


def _seg(valor: Any) -> str:
    try:
        return f"{float(valor):.1f} s"
    except TypeError, ValueError:
        return "? s"


def _es_tuku(info: dict[str, Any]) -> bool:
    return (
        str((info.get("parameters") or {}).get("CommandLine", "")).lstrip().startswith("tuku")
    )


def _llamada(info: dict[str, Any]) -> str:
    params = info.get("parameters") or {}
    if "CommandLine" in params:
        return f"$ {params['CommandLine']}"
    args = " ".join(f"{k}={v}" for k, v in params.items())
    return f"{info.get('name', 'herramienta')} {args}".rstrip()


@dataclass
class Conclusion:
    """Si la conversación hizo lo que el escenario espera, y por qué no."""

    ok: bool
    chequeos: list[tuple[bool, str]]
    parcial: bool


def evaluar(plan: Plan, turnos: list[dict[str, Any]], doctor: tuple[int, str]) -> Conclusion:
    """Contrasta cada turno con la tabla del escenario y comprueba el vault al final.

    Lo que se puede afirmar sin leer: que un turno vacío no cambió nada, que uno
    que escribe trae el comando que la tabla nombra, que cada cambio tiene su
    comando `tuku` en la traza y que `tuku doctor` queda sano. Lo demás (si la
    pregunta del agente era la correcta) lo juzga quien lee.
    """
    chequeos: list[tuple[bool, str]] = []
    for n, t in enumerate(turnos, start=1):
        if t.get("codigo", 0) != 0:
            chequeos.append((False, f"Turno {n}: el arnés salió {t['codigo']}"))
        esperado = plan.esperado.get(n)
        if esperado is None:
            continue
        cambio = sorted(t["delta"])
        if not esperado.cambia:
            if cambio:
                chequeos.append(
                    (False, f"Turno {n}: la tabla dice vacío y cambió {', '.join(cambio)}")
                )
            else:
                chequeos.append((True, f"Turno {n}: vacío, como dice la tabla"))
            continue
        faltan = [c for c in esperado.comandos if not any(c in w for w in t["escribe"])]
        if not cambio:
            pedido = ", ".join(f"`{c}`" for c in esperado.comandos) or esperado.texto
            chequeos.append((False, f"Turno {n}: esperaba {pedido} y el vault no cambió"))
        elif faltan:
            nombres = ", ".join(f"`{c}`" for c in faltan)
            chequeos.append(
                (False, f"Turno {n}: esperaba {nombres} y no está entre lo que escribió")
            )
        else:
            chequeos.append(
                (True, f"Turno {n}: escribió lo que dice la tabla ({esperado.texto})")
            )
    salidas = [(n, t["fuera"]) for n, t in enumerate(turnos, 1) if t.get("fuera")]
    for n, fuera in salidas:
        vistas = ", ".join(f"`{f}`" for f in fuera[:3]) + (" …" if len(fuera) > 3 else "")
        chequeos.append(
            (False, f"Turno {n}: el agente salió del vault ({vistas}); el turno no prueba nada")
        )
    if not salidas:
        chequeos.append((True, "El agente no salió del vault"))
    sin_comando = [n for n, t in enumerate(turnos, 1) if t["delta"] and not t["escribe"]]
    for n in sin_comando:
        chequeos.append((False, f"Turno {n}: el vault cambió sin un comando tuku en la traza"))
    if not sin_comando:
        chequeos.append((True, "Cada cambio del vault tiene su comando tuku en la traza"))
    codigo, salida = doctor
    ultima = salida.strip().splitlines()[-1] if salida.strip() else ""
    chequeos.append(
        (codigo == 0, f"tuku doctor {'sano' if codigo == 0 else f'salió {codigo}'}: {ultima}")
    )
    return Conclusion(
        ok=all(ok for ok, _ in chequeos),
        chequeos=chequeos,
        parcial=len(turnos) < len(plan.pasos),
    )


_ARRANQUE = "import sys; from tuku.cli import main; sys.exit(main(sys.argv[1:]))"


def correr_doctor(vault: Path) -> tuple[int, str]:
    """`tuku doctor` sobre el vault, con el CLI del checkout."""
    p = subprocess.run(
        [sys.executable, "-c", _ARRANQUE, "doctor", "--vault", str(vault)],
        env={**os.environ, "TUKU_HOME": str(RAIZ_REPO)},
        capture_output=True,
        text=True,
        check=False,
    )
    return p.returncode, (p.stdout + p.stderr).strip()


def asegurar_base(plan: Plan) -> Path:
    """El vault de partida del escenario, generándolo si todavía no existe."""
    if plan.base is None:
        raise EscenarioNoEncontrado(
            f"{plan.archivo.name} no declara su vault de partida con `cp -r ../../…/mi-vault .`"
        )
    carpeta, escenario = plan.base
    base = RAIZ_REPO / "playground" / carpeta / escenario / "mi-vault"
    if not base.is_dir():
        prefijo = carpeta[:6].replace("-", "_")
        tests = sorted((ESCENARIOS).glob(f"test_{prefijo}_*.py"))
        if not tests:
            raise EscenarioNoEncontrado(f"no sé cómo generar {base}")
        subprocess.run([sys.executable, "-m", "pytest", str(tests[0]), "-q"], check=True)
    return base


def con_cronometro(f: Callable[[], str]) -> tuple[str, float]:
    inicio = time.monotonic()
    return f(), time.monotonic() - inicio
