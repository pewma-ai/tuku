# 002-05 · Cierre de compromisos

> **Principio:** [P1 (texto operable a mano)](../../docs/principios.md#L9), [P4 (determinismo)](../../docs/principios.md#L33) · **Brief:** [Triangulación tiempo × compromiso](../../docs/brief.md#L27) · **Spec:** [`spec/pendientes.md`](../../spec/pendientes.md) · **Origen:** [Lección 4 de `mac-jpgil`](../../devel/lecciones-macjpgil.md) (cierres sin pareja)

Cerrar un compromiso debe ser tan directo como tacharlo en un cuaderno: registrar un hecho con `~~(Hecho)~~` repite el texto del pendiente y lo elimina de la tabla activa de forma determinista, conservando el historial en la bitácora sin inventar tareas ficticias.

## Estado inicial

```bash
cp -r ../../002-04-abrir-pendiente/abrir-el-pendiente-copia-el/mi-vault .
```

## Escenario: el cierre repite el texto y borra el ítem

Dado un pendiente abierto en `esta semana` con cuerpo `avisar de los GGCC a la administradora`
Cuando se escribe el cierre correspondiente en la bitácora
```bash
tuku entry add --vault mi-vault --day 2026-08-11 --hour 19:05 --scope personal --body "~~(Hecho)~~: avisar de los GGCC a la administradora"
```
Entonces la fila desaparece de la tabla de `PENDIENTES.md`
Y la tabla queda vacía con su cabecera intacta
Y el registro previo de apertura de las 14:20 permanece intacto en `AHORA.md`
Y `tuku doctor` valida que no quedan consecuencias pendientes

## Escenario: un cierre sin pendiente abierto se reporta, no se inventa nada

Dado que nunca se abrió ningún pendiente con el cuerpo `comprar una maleta` y el anterior ya está cerrado
```bash
tuku entry add --vault mi-vault --day 2026-08-11 --hour 19:05 --scope personal --body "~~(Hecho)~~: avisar de los GGCC a la administradora"
```
Cuando se ingresa un cierre huérfano
```bash
tuku entry add --vault mi-vault --day 2026-08-11 --hour 19:10 --scope personal --body "~~(Hecho)~~: comprar una maleta"
```
Entonces el comando reporta que no había pareja abierta sin rechazar la llamada (código 0)
Y `PENDIENTES.md` permanece intacto, sin crear filas artificiales
Y la línea queda escrita en `AHORA.md` (un error del autor se informa, nunca se censura)

## Escenario: cerrar dos veces no vuelve a mover

Dado el pendiente ya cerrado
```bash
tuku entry add --vault mi-vault --day 2026-08-11 --hour 19:05 --scope personal --body "~~(Hecho)~~: avisar de los GGCC a la administradora"
```
Cuando se corre el mismo comando de cierre una segunda vez
```bash
tuku entry add --vault mi-vault --day 2026-08-11 --hour 19:05 --scope personal --body "~~(Hecho)~~: avisar de los GGCC a la administradora"
```
Entonces el diff contra el estado previo es vacío (idempotente)
Y el comando reporta cierre sin pareja, pues el pendiente ya no estaba abierto

## Escenario: comando directo tuku todo close elimina el ítem y estampa constancia de cierre

Dado un pendiente abierto en `esta semana` con cuerpo `avisar de los GGCC a la administradora`
Cuando se cierra directamente con el comando todo close
```bash
TUKU_NOW="2026-08-11 19:30" tuku todo close --vault mi-vault --body "avisar de los GGCC a la administradora"
```
Entonces la fila desaparece de `PENDIENTES.md`
Y estampa la constancia en `AHORA.md` bajo `## Martes 11 de agosto` recuperando el ámbito `personal`:
`- 19:30 - [[personal]] ~~(Hecho)~~: avisar de los GGCC a la administradora`
Y una segunda ejecución directa es idempotente y reporta sin pareja
```bash
TUKU_NOW="2026-08-11 19:30" tuku todo close --vault mi-vault --body "avisar de los GGCC a la administradora"
```

## Aceptación humana (en Obsidian)

- Al leer el martes 11 en Obsidian, la apertura de las 14:20 y el cierre de las 19:05 deben leerse claramente como la misma tarea tachada en el transcurso del día.
- El mensaje de advertencia del cierre huérfano debe ser transparente y orientador, sin sonar punitivo ni dejar el archivo desincronizado.
