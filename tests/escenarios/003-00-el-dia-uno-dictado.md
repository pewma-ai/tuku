# Epic 003 · El día uno, dictado

> El mismo día uno del epic 002, con la misma entrada del corpus, pero dictada en lenguaje natural en vez de invocada a mano. El vault de salida tiene que ser el mismo.

Es la réplica agéntica del 002 y esa es su forma de verificarse: el estado final ya existe, producido a mano y revisado, así que el epic no tiene que decidir qué es correcto, solo si el agente llega ahí.

Empieza donde el 002: el fixture `vacio`. La diferencia no está en el estado inicial sino en quién arma las llamadas, y por eso este epic va aparte y no dentro del anterior.

## Qué tiene que funcionar

1. **El agente compila el dictado en llamadas `tuku`.** Recibe una sesión de dictado de [`referencia-faena.md`](../../corpus/referencia/referencia-faena.md), Parte 1, y emite invocaciones con sus campos. No escribe archivos: escribe el comando ([`spec/agente.md`](../../spec/agente.md)).
2. **Los campos son los correctos.** Cuántos hechos hay en una frase, a qué ámbito va cada uno, de qué clase es, y a qué hora, que se deriva de la jornada que el dictado describe y no viene dicha.
3. **Lo que el hecho sugiere se propone y no se ejecuta.** El principio 3 con el agente en el circuito, que es lo único que lo prueba de verdad.
4. **El vault resultante es el del epic 002.** Mismo corpus, misma salida.

## Decisiones previas

1. Qué arnés de agente se usa y cómo se aísla para no gastar tokens por accidente.
2. Dónde se especifica el comportamiento del agente al dirigirse al autor: trato, registro, cómo lo nombra en conversación.
3. **Con qué criterio se compara lo que no es byte a byte.** Nadie garantiza que un LLM devuelva el mismo texto dos veces, pero sí que diga lo mismo. Los campos son estructurados y sí se comparan exactos; el cuerpo del registro y el de una nota son prosa y piden otro criterio.

## Qué se verifica

- **Se comparan llamadas, no prosa.** El agente emite invocaciones `tuku entry add`, los campos van byte a byte contra la lista congelada, y solo el cuerpo se juzga con el criterio de la decisión 3.
- **El agente no escribe archivos.** Lo único que toca el vault son los comandos que emitió.
- **Rechazar una propuesta no deja rastro en ninguna primitiva.**
- Los escenarios de este epic **gastan tokens**, por lo que van fuera de la corrida por defecto marcados como `agentic`.

## Criterio de salida

Dictar el día uno del corpus produce un vault equivalente al que el epic 002 produjo a mano, con los campos idénticos y el cuerpo juzgado por el criterio que este epic fije.

## No entra

El histórico poblado y el destilado (Epic 004). Inferir lo que nadie pidió (Epic 006).

## Escenarios del epic

- [`003-01-dictado-del-dia-uno.md`](003-01-dictado-del-dia-uno.md) — El agente compila el dictado en llamadas `tuku`. Gasta tokens, fuera de la corrida por defecto.
- [`003-02-propuesta-no-escribe.md`](003-02-propuesta-no-escribe.md) — El agente propone y no escribe, y rechazarla no deja rastro.
