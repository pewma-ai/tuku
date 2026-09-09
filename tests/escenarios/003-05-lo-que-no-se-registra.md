# Escenario · 003-05-lo-que-no-se-registra

**Cubre:** epic 003, quinto peldaño: los casos negativos. Gemelos deterministas: [`002-03`](002-03-lint-de-registro.md) y [`002-05`](002-05-cerrar-pendiente.md).

Los cuatro escenarios anteriores afirman que algo quedó escrito. Este afirma lo contrario, y por eso es el más difícil de sostener: **lo que no ocurrió no deja rastro que mirar**. Hay que buscarlo donde podría haber aparecido.

Tres cosas en un mismo turno, porque las tres son la misma pregunta: qué hace el agente con lo que el autor dice pero que no es un hecho de su día.

## Estado inicial

El que dejó [`003-04-un-hecho-con-consecuencia`](003-04-un-hecho-con-consecuencia.md): un pendiente abierto en la tabla.

```bash
cp -r ../../003-04-un-hecho-con-consecuencia/lo-que-queda-por-hacer-se/mi-vault .
```

Que haya un pendiente abierto no es decorado. Es lo que hace verificable que no se cierre solo: sobre una tabla vacía, "no se cerró nada" se cumpliría sin que el agente hiciera nada bien.

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

Y el registro de las 12:05 no lleva ninguna marca de la ontología cerrada, porque ordenar los cables no dejó nada abierto ni cerró nada
Y la palabra "recuérdame" no aparece en `AHORA.md`
Y `PENDIENTES.md` queda igual que antes: ni una fila nueva, ni una que desaparezca
Y el pendiente que ya estaba abierto sigue abierto

Las tres frases van juntas a propósito. Por separado, un agente que no escribe nada pasaría los últimos dos casos sin mérito; mezcladas con una que sí produce un registro, se ve si distingue.

## Qué se afirma sobre lo que no pasó

- **"Recuérdame" va dirigido al agente, no es parte del día.** El `AGENTS.md` del vault lo dice en una línea. Lo que se registra es el hecho, no la conversación.
- **Una pregunta no escribe.** Es la última fila de la tabla de despacho: pregunta o delibera, ningún comando.
- **Un hecho que nunca estuvo pendiente no es un cierre.** Marcarlo `~~(Hecho)~~` haría que el sistema mienta sobre el pasado: diría que se cerró algo que nadie había abierto.

## Qué hace fallar y qué solo se reporta

**Falla:** más de un comando, un pendiente nuevo, un cierre, cualquier marca cerrada en el registro, o que la instrucción del autor quede escrita como si fuera un hecho.

**Se reporta:** la clasificación, y qué responde a la pregunta. Que la responda bien es deseable y no es lo que este escenario mide.

## Qué se mira a mano

`turno-1.md`, sobre todo la respuesta a la pregunta. Si la contestó mirando `PENDIENTES.md`, bien. Si la contestó de memoria a partir de la conversación, el vault le dio igual y eso se va a notar en el epic 004.

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k "003_01 or 003_02 or 003_03 or 003_04 or 003_05" -m "not red and not pendiente"
```
