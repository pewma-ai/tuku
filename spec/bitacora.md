# spec · bitácora

> La única entrada del sistema. Se justifica por el principio 1 y el principio 3 de [`../docs/principios.md`](../docs/principios.md). El marco que la rodea (por qué el registro termina donde termina) está en [flujo-informacion.md](flujo-informacion.md).

Lo hablado y lo registrado no son lo mismo. El dictado va dirigido a quien lleva la bitácora; la entrada registra el hecho. Son dos registros distintos: el habla es situada y efímera, la entrada tiene que sostenerse sola durante años.

## Cuatro principios

Todo lo demás son ejemplos.

1. **Se registra el hecho, no la conversación.** Fuera lo dirigido a quien escucha, las muletillas y el rodeo. La unidad es el hecho y no la frase: una sola frase puede dar varias entradas. Lo evaluativo tampoco va al cuerpo, elige el tipo.
2. **La entrada se sostiene sola.** Se leerá años después, sin el resto del día ni la conversación que la originó. Deícticos resueltos, personas con su rol la primera vez, tiempo relativo convertido en fecha.
3. **No se agrega lo que no se dijo.** Ni cuantificadores, ni conclusiones, ni pendientes. Lo que el hecho sugiere se propone al autor y se espera su aprobación.
4. **La forma la fija la marca, no el gusto.** `**pendiente**` va en infinitivo y su cierre `~~(Hecho)~~` repite ese mismo texto. Los demás hechos van en pasado y primera persona, y las observaciones vigentes en presente. Registro neutro, sin voseo ni fórmulas de encabezado.

## Formato de la línea

```text
- HH:MM - [[ambito]] ~~(Hecho)~~ **clasificacion**: cuerpo
```

Ámbito y clasificación son opcionales según el contexto. La marca de la ontología cerrada va en la misma posición, antes de la clasificación abierta.

## Ejemplos

**La instrucción no se registra.** Dictado: *"Recuérdame avisar de los GGCC al arrendatario"*

```text
- 09:12 - [[arriendo-depto-centro]] **pendiente**: avisar de los GGCC al arrendatario
```

"Recuérdame" iba dirigido a quien escucha. Desaparece.

**El cierre repite el texto del pendiente.** Dictado: *"Ya le recordé los GGCC al arrendatario"*

```text
- 18:40 - [[arriendo-depto-centro]] ~~(Hecho)~~: avisar de los GGCC al arrendatario
```

No se reescribe en pasado. Se lee como la tarea tachada, y el emparejamiento queda literal en vez de semántico.

**Una frase, varios hechos.** Dictado: *"le avisé de los GGCC, me dijo que este mes no lo hará y eso me está molestando pues se repite"*

```text
- 18:40 - [[arriendo-depto-centro]] ~~(Hecho)~~: avisar de los GGCC al arrendatario
- 18:40 - [[arriendo-depto-centro]] **señal**: el arrendatario respondió que este mes no pagará los GGCC, y se repite
```

El cierre propio y la respuesta del tercero son hechos distintos.

**Lo que el hecho sugiere se propone.** El impago recurrente pide un pendiente de recobro, pero el autor no lo pidió. Se propone y se espera aprobación antes de crearlo.

**La entrada se sostiene sola.** *"salí con mi hijo Mateo el otro día"* no se registra así: Mateo lleva su rol la primera vez que aparece y "el otro día" se convierte en fecha. En tres años nadie va a poder reconstruir ninguna de las dos cosas desde la entrada.

## Ontologías: una cerrada y una abierta

En la misma entrada conviven dos vocabularios de naturaleza distinta. No hay que confundirlos aunque compartan aspecto.

**Cerrada, de TUKU.** `**pendiente**`, `~~(Hecho)~~` y `**cadencia**`. Son **mecánicos**: cada marca es la señal de una consecuencia determinista, y el janitor actúa sobre ella sin interpretar.

Cerrada significa **cerrada para el autor**. No crece con el uso ni la puede extender quien lleva la bitácora. Sí crece cuando el diseño de TUKU incorpora una consecuencia nueva, y eso es una decisión de diseño, no de uso. Hoy son tres.

El costo que la mantiene honesta: la lista vive en el código del linter, así que agrandarla es un cambio de versión de TUKU, no una anotación en un documento.

**Abierta, del autor.** `**progreso**`, `**decisión**`, `**fricción**`, `**señal**`, `**nota**`. Son **semánticos**: ningún janitor actúa sobre ellos. Sirven para leer, filtrar y destilar. Si el autor usa un tipo nuevo se acepta, y en un ciclo posterior se le pregunta qué significa para formalizarlo.

**Dónde vive cada una.** La cerrada es de TUKU: va en el código del linter y el autor no la puede cambiar. Los vocabularios abiertos viven en el `LIBRO-DE-ESTILO.md` del vault del autor (semilla en [`../template/vanilla/LIBRO-DE-ESTILO.md`](../template/vanilla/LIBRO-DE-ESTILO.md)), cada uno bajo su propio encabezado, y de ahí los lee el janitor:

| Vocabulario abierto | Encabezado en el libro de estilo |
| --- | --- |
| Clasificaciones de entrada | `### Clasificaciones` |
| Horizontes de pendientes | `### Horizontes` |
| Tipos de nota | `### Tipos de nota` |

Formalizar un tipo nuevo es agregar una fila bajo el encabezado que corresponda, en un documento en prosa que el autor lee y escribe. No hay segunda copia en ninguna parte, así que **los encabezados son contrato**: renombrarlos rompe al janitor.

Consecuencia directa para el linter: `jntr.entrada-lint` valida la ontología cerrada de forma **estricta** y la abierta de forma **permisiva**. Un tipo desconocido se reporta para preguntar más adelante, nunca se rechaza como error. Un linter que rechaza vocabulario nuevo impide que la organización emerja, que es justo lo que el diseño busca.

**Las dos van en la misma posición**, después del ámbito. La marca cerrada primero, la clasificación abierta después, y ambas son opcionales:

```text
- HH:MM - [[ambito]] ~~(Hecho)~~ **clasificacion**: cuerpo
```

Que compartan zona no las mezcla: se distinguen por su forma. `~~(Hecho)~~` y `**pendiente**` son literales fijos que el janitor reconoce sin ambigüedad, y todo lo demás en esa zona es vocabulario del autor y se trata como abierto. Un cierre puede entonces ser además `**Hito**` sin que ninguna de las dos ontologías pierda su lugar.

## Los dos ganchos deterministas

`**pendiente**` abre, `~~(Hecho)~~` cierra. Van en la misma posición, después del ámbito. En el cierre la clasificación abierta sigue disponible a continuación (`**Hito**`, `**decisión**`) o puede no ir, porque `~~(Hecho)~~` ya señala el cierre por sí solo.

El cuerpo es el mismo en los tres lugares: la entrada que abre, el ítem en `PENDIENTES.md` y la entrada que cierra. Abrir es copiarlo, cerrar es encontrarlo y borrarlo. Ninguna de las dos operaciones interpreta nada. El detalle de esa doble escritura está en [pendientes.md](pendientes.md).

## No entra

- Qué pasa con el cuerpo una vez que llega a `PENDIENTES.md` (escalera de horizontes, vencimiento). Eso es [`pendientes.md`](pendientes.md).
- Cómo se infiere el ámbito o se resuelve la regla más cercana. Eso es [`ambitos.md`](ambitos.md).
- Cómo un agente decide qué inyectar antes de interpretar el dictado. Eso es [`agente.md`](agente.md).
