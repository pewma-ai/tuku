# Escenario · 002-010-dictado-del-dia-uno

> Corpus, no diseño: esto es un caso a favor del que se prueba el sistema, referencia `spec/`
> pero no lo reemplaza. Si el resultado contradice `spec/`, se corrige `spec/`, no este archivo
> (ver `devel/epics.md`, "los epics mueven el diseño").

**Cubre:** epic 002, fase 1, la parte con LLM. Es el único escenario del epic que gasta tokens, y el dueño del fixture que los otros nueve consumen.

## Por qué va al final y no al principio

En la narración del día uno, el dictado ocurre primero: el autor habla y de ahí sale todo lo demás. En la cadena de pruebas va último, y es a propósito. Si el primer paso dependiera de una respuesta de agente, los nueve pasos deterministas colgarían de ella y dejarían de ser reproducibles.

Así que se invierte: la salida del agente se **congela** en `fixtures/002-010-dictado-del-dia-uno/entradas.md`, la cadena determinista consume ese texto, y este escenario verifica aparte que el agente vivo lo reproduce. Es la traducción a suite de "el LLM aparece en los dos extremos y el medio es determinista".

Congelar acá está sancionado por [`README.md`](README.md): una respuesta de agente no tiene original vivo en el repositorio contra el cual compararse, y esa es exactamente la condición que justifica un fixture.

## Estado inicial

Dos, y no uno:

- Para la verificación del agente, el fixture `vacio`, igual que [`002-001`](002-001-entrada-en-su-dia.md). El agente tiene que trabajar sobre el mismo vault que tenía el autor cuando dictó.
- Para la revisión a mano, el estado final que dejó [`002-009`](002-009-propuesta-no-escribe.md), que es el día uno completo.

## El fixture

```text
fixtures/002-010-dictado-del-dia-uno/
  dictado.md     # lo que el autor dijo, en lenguaje natural
  entradas.md    # las líneas de bitácora que produjo, congeladas
```

`dictado.md` sale de [`../../corpus/referencia/referencia-faena.md`](../../corpus/referencia/referencia-faena.md), martes 11 de agosto, adaptado a lo que un vault del día uno puede recibir: solo el ámbito `personal` existe al empezar, así que el dictado se queda en lo personal y en lo que obliga a crear el ámbito nuevo.

## Escenario: el dictado produce las entradas congeladas

Dado un vault recién instalado con `--desde 2026-08-11`
Y el dictado completo del martes 11
Cuando el agente lo procesa siguiendo los cinco pasos del flujo
Entonces cada línea que produce coincide con `entradas.md` en su **ontología cerrada**: la marca, su posición y el ámbito
Y las consecuencias son las mismas que dejó la cadena determinista: los mismos pendientes, con el mismo cuerpo, en los mismos callouts

La clasificación abierta se mide aparte y no bloquea, porque es vocabulario del autor y no del sistema (criterio de salida de la fase 1).

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

Cerrar el pendiente equivocado no tiene forma de deshacerse sola ([`../../spec/agente.md`](../../spec/agente.md)).

## Cómo se corre

**Fuera de la corrida por defecto.** Es el único escenario que consume tokens, así que se pide explícitamente:

```bash
uv run pytest tests/escenarios/ -k 002_010
```

Cómo se aísla el arnés para no gastar tokens por accidente es la decisión 3 de las que `epics.md` pone antes de empezar el epic, y hay que resolverla antes de escribir este test.

## Qué se mira a mano

Casi todo este escenario, y no es un defecto del test: es lo que `README.md` dice que hay que escribir acá en vez de fingir que un `assert` lo cubre.

- **La redacción, contra el libro de estilo.** Registro neutro, sin voseo, sin fórmulas de encabezado, pasado y primera persona para los hechos, presente para las observaciones vigentes.
- **Que cada entrada se sostenga sola.** Deícticos resueltos, personas con su rol la primera vez, tiempo relativo convertido en fecha. La prueba es leerla dentro de tres años.
- **El desglose.** Comparar el dictado con las entradas y ver si el corte en hechos fue el que haría una persona, o si el agente cortó por frase.
- **Cuánto se desvió de `entradas.md`** y en qué. Una diferencia de redacción es información sobre la spec; una diferencia de consecuencia es un defecto.
