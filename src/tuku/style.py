"""tuku style: validación y lint de LIBRO-DE-ESTILO.md.

Revisa que LIBRO-DE-ESTILO.md mantenga los contratos que los comandos de TUKU
necesitan para operar:
1. El marcador del autor: `**Nombre del autor:**` (requerido por `tuku init --author`).
2. Los tres encabezados de contrato de las tablas:
   - `### Clasificaciones`
   - `### Horizontes`
   - `### Tipos de nota`
3. Que cada tabla de contrato exista y contenga términos válidos.

Toda falla reporta el defecto y la corrección (spec/cli.md).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from tuku.lint import ERROR, PREGUNTA
from tuku.resultado import Resultado
from tuku.vocab import ENCABEZADOS

_MARCADOR_AUTOR = "**Nombre del autor:**"
_TERMINO = re.compile(r"^\|\s*`([^`]+)`\s*\|")


@dataclass(frozen=True)
class HallazgoEstilo:
    """Un hallazgo del lint de estilo."""

    linea: int | None
    grado: str
    defecto: str
    correccion: str

    def __str__(self) -> str:
        ref = f"LIBRO-DE-ESTILO.md:{self.linea}" if self.linea else "LIBRO-DE-ESTILO.md"
        marca = "error" if self.grado == ERROR else "pregunta"
        return f"{ref}: {marca}: {self.defecto}. {self.correccion}"


def lint(libro: str) -> list[HallazgoEstilo]:
    """Revisa LIBRO-DE-ESTILO.md y devuelve la lista de hallazgos."""
    hallazgos: list[HallazgoEstilo] = []
    lineas = libro.splitlines()

    # 1. Marcador del autor
    tiene_autor = any(linea.lstrip().startswith(_MARCADOR_AUTOR) for linea in lineas)
    if not tiene_autor:
        hallazgos.append(
            HallazgoEstilo(
                linea=None,
                grado=ERROR,
                defecto=f"falta el marcador '{_MARCADOR_AUTOR}'",
                correccion=(
                    "Agrégalo bajo la sección '## El autor' para que "
                    "`tuku init --author` funcione."
                ),
            )
        )

    # 2. Encabezados de contrato y sus tablas
    for encabezado in ENCABEZADOS.values():
        try:
            ini = next(i for i, linea in enumerate(lineas) if linea.strip() == encabezado)
        except StopIteration:
            hallazgos.append(
                HallazgoEstilo(
                    linea=None,
                    grado=ERROR,
                    defecto=f"falta el encabezado de contrato '{encabezado}'",
                    correccion=(
                        "Es contrato para automatizaciones: agrégalo con su tabla debajo."
                    ),
                )
            )
            continue

        fin = next(
            (i for i in range(ini + 1, len(lineas)) if lineas[i].startswith(("## ", "### "))),
            len(lineas),
        )
        cabeceras = ("Clasificación", "Horizonte", "Tipo")
        terminos = [
            m.group(1)
            for linea in lineas[ini + 1 : fin]
            if (m := _TERMINO.match(linea)) and m.group(1) not in cabeceras
        ]
        if not terminos:
            hallazgos.append(
                HallazgoEstilo(
                    linea=ini + 1,
                    grado=PREGUNTA,
                    defecto=f"la tabla de '{encabezado}' no tiene ningún término declarado",
                    correccion=(
                        "Declara al menos un término en la primera columna entre backticks "
                        "(p. ej. `progreso`)."
                    ),
                )
            )

    return hallazgos


def formatear(hallazgos: list[HallazgoEstilo]) -> str:
    """Formatea los hallazgos para salida de CLI o reporte."""
    if not hallazgos:
        return "style lint: sin hallazgos."
    errores = sum(1 for h in hallazgos if h.grado == ERROR)
    preguntas = len(hallazgos) - errores
    resumen = f"style lint: {errores} error(es), {preguntas} pregunta(s)."
    return "\n".join([*(str(h) for h in hallazgos), resumen])


def lint_del_vault(vault: Path) -> Resultado:
    """Revisa los contratos de `LIBRO-DE-ESTILO.md` y reporta; no escribe."""
    from tuku.config import archivo_vault

    libro = archivo_vault(vault, "LIBRO-DE-ESTILO.md").read_text(encoding="utf-8")
    hallazgos = lint(libro)
    mensaje = formatear(hallazgos)
    if any(h.grado == ERROR for h in hallazgos):
        return Resultado.rechazo(mensaje, error=False)
    return Resultado.hecho(mensaje)
