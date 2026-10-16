# 002-13 · Links Markdown y `tuku fix link`

> **Principio:** [P1 (soberanía y equivalente manual)](../../docs/principios.md#L9), [P4 (determinismo)](../../docs/principios.md#L33) · **Spec:** [`spec/cli.md`](../../spec/cli.md), [`spec/bitacora.md`](../../spec/bitacora.md)

El enlace de TUKU es un link Markdown con ruta relativa al archivo que lo contiene. Obsidian, con su configuración por defecto, escribe wikilinks cuando el autor enlaza a mano: `tuku doctor link` los reporta y `tuku fix link` los convierte. Lo que requiere una decisión del autor no se escribe y se devuelve como decisión.

Fuera de la cadena: siembra su propio vault.

## Escenario: doctor link reporta el wikilink y fix link lo convierte

Dado un vault con una nota que enlaza a mano con un wikilink, de fecha antigua
```bash
tuku init mi-vault --date 2026-08-10
printf '# Nota\n\ncuerpo\n\n## Ver además\n\n* [[personal]] — el ámbito de la nota\n' > mi-vault/notas/prueba.md
touch -t 202001010000 mi-vault/notas/prueba.md
```
Cuando se revisa el tema `link` y luego se repara
```bash
tuku doctor link --vault mi-vault
tuku fix link --vault mi-vault
tuku doctor link --vault mi-vault
```
Entonces la primera revisión sale con código 1 (`RECHAZO`) y nombra `tuku fix link`
Y la reparación sale con código 0 y deja `[personal](../ambitos/personal/personal.md)` en la nota
Y la fecha de modificación de la nota sigue siendo la antigua
Y la segunda revisión sale con código 0

## Escenario: una segunda reparación no cambia nada

Dado el vault del escenario anterior ya reparado
```bash
tuku init mi-vault --date 2026-08-10
printf '# Nota\n\ncuerpo\n\n## Ver además\n\n* [[personal]] — el ámbito de la nota\n' > mi-vault/notas/prueba.md
tuku fix link --vault mi-vault
```
Cuando se repara otra vez
```bash
tuku fix link --vault mi-vault
```
Entonces sale con código 0 y el delta contra el estado previo es vacío

## Escenario: un wikilink ambiguo se devuelve como decisión sin escribir

Dado una nota con un wikilink que coincide con dos archivos
```bash
tuku init mi-vault --date 2026-08-10
mkdir mi-vault/ambitos/personal/a mi-vault/ambitos/personal/b
touch mi-vault/ambitos/personal/a/doble.md mi-vault/ambitos/personal/b/doble.md
printf '# Nota\n\ncuerpo\n\n## Ver además\n\n* [[doble]] — cuál de los dos\n' > mi-vault/notas/ambigua.md
```
Cuando se repara
```bash
tuku fix link --vault mi-vault
```
Entonces sale con código 1 (`RECHAZO`), la nota queda como estaba y la salida nombra la decisión y los dos archivos candidatos
