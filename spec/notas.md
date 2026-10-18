# spec · notas

> `notas/` es un zettelkasten de formato libre. Se justifica por el principio 6 de [`../docs/principios.md`](../docs/principios.md) (la deliberación como eje) y, para las notas sobre personas, por el principio 8.

Una nota vale mientras la idea conserve sentido y no pertenece a un momento.

## Notas tipadas

Algunas notas no son libres: son sobre algo que se repite en la bitácora y que merece página propia. Una persona, un cliente, un sistema, una reunión recurrente.

**`subtype` no es `type`.** Toda nota lleva `type: Note`, el campo OKF de lista cerrada que [`vault.md`](vault.md) exige en cualquier archivo que guarde conocimiento. `subtype` es lo que subdivide ese `Note`: de lista abierta, en minúscula, y solo lo declaran las notas tipadas. Conviven en el mismo frontmatter y ninguno reemplaza al otro. Va en inglés como todos los nombres de campo, que son superficie de máquina.

**"Persona" no es una entidad del diseño.** Serlo la volvería un caso especial, y en cuanto apareciera el segundo concepto inferido habría que abrir otro. El concepto general es la **nota tipada**: una nota que declara `subtype` en su frontmatter y que por eso tiene plantilla y procedimiento de destilado.

La lista de tipos es **abierta**, igual que las clasificaciones y los horizontes (ver [`bitacora.md`](bitacora.md)). Vive en `LIBRO-DE-ESTILO.md` bajo `### Tipos de nota` y crece cuando el uso revela uno nuevo. Cada tipo tiene su archivo en `reglas/subtipos/` (`persona.tuku.md`), con lo que declara abajo; la tabla del libro es la única fuente del resto, entre ello si es enlazable. `tuku note create --subtype persona` escribe el campo y rechaza un tipo que la tabla no lista, con la lista de los que sí: agregar un tipo es agregar una fila.

## El destilado no depende del tipo

Lo que cambia entre tipos es la plantilla y qué se infiere. El procedimiento es el mismo:

1. Algo se repite en la bitácora lo suficiente como para merecer página.
2. Se propone al autor, que aprueba.
3. Se barre el histórico buscando todas las menciones.
4. Se sintetiza: los hechos primero, las inferencias después y marcadas como tales.
5. Se escribe la nota con la plantilla del tipo.
6. Se indexa y las menciones sueltas se convierten en enlaces.

El paso 3 es caro y conviene aislarlo: barrer meses de bitácoras no cabe dentro de una conversación. Se ejecuta en **contexto aislado**, vía `tuku note distill`, que todavía no existe.

## Lo que declara un tipo

| Campo | Qué define |
| --- | --- |
| Plantilla | Qué secciones tiene la nota |
| Qué barrer | Dónde buscar menciones |
| Qué inferir | Qué se sintetiza y qué se deja como hecho crudo |
| Cómo enlazar | Cómo se nombra el archivo y cómo se referencia |
| Enlazable | Si `tuku context` ofrece sus notas al agente para enlazarlas al registrar (ver abajo). Es la columna de la tabla del libro, no una línea del archivo |

Los tipos y su columna "Enlazable" están en `### Tipos de nota` del libro de estilo: `persona` es enlazable, `idea` no. Se decide por tipo y no nota por nota, para que ninguna quede olvidada.

## Enlazar notas

Una nota se nombra por su título y por los otros nombres que declara en `aliases`, una lista YAML del frontmatter:

```yaml
---
type: Note
subtype: persona
aliases: [Rodolfo, don Rodolfo]
---
```

`aliases` es el campo que Obsidian usa para lo mismo, así que el editor de referencia lo entiende sin configurar nada. `tuku` lo lee con su propio lector de frontmatter, como `type` y `subtype`.

