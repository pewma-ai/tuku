"""`tuku doctor link` y `tuku fix link` sobre un vault mínimo en disco."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from tuku import doctor, fix, init

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent


def _vault(tmp_path: Path, archivos: dict[str, str]) -> Path:
    for rel, texto in archivos.items():
        ruta = tmp_path / rel
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(texto, encoding="utf-8")
    return tmp_path


def test_un_vault_sembrado_no_tiene_wikilinks_ni_links_rotos(tmp_path: Path) -> None:
    destino = init.init(tmp_path / "v", home=RAIZ_REPO)
    revision = doctor.revisar_links(destino)
    assert revision.sano, revision.salida


def test_doctor_reporta_el_wikilink_y_nombra_fix(tmp_path: Path) -> None:
    v = _vault(tmp_path, {"AHORA.md": "- 09:00 - [[x]] algo\n", "ambitos/x/x.md": "# x\n"})
    r = doctor.revisar_links(v)
    assert not r.sano
    assert "AHORA.md:1" in r.salida and "tuku fix link" in r.salida


def test_doctor_reporta_un_link_roto(tmp_path: Path) -> None:
    v = _vault(tmp_path, {"AHORA.md": "ver [x](ambitos/x/x.md)\n"})
    r = doctor.revisar_links(v)
    assert not r.sano and "no existe" in r.salida


def test_doctor_ignora_transclusiones_y_codigo(tmp_path: Path) -> None:
    v = _vault(tmp_path, {"AHORA.md": "![[otro.md#^a]] `[[b]]`\n```\n[[c]]\n```\n"})
    assert doctor.revisar_links(v).sano


def test_doctor_con_tema_corre_solo_esa_revision(tmp_path: Path) -> None:
    v = _vault(tmp_path, {"AHORA.md": "sin links\n"})
    r = doctor.revisar_vault(v, tema="link")
    assert r.ok and "link:" in r.mensaje and "config:" not in r.mensaje


def test_fix_convierte_conserva_la_fecha_y_es_idempotente(tmp_path: Path) -> None:
    v = _vault(
        tmp_path,
        {"AHORA.md": "- 09:00 - [[x]] algo\n", "ambitos/x/x.md": "# x\n![[../P.md#^x]]\n"},
    )
    ahora = v / "AHORA.md"
    os.utime(ahora, ns=(1_000_000_000_000_000_000, 1_000_000_000_000_000_000))
    antes = ahora.stat().st_mtime_ns

    r = fix.fix_link(v)

    assert r.ok, r.mensaje
    assert ahora.read_text(encoding="utf-8") == "- 09:00 - [x](ambitos/x/x.md) algo\n"
    assert ahora.stat().st_mtime_ns == antes
    assert "![[../P.md#^x]]" in (v / "ambitos/x/x.md").read_text(encoding="utf-8")

    segunda = fix.fix_link(v)
    assert segunda.ok and "nada que convertir" in segunda.mensaje
    assert ahora.stat().st_mtime_ns == antes


def test_fix_con_hallazgos_mixtos_aplica_lo_determinista_y_lista_las_decisiones(
    tmp_path: Path,
) -> None:
    v = _vault(
        tmp_path,
        {
            "AHORA.md": "[[x]] y [[fantasma]] y [[doble]] y [roto](no/esta.md)\n",
            "ambitos/x/x.md": "# x\n",
            "a/doble.md": "",
            "b/doble.md": "",
        },
    )
    r = fix.fix_link(v)

    assert not r.ok and not r.error
    assert (v / "AHORA.md").read_text(encoding="utf-8") == (
        "[x](ambitos/x/x.md) y [[fantasma]] y [[doble]] y [roto](no/esta.md)\n"
    )
    assert "3 decisión(es)" in r.mensaje
    assert "[[fantasma]]" in r.mensaje and "ambiguo" in r.mensaje and "no/esta.md" in r.mensaje


def test_fix_alcanza_los_ciclos_cerrados(tmp_path: Path) -> None:
    v = _vault(tmp_path, {"bitacoras/b.md": "- 09:00 - [[x]]\n", "ambitos/x/x.md": "# x\n"})
    fix.fix_link(v)
    assert (v / "bitacoras/b.md").read_text(encoding="utf-8") == (
        "- 09:00 - [x](../ambitos/x/x.md)\n"
    )


def test_corregir_despacha_por_tema(tmp_path: Path) -> None:
    v = _vault(tmp_path, {"AHORA.md": "nada\n"})
    assert fix.corregir(v, "link").ok
    with pytest.raises(KeyError):
        fix.corregir(v, "inexistente")
