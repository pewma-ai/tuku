# 002-02 · Registro en su día

> **Principio:** [P1 (texto operable a mano)](../../docs/principios.md#L9), [P4 (determinismo)](../../docs/principios.md#L33) · **Brief:** [Eje tiempo y reducción de carga cognitiva](../../docs/brief.md#L27) · **Spec:** [`spec/bitacora.md`](../../spec/bitacora.md)

`tuku entry add` es la primitiva fundamental de captura: toma los campos de un hecho e inserta el registro bajo el encabezado del día correspondiente en estricto orden cronológico, sin importar el orden en que se ingresen.

## Estado inicial

```bash
cp -r ../../002-01-abrir-ciclo/crear-ahora-md-a-partir-de-la/mi-vault .
```

## Escenario: tres registros caen en el día de hoy, ordenados por hora

Dado un vault con el ciclo abierto en martes 11 y sin registros previos
Cuando se corren estas tres líneas en desorden temporal:
```bash
tuku entry add --vault mi-vault --day 2026-08-11 --hour 18:40 --body "le mandé la boleta de gastos comunes del depto centro a la administradora por WhatsApp"
tuku entry add --vault mi-vault --day 2026-08-11 --hour 09:12 --scope personal --body "**señal**: la administradora responde los mensajes con varios días de atraso"
tuku entry add --vault mi-vault --day 2026-08-11 --hour 11:30 --body "hice la consulta presencial por el standing desk"
```
Entonces los tres registros quedan bajo `## Martes 11 de agosto`
Y ordenados por hora: 09:12, 11:30 y 18:40
Y el resto de los días del ciclo permanecen vacíos

## Escenario: la fase 1 propaga hacia ámbitos y no toca PENDIENTES.md

Dado el mismo estado inicial
Cuando se corren los tres registros del día
```bash
tuku entry add --vault mi-vault --day 2026-08-11 --hour 18:40 --body "le mandé la boleta de gastos comunes del depto centro a la administradora por WhatsApp"
tuku entry add --vault mi-vault --day 2026-08-11 --hour 09:12 --scope personal --body "**señal**: la administradora responde los mensajes con varios días de atraso"
tuku entry add --vault mi-vault --day 2026-08-11 --hour 11:30 --body "hice la consulta presencial por el standing desk"
```
Entonces el diff toca `AHORA.md` y `ambitos/personal/personal.md`
Y `PENDIENTES.md` permanece intacto, byte a byte igual que al inicio

## Escenario: el registro sin ámbito y sin clasificación es válido

Dado el mismo estado inicial
Cuando se ingresa un registro mínimo sin `[[ambito]]` ni `**clasificacion**`
```bash
tuku entry add --vault mi-vault --day 2026-08-11 --hour 11:30 --body "hice la consulta presencial por el standing desk"
```
Entonces `tuku entry add` lo escribe tal cual sin forzar marcas artificiales

## Escenario: omisión de día y hora asume hoy y ahora
Dado el mismo estado inicial
Cuando se agrega una entrada omitiendo los argumentos de día y hora
```bash
TUKU_NOW="2026-08-11 16:45" tuku entry add --vault mi-vault --scope personal --body "revisión presencial de correspondencia"
```
Entonces el registro cae bajo `## Martes 11 de agosto` con la hora 16:45

## Aceptación humana (en Obsidian)

- Al leer el martes 11 en Obsidian, los tres hechos deben entenderse perfectamente sin necesidad de la conversación que los originó.
- El registro de las 18:40 (sin clasificación ni ámbito) debe leerse natural y completo, sin sentirse incompleto frente a los clasificados.
