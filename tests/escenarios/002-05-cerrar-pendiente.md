# 002-05 · Cierre de compromisos

> **Principio:** [P1 (texto operable a mano)](../../docs/principios.md#L9), [P4 (determinismo)](../../docs/principios.md#L33) · **Brief:** [Triangulación tiempo × compromiso](../../docs/brief.md#L27) · **Spec:** [`spec/pendientes.md`](../../spec/pendientes.md) · **Origen:** [Lección 4 de `mac-jpgil`](../../devel/lecciones-macjpgil.md) (cierres sin pareja)

Cerrar un compromiso opera primordialmente mediante el comando directo `tuku todo close`: busca el pendiente por su cuerpo, lo elimina de `PENDIENTES.md` de forma determinista y estampa su constancia cronológica en `AHORA.md`. La vía bitácora (`tuku entry add`) aplica esta misma consecuencia en automático ante la marca `~~(Hecho)~~`.

## Estado inicial

```bash
cp -r ../../002-04-abrir-pendiente/abrir-el-pendiente-copia-el/mi-vault .
```

## Escenario: el cierre repite el texto y borra el ítem

Dado un pendiente abierto en `esta semana` con cuerpo `avisar de los GGCC a la administradora`
Cuando se cierra directamente con el comando todo close
```bash
tuku todo close --vault mi-vault --day 2026-08-11 --hour 19:05 --body "avisar de los GGCC a la administradora"
```
Entonces la fila desaparece de la tabla de `PENDIENTES.md`
Y la tabla queda vacía con su cabecera intacta
Y estampa la constancia de cierre bajo `## Martes 11 de agosto` en `AHORA.md`
Y el registro previo de apertura de las 14:20 permanece intacto en `AHORA.md`
Y `tuku doctor` valida que no quedan consecuencias pendientes

## Escenario: un cierre sin pendiente abierto se reporta, no se inventa nada

Dado que nunca se abrió ningún pendiente con el cuerpo `comprar una maleta` y el anterior ya está cerrado
```bash
tuku todo close --vault mi-vault --day 2026-08-11 --hour 19:05 --body "avisar de los GGCC a la administradora"
```
Cuando se ingresa un cierre huérfano con todo close
```bash
tuku todo close --vault mi-vault --day 2026-08-11 --hour 19:10 --scope personal --body "comprar una maleta"
```
Entonces el comando reporta que no había pareja abierta sin rechazar la llamada (código 0)
Y `PENDIENTES.md` permanece intacto, sin crear filas artificiales
Y la línea queda escrita en `AHORA.md` (un error del autor se informa, nunca se censura)

## Escenario: cerrar dos veces no vuelve a mover

Dado el pendiente ya cerrado con todo close
```bash
tuku todo close --vault mi-vault --day 2026-08-11 --hour 19:05 --body "avisar de los GGCC a la administradora"
```
Cuando se corre el mismo comando de cierre una segunda vez
```bash
tuku todo close --vault mi-vault --day 2026-08-11 --hour 19:05 --body "avisar de los GGCC a la administradora"
```
Entonces el diff contra el estado previo es vacío (idempotente)
Y el comando reporta cierre sin pareja, pues el pendiente ya no estaba abierto

## Escenario: la vía bitácora tuku entry add cierra el pendiente en automático

Dado un pendiente abierto en el vault
```bash
tuku todo open --vault mi-vault --day 2026-08-11 --hour 15:00 --scope personal --body "pagar sesión del psicólogo"
```
Cuando se registra el cierre en la bitácora con `~~(Hecho)~~`
```bash
tuku entry add --vault mi-vault --day 2026-08-11 --hour 19:20 --scope personal --body "~~(Hecho)~~: pagar sesión del psicólogo"
```
Entonces la fila desaparece de la tabla de `PENDIENTES.md`
Y el registro de cierre queda escrito bajo `## Martes 11 de agosto` en `AHORA.md`
Y `tuku doctor` valida que no quedan consecuencias pendientes

## Aceptación humana (en Obsidian)

- Al leer el martes 11 en Obsidian, la apertura de las 14:20 y el cierre de las 19:05 deben leerse claramente como la misma tarea tachada en el transcurso del día.
- El mensaje de advertencia del cierre huérfano debe ser transparente y orientador, sin sonar punitivo ni dejar el archivo desincronizado.
