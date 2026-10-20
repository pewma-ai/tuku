"""El tutorial de `docs/tutorial/` como prueba: sus pasos salen del propio capítulo.

Un capítulo se convierte en pasos. Cada `> [!tip]` es lo que dicta el autor, tal
cual; cada bloque `bash` es un comando que corre el arnés; cada `> [!check]` son
las afirmaciones sobre el vault que siguen al paso que lo precede. Un `check` en
una sección sin paso ejecutable (editar a mano) queda para leer.

Nada se copia a un escenario: si el capítulo cambia, la prueba cambia con él.
La parte que lee el capítulo (`leer_capitulo`) no llama a ningún modelo y se prueba
en `tests/test_tutorial.py`. Correr el agente y juzgar los `check` es lo caro.
"""

from __future__ import annotations

import os
import re
import shlex
import shutil
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import conversar
import tui
import vault as banco

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent
TUTORIAL = RAIZ_REPO / "docs" / "tutorial"
ESCENARIO = "tutorial"

#: El día de cada capítulo en la historia de Andrea. El 1 al 6 son su lunes.
DIAS = {
    1: "2026-08-17",
    2: "2026-08-17",
    3: "2026-08-17",
    4: "2026-08-17",
    5: "2026-08-17",
    6: "2026-08-17",
    7: "2026-08-18",
    8: "2026-08-21",
    9: "2026-08-21",
    10: "2026-08-31",
}
HORA_INICIAL = "08:30"
MINUTOS_POR_PASO = 10
APERTURA = "Buenos días."

_TIP = re.compile(r"^>\s*\[!tip\]\s*(.*)$")
_CHECK = re.compile(r"^>\s*\[!check\]")
_EDITA = re.compile(r"^>\s*\[!warning\]\s*Edita", re.I)
_ENCABEZADO = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
_NOMBRE = re.compile(r"^(\d{2})-(.+)\.md$")
_USO_ANTES = re.compile(r"uv tool install|pipx")
_ALTERNATIVA = re.compile(r"^O\s", re.I)  #: «O dile a tu agente»: otra forma del paso anterior


class CapituloNoEncontrado(LookupError):
    """No hay un capítulo con ese número."""


class EdicionInvalida(ValueError):
    """Una línea de un bloque ```edit que el arnés no entiende, o que no encuentra su blanco."""


@dataclass
class Paso:
    """Algo que el arnés hace, y lo que el capítulo afirma después."""

    tipo: str  #: `dictar`, `comando` o `manual`
    texto: str  #: la frase, el comando o el nombre de la sección
    seccion: str
    titulo: str = ""  #: el título del callout (`Dile a tu agente, el lunes`)
    checks: list[str] = field(default_factory=list)


@dataclass
class Capitulo:
    numero: int
    slug: str
    titulo: str
    archivo: Path
    pasos: list[Paso]

    @property
    def id(self) -> str:
        """Cómo se llama su carpeta en `playground/`: `010-02-registrar`."""
        return f"010-{self.numero:02d}-{self.slug}"


def archivos() -> dict[int, Path]:
    """Los capítulos numerados de `docs/tutorial/`, sin README ni conclusión."""
    salida: dict[int, Path] = {}
    for p in sorted(TUTORIAL.glob("*.md")):
        m = _NOMBRE.match(p.name)
        if m and m.group(1) != "99":
            salida[int(m.group(1))] = p
    return salida


def _cuerpo(lineas: list[str], i: int) -> tuple[list[str], int]:
    """Las líneas `>` que siguen a la apertura de un callout, sin el `>`."""
    cuerpo: list[str] = []
    i += 1
    while i < len(lineas) and lineas[i].startswith(">"):
        cuerpo.append(lineas[i][1:].strip())
        i += 1
    return cuerpo, i


def _frase(cuerpo: list[str]) -> str:
    """Los párrafos de un `tip` unidos por una línea en blanco."""
    return "\n\n".join(p for p in cuerpo if p)


def _afirmaciones(cuerpo: list[str]) -> list[str]:
    """Cada viñeta o fila de tabla de un `check`; la separación de tabla no cuenta."""
    salida: list[str] = []
    for linea in cuerpo:
        if not linea or re.fullmatch(r"\|[\s|:-]+\|", linea):
            continue
        salida.append(re.sub(r"^-\s+", "", linea))
    return salida


def _bloque_edit(cuerpo: list[str]) -> str:
    """Las líneas del bloque ```edit de un callout «Edita a mano»."""
    dentro = False
    lineas: list[str] = []
    for linea in cuerpo:
        if linea.startswith("```"):
            dentro = linea.startswith("```edit") and not dentro
        elif dentro and linea:
            lineas.append(linea)
    if not lineas:
        raise EdicionInvalida(
            "un «Edita a mano» sin bloque ```edit: el arnés no sabe qué editar"
        )
    return "\n".join(lineas)


