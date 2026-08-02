"""Cobertura declarada: qué invariantes de `spec/` tienen test y cuáles no.

El plan (§3, nivel 2) dice que el mapeo 1:1 entre invariantes y tests es el mayor
dividendo de haber escrito las specs primero: la cobertura no se inventa, se
transcribe. Este módulo lo hace verificable.

Cómo funciona
-------------
`PENDIENTES` lista las invariantes que todavía NO tienen test. Al escribir el test
de una invariante, se borra su entrada de la lista. El test de abajo falla en dos
direcciones:

- si una invariante nueva aparece en una spec y nadie la registró, y
- si una invariante sigue en `PENDIENTES` pero ya tiene test (lista mentirosa).

Esa segunda dirección es la que importa: impide que la lista se convierta en un
cementerio de excusas que nadie limpia.
"""

from __future__ import annotations

import re
from pathlib import Path

from tests.specref import invariantes

TESTS_DIR = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Invariantes sin test. Se borran de aquí a medida que se implementan (F2).
# ---------------------------------------------------------------------------
PENDIENTES: set[str] = {
    # entidad.md (N) — F2.1
    "N4", "N5", "N6", "N8", "N9",
    # entradas.md (E) — F2.2
    "E1", "E2", "E3", "E4", "E5", "E6", "E7",
    # tarea.md (T) — F2.3
    "T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8",
    # cadencia.md (K) — F2.4
    "K1", "K2", "K3", "K4", "K5", "K6", "K8", "K9",  # K7 es negativa: nada que garantizar
    # artefactos-ciclo.md (C) — F2.5
    "C1", "C2", "C4", "C5", "C6", "C7",  # C3 es negativa
    # proceso.md (R) — F2.6
    "R1", "R2", "R3", "R4", "R6",  # R5 es negativa
    # nota.md (O) — F2.7
    "O2", "O3", "O4", "O5", "O6", "O7", "O8",
    # perfil.md (F) — F2.8
    "F1", "F4",
    # frontmatter.md (M) — F2.9 / B1
    "M1", "M2", "M3",
}

_NOMBRE_TEST = re.compile(r"def (test_(?P<inv>[A-Z]\d+)_\w+)")


def _invariantes_con_test() -> set[str]:
    """Invariantes que ya tienen al menos un `def test_<ID>_...`."""
    encontradas: set[str] = set()
    for archivo in TESTS_DIR.rglob("test_*.py"):
        for m in _NOMBRE_TEST.finditer(archivo.read_text(encoding="utf-8")):
            encontradas.add(m.group("inv"))
    return encontradas


def test_toda_invariante_esta_registrada() -> None:
    """Ninguna invariante de una spec queda fuera del radar.

    Si alguien agrega `T9` a `spec/tarea.md`, este test falla hasta que exista su
    test o se declare pendiente. Es lo que impide que la cobertura se degrade en
    silencio a medida que las specs crecen.
    """
    # Las invariantes negativas (garante `—`) declaran que algo **no** es
    # violación. No hay nada que un janitor deba detectar, así que no exigen test.
    declaradas = {
        inv.id for inv in invariantes() if inv.garante.strip() not in {"—", "-", ""}
    }
    con_test = _invariantes_con_test()
    sin_registrar = declaradas - con_test - PENDIENTES
    assert not sin_registrar, (
        f"invariantes en spec/ sin test ni entrada en PENDIENTES: {sorted(sin_registrar)}"
    )


def test_la_lista_de_pendientes_no_miente() -> None:
    """Una invariante con test no puede seguir declarada como pendiente."""
    ya_cubiertas = PENDIENTES & _invariantes_con_test()
    assert not ya_cubiertas, (
        f"estas invariantes ya tienen test; bórralas de PENDIENTES: {sorted(ya_cubiertas)}"
    )


def test_toda_invariante_declara_garante() -> None:
    """P3: cada garantía tiene un costo conocido.

    Una invariante sin garante explícito no se sabe si la verifica un janitor
    (barato, determinista) o un agente (caro, no reproducible). Esa ambigüedad es
    justo la que el test de replay existe para detectar.
    """
    validos = {"janitor", "janitor de build", "motor", "test de replay"}
    malas = [
        f"{inv.spec}:{inv.id} → {inv.garante!r}"
        for inv in invariantes()
        # `—` es legítimo en invariantes negativas: las que declaran que algo
        # **no** es violación (K7, C3, P5) no tienen nada que garantizar.
        if inv.garante.strip() not in {"—", "-", ""}
        and not any(v in inv.garante.lower() for v in validos)
    ]
    assert not malas, f"invariantes sin garante reconocible: {malas}"
