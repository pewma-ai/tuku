"""`process cycle`: abrir el siguiente ciclo, repetir el abierto o guardar uno pasado."""

from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path

from tuku.cli import EXITO, main
from tuku.cycle import abrir_en_vault, tiene_registros
from tuku.init import init

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent
SEMANA_1 = date(2026, 9, 7)
AHORA = datetime(2026, 9, 20, 10, 0)


def _vault(tmp: Path, *, nombres: str | None = None) -> Path:
    vault = init(tmp / "v", desde=SEMANA_1, home=RAIZ_REPO)
    if nombres is not None:
        config = vault / "reglas" / "config.tuku.md"
        texto = re.sub(
            r"(\| `cycle_name`\s*\| )`[^`]*`",
            rf"\1`{nombres}`",
            config.read_text(encoding="utf-8"),
        )
        config.write_text(texto, encoding="utf-8")
    return vault


def _ahora(vault: Path) -> str:
    return (vault / "AHORA.md").read_text(encoding="utf-8")


def _abrir(vault: Path, **kwargs: object) -> tuple[bool, str]:
    r = abrir_en_vault(vault, now=AHORA, **kwargs)  # type: ignore[arg-type]
    return r.ok, r.mensaje


def _dias(texto: str) -> int:
    return len(re.findall(r"^## \w+ \d+ de \w+$", texto, re.MULTILINE))


def test_repetir_el_ciclo_abierto_lo_verifica_y_sin_registros_lo_regenera(
    tmp_path: Path,
) -> None:
    assert not tiene_registros("## Lunes 7 de septiembre\n\n## Martes 8 de septiembre\n")
    assert tiene_registros("## Lunes 7 de septiembre\n- 09:00 - **nota**: cuerpo\n")

    vault = _vault(tmp_path, nombres="turno, semana")
    antes = _ahora(vault)
    ok, mensaje = _abrir(vault, desde=date(2026, 9, 9))
    assert ok and "ya cubre" in mensaje and _ahora(vault) == antes, (
        "un día de la semana abierta"
    )

    ok, mensaje = _abrir(vault, desde=SEMANA_1, hasta=date(2026, 9, 15))
    assert not ok and "lunes a domingo" in mensaje and "2026-09-13" in mensaje

    ok, _ = _abrir(vault, desde=SEMANA_1, hasta=date(2026, 9, 14), nombre="turno")
    assert ok, "sin registros se regenera, que es como se corrige su --to"
    assert "cycle: turno" in _ahora(vault) and "to: 2026-09-14" in _ahora(vault)
    assert _dias(_ahora(vault)) == 8

    (vault / "AHORA.md").write_text(
        _ahora(vault).replace(
            "## Martes 8 de septiembre",
            "## Martes 8 de septiembre\n- 09:00 - **nota**: no se pierde",
        ),
        encoding="utf-8",
    )
    ok, mensaje = _abrir(vault, desde=SEMANA_1, hasta=date(2026, 9, 16), nombre="turno")
    assert not ok and "tiene registros" in mensaje and "no se pierde" in _ahora(vault)


def test_un_ciclo_con_registros_no_se_pisa(tmp_path: Path) -> None:
    vault = _vault(tmp_path)
    (vault / "AHORA.md").write_text(
        _ahora(vault).replace(
            "## Martes 8 de septiembre",
            "## Martes 8 de septiembre\n- 09:00 - **nota**: no se pierde",
        ),
        encoding="utf-8",
    )

    ok, mensaje = _abrir(vault, desde=date(2026, 9, 14))

    assert not ok
    assert "bitacoras/bitacora-2026-09-07-2026-09-13.md" in mensaje
    assert "](../ambitos/" in mensaje, "el rechazo dice que los links bajan un nivel"
    assert "no se pierde" in _ahora(vault)


def test_el_ciclo_siguiente_empieza_el_dia_despues_sin_hoyos_ni_solapes(tmp_path: Path) -> None:
    vault = _vault(tmp_path / "a")
    ok, _ = _abrir(vault)
    assert ok and "from: 2026-09-14" in _ahora(vault), "sin --from, el día siguiente al to"

    ok, mensaje = _abrir(vault, desde=date(2026, 9, 28))
    assert not ok and "2026-09-20" in mensaje and "2026-09-21" in mensaje
    assert "dejaría días sin ciclo" in mensaje

    vault = _vault(tmp_path / "b", nombres="semana, turno")
    ok, mensaje = _abrir(vault, desde=date(2026, 9, 9), hasta=date(2026, 9, 12), nombre="turno")
    assert not ok and "pisaría" in mensaje and "--from 2026-09-14" in mensaje
    assert "from: 2026-09-07" in _ahora(vault)


