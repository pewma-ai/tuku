"""`tuku doctor` sin --verbose muestra solo los hallazgos y los avisos."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from tuku import doctor, entry, init
from tuku.doctor import Revision, formatear

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent

SANA = Revision("config", "config: 5 campos declarados.", True)
AVISO = Revision("version", "version: aviso: el vault es anterior.", True, aviso=True)
ROTA = Revision("link", "AHORA.md:1: error: x.\nlink: 1 error(es).", False)


def test_un_vault_sano_sin_avisos_solo_dice_que_esta_sano() -> None:
    assert formatear([SANA, SANA]) == "doctor: el vault está sano."


def test_con_verbose_muestra_todas_las_revisiones() -> None:
    assert formatear([SANA, SANA], verbose=True) == (
        "config: 5 campos declarados.\n"
        "config: 5 campos declarados.\n"
        "doctor: el vault está sano."
    )


def test_un_aviso_se_muestra_aunque_la_revision_este_sana() -> None:
    salida = formatear([SANA, AVISO])
    assert salida == "version: aviso: el vault es anterior.\ndoctor: el vault está sano."


def test_una_revision_con_hallazgos_se_muestra_y_las_sanas_no() -> None:
    salida = formatear([SANA, ROTA, AVISO])
    assert "config:" not in salida
    assert "AHORA.md:1: error: x." in salida and "version: aviso" in salida
    assert "doctor: 1 revisión(es) con hallazgos: link." in salida


def test_con_verbose_los_hallazgos_siguen_estando() -> None:
    salida = formatear([SANA, ROTA], verbose=True)
    assert "config:" in salida and "AHORA.md:1: error: x." in salida


def test_una_pregunta_del_lint_es_un_aviso_y_no_falla(tmp_path: Path) -> None:
    vault = init.init(tmp_path / "v", home=RAIZ_REPO, desde=date(2026, 8, 10))
    entry.add_al_vault(
        vault,
        body="**cachureo**: ordené los cables",
        scope="personal",
        day=date(2026, 8, 11),
        hour="12:05",
    )

    corto = doctor.revisar_vault(vault)
    largo = doctor.revisar_vault(vault, verbose=True)

    assert corto.ok and largo.ok
    assert "pregunta" in corto.mensaje and "cachureo" in corto.mensaje
    assert "config:" not in corto.mensaje and "config:" in largo.mensaje
    assert corto.mensaje.endswith("doctor: el vault está sano.")


def test_un_vault_sembrado_sin_novedades_no_imprime_nada_mas_que_el_cierre(
    tmp_path: Path,
) -> None:
    vault = init.init(tmp_path / "v", home=RAIZ_REPO)
    r = doctor.revisar_vault(vault)
    assert r.ok
    assert r.mensaje.splitlines()[-1] == "doctor: el vault está sano."
    assert "files:" not in r.mensaje
