# spec · bitácora

> La única entrada del sistema. Se justifica por el principio 1 y el principio 3 de [`../docs/principios.md`](../docs/principios.md). El marco que la rodea (por qué el registro termina donde termina) está en [flujo-informacion.md](flujo-informacion.md).

Lo hablado y lo registrado no son lo mismo. El dictado va dirigido a quien lleva la bitácora; el registro captura el hecho. Son dos cosas distintas: el habla es situada y efímera, el registro tiene que sostenerse solo durante años.

## Cuatro principios

Todo lo demás son ejemplos.

1. **Se registra el hecho, no la conversación.** Fuera lo dirigido a quien escucha, las muletillas y el rodeo. La unidad es el hecho y no la frase: una sola frase puede dar varios registros. Lo evaluativo tampoco va al cuerpo, elige el tipo.
2. **El registro se sostiene solo.** Se leerá años después, sin el resto del día ni la conversación que lo originó. Deícticos resueltos, personas con su rol la primera vez, tiempo relativo convertido en fecha.
3. **No se agrega lo que no se dijo.** Ni cuantificadores, ni conclusiones, ni pendientes. Lo que el hecho sugiere se propone al autor y se espera su aprobación.
4. **La forma la fija la marca, no el gusto.** `**pendiente**` va en infinitivo y su cierre `(Hecho)` repite ese mismo texto. Los demás hechos van en pasado y primera persona, y las observaciones vigentes en presente. Registro neutro, sin voseo ni fórmulas de encabezado.

## Formato de la línea

```text
- HH:MM - [ambito](ruta) (Hecho) **clasificacion**: ~~cuerpo~~
```

Ámbito y clasificación son opcionales según el contexto, y la hora también en un día pasado (ver abajo). La marca de la ontología cerrada va en la misma posición, antes de la clasificación abierta.

El ámbito es un **link Markdown cuya ruta es relativa al archivo que contiene la línea**, y la calcula `tuku` a partir del árbol de `ambitos/`: un ámbito anidado lleva su ruta completa (`ambitos/trabajo/pewma/pewma.md`). Quien dicta pasa el nombre; nadie escribe la ruta. Sin `--scope`, `tuku entry create`, `tuku todo open` y `tuku todo close` usan el `scope_default` de `reglas/config.tuku.md`. En `AHORA.md`, que vive en la raíz, es `[arriendo-depto-centro](ambitos/arriendo-depto-centro/arriendo-depto-centro.md)`. Los lectores aceptan también el wikilink `[[ambito]]` hasta que `tuku fix link` lo convierte ([markdown.md](markdown.md)).

### De dónde salen el día y la hora

**El día y la hora no vienen del dictado**: se derivan de la jornada que el dictado describe, y eso es juicio de quien registra, no lectura mecánica (ver [`../corpus/referencia/referencia-faena.md`](../corpus/referencia/referencia-faena.md), Parte 2).

Cuando quien invoca no proporciona el día o la hora (o no se pueden derivar), los valores por defecto son:
- **El día:** la fecha actual (**HOY**), situando el registro bajo la sección correspondiente al día de hoy en `AHORA.md`.
- **La hora:** si el día es hoy, la hora actual (**AHORA**), con formato `HH:MM`. Si el día es pasado, el registro va sin hora, al final de ese día: `- [colegio-los-robles](ambitos/negocio/clientes/colegio-los-robles/colegio-los-robles.md) llamé a Rodolfo`. La hora de hoy en un día pasado sería inventada.

Ambos se evalúan en la zona horaria que declara `TZ` en `reglas/config.tuku.md`. Ninguno se elige por plausible: o se deriva del dictado, o es el momento actual, o la hora queda en blanco. Son los dos únicos campos del registro con valor por defecto, y por eso están declarados acá y no quedan a criterio del comando (ver [cli.md](cli.md)).

Para ordenar, un registro sin hora toma la del registro anterior de su día: el siguiente que llega con hora se ubica a continuación si su hora es igual o mayor.

## Ejemplos

**La instrucción no se registra.** Dictado: *"Recuérdame avisar de los GGCC al arrendatario"*

```text
- 09:12 - [arriendo-depto-centro](ambitos/arriendo-depto-centro/arriendo-depto-centro.md) **pendiente**: avisar de los GGCC al arrendatario
```

"Recuérdame" iba dirigido a quien escucha. Desaparece.