def test_el_nombre_avanza_en_cycle_name_y_uno_fuera_de_la_lista_pide_force(
    tmp_path: Path,
) -> None:
    vault = _vault(tmp_path, nombres="turno, descanso")

    ok, mensaje = _abrir(vault)
    assert not ok and "--to" in mensaje, "con otro nombre el rango no se deduce"

    ok, _ = _abrir(vault, desde=date(2026, 9, 14), hasta=date(2026, 9, 21))
    assert ok and "cycle: turno" in _ahora(vault) and _dias(_ahora(vault)) == 8

    ok, _ = _abrir(vault, hasta=date(2026, 9, 26))
    assert ok and "cycle: descanso" in _ahora(vault) and "from: 2026-09-22" in _ahora(vault)

    ok, _ = _abrir(vault, hasta=date(2026, 10, 3))
    assert ok and "cycle: turno" in _ahora(vault), "al llegar al final vuelve al primero"

    ok, mensaje = _abrir(vault, hasta=date(2026, 10, 8), nombre="invernada")
    assert not ok and "invernada" in mensaje and "--force" in mensaje
    ok, _ = _abrir(vault, hasta=date(2026, 10, 8), nombre="invernada", force=True)
    assert ok and "cycle: invernada" in _ahora(vault)


def test_un_ciclo_pasado_se_guarda_en_bitacoras_sin_tocar_ahora(tmp_path: Path) -> None:
    vault = _vault(tmp_path)
    antes = _ahora(vault)

    ok, mensaje = _abrir(vault, desde=date(2026, 8, 12))
    assert not ok and "--name" in mensaje

    ok, mensaje = _abrir(vault, desde=date(2026, 8, 12), nombre="semana")
    pasado = vault / "bitacoras" / "bitacora-2026-08-10-2026-08-16-semana.md"
    assert ok and pasado.is_file()
    texto = pasado.read_text(encoding="utf-8")
    assert "status: stable" in texto and "cycle: semana" in texto and _dias(texto) == 7
    assert _ahora(vault) == antes

    ok, mensaje = _abrir(vault, desde=date(2026, 8, 12), nombre="semana")
    assert ok and "ya existe" in mensaje


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


def test_la_semana_se_siembra_de_lunes_a_domingo_desde_cualquier_dia(tmp_path: Path) -> None:
    vault = _vault(tmp_path / "a")
    (vault / "AHORA.md").unlink()
    ok, _ = _abrir(vault, desde=date(2026, 9, 9))
    ahora = _ahora(vault)
    assert ok
    assert (
        "from: 2026-09-07" in ahora and "to: 2026-09-13" in ahora and "cycle: semana" in ahora
    )
    assert "## Lunes 7 de septiembre" in ahora and "## Domingo 13 de septiembre" in ahora
    assert "AAAA-MM-DD" not in ahora and "NOMBRE" not in ahora

    sembrado = init(tmp_path / "b", desde=date(2026, 9, 9), home=RAIZ_REPO)
    assert "from: 2026-09-07" in _ahora(sembrado) and "cycle: semana" in _ahora(sembrado)
    ok, mensaje = _abrir(sembrado, desde=date(2026, 9, 9))
    assert ok and "ya cubre" in mensaje, "init y process cycle abren la misma semana"


def test_el_pendiente_de_revisar_la_bitacora_anterior_se_abre_una_sola_vez(
    tmp_path: Path,
) -> None:
    sin_bitacora = _vault(tmp_path / "a")
    assert _filas(sin_bitacora) == [], "el primer ciclo no trae pendiente de revisión"
    assert (
        main(["process", "cycle", "--from", "2026-09-14", "--vault", str(sin_bitacora)])
        == EXITO
    )
    assert _filas(sin_bitacora) == []

    vault = _vault(tmp_path / "b")
    _cerrar_a_mano(vault)
    assert main(["process", "cycle", "--from", "2026-09-14", "--vault", str(vault)]) == EXITO

    (fila,) = _filas(vault)
    assert REVISAR in fila
    assert "2026-09-14" in fila
    lunes = _ahora(vault).split("## Lunes 14 de septiembre")[1]
    assert REVISAR in lunes.split("## Martes")[0]

    antes = (vault / "PENDIENTES.md").read_bytes()
    assert main(["process", "cycle", "--from", "2026-09-14", "--vault", str(vault)]) == EXITO
    assert (vault / "PENDIENTES.md").read_bytes() == antes


def test_process_lista_los_de_tuku_y_los_del_autor_y_cycle_abre(
    tmp_path: Path, capsys: object
) -> None:
    vault = _vault(tmp_path)
    (vault / "procesos").mkdir()
    (vault / "procesos" / "cierre-de-mes.md").write_text("# Cierre de mes\n", encoding="utf-8")
    assert main(["process", "--vault", str(vault)]) == EXITO
    salida = capsys.readouterr().out  # type: ignore[attr-defined]
    assert "- cycle: " in salida and "- procesos/cierre-de-mes.md: Cierre de mes" in salida
    assert main(["process", "cycle", "--from", "2026-09-14", "--vault", str(vault)]) == EXITO
    assert "from: 2026-09-14" in _ahora(vault)
