"""Escritura atómica que no pisa lo que otro programa cambió, y sus reintentos."""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path

import pytest

from tuku import archivo, cli, init
from tuku.cli import RECHAZO

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent


def test_escribe_de_una_vez_conserva_permisos_y_puede_conservar_la_fecha(
    tmp_path: Path,
) -> None:
    ruta = tmp_path / "AHORA.md"
    ruta.write_text("antes\n", encoding="utf-8")
    ruta.chmod(0o640)
    archivo.escribir(ruta, "después\n")
    assert ruta.read_text(encoding="utf-8") == "después\n"
    assert ruta.stat().st_mode & 0o777 == 0o640
    assert [p.name for p in tmp_path.iterdir()] == ["AHORA.md"]

    ruta = tmp_path / "nota.md"
    ruta.write_text("[[x]]\n", encoding="utf-8")
    antes = ruta.stat().st_mtime_ns - 10**9
    os.utime(ruta, ns=(antes, antes))
    archivo.escribir(ruta, "[x](x.md)\n", conservar_fecha=True)
    assert ruta.stat().st_mtime_ns == antes


def test_un_cambio_ajeno_se_reintenta_dentro_de_un_intento_y_se_pisa_fuera_de_el(
    tmp_path: Path,
) -> None:
    ruta = tmp_path / "AHORA.md"
    ruta.write_text("uno\n", encoding="utf-8")
    archivo.leer(ruta)
    ruta.write_text("dos\n", encoding="utf-8")
    archivo.escribir(ruta, "tres\n")
    assert ruta.read_text(encoding="utf-8") == "tres\n"

    ruta = tmp_path / "PENDIENTES.md"
    ruta.write_text("| fila |\n", encoding="utf-8")
    esperas: list[float] = []
    intentos = 0

    def comando() -> str:
        nonlocal intentos
        intentos += 1
        texto = archivo.leer(ruta)
        if intentos == 1:
            ruta.write_text("| fila del autor |\n", encoding="utf-8")
        archivo.escribir(ruta, texto + "| nueva |\n")
        return "hecho"

    assert archivo.con_reintentos(comando, esperas.append) == "hecho"
    assert esperas == [0.1]
    assert ruta.read_text(encoding="utf-8") == "| fila del autor |\n| nueva |\n"


def test_tras_tres_reintentos_dice_que_escribio_y_que_falto(tmp_path: Path) -> None:
    ahora, pendientes = tmp_path / "AHORA.md", tmp_path / "PENDIENTES.md"
    for r in (ahora, pendientes):
        r.write_text("x\n", encoding="utf-8")
    esperas: list[float] = []

    def comando() -> None:
        archivo.escribir(ahora, "registro\n")
        texto = archivo.leer(pendientes)
        pendientes.write_text(texto + "editado en Obsidian\n", encoding="utf-8")
        archivo.escribir(pendientes, "fila\n")

    with pytest.raises(archivo.SinReintentos) as error:
        archivo.con_reintentos(comando, esperas.append)
    assert esperas == list(archivo.ESPERAS)
    assert error.value.mensaje(tmp_path) == (
        "escribí AHORA.md. Faltó PENDIENTES.md, y lo que venía después de él: otro programa "
        "lo estaba editando. Corre el mismo comando de nuevo."
    )
    assert pendientes.read_text(encoding="utf-8").endswith("editado en Obsidian\n")


def test_sin_nada_escrito_lo_dice() -> None:
    error = archivo.SinReintentos(Path("/v/PENDIENTES.md"), ())
    assert error.mensaje(Path("/v")) == (
        "no escribí nada: otro programa estaba editando PENDIENTES.md. "
        "Corre el mismo comando de nuevo."
    )


def test_el_cli_rechaza_con_el_mensaje_de_lo_que_falto(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    vault = init.init(tmp_path / "v", home=RAIZ_REPO, desde=date(2026, 8, 10))

    def choca(_: object) -> int:
        raise archivo.SinReintentos(vault / "PENDIENTES.md", (vault / "AHORA.md",))

    monkeypatch.setattr(archivo, "con_reintentos", choca)
    assert cli.main(["todo", "open", "--body", "pagar", "--vault", str(vault)]) == RECHAZO
    assert capsys.readouterr().err.startswith(
        "tuku todo open: escribí AHORA.md. Faltó PENDIENTES.md"
    )
