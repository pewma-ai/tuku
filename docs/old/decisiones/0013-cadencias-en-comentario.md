# ADR 0013 — Las cadencias viven en comentario HTML dentro del archivo de entidad

## Contexto

Las cadencias asociadas a una entidad o a un tipo de entidad necesitan un lugar físico en el
repositorio. Dos opciones naturales:

**Archivos YAML separados**: `entidades/trabajo/jefatura.cadencias.yaml` o un directorio
`cadencias/` con un archivo por entidad. Es la forma convencional de separar configuración
de contenido.

**Dentro del archivo de la entidad**, en un bloque cercado. Mantiene todo lo relativo a la
entidad en un solo lugar y aprovecha la regla ya establecida de que borrar la entidad borra
sus cadencias.

## Decisión

**Las cadencias viven dentro del archivo de la entidad, en un comentario HTML canónico**:

```
<!-- tuku:cadencias
- id: cad-uno-a-uno
  ...
-->
```

El comentario es la fuente canónica. Lo que el usuario lee —en lenguaje natural— es una zona
`tuku:derived` generada a partir del comentario, igual que cualquier otra proyección del
sistema.

Esta disposición invierte la relación habitual: en el resto del sistema, el comentario
guarda metadata *sobre* algo visible; aquí el comentario guarda **la fuente** y lo visible
es la proyección. La regla es la misma —fuente en el lugar canónico, proyección como
derivada— aplicada al revés.

## Consecuencias

**A favor.**

- Borrar la entidad o el tipo borra sus cadencias en el mismo commit, sin lógica de
  limpieza adicional.
- Un tipo de entidad (`tipos/negocio/cliente.md`) es autocontenido: plantilla + cadencias en
  un solo archivo, compartible entre perfiles sin dependencias.
- No hay una carpeta `cadencias/` separada que mantener sincronizada con el árbol de
  entidades.

**En contra, y aceptado.**

- El comentario HTML es invisible en Obsidian y en cualquier renderizador: el usuario que
  quiera editar la cadencia tiene que saber que existe y dónde está. El agente es quien
  normalmente la escribe y la modifica.
- Hay riesgo de que quien lea el archivo edite la zona visible (la proyección en lenguaje
  natural) creyendo que es la fuente. La `INSTRUCCIONES.md` de la spec y el marcado
  `tuku:derived` con hash mitigan esto, pero no lo eliminan.
- Las cadencias no son visibles en un grep simple sobre el árbol; requieren parsear el
  comentario. El colector de cadencias lo hace antes de cada evaluación.

## Estado

`aceptado`
