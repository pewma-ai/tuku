"""Test del escenario 002-10-cli-superficie.

Escenario: 002-10-cli-superficie.md

Fija la superficie del CLI que agrega el epic 002: los nouns en `tuku -h`, sus
verbs, los códigos de salida y la regla transversal de que toda salida de error
nombre el defecto y la corrección.

Fuera de la cadena: no produce un estado que herede nadie. El vault que necesita
para ejercer los códigos vive en un tempdir, no en `playground/`.

Ejecutable directo: python3 tests/escenarios/test_002_11_cli_superficie.py
"""

from __future__ import annotations

import io
import sys
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from tuku.cli import ENTORNO, EXITO, RECHAZO, USO, main  # noqa: E402
from tuku.lint import lint  # noqa: E402

MAL_ESCRITA = "- 13:00 - [[personal]] **Pendiente**: comprar una maleta"
DESCONOCIDO = "- 12:05 - [[personal]] **cachureo**: ordené los cables"


def _correr(argv: list[str]) -> tuple[int | None, str, str]:
    """Llama a `main(argv)` capturando salida, error y el código con que sale."""
    out, err = io.StringIO(), io.StringIO()
    codigo: int | None = None
    with redirect_stdout(out), redirect_stderr(err):
        try:
            codigo = main(argv)
        except SystemExit as e:
            codigo = e.code if isinstance(e.code, int) else 1
    return codigo, out.getvalue(), err.getvalue()


@contextmanager
def _vault_sembrado() -> Iterator[Path]:
    """Un vault vanilla en un tempdir, con el ciclo del 11 al 17 de agosto."""
    with tempfile.TemporaryDirectory() as tmp:
        destino = Path(tmp) / "vault"
        codigo, _, err = _correr(["init", str(destino)])
        assert codigo == EXITO, err
        yield destino


def test_002_10_tuku_h_nombra_los_nouns_del_epic() -> None:
    codigo, salida, _ = _correr(["-h"])
    assert codigo == EXITO
    for noun in (
        "init",
        "entry",
        "vocab",
        "cycle",
        "style",
        "todo",
        "scope",
        "link",
        "note",
    ):
        assert noun in salida, f"`tuku -h` no nombra {noun}"


def test_002_10_cada_noun_lista_sus_verbs() -> None:
    codigo, salida, _ = _correr(["entry", "-h"])
    assert codigo == EXITO
    assert "add" in salida and "lint" in salida, salida

    codigo, salida, _ = _correr(["vocab", "-h"])
    assert codigo == EXITO
    assert "show" in salida, salida

    codigo, salida, _ = _correr(["cycle", "-h"])
    assert codigo == EXITO
    assert "open" in salida, salida

    codigo, salida, _ = _correr(["style", "-h"])
    assert codigo == EXITO
    assert "lint" in salida, salida

    codigo, salida, _ = _correr(["todo", "-h"])
    assert codigo == EXITO
    assert "open" in salida and "close" in salida and "lint" in salida, salida

    codigo, salida, _ = _correr(["scope", "-h"])
    assert codigo == EXITO
    assert "create" in salida and "lint" in salida, salida

    codigo, salida, _ = _correr(["link", "-h"])
    assert codigo == EXITO
    assert "backfill" in salida, salida

    codigo, salida, _ = _correr(["note", "-h"])
    assert codigo == EXITO
    assert "create" in salida and "lint" in salida, salida

    codigo, salida, _ = _correr(["entry", "add", "-h"])
    assert codigo == EXITO
    for pieza in ("line", "--vault", "--day"):
        assert pieza in salida, f"`tuku entry add -h` no nombra {pieza}"


def test_002_10_un_noun_sin_verb_es_error_de_uso() -> None:
    codigo, _, _ = _correr(["entry"])
    assert codigo == USO, "un noun sin verb debería ser error de uso, no rechazo"


def test_002_10_el_lint_sale_con_rechazo_solo_ante_la_ontologia_cerrada() -> None:
    with _vault_sembrado() as vault:
        dia = _primer_dia(vault)

        agregar = ["entry", "add", "--vault", str(vault), "--dia", dia]
        codigo, _, err = _correr([*agregar, DESCONOCIDO])
        assert codigo == EXITO, err
        codigo, salida, _ = _correr(["entry", "lint", "--vault", str(vault)])
        assert codigo == EXITO, f"una pregunta abierta no debería mover el código: {salida}"

        codigo, _, err = _correr([*agregar, MAL_ESCRITA])
        assert codigo == EXITO, err
        codigo, salida, _ = _correr(["entry", "lint", "--vault", str(vault)])
        assert codigo == RECHAZO, f"la ontología cerrada debería mover el código: {salida}"
        assert codigo != USO


def test_002_10_un_directorio_que_no_es_vault_dice_que_hacer() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        codigo, _, err = _correr(["entry", "lint", "--vault", tmp])
    assert codigo == RECHAZO
    assert "AHORA.md" in err, "el error no nombra el archivo que falta"
    assert "tuku init" in err, "el error no dice cómo corregirse"


def test_002_10_todo_hallazgo_nombra_la_correccion() -> None:
    with _vault_sembrado() as vault:
        dia = _primer_dia(vault)
        _correr(["entry", "add", "--vault", str(vault), "--dia", dia, MAL_ESCRITA, DESCONOCIDO])
        ahora = (vault / "AHORA.md").read_text(encoding="utf-8")

    hallazgos = lint(ahora, abiertos=["progreso"])
    assert hallazgos, "el barrido no encontró ningún hallazgo que revisar"
    for h in hallazgos:
        assert h.correccion.strip(), f"hallazgo sin corrección: {h.defecto}"


def test_002_10_ningun_comando_escribe_una_propuesta() -> None:
    """La mitad estructural del principio 3, la única verificable sin agente.

    La propuesta es la consecuencia que a propósito no tiene comando: se muestra
    y espera, y una rechazada no escribe nada, así que no hay nada que limpiar.
    Que el agente proponga en vez de escribir necesita al agente en el circuito
    y se prueba en el epic 003.
    """
    _, salida, _ = _correr(["-h"])
    assert "propose" not in salida, "apareció un verbo que persiste propuestas"

    fuentes = (RAIZ / "src" / "tuku").glob("*.py")
    for fuente in fuentes:
        texto = fuente.read_text(encoding="utf-8")
        assert "propuestas/" not in texto, f"{fuente.name} escribe en propuestas/"


def test_002_10_los_codigos_son_distintos() -> None:
    codigos = [EXITO, RECHAZO, USO, ENTORNO]
    assert len(set(codigos)) == len(codigos), "dos causas comparten código de salida"


def _primer_dia(vault: Path) -> str:
    for linea in (vault / "AHORA.md").read_text(encoding="utf-8").splitlines():
        if linea.startswith("## "):
            return linea.removeprefix("## ")
    raise AssertionError("el vault sembrado no tiene ningún encabezado de día")


if __name__ == "__main__":
    test_002_10_tuku_h_nombra_los_nouns_del_epic()
    test_002_10_cada_noun_lista_sus_verbs()
    test_002_10_un_noun_sin_verb_es_error_de_uso()
    test_002_10_el_lint_sale_con_rechazo_solo_ante_la_ontologia_cerrada()
    test_002_10_un_directorio_que_no_es_vault_dice_que_hacer()
    test_002_10_todo_hallazgo_nombra_la_correccion()
    test_002_10_ningun_comando_escribe_una_propuesta()
    test_002_10_los_codigos_son_distintos()
    print("ok: la superficie del CLI del epic 002 está fijada")
