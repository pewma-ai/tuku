"""Tests del doctor: la revisión de las tablas de contrato."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from tuku import doctor, entry, init
from tuku.doctor import (
    TIPOS_REQUERIDOS,
    Revision,
    ausente,
    formatear,
    revisar_archivos,
    revisar_frontmatter,
    revisar_tipos,
    tipo_declarado,
    tipos_declarados,
)

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent

# Con el separador espaciado que produce el formateador de tablas de Obsidian.
TABLA = (
    "---\ntype: Config\n---\n\n"
    "| `type`    | Qué archivo | Se reconoce por |\n"
    "| --------- | ----------- | --------------- |\n"
    + "".join(f"| `{t}` | un archivo | algo |\n" for t in TIPOS_REQUERIDOS)
)


def test_la_tabla_de_tipos_se_lee_y_se_revisa() -> None:
    assert tipos_declarados(TABLA) == list(TIPOS_REQUERIDOS), (
        "el encabezado no cuenta como tipo"
    )

    callout = "> [!warning] Estos nombres no son tuyos\n> Renombrar uno rompe todo.\n\n"
    con_callout = TABLA.replace("---\n\n|", f"---\n\n{callout}|")
    assert tipos_declarados(con_callout) == list(TIPOS_REQUERIDOS)

    sana = revisar_tipos(TABLA)
    assert sana.sano and str(len(TIPOS_REQUERIDOS)) in sana.salida

    sin_tipo = revisar_tipos(TABLA.replace("| `Cadence` | un archivo | algo |\n", ""))
    assert not sin_tipo.sano and "`Cadence`" in sin_tipo.salida

    sin_archivo = revisar_tipos(None)
    assert not sin_archivo.sano and "reglas/types.md" in sin_archivo.salida


ROTA = [Revision("types", "roto", False), Revision("cycle", "bien", True)]


def test_el_reporte_nombra_lo_roto_y_apunta_al_template_original() -> None:
    salida = formatear(ROTA)
    assert "types" in salida and "sano" not in salida

    con_fuente = formatear(ROTA, fuente=Path("/casa/.tuku/template/vanilla"))
    assert "/casa/.tuku/template/vanilla" in con_fuente.splitlines()[-1]
    assert "no toca nada" in con_fuente

    assert "Reinstala TUKU" in formatear(ROTA, fuente=None).splitlines()[-1]

    sano = formatear([Revision("types", "bien", True)], fuente=Path("/casa/.tuku"))
    assert "/casa/.tuku" not in sano and sano.endswith("el vault está sano.")


SANA = Revision("config", "config: 5 campos declarados.", True)
AVISO = Revision("version", "version: aviso: el vault es anterior.", True, aviso=True)
ROTA_LINK = Revision("link", "AHORA.md:1: error: x.\nlink: 1 error(es).", False)


def test_sin_verbose_solo_hallazgos_y_avisos() -> None:
    assert formatear([SANA, SANA]) == "doctor: el vault está sano."
    assert formatear([SANA, SANA], verbose=True) == (
        "config: 5 campos declarados.\n"
        "config: 5 campos declarados.\n"
        "doctor: el vault está sano."
    )
    assert formatear([SANA, AVISO]) == (
        "version: aviso: el vault es anterior.\ndoctor: el vault está sano."
    )

    salida = formatear([SANA, ROTA_LINK, AVISO])
    assert "config:" not in salida
    assert "AHORA.md:1: error: x." in salida and "version: aviso" in salida
    assert "doctor: 1 revisión(es) con hallazgos: link." in salida

    salida = formatear([SANA, ROTA_LINK], verbose=True)
    assert "config:" in salida and "AHORA.md:1: error: x." in salida


def _vault(tmp: Path, archivos: dict[str, str]) -> Path:
    for relativo, contenido in archivos.items():
        destino = tmp / relativo
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(contenido, encoding="utf-8")
    return tmp


COMPLETO = {
    "AHORA.md": "---\ntype: Logbook\n---\n",
    "PENDIENTES.md": "---\ntype: Todo\n---\n",
    "LIBRO-DE-ESTILO.md": "---\ntype: Style Guide\n---\n",
    "ambitos/personal/personal.md": "---\ntype: Scope\n---\n",
    "ambitos/AGENTS.md": "# Reglas, sin frontmatter a propósito\n",
    "reglas/config.tuku.md": "---\ntype: Config\n---\n",
    "reglas/types.md": "---\ntype: Config\n---\n",
    "reglas/plantilla/AHORA.md": "---\ntype: Logbook\n---\n",
}
VALIDOS = ["Config", "Logbook", "Scope", "Style Guide", "Todo"]


def test_el_vault_sembrado_y_una_pregunta_del_lint_no_fallan(tmp_path: Path) -> None:
    sembrado = init.init(tmp_path / "limpio", home=RAIZ_REPO)
    r = doctor.revisar_vault(sembrado)
    assert r.ok
    assert r.mensaje.splitlines()[-1] == "doctor: el vault está sano."
    assert "files:" not in r.mensaje

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


def test_un_vault_completo_esta_sano_y_no_exige_frontmatter_a_agents_ni_plantilla(
    tmp_path: Path,
) -> None:
    vault = _vault(tmp_path, COMPLETO)

    assert revisar_archivos(vault).sano
    revision = revisar_frontmatter(vault, tipos_validos=VALIDOS)
    assert revision.sano
    assert "7 archivos" in revision.salida  # los 8 menos el AGENTS.md
    assert "AGENTS.md" not in revision.salida
    assert "plantilla/AHORA.md" not in revision.salida


def test_un_vault_con_defectos_los_nombra(tmp_path: Path) -> None:
    sin_type = revisar_frontmatter(
        _vault(tmp_path / "a", {**COMPLETO, "notas/suelta.md": "# Sin frontmatter\n"}),
        tipos_validos=VALIDOS,
    )
    assert not sin_type.sano
    assert "notas/suelta.md" in sin_type.salida and "no declara `type`" in sin_type.salida

    raro = revisar_frontmatter(
        _vault(tmp_path / "b", {**COMPLETO, "ambitos/raro.md": "---\ntype: Cosa\n---\n"}),
        tipos_validos=VALIDOS,
    )
    assert not raro.sano and "`type: Cosa`" in raro.salida

    faltante = {k: v for k, v in COMPLETO.items() if k != "reglas/types.md"}
    sin_archivo = revisar_archivos(_vault(tmp_path / "c", faltante))
    assert not sin_archivo.sano
    assert "reglas/types.md: error: falta el archivo." in sin_archivo.salida


def test_el_type_solo_cuenta_en_el_frontmatter_y_una_revision_ausente_falla() -> None:
    assert tipo_declarado("# Prosa\n\ntype: Config\n") is None
    assert tipo_declarado("---\ntype: Config\n---\n\ncuerpo\n") == "Config"

    revision = ausente("todo", "PENDIENTES.md")
    assert not revision.sano and "falta PENDIENTES.md" in revision.salida


CONFIG = "| Campo | Valor |\n| --- | --- |\n| `tuku_version` | `{}` |\n"


def test_la_version_del_vault_se_compara_con_la_del_paquete() -> None:
    anterior = doctor.revisar_version(CONFIG.format("1.0"), "2.0")
    assert anterior.sano
    assert (
        "1.0" in anterior.salida and "2.0" in anterior.salida and "~/.tuku" in anterior.salida
    )

    al_dia = doctor.revisar_version(CONFIG.format("2.0"), "2.0")
    assert al_dia.sano and "al día" in al_dia.salida

    sin_referencia = doctor.revisar_version(CONFIG.format("1.0"), None)
    assert sin_referencia.sano and "sin sello" in sin_referencia.salida

    assert doctor.revisar_version(None, "2.0").sano
