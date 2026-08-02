# ADR 0014 — Las tareas usan formato posicional con metadatos del motor en comentario

## Contexto

Las tareas son el objeto más escrito del sistema: el usuario las crea a mano, el agente las
emite por cadencia o proceso, el motor las actualiza en cada ciclo. Su formato define la
ergonomía de uso y la complejidad del parser.

Dos opciones principales:

**Formato de tabla Markdown**: columnas fijas, legible en Obsidian, fácil de ordenar
visualmente. Su costo es que los diffs son ruidosos por realineación, la edición a mano es
incómoda y los campos del motor contaminarían columnas que el usuario no necesita ver.

**Formato posicional en una línea**: campos fijos al inicio, texto libre al final. Difícil
de leer en el canónico, pero el canónico no está pensado para ser leído — la comodidad
vive en las proyecciones.

## Decisión

Las tareas usan **formato posicional** en la línea, con los campos del motor en un
**comentario HTML indentado** en la línea siguiente:

```
- [estado] <created> <effort> <entity|-> <deadline|-> <followup|-> <blockuntil|-> <originator> <texto> ^t-id
            <!-- tuku: cycles=… process=… outcome=… completed=… deps=… blocks=… -->
```

Los campos del usuario son posicionales y fijos: el parser los lee sin ambigüedad contando
posiciones. Los campos del motor —`cycles`, `outcome`, `completed`, `deps`, `blocks`,
`process`, `step`— van en el comentario en formato `clave=valor`, siempre en una sola línea,
para que sean tan grepeables como un campo posicional.

Un campo opcional vacío lleva `-` como placeholder, no se omite: omitir obliga al parser a
adivinar cuál campo falta contando desde el final.

## Consecuencias

**A favor.**

- El parser es trivial: posiciones fijas, sin ambigüedad.
- El esquema de campos del motor es abierto: agregar `outcome=` o `process=` a las tareas
  que lo necesitan no requiere migrar las demás. Los campos posicionales del usuario son
  estables; los del motor crecen sin romper nada.
- El diff de Git distingue sin ambigüedad qué tocó el usuario (la línea) y qué tocó el motor
  (el comentario).
- El comentario es invisible en Obsidian: la lista se lee limpia aunque cada tarea lleve
  trazabilidad completa.

**En contra, y aceptado.**

- El archivo canónico (`tareas/tareas.md`) es incómodo de leer directamente. Esta es una
  consecuencia deliberada de la separación canónico/vista: la comodidad de lectura está en
  las proyecciones.
- Los enlaces a entidades son `id` planos, no enlaces Markdown clicables. Navegar desde el
  canónico requiere buscar por `id`; navegar desde una proyección usa el enlace enriquecido.
- El placeholder `-` en campos opcionales vacíos añade ruido visual en las líneas más cortas.

## Estado

`aceptado`
