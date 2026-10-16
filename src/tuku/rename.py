"""Renombrar lo que el autor nombró, sin romper lo que apunta a ello.

Un vault es texto enlazado, así que cambiarle el nombre a algo no es mover un
archivo: es mover el archivo **y** arreglar todo lo que lo nombraba. Hecho a
medias deja enlaces rotos que nadie ve hasta que hacen falta.

Existe por una razón medible. Un agente sabe renombrar sin este comando: abre
los archivos, busca las menciones y las edita una por una. Le sale bien y le
cuesta caro, y cada corrida puede olvidar un lugar distinto. Con el comando es
una llamada, siempre la misma, y lo que el vault promete no depende de cuánto
esfuerzo le quedaba al modelo.

Acá vive el núcleo puro: funciones de texto a texto que no tocan disco. Los
casos de uso que leen, escriben y devuelven un `Resultado` están en el módulo
del noun que renombran (`scope`, `note`, `entry`).
"""

from __future__ import annotations

import re
from urllib.parse import unquote

from tuku import link

#: Un enlace es `[[nombre]]`, y también `[[nombre#ancla]]` o `[[nombre|alias]]`.
#: El nombre se compara entero: `[[depto]]` no se toca al renombrar `[[dept]]`.
_ENLACE = r"\[\[{nombre}((?:#|\|)[^\]]*)?\]\]"


def renombrar_enlaces(texto: str, viejo: str, nuevo: str) -> tuple[str, int]:
    """Cambia los enlaces a `viejo` por enlaces a `nuevo` y devuelve cuántos cambió.

    Entiende los dos formatos: `[[viejo]]` pasa a `[[nuevo]]`, y
    `[viejo](ambitos/viejo/viejo.md)` pasa a `[nuevo](ambitos/nuevo/nuevo.md)`.

    Respeta lo que va después del nombre, que es lo que distingue un enlace de
    una transclusión (`#^ancla`) o de un alias (`|otro texto`): eso apunta a una
    parte del destino, no al destino, y renombrar no lo altera.

    **Solo toca enlaces.** Una mención en prosa se deja como está: el autor
    escribió esa frase y no es de TUKU reescribirla. Lo que sí queda dicho es
    cuántos enlaces cambiaron, para que el comando pueda reportarlo.
    """
    if not viejo or viejo == nuevo:
        return texto, 0
    patron = re.compile(_ENLACE.format(nombre=re.escape(viejo)))
    texto, wikis = patron.subn(lambda m: f"[[{nuevo}{m.group(1) or ''}]]", texto)
    texto, mds = _renombrar_md(texto, viejo, nuevo)
    return texto, wikis + mds


_MD = re.compile(r"(?<!!)\[(?P<texto>[^\]\n]*)\]\((?P<destino>[^)\s]+)\)")


def _renombrar_md(texto: str, viejo: str, nuevo: str) -> tuple[str, int]:
    """Cambia el texto y la ruta de los links Markdown que apuntan a `viejo`.

    Un link apunta a `viejo` si el archivo o la carpeta a la que va se llama así
    (`ambitos/viejo/viejo.md`, `notas/viejo.md`). Cada tramo de la ruta que sea
    `viejo` (carpeta) o `viejo.md` (archivo) pasa a `nuevo`, y el texto solo
    cambia si era el nombre mismo: un texto distinto lo eligió el autor.
    """

    def cambiar(m: re.Match[str]) -> str:
        if link.nombre_de(m.group()) != viejo:
            return m.group()
        ruta, ancla = m.group("destino").partition("#")[::2]
        tramos = [
            nuevo if t == viejo else f"{nuevo}.md" if t == f"{viejo}.md" else t
            for t in unquote(ruta).split("/")
        ]
        destino = "/".join(tramos) + (f"#{ancla}" if ancla else "")
        etiqueta = nuevo if m.group("texto") == viejo else m.group("texto")
        return link.md(etiqueta, destino)

    cambios = 0

    def contar(m: re.Match[str]) -> str:
        nonlocal cambios
        salida = cambiar(m)
        cambios += salida != m.group()
        return salida

    return _MD.sub(contar, texto), cambios


def renombrar_ancla(texto: str, viejo: str, nuevo: str) -> tuple[str, int]:
    """Cambia el ancla `^viejo` por `^nuevo`, incluida la de una transclusión.

    Las páginas de ámbito transcluyen su bloque de pendientes por un ancla que
    lleva el nombre del ámbito (`![[...#^personal]]`), así que un renombrado que
    la ignore deja la página apuntando a un bloque que ya no existe.
    """
    if not viejo or viejo == nuevo:
        return texto, 0
    # `\b` no sirve: el guion no es carácter de palabra, así que `^personal`
    # casaría dentro de `^personal-2`, y los nombres de ámbito llevan guiones.
    patron = re.compile(rf"\^{re.escape(viejo)}(?![\w-])")
    return patron.subn(f"^{nuevo}", texto)


def renombrar_titulo(texto: str, nuevo: str) -> str:
    """Reemplaza el `# Título` de un documento, que es su nombre visible.

    Si no hay encabezado no inventa uno: un documento sin título es un defecto
    que le toca reportar al lint, no algo que el renombrado deba tapar.
    """
    return re.sub(r"^# .*$", f"# {nuevo}", texto, count=1, flags=re.MULTILINE)


#: Un registro de bitácora: `- HH:MM - [ambito](ruta) cuerpo`. El ámbito es
#: opcional, y lo que se corrige es el cuerpo: la hora y el ámbito los fija otra
#: cosa (`tuku entry add`), y cambiarlos acá los dejaría fuera de su control.
_REGISTRO = re.compile(rf"^(- (\d{{2}}:\d{{2}}) - (?:{link.ENLACE} )?)(.*)$")


def cuerpo_del_registro(ahora: str, dia: str, hora: str) -> str | None:
    """El cuerpo del registro de ese día y esa hora, o `None` si no está.

    Se busca dentro de la sección del día, no en todo el archivo: la misma hora
    se repite en días distintos y corregir el registro equivocado es
    exactamente el modo de falla que este comando existe para evitar.
    """
    encabezado = dia if dia.startswith("## ") else f"## {dia}"
    dentro = False
    for linea in ahora.splitlines():
        if linea.startswith("## "):
            dentro = linea.strip() == encabezado
            continue
        if not dentro:
            continue
        m = _REGISTRO.match(linea)
        if m is not None and m.group(2) == hora:
            return m.group(3)
    return None


def corregir_registro(ahora: str, dia: str, hora: str, cuerpo: str) -> tuple[str, bool]:
    """`AHORA.md` con el cuerpo de ese registro reemplazado.

    Conserva la hora y el ámbito, que son de `tuku entry add`. Devuelve si
    cambió algo, para que el caso de uso distinga "corregido" de "no estaba".
    """
    encabezado = dia if dia.startswith("## ") else f"## {dia}"
    lineas = ahora.splitlines(keepends=True)
    dentro = False
    cambio = False
    for i, linea in enumerate(lineas):
        if linea.startswith("## "):
            dentro = linea.strip() == encabezado
            continue
        if not dentro:
            continue
        m = _REGISTRO.match(linea.rstrip("\n"))
        if m is not None and m.group(2) == hora and m.group(3) != cuerpo:
            final = "\n" if linea.endswith("\n") else ""
            lineas[i] = f"{m.group(1)}{cuerpo}{final}"
            cambio = True
            break
    return "".join(lineas), cambio