def leer_capitulo(numero: int, archivo: Path | None = None) -> Capitulo:
    """Los pasos de un capítulo, en el orden en que aparecen."""
    if archivo is None:
        hallados = archivos()
        if numero not in hallados:
            raise CapituloNoEncontrado(
                f"no hay capítulo {numero}; hay del {min(hallados)} al {max(hallados)}"
            )
        archivo = hallados[numero]
    lineas = archivo.read_text(encoding="utf-8").splitlines()
    m = _NOMBRE.match(archivo.name)
    slug = m.group(2) if m else archivo.stem
    titulo = ""
    seccion = ""
    subseccion = False
    pasos: list[Paso] = []
    i = 0
    while i < len(lineas):
        linea = lineas[i]
        if enc := _ENCABEZADO.match(linea):
            if len(enc.group(1)) == 1:
                titulo = enc.group(2)
            else:
                seccion = enc.group(2)
                subseccion = len(enc.group(1)) > 2
            i += 1
        elif tip := _TIP.match(linea):
            cuerpo, i = _cuerpo(lineas, i)
            titulo_tip = tip.group(1).strip()
            if not _ALTERNATIVA.match(titulo_tip):
                pasos.append(Paso("dictar", _frase(cuerpo), seccion, titulo_tip))
        elif linea.startswith("```bash"):
            i += 1
            while i < len(lineas) and not lineas[i].startswith("```"):
                comando = lineas[i].strip()
                if comando and not _USO_ANTES.search(comando):
                    pasos.append(Paso("comando", comando, seccion))
                i += 1
            i += 1
        elif _EDITA.match(linea):
            cuerpo, i = _cuerpo(lineas, i)
            pasos.append(Paso("editar", _bloque_edit(cuerpo), seccion, "Edita a mano"))
        elif _CHECK.match(linea):
            cuerpo, i = _cuerpo(lineas, i)
            afirmaciones = _afirmaciones(cuerpo)
            if not pasos:
                pasos.append(Paso("dictar", APERTURA, seccion, "Abre la conversación"))
            if pasos[-1].tipo != "manual" and (pasos[-1].seccion == seccion or not subseccion):
                pasos[-1].checks += afirmaciones
            else:
                pasos.append(Paso("manual", seccion, seccion, checks=afirmaciones))
        else:
            i += 1
    return Capitulo(numero, slug, titulo, archivo, pasos)


def rango(texto: str, maximo: int) -> list[int]:
    """`6`, `3-6` o `1,4,7`: los capítulos que se piden. Vacío, todos."""
    if not texto:
        return list(range(1, maximo + 1))
    salida: set[int] = set()
    for trozo in texto.split(","):
        a, _, b = trozo.partition("-")
        if not a.strip().isdigit() or (b and not b.strip().isdigit()):
            raise CapituloNoEncontrado(f"no entiendo {trozo!r}; usa 6, 3-6 o 1,4,7")
        salida.update(range(int(a), int(b or a) + 1))
    return sorted(salida)


def siguiente_lunes(dia: str) -> str:
    d = date.fromisoformat(dia)
    return (d + timedelta(days=7 - d.weekday())).isoformat()


class Reloj:
    """El `TUKU_NOW` de cada paso: el día del capítulo, y diez minutos más por paso."""

    def __init__(self, numero: int) -> None:
        self.dia = DIAS[numero]
        self.hora = datetime.strptime(HORA_INICIAL, "%H:%M")

    def ahora(self, paso: Paso) -> str:
        if "lunes" in paso.titulo.lower():
            self.dia = siguiente_lunes(self.dia)
            self.hora = datetime.strptime(HORA_INICIAL, "%H:%M")
        else:
            self.hora += timedelta(minutes=MINUTOS_POR_PASO)
        return f"{self.dia} {self.hora:%H:%M}"


def vault_de_partida(cap: Capitulo) -> Path:
    """El vault donde terminó el capítulo anterior, archivado en `playground/`."""
    previo = leer_capitulo(cap.numero - 1)
    base = banco.ARCHIVO / previo.id / ESCENARIO / "mi-vault"
    if not base.is_dir():
        raise CapituloNoEncontrado(
            f"el capítulo {cap.numero} parte del vault del {previo.numero}, que no está en "
            f"{base}. Corre antes: test-tui.py tutorial {previo.numero}"
        )
    return base


