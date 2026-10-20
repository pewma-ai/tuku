"""Configuración global y hooks de pytest para la suite de TUKU."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--unittests",
        "--unit",
        action="store_true",
        default=False,
        help="Ejecutar únicamente los tests unitarios (tests/unitarios/)",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    for item in items:
        item_path = str(getattr(item, "path", getattr(item, "fspath", "")))
        if "tests/unitarios" in item_path:
            item.add_marker(pytest.mark.unitario)
            item.add_marker(pytest.mark.unit)

    if config.getoption("--unittests") or config.getoption("--unit"):
        seleccionados: list[pytest.Item] = []
        deseleccionados: list[pytest.Item] = []
        for item in items:
            if item.get_closest_marker("unitario") is not None:
                seleccionados.append(item)
            else:
                deseleccionados.append(item)

        config.hook.pytest_deselected(items=deseleccionados)
        items[:] = seleccionados


#: El instante que los tests le dan a los casos de uso: miércoles 12 de agosto de 2026, 09:00.
AHORA = datetime(2026, 8, 12, 9, 0)


#: Los veredictos del evaluador, para el resumen del final: (test, nivel, razón).
_VEREDICTOS: list[tuple[str, str, str]] = []


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]):  # type: ignore[no-untyped-def]
    """Un test agéntico que falla pasa por el criterio de un evaluador (`criterio.py`)."""
    outcome = yield
    informe = outcome.get_result()
    if (
        call.when != "call"
        or not informe.failed
        or item.get_closest_marker("agentic") is None
        or call.excinfo is None
    ):
        return
    import criterio

    if not criterio.activo():
        return
    slug, escenario = criterio.escenario_de(
        getattr(getattr(item, "module", None), "__doc__", None)
    )
    try:
        veredicto = criterio.juzgar(
            escenario, str(call.excinfo.getrepr(style="short")), criterio.estado_de(slug)
        )
    except Exception as e:  # el evaluador no contestó: se conserva la falla
        informe.sections.append(("Criterio", f"el evaluador no contestó: {e}"))
        return
    informe.sections.append(("Criterio", f"{veredicto.nivel}: {veredicto.razon}"))
    _VEREDICTOS.append((item.nodeid, veredicto.nivel, veredicto.razon))
    if veredicto.pasa:
        informe.outcome = "passed"


def pytest_terminal_summary(terminalreporter, exitstatus, config):  # type: ignore[no-untyped-def]
    if not _VEREDICTOS:
        return
    terminalreporter.section("criterio del evaluador")
    for nodeid, nivel, razon in _VEREDICTOS:
        terminalreporter.write_line(f"{nivel:<11} {nodeid}\n            {razon}")
