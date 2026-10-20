"""El criterio de un evaluador cuando falla un test agéntico.

Un test agéntico compara lo que hizo un agente con lo que el escenario esperaba, y
el agente puede tomar un camino equivalente que el test no previó. Pasar o fallar no
distingue eso de un defecto. Cuando un test agéntico falla, un evaluador (Claude, sin
herramientas) lee el escenario, la falla y lo que quedó, y responde con un nivel:

- **RAZONABLE**: otro camino que cumple la intención del escenario y no rompe ninguna
  regla del vault. El test pasa.
- **DISCUTIBLE**: se aparta de lo esperado de un modo que el autor podría reprochar,
  pero no daña el vault ni cruza un límite. El test pasa y queda a la vista.
- **INACEPTABLE**: cruza un límite (edita a mano, inventa, escribe lo no ratificado,
  pierde datos) o no cumple la intención. El test falla.

`TUKU_CRITERIO=0` lo apaga y deja el falla/no falla de siempre.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

import tutorial

RAIZ = Path(__file__).resolve().parent.parent.parent
NIVELES = ("RAZONABLE", "DISCUTIBLE", "INACEPTABLE")
_NIVEL = re.compile(r"^\s*NIVEL:\s*(RAZONABLE|DISCUTIBLE|INACEPTABLE)\b", re.M)
_RAZON = re.compile(r"^\s*RAZÓN:\s*(.+?)\s*\Z", re.M | re.S)
_TOPE = 6000


@dataclass(frozen=True)
class Veredicto:
    nivel: str
    razon: str

    @property
    def pasa(self) -> bool:
        return self.nivel != "INACEPTABLE"


def activo() -> bool:
    return os.environ.get("TUKU_CRITERIO", "1") != "0"


def leer_veredicto(salida: str) -> Veredicto:
    """El nivel y la razón. Lo que el evaluador no dijo con claridad cuenta como INACEPTABLE."""
    nivel = _NIVEL.search(salida)
    if nivel is None:
        return Veredicto(
            "INACEPTABLE", "el evaluador no contestó un nivel: " + salida.strip()[:200]
        )
    razon = _RAZON.search(salida)
    return Veredicto(nivel.group(1), razon.group(1).strip() if razon else "sin razón")


GUIA = Path(__file__).with_name("criterio-guia.md")


def armar_prompt(escenario: str, falla: str, estado: str) -> str:
    return (
        "Eres el evaluador de un test de TUKU, un sistema que guarda la bitácora de la vida "
        "de una persona en archivos Markdown. Un agente de IA atiende al autor con comandos "
        "`tuku`.\n\n"
        f"{GUIA.read_text(encoding='utf-8')}\n"
        "Responde con exactamente dos líneas:\n"
        "NIVEL: RAZONABLE | DISCUTIBLE | INACEPTABLE\n"
        "RAZÓN: una frase que cite lo que decide.\n\n"
        f"## Escenario\n\n{escenario[:_TOPE]}\n\n"
        f"## Cómo falló el test\n\n{falla[:_TOPE]}\n\n"
        f"## Lo que quedó\n\n{estado[:_TOPE]}\n"
    )


def estado_de(slug: str) -> str:
    """Lo que dejó la última corrida de `slug` en `playground/`: el log y los archivos vivos."""
    base = RAIZ / "playground" / slug
    partes: list[str] = []
    for vault in sorted(base.glob("*/mi-vault")) if base.is_dir() else []:
        for nombre in ("notas/conversation-log.md", "AHORA.md", "PENDIENTES.md"):
            ruta = vault / nombre
            if ruta.is_file():
                partes.append(f"### {nombre}\n\n{ruta.read_text(encoding='utf-8')[-_TOPE:]}")
    return "\n\n".join(partes) or "(la corrida no dejó archivos que mostrar)"


def escenario_de(modulo_doc: str | None) -> tuple[str, str]:
    """El slug y el texto del `.md` que nombra la línea `Escenario: SLUG.md` del módulo."""
    m = re.search(r"^Escenario:\s*(\S+?)\.md\s*$", modulo_doc or "", re.M)
    if m is None:
        return "", "(el test no declara su escenario)"
    ruta = RAIZ / "tests" / "escenarios" / f"{m.group(1)}.md"
    return m.group(1), ruta.read_text(encoding="utf-8") if ruta.is_file() else ""


def juzgar(escenario: str, falla: str, estado: str, modelo: str = "sonnet") -> Veredicto:
    return leer_veredicto(tutorial.consultar(armar_prompt(escenario, falla, estado), modelo))
