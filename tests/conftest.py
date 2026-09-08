"""Configuración global y hooks de pytest para la suite de TUKU."""

from __future__ import annotations

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--unittests",
        "--unit",
        action="store_true",
        default=False,
        help="Ejecutar únicamente los tests unitarios (tests/unitarios/)",
    )


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
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
