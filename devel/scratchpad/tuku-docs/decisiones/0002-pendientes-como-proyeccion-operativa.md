# ADR-0002 — PENDIENTES.md como proyección con rol operativo

- **Fecha:** 2026-08-23
- **Estado:** aceptada

## Contexto

Un pendiente puede modelarse como artefacto con vida propia o como proyección de la bitácora. La primera opción da un archivo con estado propio; la segunda garantiza reconstrucción pero parecía degradar el archivo a vista descartable.

## Decisión

Ambas cosas, separando roles:

- La **bitácora es la fuente de origen**: un pendiente nace y muere por una entrada.
- **`PENDIENTES.md` es la fuente de verdad operativa**: donde se consulta y se trabaja.

Se justifica por rendimiento —no recorrer más de mil archivos para responder *qué falta*— y por inducción —alguien nuevo entiende la situación sin leer el corpus completo—. No se edita a mano.

## Consecuencias

- Es reconstruible: borrarlo y reproyectar debe devolverlo idéntico (criterio de éxito 4, fila 1 del contrato de regeneración).
- El único punto de juicio en la cadena es el emparejamiento semántico entre la intención y su cierre.
