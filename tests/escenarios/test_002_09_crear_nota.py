"""Test del escenario 002-09-crear-nota.

Escenario: 002-09-crear-nota.md

Noveno paso de la cadena, punto 5 del epic en su versión mínima. La nota se
escribe donde corresponde, deja constancia en la bitácora, enlaza a su ámbito
porque la petición lo nombró, y `note lint` comprueba lo verificable sin juicio.

FIXTURE PROVISIONAL. `fixtures/002-09-crear-nota/cuerpo-nota.md` es texto
escrito a mano, no salida real de un agente. El escenario dice que el cuerpo
sale del fixture congelado de `003-01`, que todavía no existe porque el paso
agéntico está diferido. **Para regenerarlo:** implementar `003-01`, tomar de su
fixture el cuerpo que el agente redactó para esta nota, y reemplazar este
archivo. Nada de lo que este test afirma depende del texto, solo de que haya
uno: dónde queda el archivo, la constancia, el enlace y el lint son
deterministas.

Ejecutable directo: python3 tests/escenarios/test_002_09_crear_nota.py
"""

from __future__ import annotations

import sys
import tempfile
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

from cadena import correr_cli, delta, instantanea, preparar_paso  # noqa: E402

from tuku import note  # noqa: E402
from tuku.cli import EXITO, RECHAZO  # noqa: E402

SLUG = "002-09-crear-nota"
PREVIO = "002-08-crear-ambito"
DESDE = date(2026, 8, 11)
HOY = "## Martes 11 de agosto"

AMBITO = "depto-centro"
TITULO = "cómo funciona el cobro de gastos comunes en una copropiedad"
ARCHIVO = "como-funciona-el-cobro-de-gastos-comunes-en-una-copropiedad.md"
HORA = "21:15"

FIXTURE = Path(__file__).parent / "fixtures" / SLUG / "cuerpo-nota.md"


def _crear(vault: Path) -> Path:
    """El flujo del punto 5: escribir la nota y dejar constancia en la bitácora."""
    codigo, _, err = correr_cli(
        [
            "note",
            "create",
            TITULO,
            "--body-file",
            str(FIXTURE),
            "--scope",
            AMBITO,
            "--today",
            DESDE.isoformat(),
            "--time",
            HORA,
            "--day",
            HOY,
            "--vault",
            str(vault),
        ]
    )
    assert codigo == EXITO, err
    return vault / "notas" / ARCHIVO


def test_002_09_la_nota_queda_escrita_enlazada_y_con_constancia() -> None:
    vault = preparar_paso(SLUG, previo=PREVIO, desde=DESDE)
    antes = instantanea(vault)
    ruta = _crear(vault)

    assert ruta == vault / "notas" / ARCHIVO, ruta
    contenido = ruta.read_text(encoding="utf-8")
    assert f"created: {DESDE.isoformat()}" in contenido, "falta created con la fecha de hoy"
    assert FIXTURE.read_text(encoding="utf-8").strip() in contenido, "no llegó el cuerpo"

    assert f"[[{AMBITO}]]" in contenido, "la nota no enlaza a su ámbito"
    assert (vault / "ambitos" / AMBITO / f"{AMBITO}.md").is_file(), "el enlace no resuelve"

    ahora = (vault / "AHORA.md").read_text(encoding="utf-8")
    assert f"[[{ruta.stem}]]" in ahora, "la constancia no enlaza a la nota"

    assert delta(antes, instantanea(vault)) == {
        "AHORA.md": "modificado",
        f"ambitos/{AMBITO}/{AMBITO}.md": "modificado",
        f"notas/{ARCHIVO}": "nuevo",
    }

    contenido_depto = (vault / "ambitos" / AMBITO / f"{AMBITO}.md").read_text(encoding="utf-8")
    assert "## Esta semana" in contenido_depto
    linea_boleta = (
        "- le mandé la boleta de gastos comunes del depto-centro a la "
        "administradora por WhatsApp"
    )
    assert linea_boleta in contenido_depto
    assert (
        f"- **nota**: escribí la nota [[{Path(ARCHIVO).stem}]]"
        in contenido_depto
    )


def test_002_09_ver_ademas_existe_y_cada_enlace_lleva_motivo() -> None:
    vault = preparar_paso(SLUG, previo=PREVIO, desde=DESDE)
    ruta = _crear(vault)
    contenido = ruta.read_text(encoding="utf-8")

    assert note.VER_ADEMAS in contenido
    codigo, salida, err = correr_cli(["note", "lint", str(ruta)])
    assert codigo == EXITO, err
    assert "sin hallazgos" in salida


def test_002_09_el_lint_reporta_un_enlace_sin_motivo() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        sin_motivo = Path(tmp) / "sin-motivo.md"
        sin_motivo.write_text(
            f"# Nota\n\ncuerpo\n\n{note.VER_ADEMAS}\n\n* [[depto-centro]]\n",
            encoding="utf-8",
        )
        codigo, salida, _ = correr_cli(["note", "lint", str(sin_motivo)])
        assert codigo == RECHAZO
        assert "para qué conecta" in salida

        sin_seccion = Path(tmp) / "sin-seccion.md"
        sin_seccion.write_text("# Nota\n\ncuerpo\n", encoding="utf-8")
        codigo, salida, _ = correr_cli(["note", "lint", str(sin_seccion)])
        assert codigo == RECHAZO
        assert "falta la sección" in salida


def test_002_09_crear_dos_veces_no_duplica() -> None:
    vault = preparar_paso(SLUG, previo=PREVIO, desde=DESDE)
    _crear(vault)
    despues = instantanea(vault)

    _crear(vault)

    assert delta(despues, instantanea(vault)) == {}, "el segundo pase escribió"
    ahora = (vault / "AHORA.md").read_text(encoding="utf-8")
    assert ahora.count(f"[[{Path(ARCHIVO).stem}]]") == 1, "hay dos registros de constancia"


if __name__ == "__main__":
    test_002_09_la_nota_queda_escrita_enlazada_y_con_constancia()
    test_002_09_ver_ademas_existe_y_cada_enlace_lleva_motivo()
    test_002_09_el_lint_reporta_un_enlace_sin_motivo()
    test_002_09_crear_dos_veces_no_duplica()
    print(f"ok: 4 afirmaciones (queda en playground/{SLUG}/)")
