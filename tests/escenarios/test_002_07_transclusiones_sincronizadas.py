"""Test del escenario 002-07-transclusiones-sincronizadas.

Escenario: 002-07-transclusiones-sincronizadas.md

Séptimo paso de la cadena. Las dos direcciones de falla de la regla 6 de
`spec/pendientes.md`, por la segunda vía: se rompe el archivo a mano, que no es
un hecho de la vida del autor y por eso no pasa por la bitácora, y se invoca
`tuku transclusion sync`.

La falla silenciosa (callout sin transclusión) es la que justifica que el
comando exista: el pendiente no aparece en la agenda y el autor se entera
cuando ya venció.

Ejecutable directo: python3 tests/escenarios/test_002_07_transclusiones_sincronizadas.py
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

from cadena import delta, instantanea, preparar_paso  # noqa: E402

from tuku import transclusion  # noqa: E402

SLUG = "002-07-transclusiones-sincronizadas"
PREVIO = "002-06-escribir-en-un-dia-fecha"
DESDE = date(2026, 8, 11)

MIERCOLES = "## Miércoles 12 de agosto"
VIERNES = "## Viernes 14 de agosto"
ANCLA = "2026-08-12"
HUERFANA = "2026-08-14"


def _sync(vault: Path) -> list[str]:
    ahora, pendientes = vault / "AHORA.md", vault / "PENDIENTES.md"
    texto, reparaciones = transclusion.sync(
        ahora.read_text(encoding="utf-8"), pendientes.read_text(encoding="utf-8")
    )
    ahora.write_text(texto, encoding="utf-8")
    return reparaciones


def _editar_ahora(vault: Path, transformar) -> None:  # type: ignore[no-untyped-def]
    """Rompe `AHORA.md` a mano: es la segunda vía, no un registro."""
    ruta = vault / "AHORA.md"
    lineas = ruta.read_text(encoding="utf-8").splitlines()
    ruta.write_text("\n".join(transformar(lineas)) + "\n", encoding="utf-8")


def test_002_07_las_dos_direcciones_de_falla_se_reparan() -> None:
    vault = preparar_paso(SLUG, previo=PREVIO, desde=DESDE)
    sano = instantanea(vault)
    linea = transclusion.linea_de(ANCLA)

    # Falla silenciosa: el callout sigue, la transclusión desaparece.
    _editar_ahora(vault, lambda ls: [x for x in ls if x != linea])
    assert delta(sano, instantanea(vault)) == {"AHORA.md": "modificado"}

    reparaciones = _sync(vault)
    assert any(ANCLA in r and "agregada" in r for r in reparaciones), reparaciones
    lineas = (vault / "AHORA.md").read_text(encoding="utf-8").splitlines()
    assert lineas[lineas.index(MIERCOLES) + 1] == linea, "la transclusión no volvió a su día"
    assert delta(sano, instantanea(vault)) == {}, "el vault reparado no volvió al estado sano"


def test_002_07_una_transclusion_sin_callout_se_quita() -> None:
    vault = preparar_paso(SLUG, previo=PREVIO, desde=DESDE)
    sano = instantanea(vault)
    huerfana = transclusion.linea_de(HUERFANA)

    def _insertar(lineas: list[str]) -> list[str]:
        i = lineas.index(VIERNES)
        return [*lineas[: i + 1], huerfana, *lineas[i + 1 :]]

    _editar_ahora(vault, _insertar)
    reparaciones = _sync(vault)

    ahora = (vault / "AHORA.md").read_text(encoding="utf-8")
    assert any(HUERFANA in r and "quitada" in r for r in reparaciones), reparaciones
    assert huerfana not in ahora, "la transclusión huérfana sigue ahí"
    pendientes = (vault / "PENDIENTES.md").read_text(encoding="utf-8")
    assert f"^{HUERFANA}" not in pendientes, "se inventó el callout para justificarla"
    assert delta(sano, instantanea(vault)) == {}


def test_002_07_las_anclas_de_horizonte_no_se_tocan() -> None:
    vault = preparar_paso(SLUG, previo=PREVIO, desde=DESDE)
    horizonte = transclusion.linea_de("sin-fecha")

    def _insertar(lineas: list[str]) -> list[str]:
        i = lineas.index(VIERNES)
        return [*lineas[: i + 1], horizonte, *lineas[i + 1 :]]

    _editar_ahora(vault, _insertar)
    con_horizonte = instantanea(vault)
    _sync(vault)

    assert delta(con_horizonte, instantanea(vault)) == {}, "el comando tocó un horizonte"
    assert horizonte in (vault / "AHORA.md").read_text(encoding="utf-8")


def test_002_07_sobre_un_vault_sano_no_hace_nada() -> None:
    vault = preparar_paso(SLUG, previo=PREVIO, desde=DESDE)
    sano = instantanea(vault)

    assert _sync(vault) == [], "reparó algo sobre un vault sano"
    assert _sync(vault) == [], "el segundo pase reparó algo"
    assert delta(sano, instantanea(vault)) == {}


if __name__ == "__main__":
    test_002_07_las_dos_direcciones_de_falla_se_reparan()
    test_002_07_una_transclusion_sin_callout_se_quita()
    test_002_07_las_anclas_de_horizonte_no_se_tocan()
    test_002_07_sobre_un_vault_sano_no_hace_nada()
    print(f"ok: 4 afirmaciones (queda en playground/{SLUG}/)")