def sembrar(cap: Capitulo) -> Path:
    """El directorio de trabajo del capítulo: vacío en el 1, o la copia del vault anterior."""
    if cap.numero > 1:
        return conversar.preparar(vault_de_partida(cap), cap.id, ESCENARIO).parent
    banco.exigir_banco_limpio()
    banco.enlazar_fixtures()
    trabajo = banco.BANCO / cap.id / ESCENARIO
    if trabajo.exists():
        shutil.rmtree(trabajo)
    trabajo.mkdir(parents=True)
    return trabajo


def correr_comando(comando: str, trabajo: Path, ahora: str) -> tuple[int, str]:
    """Un `bash` del capítulo: `tuku …` con el CLI del checkout, sobre el vault."""
    partes = shlex.split(comando)
    if not partes or partes[0] != "tuku":
        raise CapituloNoEncontrado(f"el tutorial corre solo comandos `tuku`, no {comando!r}")
    argv = partes[1:]
    if argv[:1] == ["init"]:
        argv = [*argv, "--at", ahora[:10]]
        cwd = trabajo
    else:
        cwd = trabajo / "mi-vault"
        if "--vault" not in argv:
            argv = [*argv, "--vault", str(cwd)]
    p = subprocess.run(
        [sys.executable, "-c", tui._ARRANQUE, *argv],
        cwd=cwd,
        env={**os.environ, "TUKU_HOME": str(RAIZ_REPO), "TUKU_NOW": ahora},
        capture_output=True,
        text=True,
        check=False,
    )
    return p.returncode, (p.stdout + p.stderr).strip()


def registro_de_comando(comando: str, salida: str, delta: dict[str, str]) -> dict[str, Any]:
    return {
        "damian": comando,
        "agente": salida,
        "escribe": [],
        "delta": dict(sorted(delta.items())),
        "codigo": 0,
        "fuera": [],
    }


_LINEA_EDIT = re.compile(r"^(?P<archivo>[\w./-]+):\s*(?P<op>.+)$")
_REEMPLAZA = re.compile(r'^reemplaza "(?P<viejo>.*)" por "(?P<nuevo>.*)"$')
_BORRA_FILA = re.compile(r"^borra la fila(?: (?P<n>\d+))?$")
_ANOTA = re.compile(r'^anota "(?P<texto>.*)" en el primer registro$')
_REGISTRO = re.compile(r"^- \d\d:\d\d - ")


def _filas_de_tabla(lineas: list[str]) -> list[int]:
    """Los índices de las filas de datos: las de `|` sin la cabecera ni la separación."""
    filas = [i for i, linea in enumerate(lineas) if linea.lstrip().startswith("|")]
    return [i for i in filas[1:] if not re.fullmatch(r"\s*\|[\s|:-]+\|\s*", lineas[i])]


def aplicar_edicion(v: Path, bloque: str) -> dict[Path, bytes]:
    """Aplica las líneas de un bloque ```edit al vault `v`.

    Devuelve cómo estaban los archivos antes, para `deshacer`. `deshacer` solo, en
    una línea, no es una edición: pide devolverlos al terminar el paso.
    """
    antes: dict[Path, bytes] = {}
    try:
        _aplicar(v, bloque, antes)
    except EdicionInvalida:
        for ruta, contenido in antes.items():
            ruta.write_bytes(contenido)
        raise
    return antes


def _aplicar(v: Path, bloque: str, antes: dict[Path, bytes]) -> None:
    for linea in bloque.splitlines():
        if linea.strip() == "deshacer":
            continue
        m = _LINEA_EDIT.match(linea)
        if not m:
            raise EdicionInvalida(f"no entiendo la edición {linea!r}")
        ruta = v / m.group("archivo")
        if not ruta.is_file():
            raise EdicionInvalida(f"{linea!r}: {m.group('archivo')} no existe en el vault")
        antes.setdefault(ruta, ruta.read_bytes())
        texto = ruta.read_text(encoding="utf-8")
        op = m.group("op")
        if r := _REEMPLAZA.match(op):
            if r.group("viejo") not in texto:
                raise EdicionInvalida(f"{linea!r}: {r.group('viejo')!r} no está en el archivo")
            texto = texto.replace(r.group("viejo"), r.group("nuevo"), 1)
        elif b := _BORRA_FILA.match(op):
            lineas = texto.split("\n")
            filas = _filas_de_tabla(lineas)
            n = int(b.group("n") or 1)
            if n > len(filas):
                raise EdicionInvalida(f"{linea!r}: la tabla tiene {len(filas)} fila(s)")
            del lineas[filas[n - 1]]
            texto = "\n".join(lineas)
        elif a := _ANOTA.match(op):
            lineas = texto.split("\n")
            for i, existente in enumerate(lineas):
                if _REGISTRO.match(existente):
                    lineas[i] = existente + a.group("texto")
                    break
            else:
                raise EdicionInvalida(f"{linea!r}: el archivo no tiene registros")
            texto = "\n".join(lineas)
        else:
            raise EdicionInvalida(f"no entiendo la operación de {linea!r}")
        ruta.write_text(texto, encoding="utf-8")


