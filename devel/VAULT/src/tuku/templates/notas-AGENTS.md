# Instrucciones de agente — `notas/`

> Se siembra en `notas/AGENTS.md`. Acota el comportamiento del agente para todo lo que
> cuelga de este directorio. Formato completo en `spec/nota.md`.

## Rol

Mantienes el corpus de notas: lo organizas, lo enlazas y lo sintetizas. **No inventas
contenido.** Una nota la escribe el usuario; tú la clasificas, la enlazas y le propones un
`summary`.

## Al crear o modificar una nota

1. **Lee `notas.md` primero.** Es el mapa de lo que ya existe: reutiliza `topic` en uso y
   enlaza a notas existentes antes de proponer conceptos nuevos.
2. **Front matter**: `id`, `type: nota`, `summary` y fechas son obligatorios. `topic` y
   `entidad` son opcionales.
3. **`summary`**: una línea, máximo 10 palabras, que agregue contexto **no implícito en el
   título**. Si la nota es un stub (menos de 10 líneas), va vacío: `summary: ""`.
   - ✅ `[Curva del Dolor]` → `"Métrica de fricción que gatilla la automatización."`
   - ❌ `[Curva del Dolor]` → `"Nota sobre la curva del dolor."` (reformula el título)
4. **`topic`**: string libre, pero **prefiere un valor ya en uso**. Propón uno nuevo solo si
   ninguno encaja, y dilo explícitamente.
5. **`entidad`**: un solo `id` de entidad, o ausente si la nota es transversal. Una nota que
   sirve a tres entidades no declara ninguna.

## Enlaces

- Markdown estándar `[texto](ruta.md)`. **Nunca wikilinks `[[…]]`** fuera de bloques de
  código.
- En notas de más de 10 líneas, cierra con `----` y `## Ver Además`: hasta 5 enlaces, cada
  uno con su razón, en la forma `— para <verbo> <razón>`.
- La razón responde *"¿por qué haría clic el lector de esta nota?"*. Describe el viaje, no
  el destino.
  - ✅ `— para entender la arquitectura base.`
  - ❌ `— paradigma operativo del procesador.`

## Límites

| Nivel | Regla |
|---|---|
| **Siempre** | Leer `notas.md` antes de crear o enlazar |
| **Siempre** | Regenerar el índice tras crear o modificar una nota |
| **Preguntar** | Renombrar o consolidar notas: rompe enlaces entrantes |
| **Preguntar** | Crear un stub para un concepto que aún no existe |
| **Nunca** | Editar la zona derivada de `notas.md` a mano |
| **Nunca** | Borrar una nota sin confirmación explícita |
| **Nunca** | Presionar para completar un stub. Un stub vacío es información válida |
