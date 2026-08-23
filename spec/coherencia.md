# spec · coherencia, janitors y configuración

## El libro de estilo como fuente

El libro de estilo es el **único punto de edición humana** de las convenciones. Todo lo demás se deriva:

| Derivado | Naturaleza | Autonomía |
|---|---|---|
| Reglas de coherencia semántica | Sistematización formal del libro de estilo | Agente redacta, autor ratifica |
| `AGENTS.md` | Markdown, lenguaje propio | Agente, automático |
| `tuku.yaml` | Configuración única del repositorio | Se edita el libro de estilo; un janitor verifica consistencia |
| Código de janitors | Código fuente | Agente, con red de seguridad |

Compilar prosa en reglas verificables no es trivial. Es probablemente el punto de mayor esfuerzo real del proyecto y hay que presupuestarlo como tal.

### AGENTS.md no es el libro de estilo

Requieren lenguajes distintos. Pueden coincidir en partes, pero no se garantiza. El criterio de éxito 7 exige que `AGENTS.md` sea **legible por el autor un domingo**, no que sea idéntico al libro de estilo.

## Reglas de coherencia semántica

**Definición.** Son la sistematización lo más formal posible del libro de estilo: las mismas convenciones, expresadas de manera verificable y aplicable.

El libro de estilo **no puede ser un sistema formal** — es de consumo humano. La formalidad la absorben sus derivados, y por eso las reglas se bifurcan:

| Brazo | Cuándo | Ejecutor |
|---|---|---|
| Formalizable | La regla se verifica o se aplica sin juicio | **Janitor** |
| No formalizable | La regla requiere criterio, pero de baja carga cognitiva — las decisiones más aburridas | **Agente** |

El eje que separa los brazos es *«¿se puede verificar sin juicio?»*, no la importancia de la regla. **Cada regla escrita en el libro de estilo declara a qué brazo pertenece.**

El criterio de éxito 4 es el test: si algo que debía ser idéntico tras reconstruir solo resulta equivalente, hay juicio del agente donde correspondía una regla — la regla está en el brazo equivocado.

### Vecindad

Al modificar un archivo, el sistema determina mediante el grafo **la vecindad cercana** a revisar. Nunca el repositorio completo. Esto exige un diseño juicioso de las reglas, que en el fondo no son distintas del manual que se le daría a un escriba humano.

La transclusión pesa más que un wikilink en ese grafo.

## Janitors

Un janitor es **cualquier proceso determinista que le quite carga mecánica a un agente**. En la práctica, es el motor determinista completo:

- Proyectar `PENDIENTES.md` desde la bitácora.
- Generar resúmenes por período y por concepto.
- Disparar cadencias y alertar sobre pendientes críticos.
- Extraer vocabulario, ámbitos y áreas.
- Componer transclusiones.
- Detectar inconsistencias y referencias rotas.
- Revalidar marcas de autoría.
- Verificar consistencia entre libro de estilo y `tuku.yaml`.
- Arbitrar turnos del canal (ver `../agentes.md`).

### Configuración

**Un solo archivo YAML por repositorio de autor.** No se edita directamente: se edita el libro de estilo, y un janitor verifica que el YAML sea consistente con él.

El libro de estilo contiene una **transclusión** del fragmento YAML correspondiente, no una copia — dos copias serían dos fuentes de verdad y el janitor solo podría detectar la divergencia, no prevenirla.

Se toca el código lo mínimo posible: la lógica vive en la configuración. El YAML pasa a ser tan crítico como el parser y requiere validación de esquema.

### Red de seguridad

El mismo agente que puede fallar interpretando la bitácora es el que reescribe el parser que la lee. Un error ahí no queda contenido en una nota: corrompe silenciosamente la lectura de años de archivos.

**Todo cambio al parser —propio o descargado desde el repositorio principal de TUKU— corre contra el corpus de regresión antes de aceptarse.** Ver `../corpus-regresion/`.

### Actualización

Existe un agente encargado de actualizar el código de los janitors, y un mecanismo para bajar los janitors más recientes desde el repositorio principal de TUKU.

**Decisión abierta:** ¿un janitor descargado desde upstream se aplica solo, o pasa por la misma regresión que un cambio local?

## Decisión abierta

¿Es «janitor» el nombre de todo el motor determinista, o de una parte? Hoy se usa como sinónimo del motor completo.
