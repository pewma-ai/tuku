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

El turno es uno solo. Sostener una conversación de varios turnos es el epic 004
([`../escenarios/003-00-el-dia-uno-dictado.md`](../escenarios/003-00-el-dia-uno-dictado.md)).
"""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent

#: Cómo se le pasa un turno a cada arnés. `{prompt}` y `{modelo}` se sustituyen;
#: los argumentos de `modelo` se omiten enteros si no hay modelo configurado.
#:
#: Verificado contra `agy` real: `agy -p "..."` deja la respuesta en stdout y sale
#: 0. Su `--conversation` es lo que sostiene una sesión, y por eso no aparece acá.
#:
#: **`aislar` no es opcional y no es cosmético.** Un arnés moderno resuelve un
#: "proyecto" a partir de la máquina y no del `cwd`, así que un turno lanzado
#: dentro del vault de prueba puede contestar sobre el vault real del autor. Pasó:
#: el primer turno del `003-02` respondió con rutas de `mac-jpgil` y con el nombre
#: de su administradora de verdad, y dos de los tres tests pasaron igual, porque
#: un agente que mira otro vault tampoco toca este. Sin aislamiento, el epic mide
#: la configuración de la máquina y no el `AGENTS.md` que dice medir.
ARNESES: dict[str, dict[str, list[str]]] = {
    "agy": {
        "aislar": ["--new-project"],
        "prompt": ["-p", "{prompt}"],
        "modelo": ["--model", "{modelo}"],
    },
    "claude": {"aislar": [], "prompt": ["-p", "{prompt}"], "modelo": ["--model", "{modelo}"]},
}

#: Cuánto se espera un turno antes de darlo por colgado. Un dictado del día
#: completo tarda; uno de una frase, no. Se ajusta con `TUKU_AGENTE_TIMEOUT`.
TIMEOUT = 300


class ArnesNoDisponible(RuntimeError):
    """No hay con qué correr el turno. El escenario se salta, no falla."""


@dataclass(frozen=True)
class Arnes:
    """Qué se ejecuta y cómo se le entrega el turno."""

    nombre: str
    ejecutable: str
    modelo: str | None

    def argv(self, prompt: str) -> list[str]:
        plantilla = ARNESES[self.nombre]
        partes = [self.ejecutable, *plantilla["aislar"]]
        if self.modelo:
            partes += [a.format(modelo=self.modelo) for a in plantilla["modelo"]]
        partes += [a.format(prompt=prompt) for a in plantilla["prompt"]]
        return partes


@dataclass
class Turno:
    """Lo que dejó un turno: lo que dijo el agente y lo que ejecutó."""

    prompt: str
    codigo: int
    stdout: str
    stderr: str
    traza: list[list[str]] = field(default_factory=list)

    @property
    def comandos(self) -> list[str]:
        """La traza como líneas de comando, para leerla y compararla."""
        return [shlex.join(["tuku", *argv]) for argv in self.traza]

    def invocaciones_de(self, *verbo: str) -> list[list[str]]:
        """Las invocaciones que empiezan con ese noun y verb, p. ej. `("entry", "add")`."""
        largo = len(verbo)
        return [argv for argv in self.traza if tuple(argv[:largo]) == verbo]

    @property
    def escribio_a_mano(self) -> bool:
        """Si el vault cambió por fuera de `tuku`, el escenario ya no prueba nada.

        No se responde desde acá: lo dice el `delta` del escenario comparado con
        lo que la traza explica. Queda como recordatorio de que la traza sola no
        alcanza, y por eso las tres evidencias del epic son tres.
        """
        raise NotImplementedError("lo afirma el escenario con su delta, no el arnés")


def configurado() -> Arnes:
    """El arnés que dice el entorno, con `agy` por defecto."""
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
    return None


def disponible() -> bool:
    return motivo_no_disponible() is None


#: El shim. Anota `argv` y el directorio desde donde se llamó, y delega en el
#: `tuku` del checkout. Importa `main` en vez de reinvocar un ejecutable para no
#: depender de que TUKU esté instalado en la máquina que corre la suite.
_SHIM = """#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, {src!r})
anotacion = {{"argv": sys.argv[1:], "cwd": os.getcwd()}}
with open(os.environ["TUKU_TRAZA"], "a", encoding="utf-8") as f:
    f.write(json.dumps(anotacion, ensure_ascii=False) + "\\n")
from tuku.cli import main
sys.exit(main(sys.argv[1:]))
"""


def _sembrar_shim(dir: Path) -> Path:
    """Deja un `tuku` ejecutable en `dir` y devuelve el archivo de traza."""
    shim = dir / "tuku"
    shim.write_text(_SHIM.format(src=str(RAIZ_REPO / "src")), encoding="utf-8")
    shim.chmod(0o755)
    return dir / "traza.jsonl"


def _leer_traza(traza: Path) -> list[list[str]]:
    if not traza.is_file():
        return []
    lineas = traza.read_text(encoding="utf-8").splitlines()
    return [json.loads(linea)["argv"] for linea in lineas if linea.strip()]


def turno(vault: Path, prompt: str, timeout: int | None = None) -> Turno:
    """Un turno del agente dentro de `vault`, con la traza de lo que ejecutó.

    El agente corre **dentro del vault**, que es como se opera en la vida real:
    lee su `AGENTS.md` porque está ahí, no porque el prompt se lo pegue. Un prompt
    que explique lo que el `AGENTS.md` ya dice invalida el escenario.
    """
    motivo = motivo_no_disponible()
    if motivo is not None:
        raise ArnesNoDisponible(motivo)
    arnes = configurado()

    with tempfile.TemporaryDirectory(prefix="tuku-shim-") as tmp:
        bin = Path(tmp)
        traza = _sembrar_shim(bin)
        entorno = {
            **os.environ,
            "PATH": f"{bin}{os.pathsep}{os.environ.get('PATH', '')}",
            "TUKU_TRAZA": str(traza),
            "TUKU_HOME": str(RAIZ_REPO),
        }
        espera = timeout or int(os.environ.get("TUKU_AGENTE_TIMEOUT", TIMEOUT))
        try:
            p = subprocess.run(
                arnes.argv(prompt),
                cwd=vault,
                env=entorno,
                capture_output=True,
                text=True,
                timeout=espera,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return Turno(
                prompt=prompt,
                codigo=124,
                stdout="",
                stderr=f"el turno pasó de {espera}s sin terminar",
                traza=_leer_traza(traza),
            )
        return Turno(
            prompt=prompt,
            codigo=p.returncode,
            stdout=p.stdout,
            stderr=p.stderr,
            traza=_leer_traza(traza),
        )


if __name__ == "__main__":
    motivo = motivo_no_disponible()
    if motivo is not None:
        print(f"arnés no disponible: {motivo}")
        sys.exit(1)
    arnes = configurado()
    print(f"arnés: {arnes.nombre} ({arnes.ejecutable}), modelo: {arnes.modelo or 'el suyo'}")
    print(f"un turno se invoca así: {arnes.argv('<el turno>')}")
