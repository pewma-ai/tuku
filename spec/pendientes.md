# spec · pendientes

> `PENDIENTES.md` es fuente de verdad, nunca derivado. Se justifica por el principio 9 de [`../docs/principios.md`](../docs/principios.md), con la excepción declarada más abajo.

Ningún pendiente vive fuera de este archivo. Todo lo demás que los muestre (`AHORA.md`, páginas de ámbito, `reportes/`) se deriva de aquí, por propagación o por transclusión.

A cambio exige disciplina, y esa disciplina la sostiene el comando, no la memoria del autor.

## La bitácora es el disparador, no el origen de los datos

- Dictado: *"Recuérdame avisar de los GGCC al arrendatario"*
  - Bitácora: `- 09:12 - [[arriendo-depto-centro]] **pendiente**: avisar de los GGCC al arrendatario`
  - El comando agrega una fila bajo el horizonte del ciclo en curso, `esta semana` en el template vanilla: `| | [[arriendo-depto-centro]] | avisar de los GGCC al arrendatario |`
- Dictado: *"Ya le recordé los GGCC al arrendatario"*
  - Bitácora: `- 18:40 - [[arriendo-depto-centro]] ~~(Hecho)~~: avisar de los GGCC al arrendatario`
  - El comando borra esa fila

Los dos ganchos son deterministas: `**pendiente**` abre, `~~(Hecho)~~` cierra (ver `bitacora.md`). El cuerpo es el mismo en los tres lugares: el registro que abre, el ítem en `PENDIENTES.md` y el registro que cierra. Abrir es copiarlo, cerrar es encontrarlo y borrarlo. Ninguna de las dos operaciones interpreta nada.

El archivo contiene solo lo abierto. El historial de lo cerrado vive en las bitácoras.

## Formato

Un archivo y una sola tabla con cuatro columnas: `| Horizonte | Cuándo | Ámbito | Detalle |`. El horizonte y la fecha viven en columnas y no en la estructura del documento.

```text
---
type: Pending
---

| Horizonte | Cuándo | Ámbito | Detalle |
| --------- | ------ | ------ | ------- |
| esta semana | | [[arriendo-depto-centro]] | avisar de los GGCC al arrendatario |
| próxima semana | | [[personal]] | comprar una maleta |
| con fecha | 2026-08-14 | [[personal]] | pagar la sesión con el psicólogo |
```

**Horizonte** indica el escalón actual del pendiente. Los del autor salen de `### Horizontes` en el libro de estilo (`esta semana`, `próxima semana`, `fin de mes` en el template vanilla) y `con fecha` es del sistema cuando tiene día asignado.

**Cuándo** lleva la fecha exacta cuando el pendiente la tiene y queda vacío cuando no. **Ámbito** es un enlace, o vacío si el pendiente todavía no aterrizó en ninguno. **Detalle** es el cuerpo, el mismo texto que el registro que lo abrió y que el que lo cierre.

Las filas se insertan ordenadas por la posición del horizonte en la escalera y por `Cuándo`. El orden es determinista y la inserción es posicional: un pendiente nuevo no reordena la tabla entera, preservando un diff limpio.

**No hay encabezados por horizonte ni de fecha.** El horizonte y la fecha viven en columnas, así que mover de escalón o fechar edita una fila existente y nunca crea ni destruye secciones.

**No hay horizonte `atrasados` ni horizonte `sin fecha`.** Estar atrasado es un cálculo sobre datos que la fila ya tiene, no un lugar donde ponerla, y no tener fecha no es un destino sino el estado normal de un pendiente del ciclo en curso.

## Escalera de horizontes

Cada pendiente está bajo exactamente un horizonte y baja de escalón a medida que se concreta:

`esta semana` → `próxima semana` / `fin de mes` → `con fecha` → cerrado

**Los cuatro horizontes son de postergación.** Un pendiente al que el autor no le dice nada queda en el horizonte del ciclo en curso, que es el default: es para ahora. Postergar es el acto deliberado, y consiste en mover la fila a un horizonte más lejano. Antes era al revés, y no decir nada salía gratis: el pendiente caía en un sumidero silencioso donde nadie lo volvía a mirar. Ahora lo caro es callarse, porque lo que no se posterga reclama atención en el ciclo en curso.

Efecto secundario valioso: una lista de deseos hay que postergarla ciclo tras ciclo, y esa fricción repetida es la señal de que no era un pendiente sino una nota. Lo que no tiene "cuándo" y nunca lo va a tener no pertenece a un archivo cuyo eje es el tiempo: va a `notas/` o a la página de su ámbito (ver [`notas.md`](notas.md)).

### Estar atrasado se calcula, no se guarda

Un pendiente está atrasado por dos vías, las dos deducibles de la fila:

- Su `Cuándo` es anterior a HOY.
- No tiene fecha, el ciclo en cuyo horizonte estaba se cerró y sigue abierto: el horizonte expiró.

