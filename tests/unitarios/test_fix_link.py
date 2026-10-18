"""`tuku doctor link` y `tuku fix link` sobre un vault mínimo en disco."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from conftest import AHORA
from tuku import doctor, fix, init

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent


def _vault(tmp_path: Path, archivos: dict[str, str]) -> Path:
    for rel, texto in archivos.items():
        ruta = tmp_path / rel
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(texto, encoding="utf-8")
    return tmp_path


def test_doctor_link_reporta_wikilinks_y_rotos_e_ignora_transclusiones_y_codigo(
    tmp_path: Path,
) -> None:
    assert doctor.revisar_links(
        init.init(tmp_path / "v", home=RAIZ_REPO, desde=AHORA.date())
    ).sano

    wiki = doctor.revisar_links(
        _vault(
            tmp_path / "a", {"AHORA.md": "- 09:00 - [[x]] algo\n", "ambitos/x/x.md": "# x\n"}
        )
    )
    assert not wiki.sano
    assert "AHORA.md:1" in wiki.salida and "tuku fix link" in wiki.salida

    roto = doctor.revisar_links(
        _vault(tmp_path / "b", {"AHORA.md": "ver [x](ambitos/x/x.md)\n"})
    )
    assert not roto.sano and "no existe" in roto.salida

    ignora = {"AHORA.md": "![[otro.md#^a]] `[[b]]`\n```\n[[c]]\n```\n"}
    assert doctor.revisar_links(_vault(tmp_path / "c", ignora)).sano

    v = _vault(tmp_path / "d", {"AHORA.md": "sin links\n"})
    r = doctor.revisar_vault(v, tema="link")
    assert r.ok and r.mensaje == "doctor link: sin hallazgos."
    detallado = doctor.revisar_vault(v, tema="link", verbose=True)
    assert "link: sin wikilinks ni links rotos." in detallado.mensaje


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


def test_fix_alcanza_los_ciclos_cerrados_y_corregir_despacha_por_tema(tmp_path: Path) -> None:
    v = _vault(tmp_path, {"bitacoras/b.md": "- 09:00 - [[x]]\n", "ambitos/x/x.md": "# x\n"})
    assert fix.corregir(v, "link").ok
    assert (v / "bitacoras/b.md").read_text(encoding="utf-8") == (
        "- 09:00 - [x](../ambitos/x/x.md)\n"
    )
    with pytest.raises(KeyError):
        fix.corregir(v, "inexistente")
