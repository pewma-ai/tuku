"""Tests del escenario 003-06-el-dia-completo.

Escenario: 003-06-el-dia-completo.md

El criterio de salida del epic: el día entero dictado de una vez tiene que dejar
el vault que la cadena del 002 dejó a mano, comando por comando.

Lo que solo se puede probar acá es lo que aparece cuando las frases conviven: un
frente que se menciona antes de existir y se enlaza hacia atrás cuando se crea, y
un cierre que seis horas después tiene que repetir el cuerpo de su apertura.

Gemela determinista: la cadena entera del epic 002.

Ejecutable directo: `python3 tests/escenarios/test_003_06_el_dia_completo.py`
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

from tuku import todo  # noqa: E402

SLUG = "003-06-el-dia-completo"
TITULO = "el día dictado entero"
MARTES = "## Martes 11 de agosto"
MIERCOLES = "## Miércoles 12 de agosto"

#: La tabla de verdad del `.md`: hora, ámbito y marca. Solo lo cerrado. El cuerpo
#: y la clasificación abierta los redacta el agente y se reportan, no fallan.
#:
#: Las 18:40 van en `personal` y no en `depto-centro`: cuando se escriben, ese
#: frente todavía no existe. El enlace llega después, y va en el cuerpo.
MARTES_11 = {
    "09:12": ("personal", None),
    "11:30": ("personal", None),
    "12:05": ("personal", None),
    "13:00": ("personal", todo.ABRE),
    "14:20": ("personal", todo.ABRE),
    "18:40": ("personal", None),
    "19:05": ("personal", todo.CIERRA),
    "19:10": ("personal", todo.CIERRA),
    "21:15": ("depto-centro", None),
}

#: Once comandos: ocho registros del martes, el ámbito, la nota (que escribe su
#: propia constancia a las 21:15) y el pendiente del miércoles.
TRADUCCION = {"entry add": 9, "scope create": 1, "note create": 1}

sin_arnes = pytest.mark.skipif(
    not agente.disponible(), reason=agente.motivo_no_disponible() or ""
)


def _dia(corrida: gherkin.Corrida, encabezado: str) -> str:
    ahora = corrida.ruta("mi-vault", "AHORA.md").read_text(encoding="utf-8")
    assert encabezado in ahora, f"no está el día {encabezado!r} en AHORA.md"
    return ahora.split(encabezado, 1)[1].split("\n## ", 1)[0]


#: El ámbito de un registro es el `[[...]]` que abre la línea. Una mención en el
#: cuerpo no lo es, y confundirlos deja pasar un registro archivado donde no va.
_AMBITO = re.compile(r"^- \d\d:\d\d - \[\[([^\]]+)\]\]")


def _ambito_de(linea: str) -> str | None:
    """El ámbito con que abre la línea, comparable.

    Se normaliza porque el autor dicta hablando ("el depto centro") y no dice
    con qué carácter se unen las palabras: `Depto Centro`, `depto_centro` y
    `depto-centro` son el mismo frente, y exigir una de las tres mediría cómo
    el agente eligió escribirlo. Nombrar **otro** frente sigue fallando.
    """
    m = _AMBITO.match(linea)
    return vault.nombre_comparable(m.group(1)) if m else None


def _registros(dia: str) -> dict[str, str]:
    """Los registros de un día, por hora. Falla si una hora se escribió dos veces."""
    por_hora: dict[str, str] = {}
    for linea in dia.splitlines():
        if not linea.startswith("- ") or " - " not in linea:
            continue
        hora = linea[2:].split(" - ", 1)[0]
        assert hora not in por_hora, f"dos registros a las {hora}:\n{dia}"
        por_hora[hora] = linea
    return por_hora


def _pendientes(corrida: gherkin.Corrida) -> str:
    return corrida.ruta("mi-vault", "PENDIENTES.md").read_text(encoding="utf-8")


@pytest.mark.agentic
@sin_arnes
def test_003_06_la_traduccion_es_la_del_dia_completo() -> None:
    """Once comandos y ninguno más, contados por verbo.

    El orden entre comandos independientes se reporta y no falla, así que se
    cuenta en vez de compararse en secuencia. El orden que sí importa (un cierre
    después de su apertura) lo afirma la tabla de pendientes, que queda vacía de
    lo cerrado solo si el agente los corrió en ese orden.
    """
    turno = gherkin.correr(SLUG, TITULO).turno
    # Sin los intentos: un comando rechazado y repetido con lo que le faltaba es
    # un hecho escrito al segundo intento, no dos hechos. Contarlos haría fallar
    # justo al agente que se corrige.
    hechos = turno.traduccion_sin_reintentos
    contados = {verbo: hechos.count(verbo) for verbo in TRADUCCION}
    assert contados == TRADUCCION, "la traza dice:\n" + "\n".join(turno.comandos)
    assert len(hechos) == sum(TRADUCCION.values()), (
        f"corrió comandos que escriben y no estaban en el dictado: {hechos}"
    )
    if turno.reintentos:
        print(f"reintentos (no fallan): {turno.reintentos}")


@pytest.mark.agentic
@sin_arnes
def test_003_06_cada_registro_del_martes_calza_con_la_tabla_de_verdad() -> None:
    """Hora, ámbito y marca. El cuerpo y la clasificación son del agente."""
    registros = _registros(_dia(gherkin.correr(SLUG, TITULO), MARTES))
    assert sorted(registros) == sorted(MARTES_11), (
        "las horas del martes no son las del dictado:\n" + "\n".join(registros.values())
    )
    for hora, (ambito_esperado, marca) in MARTES_11.items():
        ambito = vault.nombre_comparable(ambito_esperado)
        linea = registros[hora]
        assert _ambito_de(linea) == ambito, f"las {hora} van en [[{ambito}]]: {linea}"
        puestas = [m for m in (todo.ABRE, todo.CIERRA) if m in linea]
        assert puestas == ([marca] if marca else []), (
            f"las {hora} llevan {marca or 'ninguna marca cerrada'}: {linea}"
        )


@pytest.mark.agentic
@sin_arnes
def test_003_06_el_ambito_nuevo_enlaza_hacia_atras() -> None:
    """A las 18:40 el autor nombra un frente que todavía no existe.

    Lo abre tres frases después. El enlace de las 18:40 no lo escribe el agente:
    lo escribe `tuku scope create` al pasar por los registros del ciclo. Esto no
    se puede probar con una frase sola, y es la mitad de por qué este escenario
    dicta el día entero.
    """
    corrida = gherkin.correr(SLUG, TITULO)
    assert corrida.ruta("mi-vault", "ambitos", "depto-centro").is_dir(), (
        "el autor pidió abrir el frente y no quedó en ambitos/"
    )
    linea = _registros(_dia(corrida, MARTES))["18:40"]
    assert _ambito_de(linea) == "personal", (
        f"al escribirse, depto-centro no existía y ninguno calzaba: {linea}"
    )
    assert "[[depto-centro]]" in linea.split("]] ", 1)[1], (
        f"la mención al frente no quedó enlazada hacia atrás: {linea}"
    )


@pytest.mark.agentic
@sin_arnes
def test_003_06_los_dos_cierres_encontraron_su_pareja() -> None:
    """Cerrar es repetir el cuerpo del pendiente, no describir lo que se hizo.

    "Ya compré la maleta" tiene que salir como "comprar una maleta". Si el agente
    redacta el cierre en vez de repetirlo, el registro queda igual de bien escrito
    y la fila se queda abierta para siempre.
    """
    corrida = gherkin.correr(SLUG, TITULO)
    abiertos = todo.cuerpos(_pendientes(corrida))
    registros = _registros(_dia(corrida, MARTES))
    for hora in ("19:05", "19:10"):
        marca = todo.parsear(registros[hora])
        assert marca is not None, f"las {hora} no llevan una marca reconocible"
        assert marca.cuerpo not in abiertos, (
            f"el cierre de las {hora} no encontró su pareja: {marca.cuerpo!r} sigue "
            f"abierto. Abiertos: {abiertos}"
        )


@pytest.mark.agentic
@sin_arnes
def test_003_06_solo_queda_abierto_el_pendiente_de_manana() -> None:
    """La tabla final del 002, idéntica: las dos correcciones del `.md` se cancelan."""
    corrida = gherkin.correr(SLUG, TITULO)
    filas = todo.filas(_pendientes(corrida))
    assert len(filas) == 1, f"una fila abierta, y hay {len(filas)}:\n{_pendientes(corrida)}"
    assert filas[0].horizonte == todo.CON_FECHA, (
        f"lo que cae en otro día se fecha: {filas[0].linea()}"
    )
    assert filas[0].cuando == "2026-08-12", f"la fecha es la de mañana: {filas[0].linea()}"


@pytest.mark.agentic
@sin_arnes
def test_003_06_el_miercoles_abre_con_su_pendiente_propagado() -> None:
    dia = _dia(gherkin.correr(SLUG, TITULO), MIERCOLES)
    assert "[!todo]" in dia, f"el pendiente fechado no se propagó al inicio del día:\n{dia}"
    assert "09:00" in _registros(dia), f"falta el registro de las 09:00:\n{dia}"


@pytest.mark.agentic
@sin_arnes
def test_003_06_la_nota_existe_y_su_constancia_la_enlaza() -> None:
    corrida = gherkin.correr(SLUG, TITULO)
    notas = [x for x in corrida.ruta("mi-vault", "notas").glob("*.md") if x.name.islower()]
    assert len(notas) == 1, f"una nota, y hay {len(notas)}: {[x.name for x in notas]}"
    constancia = _registros(_dia(corrida, MARTES))["21:15"]
    assert f"[[{notas[0].stem}]]" in constancia, (
        f"la constancia no enlaza a la nota que se creó: {constancia}"
    )


@pytest.mark.agentic
@sin_arnes
def test_003_06_no_quedo_ninguna_marca_sin_su_consecuencia() -> None:
    """Lo mismo que `tuku doctor` revisa, sobre las cuatro marcas del día."""
    corrida = gherkin.correr(SLUG, TITULO)
    faltan = todo.sin_consecuencia(
        corrida.ruta("mi-vault", "AHORA.md").read_text(encoding="utf-8"),
        _pendientes(corrida),
    )
    assert faltan == [], f"marcas sin aplicar: {faltan}. Ejecutó: {corrida.turno.comandos}"


@pytest.mark.agentic
@sin_arnes
def test_003_06_la_instruccion_al_agente_no_entro_al_dia() -> None:
    """El dictado trae dos frases dirigidas a él: "ábrelo" y "guárdame una nota".

    Las dos producen un comando, y ninguna produce un registro que las narre. Lo
    que se registra es el hecho, no la conversación.
    """
    ahora = gherkin.correr(SLUG, TITULO).ruta("mi-vault", "AHORA.md")
    texto = ahora.read_text(encoding="utf-8").lower()
    for instruccion in ("guárdame", "ábrelo", "recuérdame"):
        assert instruccion not in texto, f"escribió {instruccion!r} como si fuera un hecho"


if __name__ == "__main__":
    if not agente.disponible():
        print(f"saltado: {agente.motivo_no_disponible()}")
        raise SystemExit(0)
    test_003_06_la_traduccion_es_la_del_dia_completo()
    test_003_06_cada_registro_del_martes_calza_con_la_tabla_de_verdad()
    test_003_06_el_ambito_nuevo_enlaza_hacia_atras()
    test_003_06_los_dos_cierres_encontraron_su_pareja()
    test_003_06_solo_queda_abierto_el_pendiente_de_manana()
    test_003_06_el_miercoles_abre_con_su_pendiente_propagado()
    test_003_06_la_nota_existe_y_su_constancia_la_enlaza()
    test_003_06_no_quedo_ninguna_marca_sin_su_consecuencia()
    test_003_06_la_instruccion_al_agente_no_entro_al_dia()
    print("ok: el día entero dictado deja el vault del epic 002")