Guardarlo además como encabezado repetía un dato que la columna `Cuándo` ya tenía, con el riesgo de que las dos copias discreparan. Un comando lo calcula y lo informa; en `PENDIENTES.md` no se mueve nada.

Consecuencia: **ninguna automatización escribe en `PENDIENTES.md` por calendario.** El archivo cambia cuando el autor cambia algo, y no porque pasó la medianoche. Es el principio 3 de [`../docs/principios.md`](../docs/principios.md): una consecuencia mayor no ocurre sin que nadie la aprobara.

Con fecha exacta pasa a `con fecha` y aparece bajo el día correspondiente de `AHORA.md`, propagado por un comando.

**Escribir en un día futuro es fecharlo.** Un registro `**pendiente**` escrito bajo un día posterior a hoy en `AHORA.md` abre el pendiente ya con la fecha de ese día, y queda propagado al inicio de ese día. No hay un comando aparte para agendar: agendar es escribir donde corresponde, que es lo que alguien haría en una agenda de papel.

**El día de hoy no fecha**, y va al horizonte del ciclo en curso. Escribir bajo el día de hoy es el acto por defecto de registrar, no una decisión de agendar: el autor escribe ahí porque hoy es cuando habla. Si eso fechara, todo lo que mencionara quedaría venciendo hoy, que casi nunca es cierto. Fechar queda como lo que es, un acto deliberado: escribirlo en el día en que toca.

Esto ataja el escalón: un pendiente puede nacer en `con fecha` sin pasar por ningún horizonte del autor. La escalera describe cómo se concreta lo que nació difuso, no un camino obligatorio.

El movimiento de escalón **no se registra en la bitácora**: mover un pendiente no es un hecho de la vida del autor, es un hecho del sistema. El comando lo hace por sí mismo (segunda vía, ver [`flujo-informacion.md`](flujo-informacion.md)).

## Dónde se muestra, y cómo llega

`PENDIENTES.md` **no se transcluye**. Sus pendientes están repartidos entre horizontes, así que ningún bloque contiguo contiene lo que una vista necesita, y una transclusión no sabe rebanar por otro eje.

La regla general, que decide los dos casos con un solo criterio:

> **Se transcluye cuando el origen ya agrupa contiguo lo que el destino muestra. Se propaga cuando no.**

| Vista | Cómo llega | Por qué |
| --- | --- | --- |
| El día, en `AHORA.md` | Propagación | Los pendientes de un día están repartidos entre horizontes |
| El ámbito, en su página | Transclusión desde `ambitos/PENDIENTES-AMBITOS.md` | Ese archivo se genera con un callout por ámbito, así que cada grupo ya es contiguo |

`tuku todo propagate` produce las dos. Es idempotente: correrlo dos veces da el mismo resultado, y sobre un vault cuadrado no cambia nada.

Lo que se gana al propagar en vez de transcluir es que la vista no depende de que un ancla siga existiendo, que era la falla silenciosa de este archivo: un pendiente que existía y no aparecía en su día, y el autor se enteraba cuando ya había vencido. Lo que se pierde es que una copia sí puede quedar vieja. Se compra de vuelta barato, porque una vista derivada se verifica **re-derivando y comparando**, que es una función pura contra su salida.

### La región del día

Dentro de cada `## <día>` de `AHORA.md`, el comando es dueño de **lo que va entre el encabezado y el primer registro**. Ahí escribe los pendientes con fecha de ese día dentro de un callout `> [!todo] Pendientes del día` (únicamente si ese día tiene pendientes en `PENDIENTES.md`), y al regenerar reemplaza esa región entera.

No hay marca que la delimite, y es a propósito: los registros empiezan siempre por `- HH:MM - `, así que la frontera es estructura visible. Un comentario invisible se rompe al editar el archivo y nadie se entera.

**Consecuencia directa:** no se escribe prosa suelta bajo el encabezado de un día. Lo que quede ahí lo reemplaza la siguiente propagación.

### El archivo por ámbito

`ambitos/PENDIENTES-AMBITOS.md` es generado y agrupa por ámbito, un callout por cada uno. Vive en `ambitos/` y no en `reportes/` porque no es un reporte: los reportes son documentos fechados, uno por ciclo, que el autor lee y archiva. Este no lleva fecha, se regenera entero cada vez y existe para ser transcluido, así que vive junto a lo que lo consume. MAYÚSCULAS porque lo escribe TUKU.

```markdown
> [!todo] Pendientes en **Personal** ^personal
> - pagar la sesión con el psicólogo
> - comprar una maleta
```

La página del ámbito lo transcluye con ruta relativa:

```markdown
![[../PENDIENTES-AMBITOS.md#^personal]]
```

