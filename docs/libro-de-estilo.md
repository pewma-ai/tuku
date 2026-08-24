# TUKU: Libro de estilo

> Este documento gobierna el libro del autor: cómo se escribe y cómo se organiza. Lo lee el autor y lo leen los agentes. Empieza conciso a propósito. Lo que falte irá apareciendo con el uso, y los agentes lo propondrán.

### Los tres archivos principales

**`BITACORA.md`** — lo que pasó. Una línea por hecho, con fecha y hora. Inmutable: si algo cambió, se escribe una nueva línea.

**`PENDIENTES.md`** — lo que falta, y solo lo que falta. No se edita a mano: se actualiza de forma determinista según las entradas de la bitácora.

**Las notas** — lo que se entendió. Viven en la carpeta del ámbito correspondiente y tienen formato libre.

### Cómo se escribe una línea de bitácora

```
ámbito: tipo — lo que pasó
```

Ejemplos:

```
pyme: progreso — despaché el pedido de la [[Escuela San Marcos]], falta la factura
casa: nota — llamé al gásfiter, viene el jueves
```

Los cinco tipos canónicos:

| Tipo | Cuándo |
|---|---|
| `progreso` | Avance concreto en una tarea o proyecto |
| `decisión` | Elección fundamentada y su justificación |
| `fricción` | Bloqueo o costo mayor al esperado |
| `señal` | Observación temprana que aún no madura |
| `nota` | Registro general que no calza en los anteriores |

Si el autor utiliza un tipo nuevo, el sistema lo acepta y en un ciclo posterior el agente preguntará su significado para formalizarlo.

### Pendientes

Los pendientes se abren y se cierran escribiendo en la bitácora, nunca editando el archivo `PENDIENTES.md` directamente:

```
casa: nota — recordar comprar pintura antes del fin de mes
casa: progreso — compré la pintura, quedó en el garaje
```

La primera entrada abre el pendiente; la segunda lo cierra y lo consolida como hecho en la bitácora. Si el sistema no tiene certeza sobre la correspondencia entre ambas, solicita confirmación.

### Enlaces

Se utiliza `[[nombre]]` para referenciar entidades con página propia: un cliente, un proyecto, una persona o una reunión.

Se recomienda enlazar de manera generosa. El valor emerge en el mediano plazo, cuando cualquier página permite navegar hacia su contexto original.

### Ámbitos

Los ámbitos son carpetas y representan la estructura de los frentes de actividad del autor.

```
ámbitos/
  personal/
    personal.md
```

El repositorio inicia solo con `personal/`. Cuando se registran hechos ajenos a ese ámbito, el agente propone crear una nueva rama —`trabajo/`, un cliente, un proyecto— y el árbol crece de forma orgánica: `trabajo/observatorio/proyecto-x`.

Cada ámbito cuenta con una página principal (`personal.md`) que define su naturaleza y alcance. Un cliente externo no opera igual que un proyecto interno; esa página proporciona el contexto necesario tanto a personas como a agentes.

Cumplen tres propósitos:

- **Archivar:** cuando un frente concluye, se archiva la rama completa.
- **Definir reglas:** un `AGENTS.md` dentro de una carpeta aplica a toda su descendencia. La regla más específica prevalece.
- **Suspender:** marcar temporalmente una rama como inactiva (*vacaciones, pausar seguimiento de trabajo*).

### Observaciones sobre el autor

A partir del registro continuo, el agente destila notas como *El modelo de cliente en la Pyme* o *Proyectos internos de software*, documentando patrones de trabajo observados.

Se redactan siempre como observaciones descriptivas, nunca como normas prescriptivas. El autor puede editarlas o corregirlas en cualquier momento.

### Ver además

Al pie de las páginas de referencia se incluye una lista de enlaces **acompañados del motivo explícito de la conexión**. El motivo es tan relevante como el enlace: garantiza recuperar la línea de razonamiento años después.

Los documentos generados automáticamente no llevan sección "Ver además".

---

### Reglas

Especificación verificable del libro de estilo. Cada regla declara explícitamente su ejecutor: un proceso determinista (*janitor*) o un agente de IA.

| Regla | Responsable |
|---|---|
| Toda línea de bitácora tiene fecha, hora, ámbito y tipo | janitor |
| Todo pendiente abierto se origina en una línea de bitácora | janitor |
| Todo `[[enlace]]` resuelve a una página existente | janitor |
| Ninguna entrada de bitácora queda sin ámbito | janitor |
| Un pendiente que se cierra corresponde al que se abrió | agente |
| Las páginas de referencia llevan "Ver además" con motivo explícito | agente |
| Las notas sobre el autor están redactadas como observación | agente |

Esta tabla se amplía cuando una práctica se consolida como invariante. Si una regla no cabe aquí de forma directa, aún no califica como regla del sistema.