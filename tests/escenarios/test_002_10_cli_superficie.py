"""Tests del escenario 002-10-cli-superficie.

Escenario: 002-10-cli-superficie.md

La ayuda y los códigos de salida son superficie pública, y son la mitad del
entregable del epic que la cadena no mira: la cadena verifica el vault, este
verifica el comando. Más la regla transversal de `spec/cli.md`, convertida en
barrido: toda salida de error nombra el defecto y la corrección.

Los comandos salen del `.md`. Dos afirmaciones no son escenarios y se quedan en
Python porque no hay comando que las exprese: el barrido sobre los hallazgos que
el lint sabe producir, y la inspección de las fuentes que verifica que ningún
comando persista propuestas.

Está fuera de la cadena: no hereda de ningún paso ni deja estado para el
siguiente.

Ejecutable directo: `python3 tests/escenarios/test_002_10_cli_superficie.py`
"""

import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import gherkin  # noqa: E402

from tuku.cli import ENTORNO, EXITO, RECHAZO, USO, comandos, main  # noqa: E402
from tuku.lint import lint  # noqa: E402

SLUG = "002-10-cli-superficie"
MAL_ESCRITA = "- 13:00 - [[personal]] **Pendiente**: comprar una maleta"
DESCONOCIDO = "- 12:05 - [[personal]] **cachureo**: ordené los cables"
DIA = "## Martes 11 de agosto"

#: Cada noun del CLI con los verbs que su ayuda tiene que nombrar.
VERBS = {
    "entry": ("add", "rename", "lint"),
    "vocab": ("show",),
    "cycle": ("open", "lint"),
    "style": ("lint",),
    "todo": ("open", "close", "lint"),
    "scope": ("create", "rename", "lint"),
    "link": ("backfill",),
    "note": ("create", "rename", "lint"),
}


def test_002_10_tuku_h_nombra_los_nouns_del_epic() -> None:
    corrida = gherkin.correr(SLUG, "nombra los nouns del epic")
    assert corrida.codigo == EXITO, corrida.stderr
    for noun in ("init", "doctor", "rebuild", *VERBS):
        assert noun in corrida.stdout, f"`tuku -h` no nombra {noun}"


def test_002_10_cada_noun_lista_sus_verbs() -> None:
    corrida = gherkin.correr(SLUG, "cada noun lista sus verbs")

    for noun, verbs in VERBS.items():
        ayuda = corrida.de(f"tuku {noun} -h")
        assert ayuda.codigo == EXITO, ayuda.stderr
        for verb in verbs:
            assert verb in ayuda.stdout, f"`tuku {noun} -h` no nombra {verb}"

    add = corrida.de("entry add -h")
    for pieza in ("--body", "--scope", "--day", "--hour"):
        assert pieza in add.stdout, f"`tuku entry add -h` no nombra {pieza}"

    rename = corrida.de("entry rename -h")
    for pieza in ("--body", "--day", "--hour"):
        assert pieza in rename.stdout, f"`tuku entry rename -h` no nombra {pieza}"


def test_002_10_cada_comando_dice_como_se_hace_lo_mismo_a_mano() -> None:
    patrones_vault = (".md", "ambitos/", "notas/", "reglas/", "template/")
    patrones_codigo = ("def ", "import ", "module", "function", "class ")

    for cmd in sorted(comandos()):
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                main([*cmd.split(), "-h"])
        except SystemExit:
            pass
        salida = buf.getvalue().strip()
        assert "A mano:" in salida, f"`tuku {cmd} -h` no tiene el campo 'A mano':\n{salida}"
        assert any(ext in salida for ext in patrones_vault), (
            f"`tuku {cmd} -h` no nombra archivos del vault:\n{salida}"
        )
        assert not any(tecnico in salida for tecnico in patrones_codigo), (
            f"`tuku {cmd} -h` usa jerga técnica de código:\n{salida}"
        )


def test_002_10_un_noun_sin_verb_es_error_de_uso() -> None:
    corrida = gherkin.correr(SLUG, "un noun sin verb es error de uso")
    assert corrida.codigo == USO, "un noun sin verb debería ser error de uso, no rechazo"


def test_002_10_el_lint_sale_con_rechazo_solo_ante_la_ontologia_cerrada() -> None:
    corrida = gherkin.correr(SLUG, "el lint sale con rechazo cuando encuentra un error")

    lints = [r for r in corrida.resultados if "entry lint" in r.comando]
    assert len(lints) == 2, [r.comando for r in corrida.resultados]

    abierta, cerrada = lints
    assert abierta.codigo == EXITO, (
        f"una pregunta abierta no debería mover el código: {abierta.stdout}"
    )
    assert cerrada.codigo == RECHAZO, (
        f"la ontología cerrada debería mover el código: {cerrada.stdout}"
    )
    assert cerrada.codigo != USO


def test_002_10_un_directorio_que_no_es_vault_dice_que_hacer() -> None:
    corrida = gherkin.correr(SLUG, "un directorio que no es un vault se rechaza")

    assert corrida.codigo == RECHAZO
    assert "AHORA.md" in corrida.stderr, "el error no nombra el archivo que falta"
    assert "tuku init" in corrida.stderr, "el error no dice cómo corregirse"


def test_002_10_todo_hallazgo_nombra_la_correccion() -> None:
    """Barrido sobre los hallazgos, no un escenario: no hay comando que lo exprese."""
    corrida = gherkin.correr(SLUG, "el lint sale con rechazo cuando encuentra un error")
    ahora = corrida.ruta("mi-vault", "AHORA.md").read_text(encoding="utf-8")

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
    ayuda = gherkin.correr(SLUG, "nombra los nouns del epic")
    assert "propose" not in ayuda.stdout, "apareció un verbo que persiste propuestas"

    for fuente in (RAIZ / "src" / "tuku").glob("*.py"):
        texto = fuente.read_text(encoding="utf-8")
        assert "propuestas/" not in texto, f"{fuente.name} escribe en propuestas/"


def test_002_10_los_codigos_son_distintos() -> None:
    codigos = [EXITO, RECHAZO, USO, ENTORNO]
    assert len(set(codigos)) == len(codigos), "dos causas comparten código de salida"


if __name__ == "__main__":
    test_002_10_tuku_h_nombra_los_nouns_del_epic()
    test_002_10_cada_noun_lista_sus_verbs()
    test_002_10_cada_comando_dice_como_se_hace_lo_mismo_a_mano()
    test_002_10_un_noun_sin_verb_es_error_de_uso()
    test_002_10_el_lint_sale_con_rechazo_solo_ante_la_ontologia_cerrada()
    test_002_10_un_directorio_que_no_es_vault_dice_que_hacer()
    test_002_10_todo_hallazgo_nombra_la_correccion()
    test_002_10_ningun_comando_escribe_una_propuesta()
    test_002_10_los_codigos_son_distintos()
    print("ok: la superficie del CLI del epic 002 está fijada")
