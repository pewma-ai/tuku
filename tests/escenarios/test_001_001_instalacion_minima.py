"""Test byte a byte del escenario 001-001-instalacion-minima.

Escenario: 001-001-instalacion-minima.md

`instalar()` hace dos cosas: copia `template/vanilla/` tal cual, y sustituye
las fechas de `AHORA.md`. **Nada se compara contra una copia congelada del
template.** Los archivos copiados se contrastan en vivo contra
`template/vanilla/`, y el `AHORA.md` esperado se deriva del template real
aplicándole las siete fechas que este escenario fija a mano. Un cambio en el
template no obliga a regenerar nada; un cambio en la lógica de sembrado sigue
rompiendo el test.

Tres afirmaciones, y las tres fallan por separado:

1. El árbol instalado no difiere de `template/vanilla/` en ningún archivo
   salvo `AHORA.md`, ni sobra ni falta ninguno.
2. `AHORA.md` queda exactamente como el template con las fechas resueltas.
3. No sobrevive ningún placeholder en ningún archivo del vault.

La tercera es la que cubre el crecimiento del template: si un archivo nuevo
de `template/vanilla/` trae `DD de mes` y el instalador no lo sustituye, las
otras dos pasan en silencio y esta no.

La corrida byte a byte instala en `playground/001-001-instalacion-minima/`
(git-ignored, se pisa en cada corrida), así el estado cero queda a la vista
para el `## Qué se mira a mano` del escenario.

Una segunda función, `test_001_001_instalador_siembra_el_autor`, es la única
cobertura del flag `--autor`: instalar con un nombre lo escribe en la sección
"El autor" de `LIBRO-DE-ESTILO.md` y borra el placeholder "por declarar".
Esa función se queda en un tempdir: solo hace un `assert` de detalle, no deja
superficie de revisión a mano.

Fecha fija: 2026-08-11 (martes), el mismo día donde arranca el ground truth
de corpus/referencia/referencia-faena.md ("Turno Faena"). El usuario real
instala con la fecha de hoy (ver template/README.md); este test la fija para
que el resultado sea comparable byte a byte, como pide el principio 9.

Ejecutable directo, sin pytest:
`python3 tests/escenarios/test_001_001_instalacion_minima.py`
"""

from __future__ import annotations

import sys
import tempfile
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

from install_test_scenario import instalar  # noqa: E402
from vault import (  # noqa: E402
    ahora_sembrado,
    diff_recursivo,
    placeholders_sin_sustituir,
    preparar_playground,
)

FECHA_FIJA = date(2026, 8, 11)
TEMPLATE_VANILLA = RAIZ / "template" / "vanilla"

#: Los siete días resueltos que corresponden a FECHA_FIJA, escritos a mano.
#: Es lo único que este test afirma sin derivarlo del template: el mapeo de
#: fecha a nombre de día es donde estuvo el bug que este escenario destapó
#: (los días salían en orden fijo Lunes..Domingo sin mirar el día real).
DESDE, HASTA = "2026-08-11", "2026-08-17"
DIAS = [
    "## Martes 11 de agosto",
    "## Miércoles 12 de agosto",
    "## Jueves 13 de agosto",
    "## Viernes 14 de agosto",
    "## Sábado 15 de agosto",
    "## Domingo 16 de agosto",
    "## Lunes 17 de agosto",
]


def test_001_001_instalador_siembra_el_autor() -> None:
    """El flag --autor escribe el nombre en la sección "El autor" del libro de estilo.

    Única cobertura de `--autor`: instalar con un nombre reemplaza el placeholder
    "por declarar" por ese nombre, sobre la línea `**Nombre del autor:**`.
    """
    # Tempdir a propósito: lo que se mira a mano del 001-001 es el estado cero
    # que deja la función byte a byte; esta solo verifica que --autor escribe
    # el nombre, no deja nada que revisar en playground/.
    with tempfile.TemporaryDirectory() as tmp:
        destino = Path(tmp) / "vault"
        instalar("vanilla", destino, FECHA_FIJA, autor="Fulana Pérez de Tal")

        libro = (destino / "LIBRO-DE-ESTILO.md").read_text(encoding="utf-8")
        assert "**Nombre del autor:** Fulana Pérez de Tal" in libro
        assert "por declarar" not in libro


def test_001_001_instalacion_minima_byte_a_byte() -> None:
    destino = preparar_playground("001-001-instalacion-minima")
    instalar("vanilla", destino, FECHA_FIJA)

    diferencias = diff_recursivo(destino, TEMPLATE_VANILLA, ignorar=frozenset({"AHORA.md"}))
    assert not diferencias, f"difiere de template/vanilla/: {diferencias}"

    obtenido = (destino / "AHORA.md").read_text(encoding="utf-8")
    esperado = ahora_sembrado(TEMPLATE_VANILLA, desde=DESDE, hasta=HASTA, dias=DIAS)
    assert obtenido == esperado, "AHORA.md no quedó como el template con las fechas resueltas"

    vivos = placeholders_sin_sustituir(destino)
    assert not vivos, f"quedaron placeholders sin sustituir: {vivos}"


if __name__ == "__main__":
    test_001_001_instalacion_minima_byte_a_byte()
    print(
        "ok: árbol idéntico a template/vanilla/, AHORA.md sembrado, sin placeholders vivos "
        "(queda en playground/001-001-instalacion-minima/)"
    )
    test_001_001_instalador_siembra_el_autor()
    print("ok: --autor siembra el nombre en LIBRO-DE-ESTILO.md")
