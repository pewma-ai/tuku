"""Tests del escenario 002-13-el-dia.

El día uno con un comando por hecho y las dos semanas siguientes, con el reloj
inyectado: cada escenario parte del vault del anterior y afirma su delta. Los
días de `AHORA.md` van del más nuevo al más viejo, la semana que sale de la
ventana se archiva sola y repetir todo no cambia nada.

Ejecutable directo: `python3 tests/escenarios/test_002_13_el_dia.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import gherkin  # noqa: E402

from tuku.cli import EXITO  # noqa: E402

SLUG = "002-13-el-dia"

#: Los escenarios en el orden de la cadena: cada uno copia el vault del anterior.
CADENA = (
    "los registros del martes caen en su día",
    "los pendientes nacen con su Creado",
    "cerrar un pendiente el mismo día",
    "un ámbito con su jerarquía",
    "una nota enlazada a su ámbito",
    "el foco es del autor",
    "el lunes 17 todavía no archiva",
    "el lunes 24 archiva",
    "un registro de fecha antigua",
    "repetir el día no cambia nada",
)

PERSONAL = "[personal](ambitos/personal/personal.md)"
MARTES = "## Martes 11 de agosto"
GGCC = "avisar de los GGCC a la administradora"
NOTA = "como-funciona-el-cobro-de-gastos-comunes-en-una-copropiedad"
FIXTURE = Path(__file__).parent / "fixtures" / SLUG / "cuerpo-nota.md"
BITACORA = "bitacoras/bitacora-20260810-20260816.md"
VENTANA = "> [!todo] Pendientes de los próximos 7 días"
FOCO_AUTOR = "> Cerrar la semana sin deuda con la administración."


def _paso(titulo: str) -> gherkin.Corrida:
    """El escenario `titulo`, después de correr los que lo preceden en la cadena."""
    for previo in CADENA[: CADENA.index(titulo)]:
        gherkin.correr(SLUG, previo)
    return gherkin.correr(SLUG, titulo)


def _leer(corrida: gherkin.Corrida, *partes: str) -> str:
    return corrida.ruta("mi-vault", *partes).read_text(encoding="utf-8")


def _region(texto: str, encabezado: str) -> list[str]:
    """Las líneas bajo `encabezado`, hasta el siguiente `## `."""
    return texto.split(encabezado, 1)[1].split("\n## ", 1)[0].splitlines()


def _registros(texto: str, encabezado: str) -> list[str]:
    return [linea for linea in _region(texto, encabezado) if linea.startswith("- ")]


def _horas(texto: str, encabezado: str) -> list[str]:
    return [linea[2:7] for linea in _registros(texto, encabezado)]


def _dias(texto: str) -> list[str]:
    return [linea[3:] for linea in texto.splitlines() if linea.startswith("## ")]


def _ventana(ahora: str) -> list[str]:
    """Las líneas del bloque de pendientes de la ventana."""
    bloque = ahora.split(VENTANA, 1)[1].split("\n\n", 1)[0].splitlines()
    return [linea for linea in bloque if linea.startswith("> - ")]


def _filas(pendientes: str) -> list[list[str]]:
    filas = [ln for ln in pendientes.splitlines() if ln.startswith("| ")][2:]
    return [[celda.strip() for celda in ln.strip("|").split("|")] for ln in filas]


def test_002_13_los_registros_del_martes_caen_en_su_dia() -> None:
    corrida = _paso(CADENA[0])
    assert corrida.codigo == EXITO, corrida.stderr
    ahora = _leer(corrida, "AHORA.md")

    assert _dias(ahora) == ["Martes 11 de agosto"]
    assert ahora.index("> [!abstract] Foco") < ahora.index(MARTES)
    assert _horas(ahora, MARTES) == ["18:40", "12:05", "11:30", "10:00", "09:12"]
    assert corrida.delta_de("mi-vault") == {
        "AHORA.md": "modificado",
        "ambitos/personal/personal.md": "modificado",
    }
    lint = corrida.de("doctor entry")
    assert lint.codigo == EXITO and "cachureo" in lint.stdout, lint.stdout


def test_002_13_los_pendientes_nacen_con_su_creado() -> None:
    corrida = _paso(CADENA[1])
    assert corrida.codigo == EXITO, corrida.stderr

    filas = _filas(_leer(corrida, "PENDIENTES.md"))
    assert [(f[0], f[1], f[4]) for f in filas] == [
        ("esta semana", "", "comprar una maleta"),
        ("esta semana", "", GGCC),
        ("próxima semana", "", "renovar el seguro del local"),
        ("con fecha", "2026-08-13", "llamar al contador"),
        ("con fecha", "2026-08-31", "pagar la patente"),
    ]
    assert {f[2] for f in filas} == {"2026-08-11"}

    ahora = _leer(corrida, "AHORA.md")
    assert _ventana(ahora) == [
        f"> - {PERSONAL} - comprar una maleta",
        f"> - {PERSONAL} - {GGCC}",
        f"> - Ago/13 - {PERSONAL} - llamar al contador",
    ]
    jueves = _region(ahora, "## Jueves 13 de agosto")
    assert jueves[1] == "> [!todo] Pendientes del día", jueves
    assert _dias(ahora) == ["Jueves 13 de agosto", "Martes 11 de agosto"]

    ambitos = _leer(corrida, "ambitos", "PENDIENTES-AMBITOS.md")
    personal = ambitos.split("^personal\n", 1)[1].split("\n\n", 1)[0].splitlines()
    assert len(personal) == 5, personal


def test_002_13_cerrar_un_pendiente_el_mismo_dia_deja_solo_el_cierre() -> None:
    corrida = _paso(CADENA[2])
    assert corrida.de("doctor todo").codigo == EXITO, corrida.de("doctor todo").stdout

    assert GGCC not in _leer(corrida, "PENDIENTES.md")
    ahora = _leer(corrida, "AHORA.md")
    assert not any(GGCC in linea for linea in _ventana(ahora))
    martes = _registros(ahora, MARTES)
    assert f"- 19:05 - {PERSONAL} (Hecho): ~~{GGCC}~~" in martes
    assert "13:20" not in _horas(ahora, MARTES), "quedó la apertura cerrada el mismo día"


def test_002_13_un_ambito_con_su_jerarquia() -> None:
    corrida = _paso(CADENA[3])
    assert corrida.de("doctor scope").codigo == EXITO, corrida.de("doctor scope").stdout
    depto = "ambitos/depto-centro/depto-centro.md"
    gastos = "ambitos/depto-centro/gastos/gastos.md"

    assert "![[../PENDIENTES-AMBITOS.md#^depto-centro]]" in _leer(corrida, depto)
    assert "![[../../PENDIENTES-AMBITOS.md#^gastos]]" in _leer(corrida, gastos)
    assert "parent: depto-centro" in _leer(corrida, gastos)

    ahora = _leer(corrida, "AHORA.md")
    martes = _registros(ahora, MARTES)
    assert f"- 19:30 - [depto-centro]({depto}) **nota**: abrí el ámbito" in martes
    assert (
        f"- 19:35 - [gastos]({gastos}) **nota**: abrí el ámbito bajo [depto-centro]({depto})"
        in martes
    )
    boleta = next(x for x in martes if "18:40" in x)
    assert "depto centro" in boleta and "](ambitos/depto-centro" not in boleta
    assert "personal" in boleta, "crear el ámbito no mueve el registro"

    antes = corrida.antes["mi-vault/AHORA.md"].decode("utf-8").splitlines()
    despues = [x for x in ahora.splitlines() if "abrí el ámbito" not in x]
    assert despues == antes, "crear el ámbito no modifica ninguna línea ya escrita"


def test_002_13_una_nota_enlazada_a_su_ambito() -> None:
    corrida = _paso(CADENA[4])
    assert corrida.de("doctor note").codigo == EXITO, corrida.de("doctor note").stdout

    nota = _leer(corrida, "notas", f"{NOTA}.md")
    assert "type: Note" in nota and "created: 2026-08-11" in nota
    assert FIXTURE.read_text(encoding="utf-8").strip() in nota
    assert "[depto-centro](../ambitos/depto-centro/depto-centro.md)" in nota

    enlace = f"[{NOTA}](notas/{NOTA}.md)"
    depto = "[depto-centro](ambitos/depto-centro/depto-centro.md)"
    constancia = f"- 21:15 - {depto} **nota**: escribí la nota {enlace}"
    assert _registros(_leer(corrida, "AHORA.md"), MARTES)[0] == constancia
    pagina = _leer(corrida, "ambitos", "depto-centro", "depto-centro.md")
    assert f"- **nota**: escribí la nota [{NOTA}](../../notas/{NOTA}.md)" in pagina
    assert corrida.delta_de("mi-vault") == {
        "AHORA.md": "modificado",
        "ambitos/depto-centro/depto-centro.md": "modificado",
        f"notas/{NOTA}.md": "nuevo",
    }


def test_002_13_el_foco_es_del_autor_y_tuku_lo_conserva() -> None:
    corrida = _paso(CADENA[5])
    assert corrida.codigo == EXITO, corrida.stderr
    ahora = _leer(corrida, "AHORA.md")

    assert ahora.index("> [!abstract] Foco") < ahora.index(FOCO_AUTOR) < ahora.index(VENTANA)
    assert _horas(ahora, MARTES)[0] == "21:40"
    assert "Escribe aquí en qué concentrarte" not in ahora


def test_002_13_el_lunes_17_todavia_no_archiva() -> None:
    corrida = _paso(CADENA[6])
    assert corrida.de("tuku doctor").codigo == EXITO
    assert "el vault está sano" in corrida.de("tuku doctor").stdout
    ahora = _leer(corrida, "AHORA.md")

    assert _dias(ahora) == ["Lunes 17 de agosto", "Jueves 13 de agosto", MARTES[3:]]
    assert not corrida.ruta("mi-vault", "bitacoras").exists()
    ventana = _ventana(ahora)
    assert f"> - {PERSONAL} - comprar una maleta" in ventana
    assert f"> - Ago/13 - {PERSONAL} - llamar al contador (atrasado)" in ventana


def test_002_13_el_lunes_24_archiva_la_semana_que_salio_de_la_ventana() -> None:
    corrida = _paso(CADENA[7])
    assert "el vault está sano" in corrida.de("tuku doctor").stdout
    ahora = _leer(corrida, "AHORA.md")

    bitacora = _leer(corrida, BITACORA)
    assert "type: Logbook" in bitacora
    assert "from: 2026-08-10\nto: 2026-08-16\n" in bitacora
    # Los registros del martes viajan en su orden, con la ruta vista desde `bitacoras/`.
    previo = corrida.antes["mi-vault/AHORA.md"].decode("utf-8")
    esperado = [
        x.replace("](ambitos/", "](../ambitos/").replace("](notas/", "](../notas/")
        for x in _registros(previo, MARTES)
    ]
    assert _registros(bitacora, MARTES) == esperado

    assert FOCO_AUTOR in ahora
    assert _dias(ahora) == [
        "Lunes 31 de agosto",
        "Lunes 24 de agosto",
        "Lunes 17 de agosto",
    ]
    assert "Jueves 13" not in ahora and MARTES not in ahora
    ventana = _ventana(ahora)
    assert f"> - {PERSONAL} - comprar una maleta (atrasado)" in ventana
    assert f"> - Ago/13 - {PERSONAL} - llamar al contador (atrasado)" in ventana

    cambios = corrida.delta_de("mi-vault")
    assert cambios[BITACORA] == "nuevo" and cambios["AHORA.md"] == "modificado"
    assert "PENDIENTES.md" not in cambios, "archivar no toca los pendientes"


def test_002_13_un_registro_de_fecha_antigua_va_a_su_bitacora() -> None:
    corrida = _paso(CADENA[8])
    assert corrida.codigo == EXITO, corrida.stderr

    bitacora = _leer(corrida, BITACORA)
    personal = PERSONAL.replace("](", "](../")
    assert _registros(bitacora, "## Miércoles 12 de agosto") == [
        f"- 10:00 - {personal} **señal**: el contador confirmó el plazo del miércoles"
    ]
    assert bitacora.index("Miércoles 12") < bitacora.index("Martes 11")

    nueva = _leer(corrida, "bitacoras", "bitacora-20260727-20260802.md")
    assert "from: 2026-07-27\nto: 2026-08-02\n" in nueva
    assert _horas(nueva, "## Miércoles 29 de julio") == ["16:30"]

    cambios = corrida.delta_de("mi-vault")
    assert cambios[BITACORA] == "modificado"
    assert cambios["bitacoras/bitacora-20260727-20260802.md"] == "nuevo"
    assert "AHORA.md" not in cambios


def test_002_13_repetir_el_dia_no_cambia_nada() -> None:
    corrida = _paso(CADENA[9])
    assert corrida.delta_de("mi-vault") == {}, "repetir el día escribió"
    assert "al día" in corrida.de("tuku regenerate").stdout
    assert "el vault está sano" in corrida.de("tuku doctor").stdout


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__, "-v"]))