def deshace(bloque: str) -> bool:
    return any(linea.strip() == "deshacer" for linea in bloque.splitlines())


_LIMITE_ARCHIVO = 3000
_LIMITE_VAULT = 6000


def _texto(ruta: Path, limite: int) -> str:
    try:
        t = ruta.read_text(encoding="utf-8")
    except OSError, UnicodeDecodeError:
        return "(no se puede leer)"
    return t if len(t) <= limite else t[:limite] + "\n… (recortado)"


def prompt_del_juez(cap: Capitulo, paso: Paso, registro: dict[str, Any], v: Path) -> str:
    """Lo que ve el juez: el paso, lo que hizo el agente, lo que cambió y el estado actual."""
    cambios = "\n".join(f"- {r}: {c}" for r, c in registro["delta"].items()) or "(nada)"
    archivos_ = "\n\n".join(
        f"### {r}\n{_texto(v / r, _LIMITE_ARCHIVO)}"
        for r, c in registro["delta"].items()
        if c != "borrado" and (v / r).is_file()
    )
    escribe = "\n".join(f"- {c}" for c in registro["escribe"]) or "(ninguno)"
    arbol = "\n".join(sorted(banco.instantanea(v)))
    afirmaciones = "\n".join(f"{n}. {a}" for n, a in enumerate(paso.checks, 1))
    return (
        f"Eres el juez de una prueba del tutorial de TUKU, capítulo {cap.numero} "
        f"«{cap.titulo}». Un autor le dijo algo a su agente y el vault cambió. Decide si "
        "cada afirmación numerada es cierta sobre el vault tal como quedó.\n\n"
        f"## Paso\n{paso.texto}\n\n"
        f"## Lo que respondió el agente\n{registro['agente'] or '(nada)'}\n\n"
        f"## Comandos tuku que escribieron\n{escribe}\n\n"
        f"## Archivos que cambiaron\n{cambios}\n\n{archivos_}\n\n"
        f"## Todos los archivos del vault\n{arbol}\n\n"
        f"## AHORA.md\n{_texto(v / 'AHORA.md', _LIMITE_VAULT)}\n\n"
        f"## PENDIENTES.md\n{_texto(v / 'PENDIENTES.md', _LIMITE_VAULT)}\n\n"
        f"## Afirmaciones\n{afirmaciones}\n\n"
        "Responde una línea por afirmación, sin nada más, con esta forma:\n"
        "`N. CUMPLE` o `N. NO CUMPLE: motivo en una frase, con la cita del archivo`.\n"
        "Una palabra distinta que dice lo mismo cumple. Una cifra, una fecha o un archivo "
        "que falta no cumple. Lo que se refiere a la conversación (qué dijo o preguntó el "
        "agente) se juzga con «Lo que respondió el agente»."
    )


_VEREDICTO = re.compile(r"^\s*(\d+)[.)]?\s*(NO CUMPLE|CUMPLE)\b[: \t]*(.*)$", re.M)


def leer_veredicto(salida: str, total: int) -> list[tuple[bool, str]]:
    """Un `(ok, motivo)` por afirmación. Lo que el juez no contestó cuenta como falla."""
    por_numero = {
        int(m.group(1)): (m.group(2) == "CUMPLE", m.group(3).strip())
        for m in _VEREDICTO.finditer(salida)
    }
    return [
        por_numero.get(n, (False, "el juez no contestó esta afirmación"))
        for n in range(1, total + 1)
    ]


