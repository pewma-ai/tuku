# spec · pendientes

> `PENDIENTES.md` es fuente de verdad, nunca derivado. Se justifica por el principio 9 de [`../docs/principios.md`](../docs/principios.md), con la excepción declarada más abajo.

Ningún pendiente vive fuera de este archivo. Todo lo demás que los muestre (`AHORA.md`, páginas de ámbito, `reportes/`) se deriva de aquí, por propagación o por transclusión.

A cambio exige disciplina, y esa disciplina la sostiene el comando, no la memoria del autor.

## La bitácora es el disparador, no el origen de los datos

- Dictado: *"Recuérdame avisar de los GGCC al arrendatario"*
  - Bitácora: `- 09:12 - [[arriendo-depto-centro]] **pendiente**: avisar de los GGCC al arrendatario`
  - El comando agrega una fila bajo `sin fecha`: `| | [[arriendo-depto-centro]] | avisar de los GGCC al arrendatario |`
- Dictado: *"Ya le recordé los GGCC al arrendatario"*
  - Bitácora: `- 18:40 - [[arriendo-depto-centro]] ~~(Hecho)~~: avisar de los GGCC al arrendatario`
  - El comando borra esa fila

Los dos ganchos son deterministas: `**pendiente**` abre, `~~(Hecho)~~` cierra (ver `bitacora.md`). El cuerpo es el mismo en los tres lugares: el registro que abre, el ítem en `PENDIENTES.md` y el registro que cierra. Abrir es copiarlo, cerrar es encontrarlo y borrarlo. Ninguna de las dos operaciones interpreta nada.

El archivo contiene solo lo abierto. El historial de lo cerrado vive en las bitácoras.

## Formato

Un archivo, un encabezado por horizonte y una tabla debajo. Las columnas son las mismas en todos.

```text
## atrasados

| Cuándo | Ámbito | Detalle |
| --- | --- | --- |
| 2026-04-02 | [[arriendo-depto-centro]] | avisar de los GGCC al arrendatario |

## sin fecha

| Cuándo | Ámbito | Detalle |
| --- | --- | --- |
| | [[personal]] | comprar una maleta |

## esta semana

| Cuándo | Ámbito | Detalle |
| --- | --- | --- |

## con fecha

| Cuándo | Ámbito | Detalle |
| --- | --- | --- |
| 2026-08-14 | [[personal]] | pagar la sesión con el psicólogo |
```

**Cuándo** lleva la fecha exacta cuando el pendiente la tiene y queda vacío cuando no. **Ámbito** es un enlace, o vacío si el pendiente todavía no aterrizó en ninguno. **Detalle** es el cuerpo, el mismo texto que el registro que lo abrió y que el que lo cierre.

Dentro de cada tabla las filas van ordenadas por `Cuándo`, y las que no tienen fecha después. El orden es determinista y la inserción es posicional: un pendiente nuevo no puede reordenar la tabla entera, o el diff del ciclo deja de leerse.

**Los seis encabezados son permanentes**: existen siempre, con su tabla vacía si hace falta, y así la escalera se lee completa de arriba abajo. Tres son de TUKU y no dependen de ningún ritmo (`atrasados`, `sin fecha`, `con fecha`); los tres del medio son del autor, salen de `### Horizontes` en el libro de estilo, y el estado cero los siembra en semanas (`esta semana`, `próxima semana`, `fin de mes`) porque es el ritmo de casi todo el mundo. Un autor que trabaja por turnos los renombra en el libro de estilo y acá.

**No hay encabezados de fecha.** La fecha vive en la columna, no en la estructura, así que agendar no crea ni destruye secciones.

## Escalera de horizontes

Cada pendiente está bajo exactamente un horizonte y baja de escalón a medida que se concreta:

`sin fecha` → `esta semana` / `próxima semana` / `fin de mes` → `con fecha` → cerrado

Con fecha exacta pasa a `con fecha` y aparece bajo el día correspondiente de `AHORA.md`, propagado por un comando.

**Escribir en un día futuro es fecharlo.** Un registro `**pendiente**` escrito bajo un día posterior a hoy en `AHORA.md` abre el pendiente ya con la fecha de ese día, y queda propagado al inicio de ese día. No hay un comando aparte para agendar: agendar es escribir donde corresponde, que es lo que alguien haría en una agenda de papel.

**El día de hoy no fecha**, y va a `sin fecha`. Escribir bajo el día de hoy es el acto por defecto de registrar, no una decisión de agendar: el autor escribe ahí porque hoy es cuando habla. Si eso fechara, todo lo que mencionara quedaría venciendo hoy, que casi nunca es cierto, y `sin fecha` no tendría vía de entrada. Fechar queda como lo que es, un acto deliberado: escribirlo en el día en que toca.

Esto ataja el escalón: un pendiente puede nacer en `con fecha` sin pasar por `sin fecha` ni por un horizonte del autor. La escalera describe cómo se concreta lo que nació difuso, no un camino obligatorio.

El movimiento de escalón **no se registra en la bitácora**: mover un pendiente no es un hecho de la vida del autor, es un hecho del sistema. El comando lo hace por sí mismo (segunda vía, ver [`flujo-informacion.md`](flujo-informacion.md)).

