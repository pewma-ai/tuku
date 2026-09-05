# spec · notas

> `notas/` es un zettelkasten de formato libre. Se justifica por el principio 6 de [`../docs/principios.md`](../docs/principios.md) (la deliberación como eje) y, para las notas sobre personas, por el principio 8.

Una nota vale mientras la idea conserve sentido y no pertenece a un momento.

## Notas tipadas

Algunas notas no son libres: son sobre algo que se repite en la bitácora y que merece página propia. Una persona, un cliente, un sistema, una reunión recurrente.

**"Persona" no es una entidad del diseño.** Serlo la volvería un caso especial, y en cuanto apareciera el segundo concepto inferido habría que abrir otro. El concepto general es la **nota tipada**: una nota que declara `tipo:` en su frontmatter y que por eso tiene plantilla y procedimiento de destilado.

La lista de tipos es **abierta**, igual que las clasificaciones y los horizontes (ver [`bitacora.md`](bitacora.md)). Vive en `LIBRO-DE-ESTILO.md` bajo `### Tipos de nota` y crece cuando el uso revela uno nuevo. Cada tipo tiene su archivo en `reglas/tipos/`.

## El destilado no depende del tipo

Lo que cambia entre tipos es la plantilla y qué se infiere. El procedimiento es el mismo:

1. Algo se repite en la bitácora lo suficiente como para merecer página.
2. Se propone al autor, que aprueba.
3. Se barre el histórico buscando todas las menciones.
4. Se sintetiza: los hechos primero, las inferencias después y marcadas como tales.
5. Se escribe la nota con la plantilla del tipo.
6. Se indexa y las menciones sueltas se convierten en enlaces.

El paso 3 es caro y conviene aislarlo: barrer meses de bitácoras no cabe dentro de una conversación. Se ejecuta en **contexto aislado**, vía `jntr.nota-destilar`.

## Lo que declara un tipo

| Campo | Qué define |
| --- | --- |
| Plantilla | Qué secciones tiene la nota |
| Qué barrer | Dónde buscar menciones |
| Qué inferir | Qué se sintetiza y qué se deja como hecho crudo |
| Cómo enlazar | Cómo se nombra el archivo y cómo se referencia |

## "Ver además"

Toda nota cierra con una sección `## Ver además`: la lista de sus enlaces salientes, cada uno con el motivo de por qué conecta, no solo el destino.

```markdown
## Ver además

* [Nota relacionada](nota-relacionada.md) — para qué sirve esa conexión, en una frase.
```

Sin el motivo, el enlace es un dato; con él, es una decisión que alguien más puede evaluar sin abrir la otra nota. Dos niveles de exigencia, y son de naturaleza distinta:

- **Que la sección exista y que cada enlace lleve motivo** es verificable sin juicio → `jntr.notas-lint`.
- **Que el motivo sea pertinente y no relleno** solo lo evalúa quien lee → agente, juicio semántico.

## Inferir sobre terceros

El tipo `persona` carga una regla que los demás no necesitan: **la nota describe a alguien que puede leerla.**

El libro de estilo ya exige que las observaciones sobre el autor se redacten como descripción y nunca como norma. Sobre un tercero eso vale más, y se suma otra: se infiere lo que sirve para trabajar mejor con esa persona, no lo que sirve para juzgarla.

La prueba es simple: **una inferencia que no se le podría mostrar a la persona no va escrita.** Verificarlo no es mecánico: lo hace el agente al redactar, con juicio ético, no un janitor.

## No entra

- **Destilar el histórico y proponer notas nuevas por iniciativa propia**, sin que el uso ya lo haya sugerido. Eso es inferencia semántica, una fase posterior de implementación (ver [`../devel/que_implementar.md`](../devel/que_implementar.md)). Acá solo la mecánica del tejido: crear, tipar, enlazar, indexar.