def consultar(prompt: str, modelo: str = "sonnet") -> str:
    """Lo que contesta Claude, sin herramientas ni configuración. El prompt va por `stdin`."""
    p = subprocess.run(
        [
            "claude",
            "-p",
            "--model",
            modelo,
            "--effort",
            "low",
            "--setting-sources",
            "",
            "--strict-mcp-config",
            "--tools",
            "",
        ],
        input=prompt,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    if p.returncode != 0 or not p.stdout.strip():
        raise RuntimeError(f"Claude no contestó como juez: {p.stderr.strip() or p.returncode}")
    return p.stdout


def juzgar(prompt: str, total: int, modelo: str = "sonnet") -> list[tuple[bool, str]]:
    return leer_veredicto(consultar(prompt, modelo), total)


@dataclass
class Resultado:
    capitulo: Capitulo
    ok: bool
    chequeos: list[tuple[bool, str]]
    a_mano: list[str]
    archivo: Path | None


Juez = Callable[[str, int], list[tuple[bool, str]]]


def correr_capitulo(
    cap: Capitulo,
    vista: tui.Vista,
    *,
    juez: Juez | None,
    turnos: int | None = None,
) -> Resultado:
    """Un capítulo en pantalla: sus pasos, el juicio de cada `check` y lo general."""
    trabajo = sembrar(cap)
    v = trabajo / "mi-vault"
    reloj = Reloj(cap.numero)
    vista.nota(f"{cap.archivo.name} · {cap.titulo}")
    vista.nota(f"vault en {v}")
    chequeos: list[tuple[bool, str]] = []
    a_mano: list[str] = []
    agentes: list[dict[str, Any]] = []
    frases: list[str] = []
    ejecutables = [p for p in cap.pasos if p.tipo != "manual"]
    total = len(ejecutables)
    n = 0
    for paso in cap.pasos:
        if paso.tipo == "manual":
            a_mano += [f"{paso.seccion}: {c}" for c in paso.checks]
            continue
        if turnos is not None and len(agentes) >= turnos and paso.tipo == "dictar":
            break
        n += 1
        por_deshacer: dict[Path, bytes] = {}
        ahora = reloj.ahora(paso)
        vista.turno(n, total, ahora)
        if paso.tipo == "dictar":
            vista.damian(paso.texto, quien="Autor")
            registro = conversar.turno(
                v, paso.texto, ahora, en_vivo=vista.evento, en_error=vista.error
            )
            agentes.append(registro)
            frases.append(paso.texto)
        elif paso.tipo == "editar":
            vista.damian(paso.texto, quien="Tú, a mano")
            antes = banco.instantanea(v)
            previos: dict[Path, bytes] = {}
            try:
                previos = aplicar_edicion(v, paso.texto)
            except EdicionInvalida as e:
                chequeos.append((False, f"Paso {n}: {e}"))
            codigo, salida = correr_comando("tuku doctor", trabajo, ahora)
            registro = registro_de_comando(
                paso.texto, salida, banco.delta(antes, banco.instantanea(v))
            )
            vista.nota(salida)
            if deshace(paso.texto):
                por_deshacer = previos
        else:
            vista.damian(paso.texto, quien="Tú")
            antes = banco.instantanea(v) if v.is_dir() else {}
            codigo, salida = correr_comando(paso.texto, trabajo, ahora)
            despues = banco.instantanea(v) if v.is_dir() else {}
            registro = registro_de_comando(paso.texto, salida, banco.delta(antes, despues))
            chequeos.append((codigo == 0, f"`{paso.texto}` salió {codigo}"))
            if salida:
                vista.nota(salida)
        vista.cierre(registro)
        if paso.checks:
            if juez is None:
                a_mano += [f"{paso.titulo or paso.texto}: {c}" for c in paso.checks]
            else:
                veredicto = juez(prompt_del_juez(cap, paso, registro, v), len(paso.checks))
                for afirmacion, (ok, motivo) in zip(paso.checks, veredicto, strict=True):
                    chequeos.append(
                        (ok, f"Paso {n}: {afirmacion}" + ("" if ok else f" → {motivo}"))
                    )
        for ruta, contenido in por_deshacer.items():
            ruta.write_bytes(contenido)
    destino = conversar.cerrar(v, cap.id, f"Tutorial · capítulo {cap.numero} · {cap.titulo}")
    archivado = destino / ESCENARIO / "mi-vault" if destino else v
    plan = tui.Plan(cap.archivo, cap.titulo, "", frases, None, {}, [], literal=True)
    general = tui.evaluar(plan, agentes, tui.correr_doctor(archivado))
    chequeos = [*general.chequeos, *chequeos]
    ok = all(c for c, _ in chequeos)
    vista._linea()
    vista._linea(f"━━ Capítulo {cap.numero}: {cap.titulo} ━━", "negrita")
    for bien, texto in chequeos:
        vista._linea(f"  {'✓' if bien else '✗'} {texto}", "verde" if bien else "rojo")
    if a_mano:
        vista._linea("Queda por leer a mano (no se verifica solo):", "tenue")
        for texto in a_mano:
            vista._linea(f"  - {texto}", "tenue")
    vista._linea("CUMPLE" if ok else "NO CUMPLE", "verde" if ok else "rojo", "negrita")
    return Resultado(cap, ok, chequeos, a_mano, archivado)