**El cierre repite el texto del pendiente.** Dictado: *"Ya le recordé los GGCC al arrendatario"*

```text
- 18:40 - [arriendo-depto-centro](ambitos/arriendo-depto-centro/arriendo-depto-centro.md) (Hecho): ~~avisar de los GGCC al arrendatario~~
```

No se reescribe en pasado. Se lee como la tarea tachada, y el emparejamiento queda literal en vez de semántico.

**Una frase, varios hechos.** Dictado: *"le avisé de los GGCC, me dijo que este mes no lo hará y eso me está molestando pues se repite"*

```text
- 18:40 - [arriendo-depto-centro](ambitos/arriendo-depto-centro/arriendo-depto-centro.md) (Hecho): ~~avisar de los GGCC al arrendatario~~
- 18:40 - [arriendo-depto-centro](ambitos/arriendo-depto-centro/arriendo-depto-centro.md) **señal**: el arrendatario respondió que este mes no pagará los GGCC, y se repite
```

El cierre propio y la respuesta del tercero son hechos distintos.

**Lo que el hecho sugiere se propone.** El impago recurrente pide un pendiente de recobro, pero el autor no lo pidió. Se propone y se espera aprobación antes de crearlo.

**El registro se sostiene solo.** *"salí con mi hijo Mateo el otro día"* no se registra así: Mateo lleva su rol la primera vez que aparece y "el otro día" se convierte en fecha. En tres años nadie va a poder reconstruir ninguna de las dos cosas desde el registro.

## Ontologías: una cerrada y una abierta

En el mismo registro conviven dos vocabularios de naturaleza distinta. No hay que confundirlos aunque compartan aspecto.

**Cerrada, de TUKU.** `**pendiente**`, `(Hecho)` y `**cadencia**`. Son **mecánicos**: cada marca es la señal de una consecuencia determinista, y el comando actúa sobre ella sin interpretar.

Cerrada significa **cerrada para el autor**. No crece con el uso ni la puede extender quien lleva la bitácora. Sí crece cuando el diseño de TUKU incorpora una consecuencia nueva, y eso es una decisión de diseño, no de uso. Hoy son tres.

El costo que la mantiene honesta: la lista vive en el código del linter, así que agrandarla es un cambio de versión de TUKU, no una anotación en un documento.

**Abierta, del autor.** `**progreso**`, `**decisión**`, `**fricción**`, `**señal**`, `**nota**`. Son **semánticos**: ningún comando actúa sobre ellos. Sirven para leer, filtrar y destilar. Si el autor usa un tipo nuevo se acepta, y en un ciclo posterior se le pregunta qué significa para formalizarlo.

**Dónde vive cada una.** La cerrada es de TUKU: va en el código del linter y el autor no la puede cambiar. Los vocabularios abiertos viven en el `LIBRO-DE-ESTILO.md` del vault del autor (semilla en [`../template/vanilla/LIBRO-DE-ESTILO.md`](../template/vanilla/LIBRO-DE-ESTILO.md)), cada uno bajo su propio encabezado, y de ahí los lee el comando:

| Vocabulario abierto | Encabezado en el libro de estilo |
| --- | --- |
| Clasificaciones de registro | `### Clasificaciones` |
| Horizontes de pendientes | `### Horizontes` |
| Tipos de nota | `### Tipos de nota` |

Formalizar un tipo nuevo es agregar una fila bajo el encabezado que corresponda, en un documento en prosa que el autor lee y escribe. No hay segunda copia en ninguna parte, así que **los encabezados son contrato**: renombrarlos rompe al comando.

Ese contrato es el que hay y **no crece**. Los tres vocabularios viven en el libro de estilo porque son estilo: lo que el autor elige para escribir. Cualquier **dato nuevo que una automatización necesite** no se agrega aquí, va a la sección de datos de `reglas/config.tuku.md`, y el libro de estilo lo transcluye si el autor necesita verlo mientras escribe. Así el dato tiene un solo lugar donde se edita y el libro de estilo sigue leyéndose como prosa.

Así es hoy; cuando el libro pase a ser estático, cada tabla vive en su archivo de `reglas/` y el comando lee ese archivo ([vault.md](vault.md), "El libro de estilo"). El comando lee la estructura visible del libro de estilo, nunca una marca invisible ([markdown.md](markdown.md), "Datos de máquina en estructura visible"), y la ausencia del encabezado es un error ruidoso.

