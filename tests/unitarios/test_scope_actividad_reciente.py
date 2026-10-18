"""`## Actividad reciente`: lo del ámbito en los ciclos cerrados de los últimos doce meses."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from tuku import init, scope

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent
ENLACE = "[colegio-los-robles](../ambitos/colegio-los-robles/colegio-los-robles.md)"


def _bitacora(desde: str, hasta: str, dias: str) -> str:
    return f"---\ntype: Logbook\nstatus: stable\nfrom: {desde}\nto: {hasta}\n---\n\n{dias}"


def test_agrupa_por_mes_del_mas_reciente_al_mas_antiguo_y_deja_fuera_lo_de_hace_mas_de_un_ano(
    tmp_path: Path,
) -> None:
    v = init.init(tmp_path / "v", home=RAIZ_REPO, desde=date(2026, 10, 12))
    scope.crear(v, "colegio-los-robles")
    (v / "bitacoras").mkdir()
    reciente = _bitacora(
        "2026-09-28",
        "2026-10-04",
        f"## Jueves 1 de octubre\n\n- 10:00 - {ENLACE} entregué 40 cuadernos\n\n"
        f"## Martes 29 de septiembre\n\n- 09:00 - {ENLACE} cotizé la reposición\n",
    )
    vieja = _bitacora(
        "2025-08-04",
        "2025-08-10",
        f"## Lunes 4 de agosto\n\n- 09:00 - {ENLACE} esto ya no cuenta\n",
    )
    (v / "bitacoras" / "bitacora-2026-09-28-2026-10-04.md").write_text(
        reciente, encoding="utf-8"
    )
    (v / "bitacoras" / "bitacora-2025-08-04-2025-08-10.md").write_text(vieja, encoding="utf-8")

    scope.actualizar_pagina(v, "colegio-los-robles")
    pagina = (v / "ambitos/colegio-los-robles/colegio-los-robles.md").read_text(
        encoding="utf-8"
    )
    recientes = pagina.split("## Actividad reciente", 1)[1]
    assert recientes.index("### Octubre 2026") < recientes.index("### Septiembre 2026")
    assert "- 1 - entregué 40 cuadernos" in recientes
    assert "- 29 - cotizé la reposición" in recientes
    assert "esto ya no cuenta" not in recientes
