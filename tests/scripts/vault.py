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

`preparar_playground()` da el directorio donde cada arnés instala: todo test
que produce un vault lo deja en `../../playground/<slug>/` (git-ignored) y
nunca en un tempdir que se descarta, para que correr la suite deje el
resultado a la vista del autor.
"""

from __future__ import annotations

import filecmp
import shutil
from pathlib import Path

#: Raíz del repo. `tests/scripts/` cuelga tres niveles bajo la raíz.
RAIZ_REPO = Path(__file__).resolve().parent.parent.parent


PLAYGROUND = RAIZ_REPO / "playground"


def preparar_dir(destino: Path) -> Path:
    """Deja `destino` existente y vacío, dentro de `playground/`.

    Todo arnés que produce un vault lo deja acá, nunca en un tempdir: así correr
    la suite deja el resultado a la vista para el `## Qué se mira a mano` del
    escenario. Es regla, no preferencia (`../escenarios/README.md`).

    Casi nunca hay nada que borrar: el `XXX-00` de cada epic limpia
    `playground/XXX-*` una vez por sesión, antes de que nada escriba, y desde ahí
    los escenarios solo crean.

    Solo se toca lo que está dentro de `playground/`, nunca la raíz.
    """
    destino = destino.resolve()
    try:
        rel = destino.relative_to(PLAYGROUND.resolve())
    except ValueError:
        raise ValueError(f"{destino} está fuera de playground/, no se toca") from None
    if str(rel) in (".", ""):
        raise ValueError("playground/ entero no se borra, solo la carpeta de un escenario")

    if destino.exists():
        shutil.rmtree(destino)
    destino.mkdir(parents=True)
    return destino


def preparar_playground(slug: str) -> Path:
    """`preparar_dir` para la carpeta propia de un escenario, por su slug.

    Dispara antes la limpieza del epic, igual que hace el runner de escenarios:
    si no, un arnés que llega por esta vía se salta el `XXX-00` y su carpeta
    sobrevive de la corrida anterior.
    """
    if not slug or "/" in slug or slug in (".", ".."):
        raise ValueError(f"slug de playground inválido: {slug!r}")
    import gherkin  # tardío: gherkin importa este módulo

    gherkin.preparar_epic(gherkin.epic_de(slug))
    return preparar_dir(PLAYGROUND / slug)


def instantanea(raiz: Path) -> dict[str, bytes]:
    """El contenido de todos los archivos del vault, por ruta relativa."""
    return {
        str(p.relative_to(raiz)): p.read_bytes()
        for p in sorted(raiz.rglob("*"))
        if p.is_file()
        and not p.name.startswith(".")
        and not p.name.endswith(".partial")
        and not p.name.endswith(".tmp")
    }


def delta(antes: dict[str, bytes], despues: dict[str, bytes]) -> dict[str, str]:
    """Rutas que cambiaron entre dos instantáneas: 'nuevo', 'borrado' o 'modificado'."""
    cambios: dict[str, str] = {}
    for ruta in antes.keys() | despues.keys():
        anterior, posterior = antes.get(ruta), despues.get(ruta)
        if anterior == posterior:
            continue
        cambios[ruta] = (
            "nuevo" if anterior is None else "borrado" if posterior is None else "modificado"
        )
    return cambios


#: Marcas que el template deja para que el instalador las sustituya. Ninguna
#: puede sobrevivir a una instalación: si sobrevive, el instalador no conoce
#: un placeholder que el template sí usa.
PLACEHOLDERS = ("AAAA-MM-DD", "DD de mes", "TZ-DEL-SISTEMA")


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
        try:
            archivo.relative_to(raiz / "reglas" / "plantilla")
            continue
        except ValueError:
            pass
        texto = archivo.read_text(encoding="utf-8")
        for numero, linea in _fuera_de_bloques_de_codigo(texto):
            for marca in PLACEHOLDERS:
                if marca in linea:
                    encontrados.append(f"{archivo.relative_to(raiz)}:{numero}: {marca}")
    return encontrados


def ahora_sembrado(template_variante: Path, *, desde: str, hasta: str, dias: list[str]) -> str:
    """El `AHORA.md` que se espera tras instalar, derivado del template real.

    `dias` son los encabezados ya resueltos (2 para día inicial y final, o 7
    para plantilla semanal completa).
    """
    plantilla_path = template_variante / "reglas" / "plantilla" / "AHORA.md"
    if not plantilla_path.is_file():
        plantilla_path = template_variante / "AHORA.md"
    plantilla = plantilla_path.read_text(encoding="utf-8")
    esperado = plantilla.replace("from: AAAA-MM-DD", f"from: {desde}")
    esperado = esperado.replace("to: AAAA-MM-DD", f"to: {hasta}")

    posiciones = [
        "Lunes",
        "Martes",
        "Miércoles",
        "Jueves",
        "Viernes",
        "Sábado",
        "Domingo",
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
