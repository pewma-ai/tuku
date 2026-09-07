# Escenario · 002-003-abrir-pendiente

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

Abrir es copiar: el janitor no interpreta, y por eso este paso no necesita LLM ([`spec/agente.md`](../../spec/agente.md)).

## Escenario: los cinco horizontes permanentes siguen existiendo

Dado el mismo estado
Cuando se abre el pendiente
Entonces los otros cuatro callouts de horizonte siguen presentes y vacíos
Y ninguno se borra por estar vacío

Los cinco son permanentes para que la escalera se lea completa ([`spec/pendientes.md`](../../spec/pendientes.md)). Los efímeros son los de fecha, y entran en [`002-005`](002-005-escribir-en-un-dia-fecha.md).

## Escenario: abrir dos veces no duplica

Dado el pendiente ya abierto
Cuando se corre el janitor otra vez sobre la misma entrada
Entonces el diff es vacío
Y `^sin-fecha` sigue con un solo ítem

## Dónde queda un pendiente escrito en el día de hoy

> [!question] Ambigüedad de `spec/`, no del escenario #REVISAR
> [`spec/pendientes.md`](../../spec/pendientes.md) dice las dos cosas: su ejemplo manda un dictado de hoy a `^sin-fecha`, y su regla "escribir en un día es fecharlo" cubre **hoy o un día futuro**. El punto 3 del epic repite "actual o futuro". No pueden valer las dos para la entrada de las 14:20.
>
> Este escenario afirma `^sin-fecha`, que es el ejemplo explícito. Si se resuelve al revés, `^sin-fecha` se queda sin vía de entrada en todo el epic 002, y esa es la señal de que la ambigüedad importa. Se resuelve en `spec/` antes de implementar el paso. El caso sin ambigüedad, un día futuro, vive en [`002-005`](002-005-escribir-en-un-dia-fecha.md).

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 002_003
```

## Qué se mira a mano

- Si la escalera se lee completa con un solo ítem en ella.
- Que el autor no haya tenido que abrir `PENDIENTES.md`, que es la mitad del criterio de salida del epic.
