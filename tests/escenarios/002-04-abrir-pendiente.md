# Escenario · 002-04-abrir-pendiente

**Cubre:** epic 002, fase 2. Punto 2 del epic, primera mitad: un registro `**pendiente**` abre el pendiente sin que el autor toque `PENDIENTES.md`.

## Estado inicial

El que dejó [`002-03-lint-de-registro`](002-03-lint-de-registro.md).


## Escenario: el registro abre el pendiente y copia el cuerpo literal

Dado el estado anterior, con los cinco callouts de horizonte vacíos
Cuando se inyecta `- 14:20 - [[personal]] **pendiente**: avisar de los GGCC a la administradora`
Entonces `^sin-fecha` contiene `- [[personal]] - avisar de los GGCC a la administradora`
Y el cuerpo es el mismo texto en los dos lugares, carácter por carácter
Y el ítem no lleva fecha, porque toda la información temporal vive en el título del callout
Y el diff contra el estado anterior toca `AHORA.md` y `PENDIENTES.md`, y nada más

Abrir es copiar: el comando no interpreta, y por eso este paso no necesita LLM ([`spec/agente.md`](../../spec/agente.md)).

## Escenario: los cinco horizontes permanentes siguen existiendo

Dado el mismo estado
Cuando se abre el pendiente
Entonces los otros cuatro callouts de horizonte siguen presentes y vacíos
Y ninguno se borra por estar vacío

Los cinco son permanentes para que la escalera se lea completa ([`spec/pendientes.md`](../../spec/pendientes.md)). Los efímeros son los de fecha, y entran en [`002-05`](002-05-escribir-en-un-dia-fecha.md).

## Escenario: abrir dos veces no duplica

Dado el pendiente ya abierto
Cuando se corre el comando otra vez sobre el mismo registro
Entonces el diff es vacío
Y `^sin-fecha` sigue con un solo ítem

## Dónde queda un pendiente escrito en el día de hoy

En `^sin-fecha`, y ya no es ambiguo: [`spec/pendientes.md`](../../spec/pendientes.md) dice ahora que **el día de hoy no fecha** y que fechar es escribir bajo un día futuro. Escribir bajo hoy es el acto por defecto de registrar, no una decisión de agendar, así que no puede significar "vence hoy". El caso que sí fecha, un día futuro, vive en [`002-05`](002-05-escribir-en-un-dia-fecha.md).

## Cómo se corre

```bash
uv run pytest tests/escenarios/ -k 002_04
```

## Qué se mira a mano

- Si la escalera se lee completa con un solo ítem en ella.
- Que el autor no haya tenido que abrir `PENDIENTES.md`, que es la mitad del criterio de salida del epic.
