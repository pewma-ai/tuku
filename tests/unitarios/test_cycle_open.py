"""Tests de la apertura de ciclo: qué pasa cuando ya hay uno abierto."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from tuku.cli import EXITO, main
from tuku.cycle import CicloEnCurso, open_cycle, tiene_registros
from tuku.init import init

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent
SEMANA_1 = date(2026, 9, 7)
SEMANA_2 = date(2026, 9, 14)


def _vault(tmp: Path) -> Path:
    return init(tmp / "v", desde=SEMANA_1, home=RAIZ_REPO)


def test_abrir_un_ciclo_es_idempotente_y_un_ciclo_vacio_se_regenera(tmp_path: Path) -> None:
    assert not tiene_registros("## Lunes 7 de septiembre\n\n## Martes 8 de septiembre\n")
    assert tiene_registros("## Lunes 7 de septiembre\n- 09:00 - **nota**: cuerpo\n")

    vault = _vault(tmp_path)
    _, creado = open_cycle(vault, SEMANA_1)
    assert not creado

    _, creado = open_cycle(vault, SEMANA_2)
    assert creado
    assert "from: 2026-09-14" in (vault / "AHORA.md").read_text(encoding="utf-8")


def test_un_ciclo_con_registros_no_se_pisa(tmp_path: Path) -> None:
    vault = _vault(tmp_path)
    ahora = vault / "AHORA.md"
    ahora.write_text(
        ahora.read_text(encoding="utf-8").replace(
            "## Martes 8 de septiembre",
            "## Martes 8 de septiembre\n- 09:00 - **nota**: no se pierde",
        ),
        encoding="utf-8",
    )

    with pytest.raises(CicloEnCurso) as e:
        open_cycle(vault, SEMANA_2)

    assert "bitacoras/bitacora-2026-09-07-2026-09-13.md" in str(e.value)
    assert "no se pierde" in ahora.read_text(encoding="utf-8")


def test_la_semana_se_siembra_de_lunes_a_domingo_desde_cualquier_dia(tmp_path: Path) -> None:
    vault = _vault(tmp_path / "a")
    (vault / "AHORA.md").unlink()
    _, creado = open_cycle(vault, date(2026, 9, 9))
    ahora = (vault / "AHORA.md").read_text(encoding="utf-8")
    assert creado
    assert "from: 2026-09-07" in ahora and "to: 2026-09-13" in ahora
    assert "## Lunes 7 de septiembre" in ahora and "## Domingo 13 de septiembre" in ahora
    assert "AAAA-MM-DD" not in ahora

    sembrado = init(tmp_path / "b", desde=date(2026, 9, 9), home=RAIZ_REPO)
    assert "from: 2026-09-07" in (sembrado / "AHORA.md").read_text(encoding="utf-8")
    _, creado = open_cycle(sembrado, date(2026, 9, 9))
    assert not creado, "init y process cycle no abren la misma semana"


# --- El pendiente de revisar la bitácora anterior --------------------------------

REVISAR = "revisar la bitácora anterior"


def _filas(vault: Path) -> list[str]:
    return [
        linea
        for linea in (vault / "PENDIENTES.md").read_text(encoding="utf-8").splitlines()
        if linea.startswith("| ") and "Horizonte" not in linea and "---" not in linea
    ]


def _cerrar_a_mano(vault: Path) -> None:
    """Lo que hace el autor para cerrar el ciclo: AHORA.md pasa a `bitacoras/`."""
    destino = vault / "bitacoras"
    destino.mkdir()
    (vault / "AHORA.md").rename(destino / "bitacora-2026-09-07-2026-09-13.md")


def test_el_pendiente_de_revisar_la_bitacora_anterior_se_abre_una_sola_vez(
    tmp_path: Path,
) -> None:
    sin_bitacora = _vault(tmp_path / "a")
    assert _filas(sin_bitacora) == [], "el primer ciclo no trae pendiente de revisión"
    assert (
        main(["process", "cycle", "--at", "2026-09-14", "--vault", str(sin_bitacora)]) == EXITO
    )
    assert _filas(sin_bitacora) == []

    vault = _vault(tmp_path / "b")
    _cerrar_a_mano(vault)
    assert main(["process", "cycle", "--at", "2026-09-14", "--vault", str(vault)]) == EXITO

    (fila,) = _filas(vault)
    assert REVISAR in fila
    assert "2026-09-14" in fila
    lunes = (
        (vault / "AHORA.md").read_text(encoding="utf-8").split("## Lunes 14 de septiembre")[1]
    )
    assert REVISAR in lunes.split("## Martes")[0]

    antes = (vault / "PENDIENTES.md").read_bytes()
    assert main(["process", "cycle", "--at", "2026-09-14", "--vault", str(vault)]) == EXITO
    assert (vault / "PENDIENTES.md").read_bytes() == antes


def test_un_ciclo_no_se_abre_hacia_atras_aunque_el_abierto_este_vacio(tmp_path: Path) -> None:
    vault = _vault(tmp_path)
    antes = (vault / "AHORA.md").read_text(encoding="utf-8")
    with pytest.raises(CicloEnCurso, match="no se abre hacia atrás"):
        open_cycle(vault, date(2026, 8, 31))
    assert (vault / "AHORA.md").read_text(encoding="utf-8") == antes


def test_process_lista_los_de_tuku_y_los_del_autor_y_cycle_abre(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    vault = _vault(tmp_path)
    (vault / "procesos").mkdir()
    (vault / "procesos" / "cierre-de-mes.md").write_text("# Cierre de mes\n", encoding="utf-8")
    assert main(["process", "--vault", str(vault)]) == EXITO
    salida = capsys.readouterr().out
    assert "- cycle: " in salida and "- procesos/cierre-de-mes.md: Cierre de mes" in salida
    assert main(["process", "cycle", "--at", "2026-09-14", "--vault", str(vault)]) == EXITO
    assert "from: 2026-09-14" in (vault / "AHORA.md").read_text(encoding="utf-8")