Enlazar una nota al registrar lo decide el agente, con `tuku context note` de referencia. Por cada tipo enlazable trae las últimas notas, de la modificada más recientemente a la más antigua, cada una con su título y sus `aliases`. El tope por tipo es `context_note_limit` de `reglas/config.tuku.md` (25 por defecto), para que el listado no crezca con el vault. Si lo que dijo el autor nombra a una de ellas, el agente escribe la primera mención como link en el `--body` de `entry create`, `todo open` o `note create`: "llamé a don Rodolfo por la cotización" queda como `llamé a [don Rodolfo](notas/rodolfo-cifuentes.md) por la cotización`. El texto del link es el que dijo el autor. Si el nombre calza con dos notas, es una ambigüedad y el agente pregunta antes de escribir ([flujo-informacion.md](flujo-informacion.md)). Una nota que `context` no trae no se enlaza: el comando no busca por su cuenta.

Los comandos no enlazan solos. Escriben el cuerpo como llega, y lo ya escrito no se toca: enlazar hacia atrás es una operación deliberada ([markdown.md](markdown.md), "Enlazar es deliberado"). Los ámbitos no se enlazan en el cuerpo: los pone `--scope`.

`aliases` y `keywords` son cosas distintas. `aliases` son otros nombres de la misma nota, y el agente los lee en `context` para enlazarla. Las `keywords` de un ámbito son palabras que lo delatan sin nombrarlo, y sirven para elegir el `--scope` ([ambitos.md](ambitos.md)).

## "Ver además"

Toda nota cierra con una sección `## Ver además`: la lista de sus enlaces salientes, cada uno con el motivo de por qué conecta, no solo el destino.

```markdown
## Ver además

* [Nota relacionada](nota-relacionada.md) — para qué sirve esa conexión, en una frase.
```

`tuku note create` agrega a esta sección, con el motivo «mencionada en el cuerpo», cada link local que trae el cuerpo, para que la regla valga sin excepciones. El motivo es mecánico; el autor puede mejorarlo.

Sin el motivo, el enlace es un dato; con él, es una decisión que alguien más puede evaluar sin abrir la otra nota. Dos niveles de exigencia, y son de naturaleza distinta:

- **Que la sección exista y que cada enlace lleve motivo** es verificable sin juicio → `doctor note`.
- **Que el motivo sea pertinente y no relleno** solo lo evalúa quien lee → agente, juicio semántico.

## Inferir sobre terceros

El tipo `persona` carga una regla que los demás no necesitan: **la nota describe a alguien que puede leerla.**

El libro de estilo ya exige que las observaciones sobre el autor se redacten como descripción y nunca como norma. Sobre un tercero eso vale más, y se suma otra: se infiere lo que sirve para trabajar mejor con esa persona, no lo que sirve para juzgarla.

La prueba es simple: **una inferencia que no se le podría mostrar a la persona no va escrita.** Verificarlo no es mecánico: lo hace el agente al redactar, con juicio ético, no un comando.

## Creación y huella en bitácora

Toda creación de nota mediante `tuku note create` deja huella en la bitácora:

- **Escribe la nota:** en `notas/<slug>.md` con frontmatter OKF (`type: Note`). Si la nota es tipada, incluye su campo `subtype`.
- **Estampa constancia:** agrega una línea cronológica en `AHORA.md` registrando la creación de la nota. Ante la omisión de día u hora, los valores por defecto normativos son la fecha actual (**HOY**) y la hora actual (**AHORA**) evaluadas en la zona horaria `TZ` de `reglas/config.tuku.md`.

### Idempotencia y reparación

`tuku note create` es estrictamente idempotente:
- Si el archivo ya existe en `notas/`, respeta su contenido y no lo sobreescribe a ciegas.
- Si la constancia en `AHORA.md` ya existe, la omite y no la duplica.

`tuku doctor note` verifica la estructura de las notas (presencia de frontmatter OKF, existencia de la sección `## Ver además` y motivos en cada enlace saliente). El linter nunca repara por su cuenta: informa el defecto y nombra la corrección exacta, ejecutando los comandos originales para restaurar la consistencia.

## No entra

- **Destilar el histórico y proponer notas nuevas por iniciativa propia**, sin que el uso ya lo haya sugerido. Eso es inferencia semántica, una fase posterior de implementación (ver [`../devel/epics.md`](../devel/epics.md)). Acá solo la mecánica del tejido: crear, tipar, enlazar, indexar.
