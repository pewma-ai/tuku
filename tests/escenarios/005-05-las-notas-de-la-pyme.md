# 005-05 · Las notas de la Pyme

> **Principio:** [P1 (texto operable a mano)](../../docs/principios.md#L9), [P6 (conjunto canónico)](../../docs/principios.md#L55), [P8 (lo que se infiere sobre alguien se le podría mostrar)](../../docs/principios.md#L71) · **Brief:** [Ámbito × deliberación](../../docs/brief.md#L25) · **Spec:** [`spec/notas.md`](../../spec/notas.md), [`spec/ambitos.md`](../../spec/ambitos.md)

Con dos semanas de operación hay ideas que valen más que un día: cómo se cotiza, cómo se paga cada canal, cuánto se puede confiar en cada proveedor, y quién es Patricia Lillo. Esas ideas van a `notas/`, cada una cerrada con sus enlaces y el motivo de cada uno, y la primera sobre alguien se escribe como una nota tipada.

Los cuerpos salen de [`fixtures/005-05-las-notas-de-la-pyme/`](fixtures/005-05-las-notas-de-la-pyme/), escritos desde la Parte 3 del [corpus](../../corpus/referencia/referencia-pyme.md).

## Escenario: las notas del negocio se escriben y pasan el lint

Dado el vault de la segunda semana de Andrea
```bash
cp -r ../../005-01-las-dos-semanas-de-andrea/la-segunda-semana-cae-sobre-lo/mi-vault .
cp ../../tests/escenarios/fixtures/005-05-las-notas-de-la-pyme/*.md .
```
Cuando Andrea guarda tres ideas del negocio
```bash
cd mi-vault
tuku note create "Cómo cotizo" --body-file ../como-cotizo.md --scope negocio --at "2026-08-23 20:00"
tuku note create "Condiciones de pago por canal" --body-file ../condiciones-de-pago.md --scope negocio --at "2026-08-23 20:05"
tuku note create "Proveedores y sus plazos reales" --body-file ../plazos-de-los-proveedores.md --scope negocio --at "2026-08-23 20:10"
```
Entonces `notas/` tiene las tres notas, cada una con `type: Note`, su cuerpo y un `## Ver además` que enlaza el ámbito con el motivo
Y el domingo 23 gana tres constancias que enlazan a las notas
Y `tuku doctor note` sale limpio sobre cada una
```bash
tuku doctor note notas/como-cotizo.md
tuku doctor note notas/condiciones-de-pago-por-canal.md
tuku doctor note notas/proveedores-y-sus-plazos-reales.md
```
Y `tuku doctor` dice que el vault está sano
```bash
tuku doctor
```

## Escenario: note lint sin archivo revisa solo las notas

Dado el vault con las tres notas
```bash
cp -r ../las-notas-del-negocio-se/mi-vault .
```
Cuando se revisan todas las notas de una vez
```bash
cd mi-vault
tuku doctor note
```
Entonces el lint sale con código 0 y deja fuera `notas/AGENTS.md`, que es del sistema y no una nota

## Escenario: un enlace del cuerpo sin motivo en Ver además se nombra

Dado el vault con las tres notas, y `Proveedores y sus plazos reales` reescrita con un editor para enlazar en su cuerpo a `Condiciones de pago por canal`
```bash
cp -r ../las-notas-del-negocio-se/mi-vault .
cp ../../tests/escenarios/fixtures/005-05-las-notas-de-la-pyme/proveedores-con-enlace.md .
cp proveedores-con-enlace.md mi-vault/notas/proveedores-y-sus-plazos-reales.md
```
Cuando se revisa la nota
```bash
cd mi-vault
tuku doctor note notas/proveedores-y-sus-plazos-reales.md
```
Entonces el lint sale con error y nombra el enlace a `condiciones-de-pago-por-canal.md`, que la nota enlaza y su `## Ver además` no lista, con la corrección: agregarlo ahí con el motivo

## Escenario: la primera nota tipada es una persona

Dado el vault con las tres notas
```bash
cp -r ../las-notas-del-negocio-se/mi-vault .
cp ../../tests/escenarios/fixtures/005-05-las-notas-de-la-pyme/patricia-lillo.md .
```
Cuando Andrea guarda lo que sabe de Patricia Lillo, del Liceo Técnico Andes
```bash
cd mi-vault
tuku note create "Patricia Lillo" --subtype persona --body-file ../patricia-lillo.md --scope liceo-tecnico-andes --at "2026-08-23 20:20"
```
Entonces `notas/patricia-lillo.md` tiene `type: Note` y `subtype: persona`, y su `## Ver además` enlaza el ámbito del liceo con su motivo
Y existe `reglas/tipos/persona.md`, el archivo de reglas del tipo, que `tuku init` siembra junto con los demás archivos del vault
Y `tuku doctor note` y `tuku doctor` salen limpios
```bash
tuku doctor note notas/patricia-lillo.md
tuku doctor
```

## Qué se mira a mano

- La nota de Patricia Lillo se podría mostrar a Patricia Lillo: describe cómo trabajar con ella y no la juzga.
- Cada motivo de `## Ver además` dice para qué sirve la conexión y no repite el título del destino.

## Aceptación humana (en Obsidian)

- Desde la nota de Patricia Lillo se llega a la página del liceo, y desde el liceo se llega a la nota por la constancia del domingo 23.
