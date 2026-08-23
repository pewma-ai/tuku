# ADR 0011 — Un proceso no agrega primitiva de almacenamiento

## Contexto

Hay objetos de trabajo que no son ni tarea ni entidad: una cotización, un proceso de
contratación, la resolución de un cambio de configuración. Tienen estados propios, pasos
conocidos, iteraciones esperadas y un resultado. Tres opciones eran posibles:

**Opción A.** Entidad efímera: cada instancia es un archivo en el árbol, con `lifecycle` y
bitácora propia. Es coherente con el modelo existente y tiene la ventaja de que todos los
mecanismos de entidad —cadencias, proyecciones, archivo— funcionan sin cambios.

**Opción B.** Tarea con estados adicionales: extender `outcome` para cubrir los estados
internos del proceso. Es la opción más barata de implementar.

**Opción C.** Sin primitiva nueva: el proceso es una plantilla que instancia un grupo de
tareas relacionadas; su estado se deduce de qué tareas del grupo siguen abiertas.

## Decisión

**Un proceso no agrega primitiva de almacenamiento.** Una instancia de proceso es un grupo
de tareas con un identificador de instancia compartido (`process=cot-0042` en el comentario
de cada tarea). Su estado es qué tareas del grupo siguen abiertas; su resultado es el
`outcome` del paso que lo cierra.

Todo el almacenamiento está en `tareas/tareas.md`. El proceso agrega solo dos campos al
comentario de tarea —`process` y `step`— y una plantilla en Markdown que describe los pasos.

## Consecuencias

**A favor.**

- El proceso se vuelve medible sin instrumentación adicional: el número de veces que se emite
  un paso `repeatable` es la métrica de fricción del proceso, y sale del mismo registro.
- No hay nuevo tipo de archivo que el motor tenga que gestionar, versionar o migrar.
- El principio de que una instancia sin tarea alguna abierta es una instancia terminada es
  trivial de implementar y de entender.

**En contra, y aceptado.**

- El "estado" de una instancia requiere una consulta —sumar las tareas abiertas del grupo—
  en vez de leer un campo. Es una operación de RADAR, no de front matter.
- La Opción A habría dado a cada cotización su propia bitácora y cadencias propias, lo que
  podría ser útil en procesos de muy larga duración. Se acepta perder eso a cambio de no
  multiplicar las entidades efímeras en el árbol.
- Las instancias de proceso en curso no son visibles de un vistazo en el árbol de archivos,
  solo a través de una consulta o proyección.

## Estado

`aceptado`
