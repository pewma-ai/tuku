# 002-05 · Cierre de compromisos

> **Principio:** [P1 (texto operable a mano)](../../docs/principios.md#L9), [P4 (determinismo)](../../docs/principios.md#L33) · **Brief:** [Triangulación tiempo × compromiso](../../docs/brief.md#L27) · **Spec:** [`spec/pendientes.md`](../../spec/pendientes.md) · **Origen:** [Lección 4 de `mac-jpgil`](../../devel/lecciones-macjpgil.md) (cierres sin pareja)

Un compromiso se cierra con `tuku todo close`: escribe el registro `(Hecho)` en `AHORA.md` y borra de `PENDIENTES.md` la fila con el mismo cuerpo. Si se abrió el mismo día, queda solo el cierre. `tuku entry add` rechaza la marca `(Hecho)` y nombra este comando.

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
Y el registro que lo abrió a las 14:20 desaparece, de `AHORA.md` y de la página del ámbito: abierto y cerrado el mismo día, queda solo el cierre
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

## Escenario: abierto y cerrado a mano el mismo día, fix deja solo el cierre

Dado un pendiente abierto el martes 11 y cerrado a mano ese mismo día: el `(Hecho)` escrito en `AHORA.md` y la fila borrada de `PENDIENTES.md`
```bash
tuku todo open --vault mi-vault --day 2026-08-11 --hour 15:00 --scope personal --body "renovar el carnet"
awk '{print} /^- 18:40 - /{print "- 19:20 - [personal](ambitos/personal/personal.md) (Hecho): ~~renovar el carnet~~"}' mi-vault/AHORA.md > ahora.tmp && mv ahora.tmp mi-vault/AHORA.md
sed -i.bak '/renovar el carnet/d' mi-vault/PENDIENTES.md && rm mi-vault/PENDIENTES.md.bak
```
Cuando se revisa y se repara
```bash
tuku todo lint --vault mi-vault
tuku fix todo --vault mi-vault
tuku todo lint --vault mi-vault
```
Entonces el primer `tuku todo lint` sale con código 1 (`RECHAZO`) y nombra `tuku fix todo`
Y `tuku fix todo` quita el registro de las 15:00 de `AHORA.md` y de la página del ámbito, y deja el cierre de las 19:20
Y el segundo `tuku todo lint` sale limpio

## Aceptación humana (en Obsidian)

- Al leer el martes 11 en Obsidian, el pendiente abierto y cerrado ese día se lee una sola vez, tachado.
- El mensaje de advertencia del cierre huérfano debe ser transparente y orientador, sin sonar punitivo ni dejar el archivo desincronizado.
