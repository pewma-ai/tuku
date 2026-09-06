# Escenario · 002-003-abrir-pendiente

> Corpus, no diseño: esto es un caso a favor del que se prueba el sistema, referencia `spec/`
> pero no lo reemplaza. Si el resultado contradice `spec/`, se corrige `spec/`, no este archivo
> (ver `devel/epics.md`, "los epics mueven el diseño").

**Cubre:** epic 002, fase 2. Punto 2 del epic, primera mitad: una entrada `**pendiente**` abre el pendiente sin que el autor toque `PENDIENTES.md`.

## Estado inicial

El que dejó [`002-002-lint-de-entrada`](002-002-lint-de-entrada.md).

## Escenario: la entrada abre el pendiente y copia el cuerpo literal

Dado el estado anterior, con los cinco callouts de horizonte vacíos
Cuando se inyecta `- 14:20 - [[personal]] **pendiente**: avisar de los GGCC a la administradora`
Entonces `^sin-fecha` contiene `- [[personal]] - avisar de los GGCC a la administradora`
Y el cuerpo es el mismo texto en los dos lugares, carácter por carácter
Y el ítem no lleva fecha, porque toda la información temporal vive en el título del callout
Y el diff contra el estado anterior toca `AHORA.md` y `PENDIENTES.md`, y nada más

Abrir es copiar. El janitor no interpreta nada, y por eso este paso no necesita LLM ([`../../spec/agente.md`](../../spec/agente.md)).

## Escenario: los cinco horizontes permanentes siguen existiendo

Dado el mismo estado
Cuando se abre el pendiente
Entonces los otros cuatro callouts de horizonte siguen presentes y vacíos
Y ninguno se borra por estar vacío

Los cinco son permanentes para que la escalera se lea completa ([`../../spec/pendientes.md`](../../spec/pendientes.md)). Los efímeros son los de fecha, y esos entran en [`002-005`](002-005-escribir-en-un-dia-fecha.md).

## Escenario: abrir dos veces no duplica

Dado el pendiente ya abierto
Cuando se corre el janitor otra vez sobre la misma entrada
Entonces el diff es vacío
Y `^sin-fecha` sigue con un solo ítem

## Dónde queda un pendiente escrito en el día de hoy

> [!question] Ambigüedad de `spec/`, no del escenario #REVISAR
> [`../../spec/pendientes.md`](../../spec/pendientes.md) dice las dos cosas. En su ejemplo de arriba, un dictado de hoy a las 09:12 produce un ítem en `^sin-fecha`. Más abajo, "escribir en un día es fecharlo" dice que una entrada `**pendiente**` escrita **en el día de hoy o en uno futuro** abre el pendiente ya con la fecha de ese día. El punto 3 del epic repite "actual o futuro".
>
> Los dos no pueden valer a la vez para la entrada de las 14:20 de hoy. Este escenario afirma `^sin-fecha`, que es lo que dice el ejemplo explícito de la spec y lo que hace que el epic tenga un caso de horizonte además de uno de fecha. El caso sin ambigüedad, escribir en un día futuro, vive entero en [`002-005`](002-005-escribir-en-un-dia-fecha.md).
>
> Si la resolución es la contraria (hoy también fecha), este escenario cambia y `^sin-fecha` se queda sin ninguna vía de entrada en el epic 002, que es la señal de que la ambigüedad importa. Se resuelve en `spec/` antes de implementar el paso.

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 002_003
```

## Qué se mira a mano

- Abrir `PENDIENTES.md` y ver si la escalera se lee completa con un solo ítem en ella.
- Que el autor no haya tenido que abrir `PENDIENTES.md` para nada, que es la mitad del criterio de salida del epic.
