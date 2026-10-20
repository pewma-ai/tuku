"""`tuku regenerate`: valida el canónico antes de escribir, y cada tema regenera lo suyo."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from tuku import doctor, init, regenerate
from tuku.cli import EXITO, main
from tuku.regenerate import TEMAS, regenerar

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent
A_MANO = "- 10:00 - [personal](ambitos/personal/personal.md) **nota**: escrito a mano"
VISTA = Path("ambitos") / "PENDIENTES-AMBITOS.md"
PAGINA = Path("ambitos") / "personal" / "personal.md"
COMANDOS = Path("reglas") / "comandos.tuku.md"


def _desfasado(tmp_path: Path) -> Path:
    """Un vault donde cada derivado está atrasado respecto de su fuente."""
    v = init.init(tmp_path / "v", home=RAIZ_REPO, desde=date(2026, 8, 10))
    ahora = v / "AHORA.md"
    ahora.write_text(
        ahora.read_text(encoding="utf-8").replace(
            "## Martes 11 de agosto\n", f"## Martes 11 de agosto\n{A_MANO}\n"
        ),
        encoding="utf-8",
    )
    (v / VISTA).unlink()
    (v / COMANDOS).write_text("viejo\n", encoding="utf-8")
    return v


def test_los_temas_son_cuatro_y_sin_tabla_se_rechaza(tmp_path: Path) -> None:
    assert TEMAS == ("todo", "scope", "comandos", "libro")
    (tmp_path / "PENDIENTES.md").write_text("sin tabla", encoding="utf-8")
    r = regenerar(tmp_path)
    assert not r.ok
    assert "PENDIENTES.md" in r.mensaje


def test_cada_tema_regenera_lo_suyo_y_deja_lo_demas(tmp_path: Path) -> None:
    v = _desfasado(tmp_path / "todo")
    regenerar(v, tema="todo", comandos="nuevo\n")
    assert (v / VISTA).is_file()
    assert "escrito a mano" not in (v / PAGINA).read_text(encoding="utf-8")
    assert (v / COMANDOS).read_text(encoding="utf-8") == "viejo\n"

    v = _desfasado(tmp_path / "scope")
    regenerar(v, tema="scope", comandos="nuevo\n")
    assert "escrito a mano" in (v / PAGINA).read_text(encoding="utf-8")
    assert not (v / VISTA).exists()
    assert (v / COMANDOS).read_text(encoding="utf-8") == "viejo\n"

    v = _desfasado(tmp_path / "comandos")
    ahora = (v / "AHORA.md").read_bytes()
    regenerar(v, tema="comandos", comandos="nuevo\n")
    assert (v / COMANDOS).read_text(encoding="utf-8") == "nuevo\n"
    assert (v / "AHORA.md").read_bytes() == ahora
    assert not (v / VISTA).exists()
    assert "escrito a mano" not in (v / PAGINA).read_text(encoding="utf-8")

    v = _desfasado(tmp_path / "todos")
    regenerar(v, comandos="nuevo\n")
    assert (v / VISTA).is_file()
    assert "escrito a mano" in (v / PAGINA).read_text(encoding="utf-8")
    assert (v / COMANDOS).read_text(encoding="utf-8") == "nuevo\n"


def test_comandos_no_necesita_un_canonico_sano(tmp_path: Path) -> None:
    v = _desfasado(tmp_path)
    (v / "PENDIENTES.md").write_text("sin tabla", encoding="utf-8")
    assert regenerar(v, tema="comandos", comandos="nuevo\n").ok
    assert not regenerar(v, tema="todo").ok


def test_cada_tema_es_idempotente_y_el_cli_los_acepta(tmp_path: Path) -> None:
    v = _desfasado(tmp_path)
    for tema in TEMAS:
        regenerar(v, tema=tema, comandos="nuevo\n")
        assert "al día" in regenerar(v, tema=tema, comandos="nuevo\n").mensaje
        assert main(["regenerate", tema, "--vault", str(v)]) == EXITO


def test_cada_canonico_rehace_solo_los_temas_que_dependen_de_el() -> None:
    assert regenerate.temas_afectados(["PENDIENTES.md"]) == ["todo"]
    assert regenerate.temas_afectados(["AHORA.md"]) == ["todo", "scope"]
    assert regenerate.temas_afectados(["bitacoras/bitacora-2026-08-03.md"]) == ["scope"]
    assert regenerate.temas_afectados(["ambitos/"]) == ["todo", "scope"]
    assert regenerate.temas_afectados(["notas/x.md", "reglas/config.tuku.md"]) == []


def test_libro_trae_la_prosa_de_tuku_y_no_toca_lo_del_autor_ni_los_valores(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TUKU_HOME", str(RAIZ_REPO))
    v = init.init(tmp_path / "v", home=RAIZ_REPO, desde=date(2026, 8, 10))
    libro = v / "LIBRO-DE-ESTILO.md"
    autor, config = v / "reglas" / "clasificaciones.user.md", v / "reglas" / "config.tuku.md"
    original = libro.read_text(encoding="utf-8")
    libro.write_text("editado a mano\n", encoding="utf-8")
    autor.write_text(
        "---\ntype: Style Guide\n---\n\n| C |\n| --- |\n| `mía` |\n",
        encoding="utf-8",
    )
    valores = config.read_text(encoding="utf-8").replace("`MMM/DD`", "`DD/MM`")
    config.write_text(valores, encoding="utf-8")

    r = regenerar(v, tema="libro")

    assert r.ok and "regenerado: LIBRO-DE-ESTILO.md" in r.mensaje
    assert libro.read_text(encoding="utf-8") == original
    assert "`mía`" in autor.read_text(encoding="utf-8"), "lo del autor no se toca"
    assert config.read_text(encoding="utf-8") == valores, "los valores del autor no se tocan"
    assert regenerar(v, tema="libro").mensaje == "regenerate: todo estaba al día."

    libro.write_text(original + "\nUna línea que el autor agregó.\n", encoding="utf-8")
    aviso = doctor.revisar_vault(v)
    assert aviso.ok and "difiere" in aviso.mensaje and "LIBRO-DE-ESTILO.md" in aviso.mensaje
