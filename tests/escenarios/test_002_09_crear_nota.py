"""Tests del escenario 002-09-crear-nota.

Escenario: 002-09-crear-nota.md

Punto 5 del epic en su versión mínima: crear una nota a petición del autor,
enlazarla a su ámbito y dejar constancia en la bitácora. Crear la nota es un
hecho de la vida del autor, que la pidió, así que se registra; mover un
pendiente de escalón es del sistema y no se registra.

Los comandos salen del `.md`, incluidas la copia del estado que dejó `002-08` y
la del fixture con el cuerpo, que es salida de agente y por eso va congelado.

Ejecutable directo: `python3 tests/escenarios/test_002_09_crear_nota.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import gherkin  # noqa: E402

from tuku import note  # noqa: E402
from tuku.cli import EXITO, RECHAZO  # noqa: E402

SLUG = "002-09-crear-nota"
AMBITO = "depto-centro"
ARCHIVO = "como-funciona-el-cobro-de-gastos-comunes-en-una-copropiedad.md"
NOMBRE = Path(ARCHIVO).stem
HOY = "2026-08-11"

FIXTURE = Path(__file__).parent / "fixtures" / SLUG / "cuerpo-nota.md"


def test_002_09_la_nota_queda_escrita_enlazada_y_con_constancia() -> None:
    corrida = gherkin.correr(SLUG, "la nota se escribe donde corresponde")
    assert corrida.codigo == EXITO, corrida.stderr
    vault = corrida.ruta("mi-vault")

    ruta = vault / "notas" / ARCHIVO
    assert ruta.is_file(), f"la nota no quedó en notas/: {list((vault / 'notas').iterdir())}"
    contenido = ruta.read_text(encoding="utf-8")
    assert "type: Note" in contenido, "falta el `type` que exige `reglas/types.md`"
    assert f"created: {HOY}" in contenido, "falta created con la fecha de hoy"
    assert FIXTURE.read_text(encoding="utf-8").strip() in contenido, "no llegó el cuerpo"

    assert f"[[{AMBITO}]]" in contenido, "la nota no enlaza a su ámbito"
    assert (vault / "ambitos" / AMBITO / f"{AMBITO}.md").is_file(), "el enlace no resuelve"

    ahora = (vault / "AHORA.md").read_text(encoding="utf-8")
    assert f"[[{NOMBRE}]]" in ahora, "la constancia no enlaza a la nota"

    assert corrida.delta_de("mi-vault") == {
        "AHORA.md": "modificado",
        f"ambitos/{AMBITO}/{AMBITO}.md": "modificado",
        f"notas/{ARCHIVO}": "nuevo",
    }

    pagina = (vault / "ambitos" / AMBITO / f"{AMBITO}.md").read_text(encoding="utf-8")
    assert "## Esta semana" in pagina
    assert (
        "- le mandé la boleta de gastos comunes del depto-centro a la "
        "administradora por WhatsApp" in pagina
    )
    assert f"- **nota**: escribí la nota [[{NOMBRE}]]" in pagina


def test_002_09_ver_ademas_existe_y_cada_enlace_lleva_motivo() -> None:
    corrida = gherkin.correr(SLUG, '"Ver además" existe y cada enlace lleva motivo')

    contenido = corrida.ruta("mi-vault", "notas", ARCHIVO).read_text(encoding="utf-8")
    assert note.VER_ADEMAS in contenido

    lint = corrida.de("note lint")
    assert lint.codigo == EXITO, lint.stderr
    assert "sin hallazgos" in lint.stdout


def test_002_09_la_nota_recien_creada_deja_el_vault_sano() -> None:
    """El doctor sobre lo que TUKU acaba de escribir.

    Una nota sin `type` hacía que el doctor reportara un archivo que el propio
    comando había escrito, y ninguna afirmación del escenario lo notaba. Va
    sobre un vault recién sembrado porque el de la cadena arrastra, a propósito
    desde el `002-03`, un registro que el doctor reporta con razón.
    """
    corrida = gherkin.correr(SLUG, "la nota recién creada deja el vault sano")

    doctor = corrida.de("tuku doctor")
    assert doctor.codigo == EXITO, doctor.stdout
    assert "el vault está sano" in doctor.stdout, doctor.stdout


def test_002_09_el_lint_reporta_un_enlace_sin_motivo() -> None:
    corrida = gherkin.correr(SLUG, "el lint reporta un enlace sin motivo")

    sin_motivo = corrida.de("note lint sin-motivo.md")
    assert sin_motivo.codigo == RECHAZO, sin_motivo.stdout
    assert "para qué conecta" in sin_motivo.stdout, sin_motivo.stdout

    sin_seccion = corrida.de("note lint sin-seccion.md")
    assert sin_seccion.codigo == RECHAZO, sin_seccion.stdout
    assert "falta la sección" in sin_seccion.stdout, sin_seccion.stdout


def test_002_09_crear_dos_veces_no_duplica() -> None:
    corrida = gherkin.correr(SLUG, "crear la nota dos veces no duplica nada")
    assert corrida.codigo == EXITO, corrida.stderr

    assert corrida.delta_de("mi-vault") == {}, "el segundo pase escribió"
    ahora = corrida.ruta("mi-vault", "AHORA.md").read_text(encoding="utf-8")
    assert ahora.count(f"[[{NOMBRE}]]") == 1, "hay dos registros de constancia"


if __name__ == "__main__":
    test_002_09_la_nota_queda_escrita_enlazada_y_con_constancia()
    test_002_09_ver_ademas_existe_y_cada_enlace_lleva_motivo()
    test_002_09_la_nota_recien_creada_deja_el_vault_sano()
    test_002_09_el_lint_reporta_un_enlace_sin_motivo()
    test_002_09_crear_dos_veces_no_duplica()
    print(f"ok: 5 afirmaciones (queda en playground/{SLUG}/)")
