"""El tutorial como prueba: cómo se leen los capítulos y el veredicto del juez.

Nada de esto llama a un modelo. Lo caro (el agente, el juez) lo corre
`tests/scripts/test-tui.py tutorial`.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))

import tutorial


def _capitulo(tmp_path: Path, texto: str, nombre: str = "02-registrar.md") -> tutorial.Capitulo:
    archivo = tmp_path / nombre
    archivo.write_text(texto, encoding="utf-8")
    return tutorial.leer_capitulo(2, archivo)


def test_el_tip_es_la_frase_y_el_check_va_con_su_paso(tmp_path: Path) -> None:
    cap = _capitulo(
        tmp_path,
        "# 2. Registrar\n\n## Uno\n\n> [!tip] Dile a tu agente\n> Hola.\n>\n> Adiós.\n\n"
        "> [!check] Qué debería pasar\n> - Queda escrito.\n> - Con hora.\n",
    )
    assert cap.titulo == "2. Registrar"
    assert cap.id == "010-02-registrar"
    [paso] = cap.pasos
    assert (paso.tipo, paso.texto) == ("dictar", "Hola.\n\nAdiós.")
    assert paso.checks == ["Queda escrito.", "Con hora."]


def test_un_bash_es_un_comando_y_la_instalacion_no_corre(tmp_path: Path) -> None:
    cap = _capitulo(
        tmp_path,
        "```bash\nuv tool install --force x\n```\n\n```bash\ntuku init mi-vault\n```\n\n"
        "> [!check] Qué debería pasar\n> - Hay vault.\n",
    )
    [paso] = cap.pasos
    assert (paso.tipo, paso.texto, paso.checks) == (
        "comando",
        "tuku init mi-vault",
        ["Hay vault."],
    )


def test_una_alternativa_no_es_otro_paso(tmp_path: Path) -> None:
    cap = _capitulo(
        tmp_path,
        "## A\n\n> [!tip] Dile a tu agente\n> Uno.\n\n> [!tip] O dile a tu agente\n> Dos.\n",
    )
    assert [p.texto for p in cap.pasos] == ["Uno."]


def test_un_check_en_un_apartado_sin_paso_queda_a_mano(tmp_path: Path) -> None:
    cap = _capitulo(
        tmp_path,
        "## Revisar\n\n> [!tip] Dile\n> Uno.\n\n### Edita a mano\n\n"
        "> [!check] Qué debería pasar\n> - Sigue sano.\n",
    )
    assert [p.tipo for p in cap.pasos] == ["dictar", "manual"]
    assert cap.pasos[1].checks == ["Sigue sano."]


def test_un_check_en_una_seccion_sin_paso_sigue_al_paso_anterior(tmp_path: Path) -> None:
    cap = _capitulo(
        tmp_path,
        "## Cambiar\n\n> [!tip] Dile\n> Uno.\n\n## Qué apareció\n\n"
        "> [!check] Qué debería pasar\n> - Hay un archivo.\n",
    )
    assert [(p.tipo, p.checks) for p in cap.pasos] == [("dictar", ["Hay un archivo."])]


def test_la_tabla_de_un_check_da_una_afirmacion_por_fila(tmp_path: Path) -> None:
    cap = _capitulo(
        tmp_path,
        "> [!tip] Dile\n> Uno.\n\n> [!check] Qué debería pasar\n> Quedan:\n>\n"
        "> | A | B |\n> | --- | --- |\n> | x | y |\n",
    )
    assert cap.pasos[0].checks == ["Quedan:", "| A | B |", "| x | y |"]


def test_un_check_antes_de_todo_paso_abre_la_conversacion(tmp_path: Path) -> None:
    cap = _capitulo(tmp_path, "# 10. X\n\n> [!check] Qué debería pasar\n> - Propone.\n")
    assert (cap.pasos[0].tipo, cap.pasos[0].texto) == ("dictar", tutorial.APERTURA)


def test_los_diez_capitulos_del_tutorial_se_leen_y_juzgan_algo() -> None:
    assert sorted(tutorial.archivos()) == list(range(1, 11))
    for n in tutorial.archivos():
        cap = tutorial.leer_capitulo(n)
        assert cap.pasos, cap.archivo.name
        assert any(p.checks for p in cap.pasos), cap.archivo.name
        assert all(p.texto for p in cap.pasos), cap.archivo.name


def test_los_capitulos_pedidos() -> None:
    assert tutorial.rango("", 10) == list(range(1, 11))
    assert tutorial.rango("6", 10) == [6]
    assert tutorial.rango("3-5", 10) == [3, 4, 5]
    assert tutorial.rango("1,4,7", 10) == [1, 4, 7]
    with pytest.raises(tutorial.CapituloNoEncontrado):
        tutorial.rango("a", 10)


def test_el_reloj_avanza_y_el_lunes_salta_a_la_semana_siguiente() -> None:
    reloj = tutorial.Reloj(9)
    assert reloj.ahora(tutorial.Paso("dictar", "x", "", "Dile")) == "2026-08-21 08:40"
    assert reloj.ahora(tutorial.Paso("dictar", "x", "", "Dile, el lunes")) == "2026-08-24 08:30"
    assert reloj.ahora(tutorial.Paso("dictar", "x", "", "Dile")) == "2026-08-24 08:40"


def test_el_veredicto_del_juez_y_lo_que_no_contesto() -> None:
    salida = "1. CUMPLE\n2. NO CUMPLE: la fila sigue en PENDIENTES.md\n"
    assert tutorial.leer_veredicto(salida, 3) == [
        (True, ""),
        (False, "la fila sigue en PENDIENTES.md"),
        (False, "el juez no contestó esta afirmación"),
    ]


def test_un_edita_a_mano_es_un_paso_con_su_bloque_edit(tmp_path: Path) -> None:
    cap = _capitulo(
        tmp_path,
        "### Hazlo\n\n> [!warning] Edita a mano\n> Borra una fila.\n>\n> ```edit\n"
        "> PENDIENTES.md: borra la fila 1\n> deshacer\n> ```\n\n"
        "> [!check] Qué debería pasar\n> - doctor avisa.\n",
    )
    [paso] = cap.pasos
    assert (paso.tipo, paso.checks) == ("editar", ["doctor avisa."])
    assert paso.texto == "PENDIENTES.md: borra la fila 1\ndeshacer"
    assert tutorial.deshace(paso.texto)


def test_un_edita_a_mano_sin_bloque_edit_se_rechaza(tmp_path: Path) -> None:
    with pytest.raises(tutorial.EdicionInvalida):
        _capitulo(tmp_path, "> [!warning] Edita a mano\n> Borra una fila.\n")


def _vault(tmp_path: Path) -> Path:
    (tmp_path / "AHORA.md").write_text(
        "# Hoy\n\n## Lunes\n\n"
        "- 08:40 - [personal](x.md) Partí.\n- 08:50 - [personal](x.md) Luego.\n",
        encoding="utf-8",
    )
    (tmp_path / "PENDIENTES.md").write_text(
        "| Detalle | Vence |\n| --- | --- |\n| uno | |\n| dos | |\n", encoding="utf-8"
    )
    return tmp_path


def test_las_tres_ediciones_y_deshacerlas(tmp_path: Path) -> None:
    v = _vault(tmp_path)
    antes = (v / "PENDIENTES.md").read_bytes()
    previos = tutorial.aplicar_edicion(
        v,
        'AHORA.md: anota " (revisado)" en el primer registro\n'
        'AHORA.md: reemplaza "Luego" por "Después"\n'
        "PENDIENTES.md: borra la fila 2",
    )
    assert "Partí. (revisado)" in (v / "AHORA.md").read_text(encoding="utf-8")
    assert "Después" in (v / "AHORA.md").read_text(encoding="utf-8")
    assert "dos" not in (v / "PENDIENTES.md").read_text(encoding="utf-8")
    assert "uno" in (v / "PENDIENTES.md").read_text(encoding="utf-8")
    for ruta, contenido in previos.items():
        ruta.write_bytes(contenido)
    assert (v / "PENDIENTES.md").read_bytes() == antes


def test_una_edicion_que_falla_no_deja_nada_a_medias(tmp_path: Path) -> None:
    v = _vault(tmp_path)
    antes = (v / "AHORA.md").read_bytes()
    with pytest.raises(tutorial.EdicionInvalida):
        tutorial.aplicar_edicion(
            v, 'AHORA.md: reemplaza "Partí" por "Salí"\nAHORA.md: reemplaza "no está" por "x"'
        )
    assert (v / "AHORA.md").read_bytes() == antes
    with pytest.raises(tutorial.EdicionInvalida):
        tutorial.aplicar_edicion(v, "PENDIENTES.md: borra la fila 9")
    with pytest.raises(tutorial.EdicionInvalida):
        tutorial.aplicar_edicion(v, "AHORA.md: haz magia")
