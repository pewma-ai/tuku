# Proceso: alta de entidad

> Ejecutable por un humano con un editor de texto, o por un agente de inteligencia media
> (P2). Formato completo en `spec/entidad.md`.

## Cuándo

Cuando hay algo nuevo que gestionar: un proyecto, un cliente, un proveedor, un área, un
profesional, un instrumento. **No** cuando ya existe una entidad con ese id en
`entidades/` (en ese caso, editar la existente).

## Pasos

1. **Decidir el ámbito.** Ver la jerarquía actual en `entidades/`. Si el ámbito no existe
   aún, crearlo antes: el motor pregunta una vez por ámbito nuevo y nunca más.

2. **Elegir el `id`.** Debe ser:
   - único en todo el perfil,
   - en kebab-case (`colegio-san-marcos`, `dr-perez`),
   - estable: no incluir estado ni fecha (ADR 0001).

3. **Crear el archivo** `entidades/<ambito>/[<nivel>/]<id>.md` con el front matter mínimo:

   ```yaml
   ---
   id: <id>
   type: <string libre, p.ej. cliente>
   lifecycle: vigente
   status: active
   alineamiento: >
     <Qué se busca lograr con esta entidad; una o dos frases.>
   created: <YYYY-MM-DD>
   modified: <YYYY-MM-DD>
   ---
   # <Nombre legible>
   ```

4. **Agregar `descripcion` inferida** si hay contexto suficiente. Es el modelo de operación
   rudimentario que el agente usa para el cierre: cómo funciona, qué lo mueve, qué fricción
   tiene. Si no hay suficiente información, dejarlo en blanco: se infiere con el tiempo.

5. **Declarar cadencias** si las hay. Van en un bloque `<!-- tuku:cadencias ... -->` dentro
   del archivo de entidad (ADR 0013).

6. **Ejecutar `tuku sync`** para que los punteros del motor apunten a la nueva entidad.

## Verificación

- `tuku janitor` pasa sin violaciones N1–N9.
- El `id` no colisiona con ninguna entidad existente (N2).
- El path refleja correctamente la jerarquía (N3/N4).
- `lifecycle: vigente` presente (N6).

## Equivalente manual

Todos los pasos son edición de archivos de texto y un único comando de terminal (`tuku sync`).
El paso 4 (descripción inferida) puede omitirse o redactarse a mano.
