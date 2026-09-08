"""Test del escenario 002-01-abrir-ciclo.

Escenario: 002-01-abrir-ciclo.md

Primer paso de la cadena del epic 002. Verifica si hay un `AHORA.md` que cubra la
fecha deseada; si no lo hay, lo crea a partir de la plantilla en
`reglas/plantilla/AHORA.md` con la semana completa (lunes a domingo). Si ya
cubre la fecha, no lo modifica (idempotencia).

Ejecutable directo: python3 tests/escenarios/test_002_01_abrir_ciclo.py
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

from cadena import delta, instantanea, preparar_paso  # noqa: E402
from vault import placeholders_sin_sustituir  # noqa: E402

from tuku.cli import EXITO, main  # noqa: E402

SLUG = "002-01-abrir-ciclo"
PREVIO = None
FECHA = date(2026, 8, 11)


def test_002_01_crea_ahora_desde_plantilla_si_no_existe() -> None:
    vault = preparar_paso(SLUG, previo=PREVIO, desde=FECHA)
    ahora = vault / "AHORA.md"
    if ahora.exists():
        ahora.unlink()

    antes = instantanea(vault)
    codigo = main(["cycle", "open", "--vault", str(vault), "--fecha", FECHA.isoformat()])
    assert codigo == EXITO
    assert delta(antes, instantanea(vault)) == {"AHORA.md": "nuevo"}

    texto = ahora.read_text(encoding="utf-8")
    assert "from: 2026-08-10" in texto
    assert "to: 2026-08-16" in texto
    assert "## Lunes 10 de agosto" in texto
    assert "## Martes 11 de agosto" in texto
    assert "## Miércoles 12 de agosto" in texto
    assert "## Jueves 13 de agosto" in texto
    assert "## Viernes 14 de agosto" in texto
    assert "## Sábado 15 de agosto" in texto
    assert "## Domingo 16 de agosto" in texto
    assert not placeholders_sin_sustituir(vault), "quedaron placeholders en el vault"


def test_002_01_idempotente_si_ahora_ya_cubre_la_fecha() -> None:
    vault = Path(RAIZ / "playground" / SLUG)
    if not (vault / "AHORA.md").exists():
        test_002_01_crea_ahora_desde_plantilla_si_no_existe()

    antes = instantanea(vault)
    codigo = main(["cycle", "open", "--vault", str(vault), "--fecha", FECHA.isoformat()])
    assert codigo == EXITO
    assert delta(antes, instantanea(vault)) == {}, "modificó AHORA.md cuando ya cubría la fecha"


if __name__ == "__main__":
    test_002_01_crea_ahora_desde_plantilla_si_no_existe()
    test_002_01_idempotente_si_ahora_ya_cubre_la_fecha()
    print(f"ok: 2 afirmaciones (queda en playground/{SLUG}/)")
