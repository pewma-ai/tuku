# 003-05 · Lo que no se registra

> **Principio:** [P1 (texto operable a mano)](../../docs/principios.md#L9), [P3 (secretario, no dueño)](../../docs/principios.md#L25), [P4 (determinismo)](../../docs/principios.md#L33) · **Brief:** [El agente y las herramientas](../../docs/brief.md#L60) · **Spec:** [`spec/despacho.md`](../../spec/despacho.md), [`spec/agente.md`](../../spec/agente.md)

Ante dictados que mezclan hechos, preguntas e instrucciones operativas al asistente, el agente extrae únicamente el hecho real para la bitácora sin estampar muletillas, sin inventar cierres y sin alterar pendientes previos.

## Estado inicial

```bash
cp -r ../../003-04-un-hecho-con-consecuencia/lo-que-queda-por-hacer-se/mi-vault .
```

## Escenario: la instrucción y la pregunta no entran a la bitácora

Dado un vault con un registro escrito y un pendiente abierto
Cuando el autor dicta un hecho, una instrucción y una pregunta, todo junto
```agente
A las doce y cinco ordené los cables del escritorio.
Recuérdame que eso es importante.
¿Cuántos pendientes tengo abiertos?
```
Entonces solo la primera frase se traduce en un comando
```text
tuku entry add --day 2026-08-11 --hour 12:05 --scope personal \
  --body "**<clasificación>**: <el cuerpo>"
```
Y el registro de las 12:05 no lleva ninguna marca de la ontología cerrada
Y la palabra "recuérdame" no aparece en `AHORA.md`
Y `PENDIENTES.md` queda igual que antes: ni una fila nueva, ni una que desaparezca
Y el pendiente que ya estaba abierto sigue abierto

## Aceptación humana (en Obsidian)

- En `AHORA.md`, el hecho de las 12:05 aparece como registro simple sin marcas como `**pendiente**` o `~~(Hecho)~~`, y sin rastros de "recuérdame".
- En `PENDIENTES.md`, la tabla conserva intacto el compromiso anterior sin modificaciones no solicitadas.