Se transcluye por **ancla de bloque sobre un callout, y no por encabezado**. El archivo lo genera TUKU, así que puede tener exactamente la estructura que la transclusión necesita, y el callout `> [!todo] Pendientes en **<Nombre>** ^<ambito>` se explica solo en los dos lugares: en el archivo generado y dentro de la página del ámbito que lo transcluye.

El ancla es el nombre del ámbito (sin `.md`). **Hay un callout por cada ámbito del árbol**, no solo por los que tienen pendientes, y un ámbito limpio lleva el suyo con el texto `SIN PENDIENTES`:

```markdown
> [!todo] Pendientes en **Depto Centro** ^depto-centro
> SIN PENDIENTES
```

Eso es lo más importante del diseño: el ancla existe **siempre**, así que ninguna página de ámbito queda apuntando a un ancla que no existe. Esa era exactamente la falla silenciosa que este rediseño persigue, la de una vista que desaparece sin avisar. Un callout que dice `SIN PENDIENTES` es información y no ausencia: le confirma al autor que ese ámbito está limpio, en vez de dejarlo dudando si la vista se rompió.

Esa transclusión es **permanente**, no de ciclo, así que no se aplana nunca. El aplanado de [`ciclo.md`](ciclo.md) es de las vistas del ciclo.

## Lo que rueda queda escrito

La cadencia de apertura del ciclo (ver [`cadencias.md`](cadencias.md) y `template/vanilla/ambitos/CADENCIAS.md`) deja en el `AHORA.md` recién abierto la constancia de qué pendientes rodaron desde el ciclo anterior al horizonte del ciclo en curso.

Un pendiente que rueda de ciclo en ciclo se vuelve invisible por costumbre, y lo que hace visible la reincidencia es que quede escrito en el ciclo donde reaparece. Además la cadena se lee de punta a punta sin recalcular nada: el ciclo cerrado dice qué se llevó consigo, el ciclo nuevo dice qué heredó.

## Reglas

1. Un pendiente está en **una sola fila de `PENDIENTES.md`**, siempre. El alcance de la regla es este archivo: lo que aparece en un día o en la página de un ámbito es una vista derivada y no cuenta como segunda aparición. Sin esa distinción, la vista se confunde con el error que la regla prohíbe.
2. **Nada se mueve por vencimiento.** Estar atrasado se calcula desde la fila, por `Cuándo` anterior a HOY o por horizonte expirado, y un comando lo informa sin tocar `PENDIENTES.md`. Guardar el atraso como encabezado duplicaba lo que la columna ya decía.
3. Al cerrar ciclo, lo que quede sin fecha en el horizonte del ciclo en curso rueda al mismo horizonte del ciclo nuevo, y **rodar deja rastro**: la apertura marca en el `AHORA.md` recién abierto qué pendientes se trajeron desde el ciclo anterior.
4. Al cerrar ciclo, la bitácora que queda archivada deja constancia de qué pendientes quedaron atrasados. Es un snapshot y no rompe la fuente única, por el mismo argumento con que [`ciclo.md`](ciclo.md) aplana el plan: al cerrar nada sigue vivo.
5. **La fecha vive en la columna `Cuándo` y en ningún otro lugar.** No se repite en el detalle ni se codifica en la estructura. La antigüedad se saca del historial de git de `PENDIENTES.md`, que se versiona como fuente.
6. HOY se evalúa en la zona horaria del autor, la que declara `TZ` en `reglas/config.tuku.md`. La VM hereda el TZ del laptop, así que no hay que convertir, pero sí declararlo para que ningún comando asuma UTC.
7. **Las vistas se regeneran, no se reparan.** Todo lo que muestra un pendiente fuera de `PENDIENTES.md` se deriva de él. Si una vista discrepa de la fuente, la que está mal es la vista, y la corrección es volver a propagar. `tuku todo lint` lo detecta re-derivando y comparando.
8. `PENDIENTES.md` se versiona como fuente. La reconstrucción desde bitácoras no lo regenera ni lo verifica. El conjunto canónico es `AHORA.md` + `bitacoras/` + `PENDIENTES.md` + `ambitos/` + `notas/`, y el principio 9 aplica solo a lo que queda fuera de esa lista.
9. **Dentro de `AHORA.md` conviven las dos naturalezas**, y hay que saber cuál es cuál: los registros son canónicos y la región propagada de cada día es derivada. Es la única parte del conjunto canónico que se puede borrar y regenerar, y por eso está delimitada por estructura visible.

## No entra

- **Las reglas de tratamiento** de pendientes (prioridad, tipos, encadenamiento, criterios de vencimiento más allá de la fecha) van en un documento propio, aún por escribir. Esto cubre solo el modelo.
- **Promover pendientes entre ciclos** en el detalle de apertura/cierre. La mecánica general está aquí (regla 3); la secuencia completa de abrir y cerrar un ciclo está en [`ciclo.md`](ciclo.md).
