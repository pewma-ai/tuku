"""Tests del escenario 003-10-el-dia-uno-en-un-turno.

Escenario: 003-10-el-dia-uno-en-un-turno.md

El criterio de salida del epic en un turno: el día uno dictado entero, con una
consulta, una instrucción, una pregunta, un cierre ambiguo y un pedido sin
comando que no se anotan.

Ejecutable directo: `python3 tests/escenarios/test_003_10_el_dia_uno_en_un_turno.py`
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests" / "scripts"))

import agente  # noqa: E402
import gherkin  # noqa: E402
import vault  # noqa: E402

from tuku import scope, todo  # noqa: E402
from tuku.cli import EXITO  # noqa: E402

SLUG = "003-10-el-dia-uno-en-un-turno"
TITULO = "el día uno entero"
MARTES = "## Martes 11 de agosto"
MIERCOLES = "## Miércoles 12 de agosto"

#: La tabla de verdad del `.md`: hora, ámbito y marca cerrada, sin los dos de
#: mañana, cuya hora no se dicta. Las aperturas de las 13:00 y las 14:20 no
#: quedan: se cerraron el mismo día.
TABLA: dict[str, dict[str, tuple[str, str | None]]] = {
    MARTES: {
        "09:12": ("personal", None),
        "11:30": ("personal", None),
        "12:05": ("personal", None),
        "18:40": ("personal", None),
        "19:05": ("personal", todo.CIERRA),
        "19:10": ("personal", todo.CIERRA),
        "21:15": ("depto-centro", None),
    },
}

#: Doce comandos: cuatro registros, cuatro aperturas y dos cierres, el ámbito y
#: la nota. La consulta, la pregunta y los dos pedidos al final no producen
#: ninguno.
TRADUCCION = {
    "entry add": 4,
    "todo open": 4,
    "todo close": 2,
    "scope create": 1,
    "note create": 1,
}

#: Los dos pendientes de mañana, su ámbito y cuándo vencen. Empiezan igual a
#: propósito: "ya pagué" calza con los dos, y por eso no se puede cerrar ninguno.
DE_MANANA = {
    "pagar la sesión con el psicólogo": ("personal", "2026-08-12 09:00"),
    "pagar los gastos comunes del depto centro": ("depto-centro", "2026-08-12 09:30"),
}

#: Lo que el día escribe, y nada más. La nota se cuenta aparte porque su nombre
#: lo elige el agente.
TOCADOS = {
    "AHORA.md",
    "PENDIENTES.md",
    "ambitos/PENDIENTES-AMBITOS.md",
    "ambitos/personal/personal.md",
    "ambitos/depto-centro/depto-centro.md",
}

sin_arnes = pytest.mark.skipif(
    not agente.disponible(), reason=agente.motivo_no_disponible() or ""
)

_AMBITO = re.compile(r"^- \d\d:\d\d - \[([^\]]+)\]\([^)]+\)")


def _corrida() -> gherkin.Corrida:
    return gherkin.correr(SLUG, TITULO)


def _ahora(corrida: gherkin.Corrida) -> str:
    return corrida.ruta("mi-vault", "AHORA.md").read_text(encoding="utf-8")


def _pendientes(corrida: gherkin.Corrida) -> str:
    return corrida.ruta("mi-vault", "PENDIENTES.md").read_text(encoding="utf-8")


def _dia(corrida: gherkin.Corrida, encabezado: str) -> str:
    ahora = _ahora(corrida)
    assert encabezado in ahora, f"no está el día {encabezado!r} en AHORA.md"
    return ahora.split(encabezado, 1)[1].split("\n## ", 1)[0]


def _ambito_de(linea: str) -> str | None:
    m = _AMBITO.match(linea)
    return vault.nombre_comparable(m.group(1)) if m else None


def _de_manana(linea: str) -> bool:
    return todo.ABRE in linea and any(linea.endswith(c) for c in DE_MANANA)


def _registros(dia: str) -> dict[str, str]:
    """Los registros dictados de un día, por hora; sin la constancia de `scope create`
    ni las aperturas de mañana."""
    por_hora: dict[str, str] = {}
    for linea in dia.splitlines():
        if not linea.startswith("- ") or " - " not in linea:
            continue
        if linea.endswith(scope.CONSTANCIA) or _de_manana(linea):
            continue
        hora = linea[2:].split(" - ", 1)[0]
        assert hora not in por_hora, f"dos registros a las {hora}:\n{dia}"
        por_hora[hora] = linea
    return por_hora


def _bloque_que_menciona(texto: str, frase: str) -> str:
    """El tramo de la respuesta, entre separadores `---`, que trae `frase`."""
    bloques = texto.split("\n---")
    return next((b for b in bloques if frase in b.lower()), "")


@pytest.mark.agentic
@sin_arnes
def test_003_10_la_traduccion_es_la_del_dia() -> None:
    """Lo que no es un hecho no se traduce en un comando."""
    turno = _corrida().turno
    hechos = turno.traduccion_sin_reintentos
    contados = {verbo: hechos.count(verbo) for verbo in TRADUCCION}
    assert contados == TRADUCCION, "la traza dice:\n" + "\n".join(turno.comandos)
    assert len(hechos) == sum(TRADUCCION.values()), (
        f"corrió comandos que escriben y no estaban en el dictado: {hechos}"
    )


@pytest.mark.agentic
@sin_arnes
def test_003_10_cada_registro_calza_con_la_tabla_de_verdad() -> None:
    """Hora, ámbito y marca cerrada de cada registro."""
    corrida = _corrida()
    for encabezado, esperado in TABLA.items():
        registros = _registros(_dia(corrida, encabezado))
        assert sorted(registros) == sorted(esperado), (
            f"las horas de {encabezado} no son las del dictado:\n"
            + "\n".join(registros.values())
        )
        for hora, (ambito, marca) in esperado.items():
            linea = registros[hora]
            assert _ambito_de(linea) == vault.nombre_comparable(ambito), (
                f"las {hora} van en {ambito}: {linea}"
            )
            puestas = [m for m in (todo.ABRE, todo.CIERRA) if m in linea]
            assert puestas == ([marca] if marca else []), (
                f"las {hora} llevan {marca or 'ninguna marca cerrada'}: {linea}"
            )


@pytest.mark.agentic
@sin_arnes
def test_003_10_los_de_manana_se_prometen_hoy_y_vencen_manana() -> None:
    corrida = _corrida()
    aperturas = [x for x in _dia(corrida, MARTES).splitlines() if _de_manana(x)]
    assert sorted(_ambito_de(x) or "" for x in aperturas) == sorted(
        vault.nombre_comparable(a) for a, _ in DE_MANANA.values()
    ), "\n".join(aperturas)
    fechados = {f.cuerpo: f.vence for f in todo.filas(_pendientes(corrida))}
    assert fechados == {c: vence for c, (_, vence) in DE_MANANA.items()}, fechados
    assert not _registros(_dia(corrida, MIERCOLES)), "escribió registros en el miércoles 12"


@pytest.mark.agentic
@sin_arnes
def test_003_10_la_consulta_no_escribe_y_nombra_los_dos_destinos() -> None:
    """Preguntar qué haría no es pedir que lo haga."""
    corrida = _corrida()
    for archivo in (_ahora(corrida), _pendientes(corrida)):
        assert "pase escolar" not in archivo.lower(), "anotó lo que solo se consultó"
    # En un turno que además escribe, el resumen final nombra `AHORA.md` de todos
    # modos: la respuesta a la consulta es el bloque que habla del pase escolar.
    bloque = _bloque_que_menciona(corrida.turno.stdout, "pase escolar")
    assert "AHORA.md" in bloque, f"no nombró dónde va el registro:\n{bloque}"
    assert "PENDIENTES.md" in bloque, f"no nombró dónde va la consecuencia:\n{bloque}"


@pytest.mark.agentic
@sin_arnes
def test_003_10_lo_dirigido_al_agente_no_entra_al_dia() -> None:
    """Se registra el hecho, no la conversación."""
    texto = _ahora(_corrida()).lower()
    for frase in ("recuérdame", "guárdame", "ábrelo", "cuántos pendientes", "apuntes"):
        assert frase not in texto, f"escribió {frase!r} como si fuera un hecho"


@pytest.mark.agentic
@sin_arnes
def test_003_10_el_ambito_deja_su_constancia_y_no_toca_lo_dictado() -> None:
    """El frente se nombra antes de existir y, al crearse, no reescribe el registro."""
    corrida = _corrida()
    martes = _dia(corrida, MARTES)
    linea = _registros(martes)["18:40"]
    assert "](ambitos/depto-centro/" not in linea.split(") ", 1)[1], (
        f"crear el frente enlazó el body del registro: {linea}"
    )
    constancias = [x for x in martes.splitlines() if x.endswith(scope.CONSTANCIA)]
    assert len(constancias) == 1, f"se esperaba una constancia de scope create:\n{martes}"


@pytest.mark.agentic
@sin_arnes
def test_003_10_los_cierres_encontraron_su_pareja_y_el_ambiguo_no_cerro_nada() -> None:
    """Quedan abiertos exactamente los dos de mañana."""
    corrida = _corrida()
    abiertos = set(todo.cuerpos(_pendientes(corrida)))
    assert abiertos == set(DE_MANANA), (
        f"la tabla debía quedar con los dos de mañana. Sobra {abiertos - set(DE_MANANA)}, "
        f"falta {set(DE_MANANA) - abiertos}"
    )
    cierres = [x for x in _ahora(corrida).splitlines() if todo.CIERRA in x]
    assert len(cierres) == 2, "cerró algo que nadie identificó:\n" + "\n".join(cierres)


@pytest.mark.agentic
@sin_arnes
def test_003_10_el_agente_pregunta() -> None:
    """Ante "ya pagué" con dos candidatos, consulta. Es la aserción más débil."""
    # Sin contar el eco de las dos preguntas del autor, que la respuesta repite.
    ecos = ("cuántos pendientes", "pase escolar", "anotarías")
    propias = [
        linea
        for linea in _corrida().turno.stdout.splitlines()
        if "?" in linea and not any(e in linea.lower() for e in ecos)
    ]
    assert propias, "no consultó nada ante un cierre ambiguo"


@pytest.mark.agentic
@sin_arnes
def test_003_10_no_cambio_nada_fuera_del_dia() -> None:
    """`notas/` no se renombró y nada fuera del día cambió."""
    corrida = _corrida()
    raiz = corrida.ruta("mi-vault")
    assert (raiz / "notas").is_dir() and not (raiz / "apuntes").exists(), (
        "renombró notas/ sin preguntar"
    )
    delta = corrida.delta_de("mi-vault")
    notas = {r for r in delta if r.startswith("notas/")}
    assert len(notas) == 1 and delta[next(iter(notas))] == "nuevo", f"notas: {notas}"
    resto = set(delta) - notas
    assert resto == TOCADOS, f"sobra {resto - TOCADOS}, falta {TOCADOS - resto}"


@pytest.mark.agentic
@sin_arnes
def test_003_10_el_doctor_aprueba_el_vault() -> None:
    """El vault que dejó el agente está sano."""
    doctor = _corrida().de("tuku doctor")
    assert doctor.codigo == EXITO, doctor.stdout


if __name__ == "__main__":
    if not agente.disponible():
        print(f"saltado: {agente.motivo_no_disponible()}")
        raise SystemExit(0)
    test_003_10_la_traduccion_es_la_del_dia()
    test_003_10_cada_registro_calza_con_la_tabla_de_verdad()
    test_003_10_los_de_manana_se_prometen_hoy_y_vencen_manana()
    test_003_10_la_consulta_no_escribe_y_nombra_los_dos_destinos()
    test_003_10_lo_dirigido_al_agente_no_entra_al_dia()
    test_003_10_el_ambito_deja_su_constancia_y_no_toca_lo_dictado()
    test_003_10_los_cierres_encontraron_su_pareja_y_el_ambiguo_no_cerro_nada()
    test_003_10_el_agente_pregunta()
    test_003_10_no_cambio_nada_fuera_del_dia()
    test_003_10_el_doctor_aprueba_el_vault()
    print(f"ok: 10 afirmaciones (queda en playground/{SLUG}/)")