Consecuencia directa para el linter: `tuku doctor entry` valida la ontología cerrada de forma **estricta** y la abierta de forma **permisiva**. Un tipo desconocido se reporta para preguntar más adelante, nunca se rechaza como error. Un linter que rechaza vocabulario nuevo impide que la organización emerja, que es justo lo que el diseño busca.

**Las dos van en la misma posición**, después del ámbito. La marca cerrada primero, la clasificación abierta después, y ambas son opcionales:

```text
- HH:MM - [ambito](ruta) (Hecho) **clasificacion**: ~~cuerpo~~
```

Que compartan zona no las mezcla: se distinguen por su forma. `(Hecho)` y `**pendiente**` son literales fijos que el comando reconoce sin ambigüedad, y todo lo demás en esa zona es vocabulario del autor y se trata como abierto. Un cierre puede entonces ser además `**Hito**` sin que ninguna de las dos ontologías pierda su lugar.

## Los dos ganchos deterministas

`**pendiente**` abre, `(Hecho)` cierra. Van en la misma posición, después del ámbito. En el cierre la clasificación abierta sigue disponible a continuación (`**Hito**`, `**decisión**`) o puede no ir, porque `(Hecho)` ya señala el cierre por sí solo.

**En el cierre, la marca queda a la vista y lo tachado es el cuerpo:** `(Hecho): ~~avisar de los GGCC~~`. Lo tachado es lo que ya se hizo. Quien cierra pasa `(Hecho): avisar de los GGCC` y el comando escribe la tachadura, para que a quien dicta no le toque saber dónde va. La marca tachada, `~~(Hecho)~~: cuerpo`, no es válida: `tuku doctor entry` la reporta con su corrección.

El cuerpo es el mismo en los tres lugares: el registro que abre, el ítem en `PENDIENTES.md` y el registro que cierra. Abrir es copiarlo, cerrar es encontrarlo y borrarlo. **Los links no cuentan al encontrarlo:** el mismo pendiente puede llevar `[Carmen](notas/carmen.md)` en la bitácora y `Carmen` en la tabla, o al revés, y se busca comparando el texto que queda al quitar los links. Ninguna de las dos operaciones interpreta nada. Si el cierre cae el mismo día que la apertura, queda solo el cierre. El detalle de esa doble escritura está en [pendientes.md](pendientes.md).

## Corregir un registro ya escrito

Un registro se ubica con `--match TEXTO`, obligatorio: un fragmento de su cuerpo actual. El comando corrige el último registro de `AHORA.md` que calza, que es el caso común: el autor dijo tres cosas a las 07:00 y "no era eso" habla de la última. Si el que se corrige es otro, un fragmento más largo lo distingue. Para un registro de un ciclo cerrado, el posicional `CUÁNDO` (`2026-08-10` o `"2026-08-10 18:40"`) dice dónde buscar.

| Comando | Cambia | Conserva | Dónde |
| --- | --- | --- | --- |
| `tuku entry update [CUÁNDO] --match … --body …` | el cuerpo, y la fila de `PENDIENTES.md` si es un pendiente, para que el cierre lo siga encontrando | la hora y el ámbito | `AHORA.md` |
| `tuku entry move [CUÁNDO] --match … --scope …` | el ámbito, y el de la fila de `PENDIENTES.md` si es un pendiente abierto ([ambitos.md](ambitos.md), "Lo escrito antes de abrir un ámbito") | la hora y el cuerpo | `AHORA.md` y las bitácoras cerradas |

Hoy existe `tuku entry rename --at … --body …`, que ubica por la hora; `entry update` y `entry move` están en [`../TODO.md`](../TODO.md).

Los dos son correcciones: arreglan el registro en su lugar, la bitácora queda con el registro corregido y nada más, y el historial de git guarda la versión anterior. Los dos son idempotentes: si el registro ya dice eso, lo informan y salen con 0.

## No entra

- Qué pasa con el cuerpo una vez que llega a `PENDIENTES.md` (escalera de horizontes, vencimiento). Eso es [`pendientes.md`](pendientes.md).
- Cómo se infiere el ámbito o se resuelve la regla más cercana. Eso es [`ambitos.md`](ambitos.md).
- Cómo un agente decide qué inyectar antes de interpretar el dictado. Eso es [`agente.md`](agente.md).
