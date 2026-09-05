"""Pasos deterministas compartidos entre escenarios que instalan un vault.

Lo que vive acá es lo que más de un escenario necesita afirmar sobre un vault
recién instalado. La regla que ordena este módulo es la de
`../escenarios/README.md`: un test congela solo lo que el mecanismo bajo prueba
transforma, y todo lo que se copia sin tocar se compara en vivo contra
`template/<variante>/`.

Por eso acá no hay ninguna copia del template. `ahora_sembrado()` parte del
template real y le aplica las sustituciones que el escenario espera, escritas
a mano por el test. Así un cambio en el template no obliga a regenerar nada,
y un cambio en la lógica de sembrado sigue rompiendo el test, que es lo que
debe hacer.
"""

from __future__ import annotations

import filecmp
from pathlib import Path

#: Marcas que el template deja para que el instalador las sustituya. Ninguna
#: puede sobrevivir a una instalación: si sobrevive, el instalador no conoce
#: un placeholder que el template sí usa.
PLACEHOLDERS = ("AAAA-MM-DD", "DD de mes")


def diff_recursivo(a: Path, b: Path, *, ignorar: frozenset[str] = frozenset()) -> list[str]:
    """Rutas que difieren entre dos árboles, incluidas las que sobran o faltan."""
    cmp = filecmp.dircmp(a, b, ignore=list(ignorar))
    diferencias = [*cmp.left_only, *cmp.right_only, *cmp.diff_files]
    for sub in cmp.common_dirs:
        diferencias += [f"{sub}/{d}" for d in diff_recursivo(a / sub, b / sub, ignorar=ignorar)]
    return diferencias


def _fuera_de_bloques_de_codigo(texto: str) -> list[tuple[int, str]]:
    """Las líneas del documento que no están dentro de un fence ```."""
    lineas, dentro = [], False
    for numero, linea in enumerate(texto.splitlines(), start=1):
        if linea.lstrip().startswith("```"):
            dentro = not dentro
            continue
        if not dentro:
            lineas.append((numero, linea))
    return lineas


def placeholders_sin_sustituir(raiz: Path) -> list[str]:
    """Archivos del vault instalado donde quedó una marca sin reemplazar.

    Es la red que atrapa un placeholder nuevo en el template que el instalador
    todavía no sabe sustituir. Sin esto, agregar `DD de mes` a un archivo nuevo
    de `template/vanilla/` pasa el resto de las comparaciones en silencio.

    Los bloques de código quedan fuera del escaneo, y la distinción es de
    fondo: dentro de un fence, `AAAA-MM-DD` es el ejemplo de formato que el
    autor lee para saber cómo escribir (así lo usa `ambitos/CADENCIAS.md`);
    fuera de un fence, es una marca que el instalador tenía que resolver.
    """
    encontrados = []
    for archivo in sorted(p for p in raiz.rglob("*.md") if p.is_file()):
        texto = archivo.read_text(encoding="utf-8")
        for numero, linea in _fuera_de_bloques_de_codigo(texto):
            for marca in PLACEHOLDERS:
                if marca in linea:
                    encontrados.append(f"{archivo.relative_to(raiz)}:{numero}: {marca}")
    return encontrados


def ahora_sembrado(template_variante: Path, *, desde: str, hasta: str, dias: list[str]) -> str:
    """El `AHORA.md` que se espera tras instalar, derivado del template real.

    `dias` son los siete encabezados ya resueltos, en el orden en que deben
    quedar, escritos a mano por el escenario. Son lo único que este módulo no
    puede derivar sin repetir la lógica que se está probando: el mapeo de cada
    fecha a su nombre de día es justamente donde apareció el bug que encontró
    el escenario 001-001.
    """
    plantilla = (template_variante / "AHORA.md").read_text(encoding="utf-8")
    esperado = plantilla.replace("desde: AAAA-MM-DD", f"desde: {desde}")
    esperado = esperado.replace("hasta: AAAA-MM-DD", f"hasta: {hasta}")

    posiciones = [
        "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo",
    ]
    if len(dias) != len(posiciones):
        raise ValueError(f"se esperaban {len(posiciones)} días, llegaron {len(dias)}")
    for posicion, real in zip(posiciones, dias, strict=True):
        placeholder = f"## {posicion} DD de mes"
        if placeholder not in esperado:
            raise AssertionError(
                f"el template ya no trae el encabezado '{placeholder}'. "
                "Si cambió la forma de AHORA.md, este paso compartido cambia con él."
            )
        esperado = esperado.replace(placeholder, real)
    return esperado
