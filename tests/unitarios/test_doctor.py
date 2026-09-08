"""Tests del doctor: la revisión de las tablas de contrato."""

from __future__ import annotations

from pathlib import Path

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

# Con el separador espaciado que produce el formateador de tablas de Obsidian.
TABLA = (
    "---\ntype: Config\n---\n\n"
    "| `type`    | Qué archivo | Se reconoce por |\n"
    "| --------- | ----------- | --------------- |\n"
    + "".join(f"| `{t}` | un archivo | algo |\n" for t in TIPOS_REQUERIDOS)
)


def test_el_encabezado_de_la_tabla_no_cuenta_como_tipo() -> None:
    assert tipos_declarados(TABLA) == list(TIPOS_REQUERIDOS)


def test_el_callout_de_advertencia_no_estorba() -> None:
    callout = "> [!warning] Estos nombres no son tuyos\n> Renombrar uno rompe todo.\n\n"
    con_callout = TABLA.replace("---\n\n|", f"---\n\n{callout}|")

    assert tipos_declarados(con_callout) == list(TIPOS_REQUERIDOS)


def test_tabla_completa_esta_sana() -> None:
    revision = revisar_tipos(TABLA)

    assert revision.sano
    assert str(len(TIPOS_REQUERIDOS)) in revision.salida


def test_falta_un_tipo_requerido() -> None:
    revision = revisar_tipos(TABLA.replace("| `Cadence` | un archivo | algo |\n", ""))

    assert not revision.sano
    assert "`Cadence`" in revision.salida


def test_falta_el_archivo_entero() -> None:
    revision = revisar_tipos(None)

    assert not revision.sano
    assert "reglas/types.md" in revision.salida


ROTA = [Revision("types", "roto", False), Revision("cycle", "bien", True)]


def test_el_reporte_nombra_las_revisiones_rotas() -> None:
    salida = formatear(ROTA)

    assert "types" in salida
    assert "sano" not in salida


def test_el_reporte_roto_apunta_al_template_original() -> None:
    salida = formatear(ROTA, fuente=Path("/casa/.tuku/template/vanilla"))

    assert "/casa/.tuku/template/vanilla" in salida.splitlines()[-1]
    assert "no toca nada" in salida


def test_sin_template_original_lo_dice() -> None:
    salida = formatear(ROTA, fuente=None)

    assert "Reinstala TUKU" in salida.splitlines()[-1]


def test_el_vault_sano_no_menciona_el_template() -> None:
    salida = formatear([Revision("types", "bien", True)], fuente=Path("/casa/.tuku"))

    assert "/casa/.tuku" not in salida
    assert salida.endswith("el vault está sano.")


def _vault(tmp: Path, archivos: dict[str, str]) -> Path:
    for relativo, contenido in archivos.items():
        destino = tmp / relativo
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(contenido, encoding="utf-8")
    return tmp


COMPLETO = {
    "AHORA.md": "---\ntype: Logbook\n---\n",
    "PENDIENTES.md": "---\ntype: Pending\n---\n",
    "LIBRO-DE-ESTILO.md": "---\ntype: Style Guide\n---\n",
    "ambitos/personal/personal.md": "---\ntype: Scope\n---\n",
    "ambitos/AGENTS.md": "# Reglas, sin frontmatter a propósito\n",
    "reglas/config.tuku.md": "---\ntype: Config\n---\n",
    "reglas/types.md": "---\ntype: Config\n---\n",
    "reglas/plantilla/AHORA.md": "---\ntype: Logbook\n---\n",
}
VALIDOS = ["Config", "Logbook", "Pending", "Scope", "Style Guide"]


def test_vault_completo_esta_sano(tmp_path: Path) -> None:
    vault = _vault(tmp_path, COMPLETO)

    assert revisar_archivos(vault).sano
    revision = revisar_frontmatter(vault, tipos_validos=VALIDOS)
    assert revision.sano
    assert "7 archivos" in revision.salida  # los 8 menos el AGENTS.md


def test_los_agents_md_no_llevan_frontmatter(tmp_path: Path) -> None:
    revision = revisar_frontmatter(_vault(tmp_path, COMPLETO), tipos_validos=VALIDOS)

    assert "AGENTS.md" not in revision.salida


def test_la_plantilla_no_tiene_que_ser_config(tmp_path: Path) -> None:
    revision = revisar_frontmatter(_vault(tmp_path, COMPLETO), tipos_validos=VALIDOS)

    assert "plantilla/AHORA.md" not in revision.salida


def test_un_archivo_sin_type(tmp_path: Path) -> None:
    archivos = {**COMPLETO, "notas/suelta.md": "# Sin frontmatter\n"}
    revision = revisar_frontmatter(_vault(tmp_path, archivos), tipos_validos=VALIDOS)

    assert not revision.sano
    assert "notas/suelta.md" in revision.salida
    assert "no declara `type`" in revision.salida


def test_un_type_que_no_esta_en_la_tabla(tmp_path: Path) -> None:
    archivos = {**COMPLETO, "ambitos/raro.md": "---\ntype: Cosa\n---\n"}
    revision = revisar_frontmatter(_vault(tmp_path, archivos), tipos_validos=VALIDOS)

    assert not revision.sano
    assert "`type: Cosa`" in revision.salida


def test_falta_un_archivo_requerido(tmp_path: Path) -> None:
    archivos = {k: v for k, v in COMPLETO.items() if k != "reglas/types.md"}
    revision = revisar_archivos(_vault(tmp_path, archivos))

    assert not revision.sano
    assert "reglas/types.md: error: falta el archivo." in revision.salida


def test_type_en_el_cuerpo_no_cuenta_como_frontmatter() -> None:
    assert tipo_declarado("# Prosa\n\ntype: Config\n") is None
    assert tipo_declarado("---\ntype: Config\n---\n\ncuerpo\n") == "Config"


def test_una_revision_ausente_no_esta_sana() -> None:
    revision = ausente("todo", "PENDIENTES.md")

    assert not revision.sano
    assert "falta PENDIENTES.md" in revision.salida
