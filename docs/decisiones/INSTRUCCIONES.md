# Cómo se escribe un ADR

> `docs/decisiones/INSTRUCCIONES.md` · Qué es una decisión de arquitectura, cuándo merece
> registrarse y con qué forma. El índice de las decisiones tomadas está en
> [`README.md`](README.md).

---

## Qué es un ADR

Un *Architecture Decision Record* es el registro de una decisión que **cerró una alternativa
que era viable**. No documenta cómo funciona el sistema —eso es [`../arquitectura.md`](../arquitectura.md)
y [`../../spec/`](../../spec/)— sino por qué funciona así y no de la otra forma que también
habría servido.

Su utilidad aparece más tarde: cuando alguien —el autor dentro de dos años, un contribuyente
nuevo, un agente— se pregunta si una restricción del diseño sigue teniendo sentido. Sin ADR,
la única forma de responder es reconstruir el razonamiento desde cero, y lo más probable es
que se reconstruya mal.

## Cuándo se escribe

Cuando la decisión cierra una alternativa defendible. No se escribe para registrar lo obvio,
ni lo que ya está en el [brief](../brief.md), ni una preferencia sin alternativa perdida.

La prueba: si dentro de dos años alguien puede preguntar razonablemente *"¿y por qué no se
hizo de la otra forma?"*, hace falta un ADR. Si la otra forma nunca fue defendible, no.

Un caso particular que sí lo merece: cuando una decisión **se deriva del brief pero no es
evidente** que se derive. El brief afirma que los datos sobreviven al motor; que de ahí se
siga un `schema_version` en el perfil y migraciones acumulativas es una cadena de varios
pasos, y esa cadena es lo que registra el ADR 0003.

Si una decisión **no** puede derivarse de lo que afirma el brief, entonces o el brief está
incompleto o la decisión está equivocada. Ambos casos merecen un ADR, y el primero además
una corrección del brief.

## Formato

Numeración correlativa de cuatro dígitos, nombre en kebab-case, y cuatro secciones:

| Sección | Contiene |
|---|---|
| **Contexto** | Las fuerzas en juego y la alternativa viable, expuesta con su mejor argumento |
| **Decisión** | Qué se decide, en presente y en afirmativo |
| **Consecuencias** | Lo que se gana y —sobre todo— lo que se acepta perder |
| **Estado** | Ver abajo |

### La alternativa se expone a favor

Un ADR que presenta la opción descartada como un espantapájaros no sirve para revisar la
decisión más tarde: si la alternativa parecía absurda, nadie entiende por qué hizo falta
decidir. Hay que dejar claro qué la hacía tentadora, y solo después por qué perdió.

### Las consecuencias incluyen el costo

La sección de consecuencias vale sobre todo por lo que declara **en contra**. Una decisión
sin costo declarado no fue una decisión: fue una preferencia. Nombrar lo que se pierde es lo
que permite, más adelante, detectar que el costo creció y que toca reabrir.

## Estados

| Estado | Significado |
|---|---|
| `propuesto` | Escrito, aún no adoptado |
| `aceptado` | Vigente. Las specs y el código se le ajustan |
| `superado por NNNN` | Reemplazado. El archivo **permanece** |

**Un ADR nunca se borra ni se reescribe.** Si la decisión cambia, se escribe uno nuevo que
declara superado al anterior y se edita el estado del viejo — nada más. El historial de lo
que se pensó es parte de la documentación: un ADR superado explica por qué se intentó lo que
se intentó, y evita que la misma alternativa se reintente sin saber que ya se probó.

## Lo que no va aquí

**Las decisiones abiertas.** Viven en la sección *Decisiones abiertas* del documento que les
corresponde —[`../arquitectura.md`](../arquitectura.md) §10 y el cierre de cada archivo de
`spec/`— o como issues. Este directorio es historial de lo cerrado, no lista de pendientes.

Cuando una de esas decisiones abiertas se cierra, y solo si cerró una alternativa viable, se
convierte en un ADR y se retira de la lista de abiertas.
