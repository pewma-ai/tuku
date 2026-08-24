# Proceso: alta de nota

> Ejecutable por un humano con un editor de texto, o por un agente de inteligencia media
> (P2). Formato completo en `spec/nota.md`.

## Cuándo

Cuando hay algo que sedimentar: una idea que vuelve, una conclusión a la que se llegó, un
concepto que hace falta nombrar para poder enlazarlo. **No** cuando es un hecho fechado (eso
es una entrada) ni cuando es algo por hacer (eso es una tarea).

## Pasos

1. **Revisar el índice.** Abrir `notas/notas.md` y buscar si el concepto ya existe. Si
   existe, la operación es editar, no crear.
2. **Elegir `topic`.** Tomar uno de los que ya aparecen como encabezado en el índice. Crear
   uno nuevo solo si ninguno encaja.
3. **Crear el archivo** `notas/<id>.md` con el front matter mínimo:

   ```yaml
   ---
   id: <kebab-case>
   type: nota
   topic: <topic>
   summary: ""
   created: <YYYY-MM-DD>
   modified: <YYYY-MM-DD>
   ---
   # <Título>
   ```

4. **Escribir el cuerpo.** Sin estructura obligatoria.
5. **Declarar `entidad`** si la nota pertenece claramente a una, con su `id`. Si sirve a
   varias, omitir el campo: es transversal.
6. **Escribir el `summary`** si la nota supera las 10 líneas: máximo 10 palabras, y que
   agregue lo que el título no dice. Si es un stub, dejarlo vacío.
7. **Agregar `## Ver Además`** si supera las 10 líneas: `----`, el encabezado, y hasta 5
   enlaces en la forma `* [Título](ruta.md) — para <verbo> <razón>`.
8. **Regenerar el índice**: `tuku janitor` (o `tuku build notas`).

## Verificación

- El índice muestra la nota bajo su `topic`, con su `summary` y su fecha.
- Los enlaces de `## Ver Además` resuelven (O4).
- No hay wikilinks `[[…]]` (O5).

## Equivalente manual

Todos los pasos salvo el 8 son edición de texto. El 8 se puede omitir: el índice quedará
desactualizado hasta la próxima corrida del janitor, y eso no rompe nada — es derivado.
