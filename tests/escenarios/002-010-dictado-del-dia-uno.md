# Escenario · 002-010-dictado-del-dia-uno

**Cubre:** epic 002, fase 1, la parte con LLM. Único escenario del epic que gasta tokens, y dueño de `entradas.md`, el fixture que los otros nueve consumen.

## Por qué va al final y no al principio

En la narración del día uno el dictado ocurre primero. En la cadena va último: si el primer paso dependiera de una respuesta de agente, los nueve deterministas colgarían de ella y dejarían de ser reproducibles.

Así que se invierte. La salida del agente se congela en `entradas.md`, la cadena determinista consume ese texto, y este escenario verifica aparte que el agente vivo lo reproduce. El LLM queda en los dos extremos y el medio es determinista.

## Estado inicial

Dos, y no uno:

- Para la verificación del agente, el fixture `vacio`, igual que [`002-001`](002-001-entrada-en-su-dia.md): tiene que trabajar sobre el mismo vault que tenía el autor al dictar.
- Para la revisión a mano, el estado final que dejó [`002-009`](002-009-propuesta-no-escribe.md), que es el día uno completo.

## El fixture

```text
fixtures/002-010-dictado-del-dia-uno/
  dictado.md     # lo que el autor dijo, generado desde el corpus
  entradas.md    # las líneas de bitácora que produjo, congeladas
```

`dictado.md` lo **genera** un agente desde [`referencia-faena.md`](../../corpus/referencia/referencia-faena.md), martes 11 de agosto, adaptado a lo que un vault del día uno recibe: solo existe el ámbito `personal`. Es regenerable, en versión mínima o con ruido.

`entradas.md` se congela: es salida de agente y no tiene original vivo contra el cual compararse.

## Escenario: el dictado produce las entradas congeladas

Dado un vault recién instalado con `--desde 2026-08-11`
Y el dictado completo del martes 11
Cuando el agente lo procesa siguiendo los cinco pasos del flujo
Entonces cada línea que produce coincide con `entradas.md` en su **ontología cerrada**: la marca, su posición y el ámbito
Y las consecuencias son las mismas que dejó la cadena determinista: los mismos pendientes, con el mismo cuerpo, en los mismos callouts

La clasificación abierta se mide aparte y no bloquea: es vocabulario del autor, no del sistema.

## Escenario: la instrucción no se registra

Dado el dictado, que incluye *"recuérdame avisar de los GGCC a la administradora"*
Cuando el agente redacta
Entonces la entrada dice `**pendiente**: avisar de los GGCC a la administradora`
Y la palabra "recuérdame" no aparece en ninguna parte de `AHORA.md`

Iba dirigida a quien lleva la bitácora. Desaparece.

## Escenario: una frase con varios hechos produce varias entradas

Dado el dictado, que en una sola frase cierra un pendiente propio y reporta la respuesta de un tercero
Cuando el agente redacta
Entonces salen dos entradas y no una
Y una lleva `~~(Hecho)~~` y la otra no

La unidad es el hecho y no la frase.

## Escenario: no se agrega lo que no se dijo

Dado el dictado completo
Cuando el agente termina
Entonces no hay ningún pendiente abierto que el dictado no haya pedido
Y lo que el hecho sugiere quedó como propuesta, tal como afirma [`002-009`](002-009-propuesta-no-escribe.md)

## Escenario: el cierre no literal se confirma antes de cerrar

Dado un dictado que da por hecha una tarea sin repetir su texto palabra por palabra
Cuando el agente lo procesa
Entonces no cierra ningún pendiente por su cuenta
Y pregunta al autor a cuál corresponde

Cerrar el pendiente equivocado no se deshace solo ([`spec/agente.md`](../../spec/agente.md)).

## Cómo se corre

**Fuera de la corrida por defecto**, porque consume tokens. Se pide explícito:

```bash
uv run pytest tests/escenarios/ -k 002_010
```

Cómo se aísla el arnés es la decisión 3 de `epics.md`, y hay que resolverla antes de escribir este test.

## Qué se mira a mano

Casi todo este escenario, por diseño y no por defecto del test.

- **La redacción, contra el libro de estilo.** Registro neutro, sin voseo, sin fórmulas de encabezado, pasado y primera persona para los hechos, presente para las observaciones vigentes.
- **Que cada entrada se sostenga sola.** Deícticos resueltos, personas con su rol la primera vez, tiempo relativo convertido en fecha. La prueba es leerla en tres años.
- **El desglose.** Si el corte en hechos fue el que haría una persona, o el agente cortó por frase.
- **Cuánto se desvió de `entradas.md`** y en qué. Una diferencia de redacción es información sobre la spec; una diferencia de consecuencia es un defecto.