## Dónde se muestra, y cómo llega

`PENDIENTES.md` **no se transcluye**. Sus pendientes están repartidos entre horizontes, así que ningún bloque contiguo contiene lo que una vista necesita, y una transclusión no sabe rebanar por otro eje.

La regla general, que decide los dos casos con un solo criterio:

> **Se transcluye cuando el origen ya agrupa contiguo lo que el destino muestra. Se propaga cuando no.**

| Vista | Cómo llega | Por qué |
| --- | --- | --- |
| El día, en `AHORA.md` | Propagación | Los pendientes de un día están repartidos entre horizontes |
| El ámbito, en su página | Transclusión desde `reportes/pendientes-por-ambito.md` | Ese archivo se genera agrupado por ámbito, así que cada grupo ya es contiguo |

`tuku todo propagate` produce las dos. Es idempotente: correrlo dos veces da el mismo resultado, y sobre un vault cuadrado no cambia nada.

Lo que se gana al propagar en vez de transcluir es que la vista no depende de que un ancla siga existiendo, que era la falla silenciosa de este archivo: un pendiente que existía y no aparecía en su día, y el autor se enteraba cuando ya había vencido. Lo que se pierde es que una copia sí puede quedar vieja. Se compra de vuelta barato, porque una vista derivada se verifica **re-derivando y comparando**, que es una función pura contra su salida.

### La región del día

Dentro de cada `## <día>` de `AHORA.md`, el comando es dueño de **lo que va entre el encabezado y el primer registro**. Ahí escribe los pendientes con fecha de ese día, y al regenerar reemplaza esa región entera.

No hay marca que la delimite, y es a propósito: los registros empiezan siempre por `- HH:MM - `, así que la frontera es estructura visible. Un comentario invisible se rompe al editar el archivo y nadie se entera.

**Consecuencia directa:** no se escribe prosa suelta bajo el encabezado de un día. Lo que quede ahí lo reemplaza la siguiente propagación.

### El archivo por ámbito

`reportes/pendientes-por-ambito.md` es generado y agrupa por ámbito, un encabezado por cada uno. La página de cada ámbito transcluye su sección:

```markdown
![[reportes/pendientes-por-ambito.md#depto-centro]]
```

Se transcluye por **encabezado y no por ancla de bloque**. El archivo lo genera TUKU, así que puede tener exactamente la estructura que la transclusión necesita, y un encabezado se explica solo al abrirlo.

Esa transclusión es **permanente**, no de ciclo, así que no se aplana nunca. El aplanado de [`ciclo.md`](ciclo.md) es de las vistas del ciclo.

## Reglas

1. Un pendiente está en **una sola fila de `PENDIENTES.md`**, siempre. El alcance de la regla es este archivo: lo que aparece en un día o en la página de un ámbito es una vista derivada y no cuenta como segunda aparición. Sin esa distinción, la vista se confunde con el error que la regla prohíbe.
2. Todo pendiente con fecha anterior a HOY pasa a `atrasados`. La fecha no se pierde al moverlo, porque vive en la columna y no en el encabezado.
3. Al cerrar ciclo, lo que quede en el horizonte del ciclo en curso sin fecha rueda al mismo horizonte del ciclo nuevo. Solo lo fechado cae en `atrasados`.
4. **La fecha vive en la columna `Cuándo` y en ningún otro lugar.** No se repite en el detalle ni se codifica en la estructura. La antigüedad se saca del historial de git de `PENDIENTES.md`, que se versiona como fuente.
5. HOY se evalúa en la zona horaria del autor. La VM hereda el TZ del laptop, así que no hay que convertir, pero sí declararlo en `reglas/` para que ningún comando asuma UTC.
6. **Las vistas se regeneran, no se reparan.** Todo lo que muestra un pendiente fuera de `PENDIENTES.md` se deriva de él. Si una vista discrepa de la fuente, la que está mal es la vista, y la corrección es volver a propagar. `tuku todo lint` lo detecta re-derivando y comparando.
7. `PENDIENTES.md` se versiona como fuente. La reconstrucción desde bitácoras no lo regenera ni lo verifica. El conjunto canónico es `AHORA.md` + `bitacoras/` + `PENDIENTES.md` + `ambitos/` + `notas/`, y el principio 9 aplica solo a lo que queda fuera de esa lista.
8. **Dentro de `AHORA.md` conviven las dos naturalezas**, y hay que saber cuál es cuál: los registros son canónicos y la región propagada de cada día es derivada. Es la única parte del conjunto canónico que se puede borrar y regenerar, y por eso está delimitada por estructura visible.

## No entra

- **Las reglas de tratamiento** de pendientes (prioridad, tipos, encadenamiento, criterios de vencimiento más allá de la fecha) van en un documento propio, aún por escribir. Esto cubre solo el modelo.
- **Promover pendientes entre ciclos** en el detalle de apertura/cierre. La mecánica general está aquí (regla 3); la secuencia completa de abrir y cerrar un ciclo está en [`ciclo.md`](ciclo.md).
