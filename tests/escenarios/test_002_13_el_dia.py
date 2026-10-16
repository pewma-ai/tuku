"""Tests del escenario 002-13-el-dia.

El día uno con un comando por hecho: cada escenario parte del vault del anterior
y afirma su delta; repetir el día no cambia nada y el doctor lo da por sano.

Ejecutable directo: `python3 tests/escenarios/test_002_13_el_dia.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import gherkin  # noqa: E402
from vault import placeholders_sin_sustituir  # noqa: E402

from tuku import scope, todo  # noqa: E402
from tuku.cli import EXITO  # noqa: E402

SLUG = "002-13-el-dia"

#: Los escenarios en el orden de la cadena: cada uno copia el vault del anterior.
CADENA = (
    "la semana abre con el vault",
    "los registros caen en su día y en orden",
    "abrir los pendientes de hoy",
    "cerrarlos el mismo día deja solo el cierre",
    "un frente nuevo se crea y enlaza hacia atrás",
    "la nota del frente queda escrita y enlazada",
    "los pendientes de mañana y pasado llegan a su día",
    "repetir el día no cambia nada",
)

PERSONAL = "[personal](ambitos/personal/personal.md)"
AMBITO = "depto-centro"
DEPTO = f"[{AMBITO}](ambitos/{AMBITO}/{AMBITO}.md)"
MARTES = "## Martes 11 de agosto"
DIAS = (
    "## Lunes 10 de agosto",
    MARTES,
    "## Miércoles 12 de agosto",
    "## Jueves 13 de agosto",
    "## Viernes 14 de agosto",
    "## Sábado 15 de agosto",
    "## Domingo 16 de agosto",
)
GGCC = "avisar de los GGCC a la administradora"
MALETA = "comprar una maleta"
MENCION = "del depto centro"
ENLAZADO = f"del {DEPTO}"
CONSTANCIA_AMBITO = f"- 18:45 - {DEPTO} **nota**: abrí el ámbito"
NOTA = "como-funciona-el-cobro-de-gastos-comunes-en-una-copropiedad"
FIXTURE = Path(__file__).parent / "fixtures" / SLUG / "cuerpo-nota.md"

#: Los cuatro pendientes fechados, en el orden en que se abren.
FECHADOS = (
    ("2026-08-13", PERSONAL, "comprar pasajes de tren"),
    ("2026-08-12", PERSONAL, "pagar la sesión con el psicólogo"),
    ("2026-08-13", PERSONAL, "llamar a la administradora"),
    ("2026-08-12", DEPTO, "pagar los gastos comunes"),
)


def _paso(titulo: str) -> gherkin.Corrida:
    """El escenario `titulo`, después de correr los que lo preceden en la cadena."""
    for previo in CADENA[: CADENA.index(titulo)]:
        gherkin.correr(SLUG, previo)
    return gherkin.correr(SLUG, titulo)


def _leer(corrida: gherkin.Corrida, *partes: str) -> str:
    return corrida.ruta("mi-vault", *partes).read_text(encoding="utf-8")


def _region(ahora: str, encabezado: str) -> list[str]:
    return ahora.split(encabezado, 1)[1].split("\n## ", 1)[0].splitlines()


def _registros(ahora: str, encabezado: str) -> list[str]:
    return [linea for linea in _region(ahora, encabezado) if linea.startswith("- ")]


def test_002_13_la_semana_abre_con_el_vault() -> None:
    corrida = _paso(CADENA[0])
    assert corrida.codigo == EXITO, corrida.stderr
    assert "ya cubre" in corrida.stdout, corrida.stdout
    assert corrida.delta_de("mi-vault") == {}

    ahora = _leer(corrida, "AHORA.md")
    assert "from: 2026-08-10" in ahora and "to: 2026-08-16" in ahora
    for dia in DIAS:
        assert dia in ahora, f"falta {dia}"
    assert not placeholders_sin_sustituir(corrida.ruta("mi-vault"))


def test_002_13_los_registros_caen_en_su_dia_y_en_orden() -> None:
    corrida = _paso(CADENA[1])
    ahora = _leer(corrida, "AHORA.md")

    martes = _registros(ahora, MARTES)
    assert [linea[2:7] for linea in martes] == ["09:12", "11:30", "12:05", "18:40"], martes
    for dia in DIAS:
        if dia != MARTES:
            assert _registros(ahora, dia) == [], f"se escribió en {dia}"
    assert corrida.delta_de("mi-vault") == {
        "AHORA.md": "modificado",
        "ambitos/personal/personal.md": "modificado",
    }

    pagina = _leer(corrida, "ambitos", "personal", "personal.md")
    assert "## Esta semana" in pagina
    assert "- **señal**: la administradora responde los mensajes con varios días de atraso" in (
        pagina
    )
    assert PERSONAL not in pagina and "- 09:12 - " not in pagina

    lint = corrida.de("entry lint")
    assert lint.codigo == EXITO, lint.stdout
    assert "cachureo" in lint.stdout, lint.stdout


def test_002_13_abrir_los_pendientes_de_hoy() -> None:
    corrida = _paso(CADENA[2])
    assert corrida.codigo == EXITO, corrida.stderr

    pendientes = _leer(corrida, "PENDIENTES.md")
    assert f"| esta semana |  | {PERSONAL} | {GGCC} |" in pendientes, pendientes
    assert todo.cuerpos(pendientes, "esta semana") == [MALETA, GGCC]
    martes = _registros(_leer(corrida, "AHORA.md"), MARTES)
    assert f"- 13:00 - {PERSONAL} **pendiente**: {MALETA}" in martes
    assert f"- 14:20 - {PERSONAL} **pendiente**: {GGCC}" in martes
    assert f"- **pendiente**: {GGCC}" in _leer(corrida, "ambitos", "personal", "personal.md")
    assert corrida.delta_de("mi-vault") == {
        "AHORA.md": "modificado",
        "PENDIENTES.md": "modificado",
        "ambitos/PENDIENTES-AMBITOS.md": "modificado",
        "ambitos/personal/personal.md": "modificado",
    }


def test_002_13_cerrarlos_el_mismo_dia_deja_solo_el_cierre() -> None:
    corrida = _paso(CADENA[3])
    assert corrida.de("19:05").codigo == EXITO
    assert corrida.de("19:10").codigo == EXITO

    pendientes = _leer(corrida, "PENDIENTES.md")
    assert todo.filas(pendientes) == [] and todo.CABECERA in pendientes
    ahora = _leer(corrida, "AHORA.md")
    pagina = _leer(corrida, "ambitos", "personal", "personal.md")
    assert f"- 19:05 - {PERSONAL} (Hecho): ~~{GGCC}~~" in ahora
    assert f"- 19:10 - {PERSONAL} (Hecho): ~~{MALETA}~~" in ahora
    for texto in (ahora, pagina):
        assert "**pendiente**" not in texto, "quedó una apertura cerrada el mismo día"
        assert f"(Hecho): ~~{MALETA}~~" in texto


def test_002_13_un_frente_nuevo_se_crea_y_enlaza_hacia_atras() -> None:
    corrida = _paso(CADENA[4])
    assert corrida.codigo == EXITO, corrida.stderr
    vault = corrida.ruta("mi-vault")
    directorio = vault / "ambitos" / AMBITO

    for archivo in (*scope.OBLIGATORIOS, f"{AMBITO}.md"):
        assert (directorio / archivo).is_file(), f"falta {archivo}"
    assert not (directorio / "CAPACIDAD.md").exists(), "CAPACIDAD.md es opcional"
    cadencias = (directorio / "CADENCIAS.md").read_text(encoding="utf-8")
    sembrado = _leer(corrida, "ambitos", "personal", "CADENCIAS.md")
    assert cadencias == sembrado.replace("personal", AMBITO)

    pagina = (directorio / f"{AMBITO}.md").read_text(encoding="utf-8")
    assert f"![[../PENDIENTES-AMBITOS.md#^{AMBITO}]]" in pagina
    assert (
        "- [personal](../personal/personal.md) le mandé la boleta de gastos comunes del "
        "depto-centro a la administradora por WhatsApp" in pagina
    )
    ambitos = _leer(corrida, "ambitos", "PENDIENTES-AMBITOS.md")
    assert f"> [!todo] Pendientes en **Depto Centro** ^{AMBITO}\n> SIN PENDIENTES" in ambitos
    assert not scope.lint_transclusiones(vault) and not scope.lint_callouts(vault)

    ahora = _leer(corrida, "AHORA.md")
    assert CONSTANCIA_AMBITO in _registros(ahora, MARTES)
    antes = corrida.antes["mi-vault/AHORA.md"].decode("utf-8").splitlines()
    despues = ahora.splitlines()
    despues.remove(CONSTANCIA_AMBITO)
    cambiadas = [(a, d) for a, d in zip(antes, despues, strict=True) if a != d]
    assert [d for _, d in cambiadas] == [a.replace(MENCION, ENLAZADO) for a, _ in cambiadas]
    assert len(cambiadas) == 1, cambiadas

    tocados = set(corrida.delta_de("mi-vault"))
    assert tocados == {
        "AHORA.md",
        "ambitos/PENDIENTES-AMBITOS.md",
        f"ambitos/{AMBITO}/{AMBITO}.md",
        *(f"ambitos/{AMBITO}/{a}" for a in scope.OBLIGATORIOS),
    }, tocados


def test_002_13_la_nota_del_frente_queda_escrita_y_enlazada() -> None:
    corrida = _paso(CADENA[5])
    assert corrida.de("note create").codigo == EXITO, corrida.stderr

    nota = _leer(corrida, "notas", f"{NOTA}.md")
    assert "type: Note" in nota and "created: 2026-08-11" in nota
    assert FIXTURE.read_text(encoding="utf-8").strip() in nota
    assert f"[{AMBITO}](../ambitos/{AMBITO}/{AMBITO}.md)" in nota

    enlace = f"[{NOTA}](notas/{NOTA}.md)"
    assert f"- 21:15 - {DEPTO} **nota**: escribí la nota {enlace}" in _leer(corrida, "AHORA.md")
    pagina = _leer(corrida, "ambitos", AMBITO, f"{AMBITO}.md")
    assert f"- **nota**: escribí la nota [{NOTA}](../../notas/{NOTA}.md)" in pagina
    assert corrida.delta_de("mi-vault") == {
        "AHORA.md": "modificado",
        f"ambitos/{AMBITO}/{AMBITO}.md": "modificado",
        f"notas/{NOTA}.md": "nuevo",
    }
    assert "sin hallazgos" in corrida.de("note lint").stdout


def test_002_13_los_pendientes_de_manana_y_pasado_llegan_a_su_dia() -> None:
    corrida = _paso(CADENA[6])
    pendientes = _leer(corrida, "PENDIENTES.md")
    for dia, ambito, cuerpo in FECHADOS:
        assert f"| con fecha | {dia} | {ambito} | {cuerpo} |" in pendientes, cuerpo
    assert todo.cuerpos(pendientes, "esta semana") == []
    assert "^" not in pendientes and "> [!todo]" not in pendientes

    ahora = _leer(corrida, "AHORA.md")
    for encabezado, dia in (
        ("## Miércoles 12 de agosto", "2026-08-12"),
        ("## Jueves 13 de agosto", "2026-08-13"),
    ):
        region = _region(ahora, encabezado)
        assert region[1] == "> [!todo] Pendientes del día", region
        callout = [x for x in region if x.startswith("> - ")]
        assert sorted(callout) == sorted(f"> - {a} - {c}" for d, a, c in FECHADOS if d == dia)

    ambitos = _leer(corrida, "ambitos", "PENDIENTES-AMBITOS.md")
    personal = ambitos.split("^personal\n", 1)[1].split("\n\n", 1)[0].splitlines()
    assert personal == [
        "> - Ago/12 - pagar la sesión con el psicólogo",
        "> - Ago/13 - comprar pasajes de tren",
        "> - Ago/13 - llamar a la administradora",
    ]
    depto = ambitos.split(f"^{AMBITO}\n", 1)[1].split("\n\n", 1)[0].splitlines()
    assert depto == ["> - Ago/12 - pagar los gastos comunes"]

    assert corrida.de("todo lint").codigo == EXITO


def test_002_13_repetir_el_dia_no_cambia_nada() -> None:
    corrida = _paso(CADENA[7])
    assert corrida.delta_de("mi-vault") == {}, "repetir el día escribió"
    assert "no había ningún pendiente abierto" in corrida.de("19:05").stdout
    assert "al día" in corrida.de("regenerate").stdout
    assert "el vault está sano" in corrida.de("doctor").stdout


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__, "-v"]))
